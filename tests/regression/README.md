# Regression Suite

This folder contains a small behavior regression suite for the chat stack.

## What it checks

Each labeled case defines expected behavior against `/chat` response fields:

- `out_of_scope`
- minimum number of citations (`min_sources`)
- required answer terms (`must_contain_any` / `must_contain_all`)
- expected citation reporting periods (`source_period_any`)

This avoids brittle exact-string matching while still catching meaningful regressions.

## Files

- `cases.json`: 7 labeled Q&A cases.
- `run_regression.py`: harness that executes cases and scores pass/fail.
- `latest_report.md`: generated report with expected vs actual behavior.

## Run

From the repository root:

```bash
python tests/regression/run_regression.py
```

By default, this uses `internal` mode (imports `app.main.chat` directly).

Optional HTTP mode (requires running server):

```bash
python tests/regression/run_regression.py --mode http --base-url http://localhost:8000
```

Keep regression cases small and representative. Add new cases when fixing bugs so they do not return.
