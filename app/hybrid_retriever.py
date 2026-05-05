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
        embedding_model_name: str = "all-MiniLM-L6-v2",
        reranker_model_name: str | None = None,
    ):
        self.corpus = corpus
        self.base = Retriever(corpus)
        self.tfidf_top_k = tfidf_top_k
        self.embed_weight = float(embed_weight)

        self.embedding_model = SentenceTransformer(embedding_model_name)
        texts = [chunk.searchable_text for chunk in corpus.chunks]
        self.corpus_embeddings = np.array(self.embedding_model.encode(texts, show_progress_bar=False))
        logger.info("Loaded embedding model '%s' and encoded corpus (%d).", embedding_model_name, len(texts))

        self.reranker = CrossEncoder(reranker_model_name) if reranker_model_name else None
        if self.reranker is not None:
            logger.info("Loaded reranker model '%s'", reranker_model_name)

    def search(self, question: str, top_k: int = 8, max_sources: int = 4) -> List[SourceCitation]:
        cleaned = question.strip()
        if not cleaned:
            return []

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
            if score <= 0:
                continue
            chunk = self.corpus.chunks[idx]
            existing = best_by_document.get(chunk.document_id)
            if existing is None or score > existing["score"]:
                best_by_document[chunk.document_id] = {
                    "chunk": chunk,
                    "score": score,
                }

        ranked_sources = sorted(best_by_document.values(), key=lambda item: item["score"], reverse=True)[:max_sources]
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
                    excerpt=chunk.text[:360].strip(),
                    score=round(float(item["score"]), 4),
                )
            )
        return results

    def _citation_label(self, reporting_period: str, source_file: str, section: str | None) -> str:
        parts = [reporting_period, source_file]
        if section:
            parts.append(section)
        return " | ".join(parts)
