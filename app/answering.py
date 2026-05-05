"""Answer composition layer.

This module formats responses for the `/chat` endpoint. It prefers an
LLM (OpenAI) when `OPENAI_API_KEY` is set, but falls back to concise
extractive answers constructed from `SourceCitation` excerpts. The
engine is intentionally small so teams can swap in other providers.
"""

from __future__ import annotations

import json
import re
from typing import Sequence
from urllib import request

from .schemas import SourceCitation
from .settings import Settings


class AnswerEngine:
    """Compose a final answer given a question and retrieved sources.

    - `answer()` returns a (answer_text, provider) tuple where provider is
      one of: `none`, `extractive`, or `openai`.
    - `is_out_of_scope()` implements a simple heuristic used by the API
      to mark when the system should be honest about missing information.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def answer(self, question: str, sources: Sequence[SourceCitation]) -> tuple[str, str]:
        if not sources:
            return "I couldn't find relevant information in the corpus.", "none"

        uncertainty_prefix = self._uncertainty_prefix(sources)
        has_strong_evidence = self._has_strong_evidence(sources)
        has_period_overlap = self._has_period_overlap(question, sources)

        if self.settings.openai_api_key:
            try:
                answer = self._answer_with_openai(question, sources)
                # If strong evidence exists but the model still refuses, return an
                # extractive fallback to keep behavior stable across model variance.
                if (has_strong_evidence or has_period_overlap) and self.is_out_of_scope(answer):
                    return self._extractive_answer(question, sources, uncertainty_prefix), "extractive"
                if uncertainty_prefix and not self.is_out_of_scope(answer) and not self._has_uncertainty_language(answer):
                    answer = f"{uncertainty_prefix} {answer}"
                return answer, "openai"
            except Exception as e:
                # Failures with the remote LLM should not crash the service;
                # fall back to extractive behavior so the API remains usable.
                import sys
                print(f"ERROR: OpenAI call failed: {e}", file=sys.stderr)
                pass

        return self._extractive_answer(question, sources, uncertainty_prefix), "extractive"

    def is_out_of_scope(self, answer: str) -> bool:
        """Heuristic to detect LLM refusals or honest 'not found' replies.

        Returns True when the answer is an explicit refusal or states the
        information is not present in the corpus. This keeps the API's
        `out_of_scope` flag aligned with natural LLM phrasing instead of a
        single exact prefix.
        """
        if not answer:
            return True

        text = answer.strip().lower()

        # Fast-path for legacy exact match
        if text.startswith("i couldn't find relevant information"):
            return True

        refusal_phrases = [
            "couldn't find",
            "could not find",
            "couldn't locate",
            "not in the corpus",
            "not in the provided sources",
            "not stated",
            "do not state",
            "does not state",
            "not mentioned",
            "do not mention",
            "does not mention",
            "no relevant information",
            "no supporting information",
            "insufficient information",
            "insufficient evidence",
            "do not support an answer",
            "does not support an answer",
            "sources do not support",
            "can't support",
            "cannot support",
            "i can't determine",
            "i cannot determine",
            "i can't find",
            "i cannot find",
            "i don't see",
            "i do not see",
            "unable to determine",
            "cannot determine",
            "can't determine",
            "not available in the provided sources",
            "not available in provided sources",
            "cannot be determined",
            "can't be determined",
            "not enough information",
        ]

        for phrase in refusal_phrases:
            if phrase in text:
                return True

        return False

    def _extractive_answer(self, question: str, sources: Sequence[SourceCitation], uncertainty_prefix: str | None = None) -> str:
        """Produce a short, citation-first answer from the provided sources."""
        if len(sources) == 1:
            source = sources[0]
            answer = (
                f"The most relevant material is in {source.citation_label}. "
                f"{source.excerpt}"
            )
            if uncertainty_prefix:
                return f"{uncertainty_prefix} {answer}"
            return answer

        intro = "The corpus points to these relevant passages:"
        bullets = [
            f"- {source.citation_label}: {source.excerpt}"
            for source in sources[: self.settings.max_sources]
        ]
        if uncertainty_prefix:
            intro = f"{uncertainty_prefix} {intro}"
        return "\n".join([intro, *bullets])

    def _uncertainty_prefix(self, sources: Sequence[SourceCitation]) -> str | None:
        if not sources:
            return None

        top_score = max(float(source.score) for source in sources)
        text_blob = " ".join(
            [
                source.excerpt.lower()
                + " "
                + source.citation_label.lower()
                + " "
                + (source.section or "").lower()
                for source in sources
            ]
        )

        cues = ["censor", "not disclosed", "redacted"]
        limited_cue_hits = sum(1 for cue in cues if cue in text_blob)
        has_strong_evidence = self._has_strong_evidence(sources)

        # Only add a partial-evidence prefix when signals are genuinely weak.
        # A single incidental cue should not downgrade otherwise strong answers.
        if limited_cue_hits >= 2 and not has_strong_evidence:
            return "The available evidence is partial, so this answer is directional rather than definitive."
        if top_score < max(self.settings.similarity_threshold + 0.16, 0.32):
            return "Evidence is limited for this question, so treat this as a best-effort summary."
        return None

    def _has_strong_evidence(self, sources: Sequence[SourceCitation]) -> bool:
        if not sources:
            return False
        top_score = max(float(source.score) for source in sources)
        avg_score = sum(float(source.score) for source in sources) / len(sources)
        return top_score >= 0.46 or avg_score >= 0.40

    def _has_period_overlap(self, question: str, sources: Sequence[SourceCitation]) -> bool:
        years = set(re.findall(r"\b(20\d{2})\b", (question or "").lower()))
        quarter_years = set(
            f"q{quarter} {year}" for quarter, year in re.findall(r"\bq([1-4])\s*(20\d{2})\b", (question or "").lower())
        )
        if not years and not quarter_years:
            return False
        source_periods = [str(source.reporting_period or "").lower() for source in sources]
        for period in source_periods:
            if quarter_years and any(qy in period for qy in quarter_years):
                return True
            if years and any(year in period for year in years):
                return True
        return False

    def _has_uncertainty_language(self, answer: str) -> bool:
        text = (answer or "").lower()
        phrases = [
            "not enough information",
            "insufficient",
            "cannot be determined",
            "can't be determined",
            "limited evidence",
            "partial",
            "directional",
            "not disclosed",
        ]
        return any(phrase in text for phrase in phrases)

    def _answer_with_openai(self, question: str, sources: Sequence[SourceCitation]) -> str:
        """Call OpenAI Chat Completions to synthesize a concise, source-grounded reply.

        The implementation is intentionally minimal; teams may replace it
        with the official SDK or another provider as needed.
        """
        source_lines = []
        for index, source in enumerate(sources, start=1):
            source_lines.append(
                f"[{index}] {source.citation_label}\n"
                f"Excerpt: {source.excerpt}"
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You answer questions over private equity quarterly report summaries. "
                    "Use only the provided sources. If the answer is not supported, say so. "
                    "Be concise, answer in plain English, and cite each factual claim with bracketed numbers like [1] or [2]."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Sources:\n{chr(10).join(source_lines)}\n\n"
                    "Write a direct answer grounded in the sources."
                ),
            },
        ]

        payload = {
            "model": self.settings.openai_model,
            "messages": messages,
            "temperature": self.settings.temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        api_request = request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(api_request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"].strip()