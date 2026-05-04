"""Answer composition layer.

This module formats responses for the `/chat` endpoint. It prefers an
LLM (OpenAI) when `OPENAI_API_KEY` is set, but falls back to concise
extractive answers constructed from `SourceCitation` excerpts. The
engine is intentionally small so teams can swap in other providers.
"""

from __future__ import annotations

import json
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

        if self.settings.openai_api_key:
            try:
                return self._answer_with_openai(question, sources), "openai"
            except Exception as e:
                # Failures with the remote LLM should not crash the service;
                # fall back to extractive behavior so the API remains usable.
                import sys
                print(f"ERROR: OpenAI call failed: {e}", file=sys.stderr)
                pass

        return self._extractive_answer(question, sources), "extractive"

    def is_out_of_scope(self, answer: str) -> bool:
        return answer.strip().lower().startswith("i couldn't find relevant information")

    def _extractive_answer(self, question: str, sources: Sequence[SourceCitation]) -> str:
        """Produce a short, citation-first answer from the provided sources."""
        if len(sources) == 1:
            source = sources[0]
            return (
                f"The most relevant material is in {source.reporting_period} ({source.summary_file}, {source.section}). "
                f"{source.excerpt}"
            )

        intro = "The corpus points to these relevant passages:"
        bullets = [
            f"- {source.reporting_period} ({source.section}): {source.excerpt}"
            for source in sources[: self.settings.max_sources]
        ]
        return "\n".join([intro, *bullets])

    def _answer_with_openai(self, question: str, sources: Sequence[SourceCitation]) -> str:
        """Call OpenAI Chat Completions to synthesize a concise, source-grounded reply.

        The implementation is intentionally minimal; teams may replace it
        with the official SDK or another provider as needed.
        """
        source_lines = []
        for index, source in enumerate(sources, start=1):
            source_lines.append(
                f"[{index}] {source.reporting_period} | {source.summary_file} | {source.section}\n"
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