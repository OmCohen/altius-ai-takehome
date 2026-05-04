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

- [ ] **Enhance answer quality — better citations format**
  - Review citation clarity in responses
  - Ensure source file + reporting period always shown
  - Test citation accuracy on retrieved passages

- [ ] **Polish UI/UX — loading states, error handling**
  - Add visual feedback while waiting for response
  - Improve error messages for failed queries
  - Test mobile responsiveness (if applicable)

- [ ] **Add basic regression test suite**
  - Create 5–10 labeled Q&A pairs
  - Build simple test harness to run them
  - Document expected vs actual behavior

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

## Progress Notes

*(Use this section to track blockers, decisions, and learnings as you work)*

---
