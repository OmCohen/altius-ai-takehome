# Altius AI Take-Home

This repository contains a chatbot for PE quarterly report summaries. It loads the provided corpus, retrieves relevant evidence with a hybrid pipeline, and returns answers in a browser UI with citations to source summaries and reporting periods.

If you are reviewing the submission, start with [SUBMISSION.md](SUBMISSION.md).

## Setup and Run

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` if you want model-generated answers.
2. Start the app with:

```bash
docker compose up --build
```

3. Open `http://localhost:8000`.

The app also works without an API key. In that mode, it returns an extractive, citation-first response from retrieved passages.

## Assignment Requirement Mapping

- Single command startup: `docker compose up --build`
- Browser chat interface: served at `http://localhost:8000`
- Grounded answers with citations: each answer includes source metadata and reporting periods
- Out-of-scope behavior: unsupported questions return an explicit refusal instead of fabricated answers
- Environment-variable keys only: see `.env.example` (no real keys committed)

## Architecture

The system is split into four layers:

1. Corpus loading: [app/corpus.py](app/corpus.py) reads `data/metadata.csv` and the markdown summaries, normalizes dates, and chunks each document by heading.
2. Query routing: [app/query_router.py](app/query_router.py) classifies greeting/smalltalk/off-topic vs corpus finance questions so retrieval runs only when needed.
3. Retrieval: [app/retrieval.py](app/retrieval.py) and [app/hybrid_retriever.py](app/hybrid_retriever.py) use a hybrid pipeline over chunk text plus metadata, with temporal intent checks (year/quarter/early-mid-late).
4. Answering/API: [app/answering.py](app/answering.py) and [app/main.py](app/main.py) return either OpenAI-grounded answers or extractive answers, and normalize out-of-scope refusals.

The browser UI lives in [app/templates/index.html](app/templates/index.html), with styling and behavior in [app/static/styles.css](app/static/styles.css) and [app/static/app.js](app/static/app.js).

## Key Design Decisions and Tradeoffs

- Retrieval runs in-process (no external vector DB) because the corpus is small. This reduces infrastructure complexity and improves debuggability, at the cost of fewer large-scale indexing features.
- Hybrid retrieval (lexical + embeddings) improves recall on paraphrased questions versus pure TF-IDF, with modest additional compute cost.
- A lightweight intent router handles greetings and off-topic prompts before retrieval. This avoids unnecessary retrieval calls and improves conversational UX.
- Temporal intent checks (year/quarter/early-mid-late phrasing) prevent answers from being grounded in clearly mismatched periods.

The app is retrieval-first and citation-first. If retrieval does not surface relevant support, it refuses clearly rather than inventing an answer.

Citation labels are standardized so the reporting period, source file, and summary file stay aligned across the API and UI.

OpenAI support is optional and controlled by environment variables. This keeps the app usable in a local or offline review while still allowing higher-quality synthesis when an API key is available.

## Evaluation Plan

With more time, evaluation would be expanded to a larger labeled set across lookup, trend, temporal, and out-of-scope prompts; retrieval and answer quality would be scored separately; and citation precision/recall would be tracked explicitly. Automated threshold sweeps for temporal and confidence gating would be added to calibrate refusal vs answer tradeoffs.

## Known Limitations and Next Improvements

The current retrieval stack is still lightweight and in-memory, so quality depends on tuning heuristics (score thresholds, temporal checks, and token coverage). Very nuanced analyst-style synthesis can still be shallow when evidence is sparse.

The summaries are already censored, so some financial questions can only be answered at a high level. The app handles that honestly, but a richer source corpus would improve usefulness.

Planned improvements:

- Better section-aware weighting by question intent (strategy vs risk vs performance)
- Optional reranker model for tighter top-citation precision
- More robust paraphrase handling and query rewrite for analyst-style language
- Expanded regression set with more temporal edge cases and adversarial out-of-scope prompts
