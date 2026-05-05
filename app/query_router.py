"""Question routing utilities.

This module separates casual/off-topic chat from corpus-grounded finance
questions. The goal is to avoid unnecessary retrieval calls and provide
clear, human responses for greetings and non-finance prompts.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class RouteDecision:
    route: str
    answer: str | None = None


GREETING_PATTERN = re.compile(
    r"^\s*(hi|hello|hey|yo|good morning|good afternoon|good evening|sup|what's up)\b[\s!.?]*$",
    re.IGNORECASE,
)

SMALLTALK_PATTERN = re.compile(
    r"\b(how are you|who are you|what can you do|thanks|thank you)\b",
    re.IGNORECASE,
)

FINANCE_KEYWORDS = {
    "fund",
    "portfolio",
    "valuation",
    "valuations",
    "nav",
    "strategy",
    "risk",
    "governance",
    "quarter",
    "q1",
    "q2",
    "q3",
    "q4",
    "credit",
    "facility",
    "subscription",
    "dividend",
    "manager",
    "lp",
    "performance",
    "fair value",
    "deployment",
    "exit",
}

FINANCE_PHRASES = {
    "credit facility",
    "capital call",
    "fair value",
    "net asset value",
    "private equity",
    "reporting period",
}


def route_question(question: str) -> RouteDecision:
    text = (question or "").strip()
    lowered = text.lower()
    if not text:
        return RouteDecision(route="empty", answer="Ask a question about the quarterly reports and I will help.")

    if GREETING_PATTERN.match(text):
        return RouteDecision(
            route="greeting",
            answer=(
                "Hi. I can help with questions about the fund's quarterly reports "
                "(strategy, valuations, NAV trends, risks, and operations)."
            ),
        )

    if SMALLTALK_PATTERN.search(lowered) and not _looks_finance_related(lowered):
        return RouteDecision(
            route="smalltalk",
            answer=(
                "I am here to analyze the quarterly report corpus. Ask me about fund "
                "strategy, valuations, NAV changes, credit facility usage, or cross-quarter trends."
            ),
        )

    if _looks_finance_related(lowered):
        return RouteDecision(route="finance")

    return RouteDecision(
        route="offtopic",
        answer=(
            "That seems outside the report corpus scope. I can help with finance/report "
            "questions tied to the provided quarterly summaries."
        ),
    )


def _looks_finance_related(text: str) -> bool:
    tokens = {token.lower() for token in re.findall(r"\w+", text)}
    keyword_hits = sum(1 for keyword in FINANCE_KEYWORDS if keyword in tokens)
    phrase_hit = any(phrase in text for phrase in FINANCE_PHRASES)
    has_period_hint = bool(re.search(r"\b20\d{2}\b", text) or re.search(r"\bq[1-4]\b", text))

    if phrase_hit:
        return True
    if keyword_hits >= 2:
        return True
    if has_period_hint and keyword_hits >= 1:
        return True

    return False
