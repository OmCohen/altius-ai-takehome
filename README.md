# Take-Home Assignment: Chatbot for PE Quarterly Reports

## Context

Private equity funds report to their limited partners on a quarterly basis. These reports are dense, repetitive across quarters, and contain a mix of narrative commentary (strategy, risks, governance) and financial data. Investors and deal teams routinely need to ask questions across many quarters — *"how did the fund's risk posture evolve in 2023?"*, *"which quarters mentioned use of the subscription credit facility?"*, *"what was the manager's commentary on valuations in Q1 2025?"* — and skimming dozens of PDFs is slow.

Your task is to build a chatbot that answers these kinds of questions over a corpus of quarterly report summaries.

## Your Task

Build a chatbot that:

1. Ingests the provided corpus of quarterly report summaries.
2. Lets a user ask questions through a chat interface.
3. Returns answers grounded in the provided documents, with citations to the source file(s) and reporting period.

The data has been derived from real PE fund reports; sensitive financial specifics have been removed or marked as censored. Design the system as if it were going into production for an investment team.

## What We Provide

- **`data/Quarterly Report Summaries/`** — ~50 markdown files. Each is a summary of a single quarterly document (Volume 1 narrative report, Financial Statement, or Appendix VI). Summaries follow a consistent section structure: General Summary, Strategy, Risks & Stress, Fund Operations & Governance, Performance.
- **`data/metadata.csv`** — One row per summary file, with columns: `Deal Name`, `File Name` (original source filename), `Date` (reporting period end, DD/MM/YYYY), `Summary File` (filename in the folder above), `File Size`, and `File Name in zip`.

The corpus covers Q2 2021 through Q3 2025.

## Requirements

- Run from a single command: `docker compose up` (or equivalent) should bring up a working chatbot reachable via a web browser. We should not need to install Python or Node locally.
- Provide a chat-style interface.
- Cite sources. Every answer should reference the underlying summary file(s) and the relevant reporting period(s).
- Handle out-of-scope questions gracefully. If the answer isn't in the corpus, the bot should say so rather than fabricate.
- Accept any LLM / embedding / API keys via environment variables. Do not commit keys.

You are free to choose the LLM, embedding model, vector store, framework, and overall approach. We care about the reasoning behind your choices, which you'll explain in the README.

## Deliverables

Submit a Git repository (zip or link) containing:

1. **Source code.**
2. **`Dockerfile`** and **`docker-compose.yml`** that bring the app up with a single command.
3. **`README.md`** containing:
   - Setup and run instructions
   - A short architecture overview
   - Key design decisions and tradeoffs
   - A short note on how you'd evaluate this system more rigorously with more time
   - Known limitations and what you'd improve next
4. **`.env.example`** showing the expected environment variables (no real keys).

## How We'll Evaluate

Roughly in order of importance:

- **Does it work?** We can run it with one command, ask questions, and get sensible answers with citations.
- **Quality of retrieval and answers.** We'll ask a mix of straightforward lookups, cross-quarter trend questions, and questions whose answers aren't in the corpus.
- **Quality of thinking.** Your README should make us understand *why* you built it the way you did. We value honest tradeoffs over long feature lists.

## Sample Questions

Use these to sanity-check your system. They are not a hidden test set — we'll ask different questions when we evaluate.

1. What was the fund's commentary on valuations in Q1 2025?
2. How did the manager describe the use of the subscription credit facility across 2024?
3. Has the fund's strategy shifted between 2022 and 2025?
4. What happened to NAV in Q3 2023? *(Note: financial specifics are censored in the data — your bot should handle this honestly.)*
5. What is the fund's policy on quarterly dividend distributions to LPs? *(Likely not in the corpus — see how your bot handles it.)*

## Submission

Send us a link to a Git repo (or a zip). If anything in the brief is unclear, feel free to reach out — otherwise, make a reasonable assumption, document it in the README, and proceed.

Good luck, and have fun with it.
