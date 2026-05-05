"""Hybrid retrieval: lexical TF-IDF + semantic embeddings + optional reranker.

This module implements a middle-ground hybrid retrieval strategy:
- Use existing TF-IDF to get an initial candidate set (fast, precise).
- If available, score candidates with semantic embeddings and combine
  lexical + semantic scores to improve recall for paraphrases.
- If a CrossEncoder is available, rerank the final candidates for
  highest relevance.

The app uses this retriever directly. If the ML dependencies are missing,
startup should fail rather than silently falling back to a weaker path.
"""

from __future__ import annotations

import logging
import re
from typing import List

import numpy as np

from sentence_transformers import CrossEncoder, SentenceTransformer

from .retrieval import Retriever
from .schemas import SourceCitation

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retriever combining TF-IDF + embeddings + optional reranker.

    Parameters
    - `corpus`: Corpus instance (same as used by `Retriever`).
    - `tfidf_top_k`: how many lexical candidates to fetch before semantic stage.
    - `embed_weight`: weight given to embedding score when combining (0-1).
    - `embedding_model_name`: sentence-transformers model to use.
    - `reranker_model_name`: CrossEncoder model name (optional).
    """

    def __init__(
        self,
        corpus,
        tfidf_top_k: int = 50,
        embed_weight: float = 0.7,
        min_final_score: float = 0.2,
        min_source_coverage: float = 0.35,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        reranker_model_name: str | None = None,
    ):
        self.corpus = corpus
        self.base = Retriever(corpus)
        self.tfidf_top_k = tfidf_top_k
        self.embed_weight = float(embed_weight)
        self.min_final_score = float(min_final_score)
        self.min_source_coverage = float(min_source_coverage)

        self.embedding_model = SentenceTransformer(embedding_model_name)
        texts = [chunk.searchable_text for chunk in corpus.chunks]
        self.corpus_embeddings = np.array(self.embedding_model.encode(texts, show_progress_bar=False))
        logger.info("Loaded embedding model '%s' and encoded corpus (%d).", embedding_model_name, len(texts))

        self.reranker = CrossEncoder(reranker_model_name) if reranker_model_name else None
        if self.reranker is not None:
            logger.info("Loaded reranker model '%s'", reranker_model_name)

    def search(self, question: str, top_k: int = 8, max_sources: int = 3) -> List[SourceCitation]:
        cleaned = question.strip()
        if not cleaned:
            return []
        signal_tokens = self._signal_tokens(cleaned)
        temporal_request = self._temporal_request(cleaned)
        period_hints = self.base._period_hints(cleaned)

        # Stage 1: lexical TF-IDF candidate retrieval (use vectorizer/matrix from Retriever)
        qvec = self.base.vectorizer.transform([cleaned])
        from sklearn.metrics.pairwise import cosine_similarity

        lexical_scores = cosine_similarity(qvec, self.base.matrix).ravel()
        candidate_idxs = lexical_scores.argsort()[::-1][: self.tfidf_top_k]

        # Prepare candidate objects and scores
        candidates = []
        for idx in candidate_idxs:
            score = float(lexical_scores[idx])
            candidates.append((idx, score))

        # Stage 2: semantic re-scoring (if embeddings available)
        q_emb = np.array(self.embedding_model.encode([cleaned], show_progress_bar=False))[0]
        cand_embs = self.corpus_embeddings[[idx for idx, _ in candidates]]
        emb_sims = (cand_embs @ q_emb) / (
            np.linalg.norm(cand_embs, axis=1) * (np.linalg.norm(q_emb) + 1e-12)
        )
        combined = []
        for (idx, lex_score), emb_score in zip(candidates, emb_sims):
            combined_score = float(self.embed_weight * float(emb_score) + (1 - self.embed_weight) * float(lex_score))
            chunk = self.corpus.chunks[idx]
            if period_hints and self.base._matches_hint(chunk.reporting_period, chunk.date, period_hints):
                combined_score += 0.08
            combined.append((idx, combined_score))
        candidates = sorted(combined, key=lambda t: t[1], reverse=True)

        # Stage 3: optional cross-encoder rerank (if available)
        if self.reranker is not None:
            # prepare pairs
            pairs = []
            for idx, _ in candidates[: top_k * 3]:
                chunk = self.corpus.chunks[idx]
                pairs.append((cleaned, chunk.text))
            rerank_scores = self.reranker.predict(pairs)
            reranked = []
            for (idx, _), rscore in zip(candidates[: top_k * 3], rerank_scores):
                reranked.append((idx, float(rscore)))
            candidates = sorted(reranked, key=lambda t: t[1], reverse=True)

        # Convert top candidates to SourceCitation via same heuristics as Retriever
        best_by_document: dict[str, dict] = {}
        for idx, score in candidates[: top_k]:
            if score < self.min_final_score:
                continue
            chunk = self.corpus.chunks[idx]
            existing = best_by_document.get(chunk.document_id)
            if existing is None or score > existing["score"]:
                best_by_document[chunk.document_id] = {
                    "chunk": chunk,
                    "score": score,
                }

        ranked_sources = sorted(best_by_document.values(), key=lambda item: item["score"], reverse=True)[:max_sources]
        if not self._matches_temporal_request(temporal_request, ranked_sources):
            return []
        if self._should_reject_match(signal_tokens, ranked_sources):
            return []

        results: List[SourceCitation] = []
        for item in ranked_sources:
            chunk = item["chunk"]
            results.append(
                SourceCitation(
                    document_id=chunk.document_id,
                    summary_file=chunk.summary_file,
                    source_file=chunk.source_file,
                    reporting_period=chunk.reporting_period,
                    date=chunk.date,
                    deal_name=chunk.deal_name,
                    section=chunk.section,
                    citation_label=self._citation_label(chunk.reporting_period, chunk.source_file, chunk.section),
                    excerpt=self.base._excerpt(chunk.text, cleaned),
                    score=round(float(item["score"]), 4),
                )
            )
        return results

    def _signal_tokens(self, question: str) -> set[str]:
        return {
            token.lower()
            for token in re.findall(r"\w+", question)
            if len(token) > 2
        }

    def _should_reject_match(self, signal_tokens: set[str], sources: list[dict]) -> bool:
        if not sources:
            return True

        top_score = float(sources[0]["score"])
        if top_score >= max(self.min_final_score + 0.12, 0.28):
            return False

        combined_text = " ".join(
            " ".join(
                [
                    item["chunk"].text.lower(),
                    (item["chunk"].section or "").lower(),
                    item["chunk"].reporting_period.lower(),
                    item["chunk"].source_file.lower(),
                ]
            )
            for item in sources
        )
        if not signal_tokens:
            return top_score < max(self.min_final_score + 0.06, 0.24)

        matched = sum(1 for token in signal_tokens if token in combined_text)
        coverage = matched / max(1, len(signal_tokens))
        return coverage < self.min_source_coverage and top_score < max(self.min_final_score + 0.12, 0.28)

    def _temporal_request(self, question: str) -> dict:
        text = (question or "").lower()
        quarter_year = re.findall(r"\bq([1-4])\s*(20\d{2})\b", text, flags=re.IGNORECASE)
        years = set(re.findall(r"\b(20\d{2})\b", text))
        early_years = set(re.findall(r"\bearly\s+(20\d{2})\b", text))
        mid_years = set(re.findall(r"\bmid\s+(20\d{2})\b", text))
        late_years = set(re.findall(r"\blate\s+(20\d{2})\b", text))
        across_years = set(re.findall(r"\bacross\s+(20\d{2})\b", text))
        between_years = re.findall(r"\bbetween\s+(20\d{2})\s+and\s+(20\d{2})\b", text)
        for start, end in between_years:
            years.add(start)
            years.add(end)
        years.update(across_years)
        return {
            "quarter_year": {(f"Q{q}".upper(), y) for q, y in quarter_year},
            "years": years,
            "early_years": early_years,
            "mid_years": mid_years,
            "late_years": late_years,
        }

    def _matches_temporal_request(self, temporal_request: dict, sources: list[dict]) -> bool:
        if not sources:
            return False
        if not temporal_request:
            return True

        source_periods = [
            str(item["chunk"].reporting_period or "").upper()
            for item in sources
            if item.get("chunk") is not None
        ]
        if not source_periods:
            return False

        source_quarter_year = set()
        source_years = set()
        for period in source_periods:
            match = re.search(r"\bQ([1-4])\s+(20\d{2})\b", period)
            if match:
                q, y = match.groups()
                source_quarter_year.add((f"Q{q}", y))
                source_years.add(y)
            else:
                year_match = re.search(r"\b(20\d{2})\b", period)
                if year_match:
                    source_years.add(year_match.group(1))

        expected_qy = temporal_request.get("quarter_year", set())
        if expected_qy and not any(qy in source_quarter_year for qy in expected_qy):
            return False

        expected_years = temporal_request.get("years", set())
        if expected_years and not expected_years.issubset(source_years):
            return False

        for year in temporal_request.get("early_years", set()):
            if not any((q, y) in source_quarter_year for q, y in [("Q1", year), ("Q2", year)]):
                return False
        for year in temporal_request.get("mid_years", set()):
            if not any((q, y) in source_quarter_year for q, y in [("Q2", year), ("Q3", year)]):
                return False
        for year in temporal_request.get("late_years", set()):
            if not any((q, y) in source_quarter_year for q, y in [("Q3", year), ("Q4", year)]):
                return False

        return True

    def _citation_label(self, reporting_period: str, source_file: str, section: str | None) -> str:
        parts = [reporting_period, source_file]
        if section:
            parts.append(section)
        return " | ".join(parts)
