# Answer Quality Baseline Evaluation

> **Baseline Snapshot:** May 4, 2026
> 
> **Retrieval Method:** TF-IDF (lexical)  
> **Answer Generation:** OpenAI GPT-4.1-mini  
> **Corpus:** 34 documents, 225 chunks (Q2 2021 – Q3 2025)

---

## Summary: 5 Sample Questions Evaluated

| Q# | Question | Type | Bot Answer Quality | Real Analyst Would Say | Gap / Notes |
|----|----------|------|--------------------|-----------------------|------------|
| **1** | Valuations in Q1 2025? | Specific lookup | ✅ **Accurate** — Mentions NAV decline and unrealized markdowns | Same — these are objective facts from the financial statements | **None — Direct match** |
| **2** | Credit facility usage across 2024? | Multi-quarter trend | ✅ **Accurate** — Synthesized Q1–Q4 usage patterns (cash support, capital call bridging) | Same — bot correctly stitched together quarterly patterns | **None — Synthesis is solid** |
| **3** | Strategy shift 2022–2025? | Long-term analysis | ✅ **Nuanced** — Correctly identifies *no material shift* but notes portfolio maturity evolution (3–5 year exit window unchanged, deployment activity waning) | Real analyst would make same conclusion: core mandate stable, but portfolio lifecycle advancing | **Slight weakness:** Could be more explicit about "why this matters" (LP implications of maturity) |
| **4** | NAV in Q3 2023? | Censored data | ✅ **Honest** — Avoids specific numbers, extracts "aggregate fair value up, portfolio above cost" | Real analyst would do same: respect data censoring, offer high-level insights | **None — Graceful handling** |
| **5** | Dividend policy? | Out-of-scope | ✅ **Correct refusal** — "No relevant information in corpus" | Real analyst would say "Not documented in the summaries provided" | **None — Appropriate boundary** |

---

## Detailed Answer Quality Assessment

### Q1: Valuations in Q1 2025

**Bot's Answer:**
> "In Q1 2025, the fund said its net asset value declined modestly and the net deficit was driven primarily by unrealised markdowns across the portfolio, which indicates valuations were marked down during the quarter."

**Real Analysis:**
- The statements match the corpus: Q1 2025 Financial Statements explicitly mention "net deficit driven primarily by unrealised markdowns"
- Bot correctly inferred the causality (markdowns → NAV decline)
- **Accuracy: 10/10** — This is factually correct and directly answerable from the data

**Citation Quality:**
- Source: Financial Statements Q1 2025 (correct file type)
- Excerpt verbatim from corpus
- **Grounding: 10/10**

---

### Q2: Subscription Credit Facility Usage Across 2024

**Bot's Answer:**
> "Across 2024, the manager said the subscription credit facility was used to support liquidity and bridge capital calls: in Q1, cash balances rose materially due to a draw on the facility; in Q2, the fund made use of the subscription-backed revolving credit facility; and in Q3, it was used to bridge capital calls and fund investments and expenses."

**Real Analysis:**
- Bot retrieved Q1, Q2, Q3 2024 sources correctly
- Synthesis is accurate: each quarter shows the same use case (liquidity management)
- Q4 source was retrieved but bot noted it added no new detail (good editorial judgment)
- **Accuracy: 9/10** — Correct pattern recognition; one minor point: doesn't quantify magnitude of draws

**Citation Quality:**
- 4 sources across quarters ✅
- Excerpts match corpus ✅
- No hallucination ✅
- **Grounding: 10/10**

**Where Real Analyst Would Differ:**
- Might add: "Consistent pattern suggests this is a planned liquidity tool, not distress borrowing"
- Might note: "No escalation or stress signals mentioned"

---

### Q3: Strategy Shift 2022–2025

**Bot's Answer:**
> "No material strategy shift is supported by the sources. In 2022, the fund described its strategy as investing in a broad range of equity and equity-related securities to resell for capital gain, typically within 3–5 years or via a suitable exit. In 2025, it is still described as pursuing broad private equity investing across equity and equity-related securities. The main difference is in stage and activity: 2025 notes show a more mature, substantially deployed portfolio with modest new purchase activity and more emphasis on follow-on investing and portfolio management."

**Real Analysis:**
- Core insight is correct: mandate unchanged, portfolio lifecycle advancing
- Accurately captured the "3–5 year" language consistency
- Noted deployment maturity (95%+ committed capital in Q2 2025 per corpus)
- **Accuracy: 8/10** — Good synthesis, but misses deeper story

**Where Real Analyst Would Go Deeper:**
- **Strategic Implication:** If deployment is 95% complete and exit window is 3–5 years (from original investment), portfolio is entering harvest phase → expect increasing distributions
- **Market Context:** 2022 was pre-rate-hike; 2025 is post-rate-hike. How did market stress change the strategy execution (even if mandate is stable)?
- **Risk Evolution:** Are there new risks emerging as portfolio matures? Concentration risk increasing?

**Citation Quality:** 4 sources, good date spread ✅  
**Grounding: 9/10** — Factually correct but analytically shallow

---

### Q4: NAV in Q3 2023

**Bot's Answer:**
> "NAV appears to have increased in Q3 2023, since aggregate fair value increased and the portfolio remained marked above cost."

**Real Analysis:**
- Inference is logical given the data provided
- Respects data censoring (exact NAV figures not disclosed in summaries)
- **Accuracy: 7/10** — Conditional statement is appropriate given uncertainty

**Where Real Analyst Would Be More Cautious:**
- Would note: "Aggregate fair value increased **but**..." 
- Might note partnership expenses, fee drag could have offset portfolio gains
- Would clarify: "Fair value up doesn't always mean NAV up after fees" 

**Citation Quality:**  
- Correctly cited "Performance (Censored)" section ✅
- Shows appropriate transparency about data limits ✅
- **Grounding: 8/10** — Good honesty about what the corpus allows

---

### Q5: Dividend Distribution Policy

**Bot's Answer:**
> "I couldn't find relevant information in the corpus."

**Real Analysis:**
- Correct refusal
- Policy docs (LPA terms) likely aren't in the narrative summaries
- No hallucination or fabrication
- **Accuracy: 10/10** — Right call

---

## Answer Quality Metrics

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Factual Accuracy** | 9/10 | No errors; 4 of 5 questions fully answerable; data censoring handled honestly |
| **Citation Grounding** | 9/10 | All excerpts are verbatim; sources correctly linked to dates; no fabrication |
| **Analytical Depth** | 6/10 | Sticks to retrieved facts; doesn't synthesize implications or market context |
| **Appropriate Boundaries** | 9/10 | Refuses out-of-scope questions; respects data limits; doesn't overreach |
| **Temporal Accuracy** | 9/10 | Correctly links sources to reporting periods; no date confusion |

**Overall Answer Quality Score: 8.4/10**

---

## Gaps vs. Real Analyst

### What the Bot Does Well
✅ Finds the right documents  
✅ Extracts facts accurately  
✅ Respects data boundaries  
✅ Avoids hallucination  
✅ Handles censored/incomplete data honestly  

### What the Bot Misses
❌ **Synthesis depth** — Doesn't connect facts to implications (e.g., "mature portfolio → harvest phase → distributions rising")  
❌ **Market context** — Ignores interest rates, credit environment, fundraising cycles that affect strategy execution  
❌ **Comparative analysis** — Doesn't compare fund performance vs. peers or market benchmarks  
❌ **Risk signaling** — Doesn't highlight emerging risks or red flags implicit in the data  
❌ **Quantitative trends** — Doesn't analyze magnitude or trajectory (e.g., NAV growth rate, markup trends)  

---

## Improvement Targets

| Gap | Importance | Feasibility |
|-----|------------|------------|
| Better retrieval (catch paraphrased questions) | **High** | Medium — Add embeddings |
| Add section weighting (Strategy vs. Performance sections) | **High** | Easy — Config change |
| Improve prompt to encourage synthesis over bullet facts | **Medium** | Easy — Prompt tuning |
| Add implicit market context to answer prompt | **Low** | Hard — Requires new data source |

---

**Last Updated:** May 4, 2026  
**Next Evaluation:** After hybrid retrieval improvements (tomorrow) — will remeasure on same 5 questions
