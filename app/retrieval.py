"""Retrieval utilities: lightweight TF-IDF retriever with simple heuristics.

This module implements a small, explainable retrieval layer used to rank
and excerpt passages from the pre-chunked corpus. It is intentionally
simple (TF-IDF + cosine similarity) so teams can reproduce results and
debug relevance decisions without opaque model embeddings.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .corpus import Corpus
from .schemas import SourceCitation


YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
QUARTER_PATTERN = re.compile(r"\bQ([1-4])(?:\s*(20\d{2}))?\b", re.IGNORECASE)
GENERIC_STOPWORDS = {
    "about",
    "also",
    "between",
    "could",
    "describe",
    "does",
    "during",
    "fund",
    "funds",
    "have",
    "how",
    "manager",
    "policy",
    "quarter",
    "quarterly",
    "report",
    "reports",
    "should",
    "tell",
    "that",
    "their",
    "there",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
}


@dataclass(frozen=True)
class RetrievedChunk:
    summary_file: str
    source_file: str
    reporting_period: str
    date: str
    deal_name: str | None
    section: str
    excerpt: str
    score: float


class Retriever:
    """TF-IDF based retriever with small relevance heuristics.

    Keep this component deterministic and dependency-light so other teams
    can run it locally. Tuning knobs are `similarity_threshold`, `top_k`
    and `max_sources` provided to `search()`.
    """

    def __init__(self, corpus: Corpus, similarity_threshold: float = 0.08):
        self.corpus = corpus
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=12000)
        self.matrix = self.vectorizer.fit_transform([chunk.searchable_text for chunk in corpus.chunks])

    def search(self, question: str, top_k: int = 8, max_sources: int = 4) -> list[SourceCitation]:
        cleaned = question.strip()
        if not cleaned:
            return []
        signal_tokens = self._signal_tokens(cleaned)
        query_vector = self.vectorizer.transform([cleaned])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        scores = self._boost_period_hints(cleaned, scores)
        ranked_indexes = scores.argsort()[::-1]
        best_by_document: dict[str, RetrievedChunk] = {}
        for index in ranked_indexes[:top_k]:
            score = float(scores[index])
            if score < self.similarity_threshold:
                continue
            chunk = self.corpus.chunks[index]
            existing = best_by_document.get(chunk.document_id)
            if existing is None or score > existing.score:
                best_by_document[chunk.document_id] = RetrievedChunk(
                    summary_file=chunk.summary_file,
                    source_file=chunk.source_file,
                    reporting_period=chunk.reporting_period,
                    date=chunk.date,
                    deal_name=chunk.deal_name,
                    section=chunk.section,
                    excerpt=self._excerpt(chunk.text, cleaned),
                    score=score,
                )
        ranked_sources = sorted(best_by_document.values(), key=lambda item: item.score, reverse=True)[:max_sources]
        if self._should_reject_match(signal_tokens, ranked_sources):
            return []
        return [
            SourceCitation(
                document_id=item.summary_file.replace("_summary_public.md", ""),
                summary_file=item.summary_file,
                source_file=item.source_file,
                reporting_period=item.reporting_period,
                date=item.date,
                deal_name=item.deal_name,
                section=item.section,
                citation_label=self._citation_label(item.reporting_period, item.source_file, item.section),
                excerpt=item.excerpt,
                score=round(item.score, 4),
            )
            for item in ranked_sources
        ]

    def _citation_label(self, reporting_period: str, source_file: str, section: str | None) -> str:
        parts = [reporting_period, source_file]
        if section:
            parts.append(section)
        return " | ".join(parts)

    def _signal_tokens(self, question: str) -> set[str]:
        tokens = {
            token.lower()
            for token in re.findall(r"\w+", question)
            if len(token) > 2 and token.lower() not in GENERIC_STOPWORDS
        }
        return tokens

    def _should_reject_match(self, signal_tokens: set[str], sources: list[RetrievedChunk]) -> bool:
        if not sources:
            return True
        top_score = sources[0].score
        if top_score >= 0.22:
            return False
        if not signal_tokens:
            return top_score < 0.15

        combined_text = " ".join(
            " ".join(
                [
                    source.excerpt.lower(),
                    source.section.lower(),
                    source.reporting_period.lower(),
                    source.source_file.lower(),
                ]
            )
            for source in sources
        )
        matched = sum(1 for token in signal_tokens if token in combined_text)
        coverage = matched / max(1, len(signal_tokens))
        return coverage < 0.35 and top_score < 0.22

    def _boost_period_hints(self, question: str, scores):
        hints = self._period_hints(question)
        if not hints:
            return scores
        boosted = scores.copy()
        for index, chunk in enumerate(self.corpus.chunks):
            if self._matches_hint(chunk.reporting_period, chunk.date, hints):
                boosted[index] = min(1.0, boosted[index] + 0.15)
        return boosted

    def _period_hints(self, question: str) -> set[str]:
        hints: set[str] = set()
        for year in YEAR_PATTERN.findall(question):
            hints.add(year)
        for quarter, year in QUARTER_PATTERN.findall(question):
            if year:
                hints.add(f"Q{quarter} {year}")
                hints.add(year)
            else:
                hints.add(f"Q{quarter}")
        return hints

    def _matches_hint(self, reporting_period: str, date: str, hints: set[str]) -> bool:
        if reporting_period in hints:
            return True
        if any(hint == date[:4] for hint in hints if len(hint) == 4 and hint.isdigit()):
            return True
        quarter = reporting_period.split()[0] if reporting_period else ""
        year = reporting_period.split()[1] if len(reporting_period.split()) > 1 else ""
        if quarter in hints and year in hints:
            return True
        return False

    def _excerpt(self, text: str, question: str, max_chars: int = 360) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " ").strip())
        if not sentences:
            return text[:max_chars].strip()
        tokens = {token.lower() for token in re.findall(r"\w+", question) if len(token) > 2}
        scored: list[tuple[int, str]] = []
        for sentence in sentences:
            lowered = sentence.lower()
            overlap = sum(1 for token in tokens if token in lowered)
            scored.append((overlap, sentence))
        scored.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
        chosen = [sentence for score, sentence in scored[:2] if score > 0]
        if not chosen:
            chosen = sentences[:2]
        excerpt = " ".join(chosen).strip()
        return excerpt[:max_chars].strip()