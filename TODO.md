# Project TODO — Altius AI Take-Home

> Last updated: May 4, 2026
> 
> **Timeline:** Today + Tomorrow (2 days)

---

## TODAY (Critical Path)

- [x] **Test core flow end-to-end locally**
  - Load corpus, check corpus stats
  - Test retrieval on simple question
  - Test answer generation (with & without OpenAI key)
  - Verify no crashes or errors

- [x] **Verify Docker setup and all dependencies**
  - Run `docker compose up --build` and ensure clean startup
  - Check all services healthy
  - Verify ports exposed correctly (8000 for FastAPI)
  - Document any missing dependencies

- [x] **Test with sample questions from brief**
  - Valuations in Q1 2025? ✅
  - Subscription credit facility usage in 2024? ✅
  - Strategy shift between 2022 and 2025? ✅
  - NAV in Q3 2023? (handle censored data gracefully) ✅
  - Dividend distribution policy? (out-of-scope test) ✅

- [x] **Create .env.example and verify no API keys in repo**
  - ✅ .env.example exists with all required vars
  - ✅ No real API keys in repo (checked)
  - ✅ .gitignore configured to block .env

---

## TOMORROW (Polish & Enhancement)

- [x] **Improve retrieval — add hybrid/embedding support**
  - ✅ Implemented hybrid retriever in `app/hybrid_retriever.py` (3-stage: TF-IDF → embeddings → optional rerank)
  - ✅ Wired `app/main.py` to use HybridRetriever (mandatory, no TF-IDF fallback)
  - ✅ Added `sentence-transformers>=2.2.2` dependency with embedding model `all-MiniLM-L6-v2`
  - ✅ Fixed Docker CUDA bloat: CPU-only PyTorch in Dockerfile
  - ✅ Docker image builds (2.44GB) and app starts successfully
  - ✅ Tested `/health` and `/search` endpoints — app fully functional

- [x] **Enhance answer quality — better citations format**
  - ✅ Added canonical citation labels to retrieved sources
  - ✅ UI now shows reporting period, source file, and summary file consistently
  - ✅ Answer text and OpenAI source prompts use the same citation format

- [x] **Polish UI/UX — loading states, error handling**
  - ✅ Added a loading bubble with animated dots and disabled composer state
  - ✅ Added specific retryable error messages for timeout, server, and validation failures
  - ✅ Preserved the draft question on failure and tightened mobile composer behavior

- [x] **Add read-only source preview**
  - ✅ Citations now expand from the chat UI and link to a read-only preview page
  - ✅ Preview route is allowlisted by document id, not raw filesystem path
  - ✅ Preview page shows the full markdown summary in a read-only panel

- [x] **Add basic regression test suite**
  - ✅ Added 7 labeled Q&A pairs in `tests/regression/cases.json`
  - ✅ Added harness in `tests/regression/run_regression.py` (internal + HTTP modes)
  - ✅ Added generated report format in `tests/regression/latest_report.md` with expected vs actual behavior

---

## NICE-TO-HAVE (Post-Submission)

- [ ] **Update README with final architecture notes**
  - Document any deviations from initial design
  - Reflect on lessons learned

- [ ] **Final QA — test edge cases and out-of-scope q's**
  - Empty queries, very long queries
  - Questions about non-existent time periods
  - Stress test with rapid-fire requests

---

## Suggested Improvements (from Regression Testing)

Based on regression suite findings, these improvements would strengthen answer quality and retrieval:

- [ ] **Apply score-threshold gating in HybridRetriever**
  - Filter out sources below similarity threshold (reduce irrelevant sources returned)
  - Consequences: fewer false positives in out-of-scope detection, cleaner answer generation

- [ ] **Improve temporal/period-aware retrieval**
  - Add soft bias toward sources matching the reporting period mentioned in the question (e.g., "early 2025" → prioritize Q1/Q2)
  - Implement confidence scoring based on temporal specificity match
  - Helps paraphrased questions like "In early 2025, did marks move up or down?"

- [ ] **Enhance refusal/uncertainty detection in answer engine**
  - Already improved `is_out_of_scope()` to catch 20+ refusal phrasings
  - Next: detect partial/conditional answers (e.g., "only Q3 2025 data available") and flag uncertainty appropriately
  - Could use embeddings to detect semantic "I don't know" even if phrasing varies

- [ ] **Implement semantic matching for test assertions**
  - Current tests use substring token matching, which is brittle to phrasing variations
  - Alternative: use embeddings to compare answer semantics to expected refusal "canonical forms" (cosine similarity > threshold)
  - Reduces false negatives for out-of-scope detection

- [ ] **Better handling of censored/partial data**
  - When corpus lacks specific data (e.g., exact NAV figures), explicitly acknowledge in answer
  - Could add a flag to SourceCitation to mark censored sections
  - Helps manage expectations for questions on sensitive financial info

- [ ] **Expand corpus with synthetic early-year data or time-series context**
  - Current corpus (Q2 2021–Q3 2025) has gaps at the start
  - Adding quarterly summaries for Q1–Q2 2021 or providing multi-year trends would improve paraphrase tolerance

---

## Progress Notes

*(Use this section to track blockers, decisions, and learnings as you work)*

- Canonical citation labels now flow from retrieval into answer generation and the browser UI.
- Chat UI now shows a live loading state, specific error messages, and a retry button when requests fail.
- Users can open a safe read-only preview for each cited source from the chat UI.
- UI polished: removed all confidence badges, limited results to top 3 sources, added "Sources" header, hid low-confidence citations, added "Suggested follow-up questions:" label for clarity.
- Commit: c51eb5d "Polish UI: remove confidence badges, limit to top 3 sources, add sources header, remove preview link, add follow-up label"
- Added a basic regression suite (7 labeled cases + runnable harness + markdown report output) to catch answer-quality regressions.

---
