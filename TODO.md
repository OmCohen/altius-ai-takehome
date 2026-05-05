# Project TODO - Altius AI Take-Home

> Last updated: May 5, 2026
> Status: Core build complete, now optimizing answer quality and reliability.

---

## Snapshot

### Completed Foundation

- [x] End-to-end local flow tested (corpus load, retrieval, answering, no crashes)
- [x] Dockerized app verified (`docker compose up --build`, healthy startup)
- [x] Sample brief questions validated (including out-of-scope refusal)
- [x] Secrets hygiene done (`.env.example`, no committed API keys)
- [x] Hybrid retrieval implemented (`app/hybrid_retriever.py`)
- [x] Citation formatting standardized across API + UI
- [x] UI resilience improved (loading state, retryable errors, draft persistence)
- [x] Safe read-only source preview added
- [x] Basic regression harness added (`tests/regression/`)

---

## Priority Roadmap

### P0 - High Impact, Do Next

- [ ] **Add score-threshold gating in hybrid retrieval**
  - Goal: reduce irrelevant citations and false-positive answers.
  - Suggested work:
    - Add minimum score threshold after rerank/final scoring.
    - Return fewer but stronger sources when confidence is low.
  - Acceptance criteria:
    - Out-of-scope prompts return fewer weak citations.
    - Regression cases show improved refusal precision.

- [ ] **Strengthen uncertainty handling in answer engine**
  - Goal: clearly distinguish "not found" vs "partially supported".
  - Suggested work:
    - Extend refusal logic to detect partial/conditional evidence.
    - Add a consistent uncertainty sentence template.
  - Acceptance criteria:
    - Answers explicitly call out missing or censored details.
    - No overconfident claims when evidence is incomplete.

- [ ] **Improve regression assertion robustness**
  - Goal: avoid brittle pass/fail checks tied to exact wording.
  - Suggested work:
    - Add semantic similarity checks for refusal/uncertainty classes.
    - Keep token checks as a fallback.
  - Acceptance criteria:
    - Fewer false negatives on paraphrased but correct answers.
    - Test report includes assertion reason per failed case.

### P1 - Retrieval Quality Upgrades

- [ ] **Improve temporal intent matching**
  - Goal: better handling of questions like "early 2025" or "across 2024".
  - Suggested work:
    - Strengthen period extraction from query.
    - Add soft boost for matching quarter/year ranges.
  - Acceptance criteria:
    - Time-specific questions consistently surface matching periods first.

- [ ] **Handle censored/partial data more explicitly**
  - Goal: increase trust when exact metrics are unavailable.
  - Suggested work:
    - Mark citations that come from censored sections.
    - Add answer phrasing for "directional only" evidence.
  - Acceptance criteria:
    - NAV/sensitive questions clearly separate facts from inference.

### P2 - Polish and Coverage

- [ ] **Expand and rebalance regression dataset**
  - Add paraphrase-heavy, long-query, and non-existent period cases.
  - Add rapid-fire request test scenario for API robustness.

- [ ] **Finalize README limitations and evaluation notes**
  - Align docs with current hybrid pipeline and known gaps.
  - Include short "what to improve next" section.

---

## Recent Improvement Suggestions (Actionable)

These are the strongest near-term upgrades based on current regression behavior:

1. **Retrieval confidence gating first**
   - Why: largest quality gain for minimal code change.
2. **Uncertainty/refusal calibration second**
   - Why: prevents confident-sounding but weakly supported answers.
3. **Semantic regression checks third**
   - Why: improves evaluation reliability while iteration speed stays high.
4. **Temporal retrieval tuning fourth**
   - Why: closes the common paraphrase and period-intent gap.

---

## Suggested Execution Order (1-2 Days)

### Day 1

- Implement P0 retrieval threshold gating.
- Implement uncertainty sentence templates in answering.
- Re-run regression and capture baseline deltas.

### Day 2

- Add semantic assertion mode in regression harness.
- Tune temporal matching boosts and validate on date-focused prompts.
- Update README + testing notes with measured outcomes.

---

## Notes

- Keep this file as the single source of truth for pending work.
- Move completed items to "Completed Foundation" and keep roadmap sections short.
