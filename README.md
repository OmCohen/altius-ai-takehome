# Altius AI Take-Home

This repository contains a working chat app for the quarterly report summaries. The app loads the corpus, retrieves the most relevant sections with a hybrid retriever, and answers in a browser with citations to the summary files and reporting periods.

## Run

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` if you want model-generated answers.
2. Start the app with:

```bash
docker compose up --build
```

3. Open `http://localhost:8000`.

The app also works without an API key. In that mode, it returns an extractive, citation-first answer from the retrieved passages.

## Architecture

The system is split into four small layers:

1. Corpus loading: [app/corpus.py](app/corpus.py) reads `data/metadata.csv` and the markdown summaries, normalizes dates, and chunks each document by heading.
2. Retrieval: [app/retrieval.py](app/retrieval.py) and [app/hybrid_retriever.py](app/hybrid_retriever.py) use a hybrid retrieval pipeline over chunk text plus metadata, with a light bias toward the reporting period mentioned in the question.
3. Answering: [app/answering.py](app/answering.py) either calls OpenAI over the retrieved sources or falls back to extractive answers when no key is set.
4. UI/API: [app/main.py](app/main.py) serves the browser chat page and the `/chat`, `/search`, and `/health` endpoints.

The browser UI lives in [app/templates/index.html](app/templates/index.html), with styling and behavior in [app/static/styles.css](app/static/styles.css) and [app/static/app.js](app/static/app.js).

## Design Choices

I used TF-IDF instead of a full vector database because the corpus is small, the summaries are already concise, and the take-home benefits more from a simple, debuggable retrieval path than from extra infrastructure.

The app is retrieval-first and citation-first. If retrieval does not surface a relevant source, it says so instead of inventing an answer. That matters more than sounding polished.

Citation labels are standardized so the reporting period, source file, and summary file stay aligned across the API and UI.

OpenAI support is optional and controlled by environment variables. This keeps the app usable in a local or offline review while still allowing higher-quality synthesis when an API key is available.

## Evaluation Plan

With more time, I would measure retrieval quality on a labeled question set, compare exact-match and trend questions, and review citation accuracy separately from answer quality. I would also add a small regression suite with the sample questions and a few known out-of-scope prompts.

## Regression Testing

A basic behavior regression suite is included in `tests/regression/`.

Run it from the repo root:

```bash
python tests/regression/run_regression.py
```

This produces `tests/regression/latest_report.md` with expected vs actual behavior for each labeled case.

## Limitations

The current retrieval stack is lexical, so very paraphrased questions can miss relevant passages. I would next add hybrid retrieval with embeddings, better section-aware ranking, and more structured citation traces that point to exact evidence sentences.

The summaries are already censored, so some financial questions can only be answered at a high level. The app handles that honestly, but a richer source corpus would improve usefulness.
