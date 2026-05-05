from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import request


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class CheckResult:
    name: str
    passed: bool
    expected: str
    actual: str


def load_cases(cases_path: Path) -> list[dict[str, Any]]:
    with cases_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list) or not data:
        raise ValueError("cases file must contain a non-empty list")
    return data


def call_internal(question: str) -> dict[str, Any]:
    from app.main import chat
    from app.schemas import ChatRequest

    response = chat(ChatRequest(question=question))
    if hasattr(response, "model_dump"):
        return response.model_dump()
    return response.dict()


def call_http(base_url: str, question: str) -> dict[str, Any]:
    payload = json.dumps({"question": question}).encode("utf-8")
    req = request.Request(
        f"{base_url.rstrip('/')}/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def contains_token(text: str, token: str) -> bool:
    return token.lower() in text.lower()


def periods_match_any(actual_periods: list[str], expected_tokens: list[str]) -> bool:
    if not expected_tokens:
        return True
    normalized_periods = [period.lower() for period in actual_periods]
    return any(any(token.lower() in period for period in normalized_periods) for token in expected_tokens)


def evaluate_case(case: dict[str, Any], response: dict[str, Any]) -> tuple[bool, list[CheckResult], dict[str, Any]]:
    expected = case.get("expected", {})
    answer = str(response.get("answer", ""))
    out_of_scope = bool(response.get("out_of_scope", False))
    sources = response.get("sources", []) or []

    source_periods = [str(source.get("reporting_period", "")) for source in sources]
    source_labels = [str(source.get("citation_label", "")) for source in sources]

    checks: list[CheckResult] = []

    expected_out_of_scope = bool(expected.get("out_of_scope", False))
    checks.append(
        CheckResult(
            name="out_of_scope",
            passed=(out_of_scope == expected_out_of_scope),
            expected=str(expected_out_of_scope),
            actual=str(out_of_scope),
        )
    )

    min_sources = int(expected.get("min_sources", 0))
    checks.append(
        CheckResult(
            name="min_sources",
            passed=(len(sources) >= min_sources),
            expected=f">={min_sources}",
            actual=str(len(sources)),
        )
    )

    must_contain_any = [str(item) for item in expected.get("must_contain_any", [])]
    if must_contain_any:
        checks.append(
            CheckResult(
                name="must_contain_any",
                passed=any(contains_token(answer, token) for token in must_contain_any),
                expected=" OR ".join(must_contain_any),
                actual=answer[:220].replace("\n", " "),
            )
        )

    must_contain_all = [str(item) for item in expected.get("must_contain_all", [])]
    if must_contain_all:
        checks.append(
            CheckResult(
                name="must_contain_all",
                passed=all(contains_token(answer, token) for token in must_contain_all),
                expected=" AND ".join(must_contain_all),
                actual=answer[:220].replace("\n", " "),
            )
        )

    forbidden_terms = [str(item) for item in expected.get("forbidden_terms", [])]
    if forbidden_terms:
        checks.append(
            CheckResult(
                name="forbidden_terms",
                passed=all(not contains_token(answer, token) for token in forbidden_terms),
                expected="none of: " + ", ".join(forbidden_terms),
                actual=answer[:220].replace("\n", " "),
            )
        )

    source_period_any = [str(item) for item in expected.get("source_period_any", [])]
    if source_period_any:
        checks.append(
            CheckResult(
                name="source_period_any",
                passed=periods_match_any(source_periods, source_period_any),
                expected=" OR ".join(source_period_any),
                actual=", ".join(source_periods) if source_periods else "none",
            )
        )

    passed = all(check.passed for check in checks)

    actual_summary = {
        "provider": response.get("provider", "unknown"),
        "out_of_scope": out_of_scope,
        "source_count": len(sources),
        "source_periods": source_periods,
        "source_labels": source_labels,
        "answer_preview": answer[:350].replace("\n", " "),
    }

    return passed, checks, actual_summary


def format_check_failures(checks: list[CheckResult]) -> str:
    failures = [check for check in checks if not check.passed]
    if not failures:
        return "None"
    chunks = []
    for fail in failures:
        chunks.append(
            f"- {fail.name}: expected {fail.expected}; actual {fail.actual}"
        )
    return "<br>".join(chunks)


def render_report(
    mode: str,
    cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
    output_path: Path,
) -> None:
    passed_count = sum(1 for result in results if result["passed"])
    total = len(results)

    lines: list[str] = []
    lines.append("# Regression Test Report")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Mode: {mode}")
    lines.append(f"- Cases: {total}")
    lines.append(f"- Passed: {passed_count}")
    lines.append(f"- Failed: {total - passed_count}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Case | Label | Result |")
    lines.append("|---|---|---|")
    for result in results:
        icon = "PASS" if result["passed"] else "FAIL"
        lines.append(f"| {result['id']} | {result['label']} | {icon} |")

    lines.append("")
    lines.append("## Expected vs Actual")
    lines.append("")

    for case, result in zip(cases, results):
        expected = case.get("expected", {})
        actual = result["actual_summary"]
        lines.append(f"### {case['id']} - {case['label']}")
        lines.append("")
        lines.append(f"- Question: {case['question']}")
        lines.append(
            "- Expected behavior: "
            f"out_of_scope={expected.get('out_of_scope', False)}, "
            f"min_sources={expected.get('min_sources', 0)}, "
            f"required_terms_any={expected.get('must_contain_any', [])}, "
            f"source_period_any={expected.get('source_period_any', [])}"
        )
        lines.append(
            "- Actual behavior: "
            f"out_of_scope={actual['out_of_scope']}, "
            f"source_count={actual['source_count']}, "
            f"provider={actual['provider']}, "
            f"source_periods={actual['source_periods']}"
        )
        lines.append(f"- Actual answer preview: {actual['answer_preview']}")
        lines.append(f"- Result: {'PASS' if result['passed'] else 'FAIL'}")
        lines.append(f"- Failed checks: {format_check_failures(result['checks'])}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run regression checks for /chat behavior.")
    parser.add_argument(
        "--cases",
        default="tests/regression/cases.json",
        help="Path to the labeled regression cases JSON file.",
    )
    parser.add_argument(
        "--mode",
        choices=["internal", "http"],
        default="internal",
        help="Execution mode: internal imports app.main.chat; http calls a running server.",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL used only in http mode.",
    )
    parser.add_argument(
        "--output",
        default="tests/regression/latest_report.md",
        help="Where to write the markdown report.",
    )
    parser.add_argument(
        "--no-fail-on-mismatch",
        action="store_true",
        help="Return exit code 0 even if one or more cases fail.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases_path = Path(args.cases)
    output_path = Path(args.output)

    cases = load_cases(cases_path)
    results: list[dict[str, Any]] = []

    for case in cases:
        question = str(case.get("question", "")).strip()
        if not question:
            raise ValueError(f"case {case.get('id', '<unknown>')} has empty question")

        if args.mode == "internal":
            response = call_internal(question)
        else:
            response = call_http(args.base_url, question)

        passed, checks, actual_summary = evaluate_case(case, response)
        results.append(
            {
                "id": case.get("id", ""),
                "label": case.get("label", ""),
                "passed": passed,
                "checks": checks,
                "actual_summary": actual_summary,
            }
        )

        print(
            f"[{case.get('id', '?')}] {'PASS' if passed else 'FAIL'} - "
            f"{case.get('label', '')}"
        )

    render_report(args.mode, cases, results, output_path)
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    failed = total - passed
    print(f"\nSummary: {passed}/{total} passed, {failed} failed")
    print(f"Report written to: {output_path}")

    if failed and not args.no_fail_on_mismatch:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Regression run failed: {exc}", file=sys.stderr)
        raise
