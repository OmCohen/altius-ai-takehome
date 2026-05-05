"""Pydantic request/response models used by the API.

Keep models minimal and well-typed so clients and tests can rely on a
stable contract. Add fields here when the API evolves.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class SourceCitation(BaseModel):
    """Represents a single retrieved source with an excerpt and score.

    Clients should display `citation_label`, `summary_file`, and `excerpt`
    when showing citations; `score` is a diagnostic float.
    """
    document_id: str
    summary_file: str
    source_file: str
    reporting_period: str
    date: str
    deal_name: str | None = None
    section: str | None = None
    citation_label: str
    excerpt: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
    out_of_scope: bool = False
    provider: str