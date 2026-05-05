# Submission Notes

This repository is arranged so a reviewer can get to the main behavior quickly.

## Start Here

1. [README.md](README.md) for setup, architecture, and tradeoffs.
2. [app/main.py](app/main.py) for the FastAPI wiring.
3. [tests/regression/run_regression.py](tests/regression/run_regression.py) for the evaluation harness.
4. [tests/regression/latest_report.md](tests/regression/latest_report.md) for the current baseline regression snapshot.

## Run

```bash
docker compose up --build
```

Then open `http://localhost:8000`.

If you want the regression report:

```bash
python tests/regression/run_regression.py
```

## Submission Scope

- FastAPI app with corpus loading, routing, retrieval, and answer generation.
- Browser chat UI with citation display.
- Regression harness and baseline report for review.
- Environment-variable configuration via `.env.example`.

## Notes

- `.env` and local caches are ignored.
- Generated regression snapshots beyond the baseline report are ignored.
- The implementation intentionally prefers grounded refusals over speculation.