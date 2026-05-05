# Regression Test Report

- Generated: 2026-05-05T14:51:09
- Mode: http
- Cases: 10
- Passed: 10
- Failed: 0

## Summary

| Case | Label | Result |
|---|---|---|
| C01 | Q1 2025 valuation commentary | PASS |
| C02 | 2024 subscription facility usage | PASS |
| C03 | Strategy shift from 2022 to 2025 | PASS |
| C04 | Q3 2023 NAV with censored data | PASS |
| C05 | Out-of-scope dividend policy | PASS |
| C06 | Paraphrased 2025 valuation question | PASS |
| C07 | Clearly unsupported period | PASS |
| C08 | Off-topic weather question | PASS |
| C09 | Future period outside corpus | PASS |
| C10 | Q3 2025 valuation direction | PASS |

## Expected vs Actual

### C01 - Q1 2025 valuation commentary

- Question: What was the fund's commentary on valuations in Q1 2025?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['valuation', 'markdown', 'net asset value', 'nav'], source_period_any=['Q1 2025', '2025'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=supported, source_count=4, provider=openai, source_periods=['Q1 2025', 'Q1 2025', 'Q2 2025', 'Q3 2025']
- Actual answer preview: In Q1 2025, the fund said valuations were under pressure, with the quarter’s modest NAV decline driven mainly by unrealised markdowns across the portfolio. [1] It also described portfolio performance as softer in the quarter, despite being broadly positive since inception. [1][2]
- Result: PASS
- Failed checks: None

### C02 - 2024 subscription facility usage

- Question: How did the manager describe the use of the subscription credit facility across 2024?
- Expected behavior: out_of_scope=False, min_sources=2, required_terms_any=['subscription', 'credit facility', 'capital call', 'liquidity'], source_period_any=['2024'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=supported, source_count=4, provider=openai, source_periods=['Q2 2024', 'Q1 2024', 'Q3 2024', 'Q4 2024']
- Actual answer preview: Across 2024, the manager said the fund used its subscription/revolving credit facility to bridge capital calls and to support investments and expenses. In Q1, the facility was drawn to support rising cash balances; in Q2, it was used during accelerated capital call activity; in Q3 and Q4, it was described as bridging capital calls and funding inves
- Result: PASS
- Failed checks: None

### C03 - Strategy shift from 2022 to 2025

- Question: Has the fund's strategy shifted between 2022 and 2025?
- Expected behavior: out_of_scope=False, min_sources=2, required_terms_any=['strategy', 'shift', 'no material', 'mandate'], source_period_any=['2022', '2025'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=supported, source_count=4, provider=openai, source_periods=['Q2 2022', 'Q2 2025', 'Q4 2022', 'Q1 2025']
- Actual answer preview: The fund’s core strategy does not appear to have shifted materially between 2022 and 2025: it remained focused on broad private equity investing in equity and equity-related securities, with exits/resales for capital gain over a typical 3–5 year horizon or when a suitable exit is available. [1][2][3][4]  What did change is the stage of the fund and
- Result: PASS
- Failed checks: None

### C04 - Q3 2023 NAV with censored data

- Question: What can we infer about NAV in Q3 2023 from the summaries?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['nav', 'fair value', 'above cost', 'censor'], source_period_any=['Q3 2023', '2023'], answer_class=partial
- Actual behavior: out_of_scope=False, answer_class=partial, source_count=4, provider=openai, source_periods=['Q3 2023', 'Q4 2023', 'Q2 2023', 'Q2 2022']
- Actual answer preview: From the summaries, we can infer that NAV in Q3 2023 was likely still supported by active capital deployment and an invested portfolio, but there is no direct statement of the Q3 NAV level or whether it rose or fell in that quarter.[1][2][3]  What is supported is that the fund was still deploying capital in Q3 2023 and remained actively invested, w
- Result: PASS
- Failed checks: None

### C05 - Out-of-scope dividend policy

- Question: What is the fund's dividend distribution policy?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=[], source_period_any=[], answer_class=refusal
- Actual behavior: out_of_scope=True, answer_class=refusal, source_count=4, provider=openai, source_periods=['Q1 2025', 'Q4 2023', 'Q3 2024', 'Q1 2023']
- Actual answer preview: I couldn't find relevant information in the corpus for that question.
- Result: PASS
- Failed checks: None

### C06 - Paraphrased 2025 valuation question

- Question: In early 2025, did portfolio marks move up or down?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=[], source_period_any=['2025'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=supported, source_count=4, provider=openai, source_periods=['Q3 2025', 'Q3 2025', 'Q2 2025', 'Q1 2025']
- Actual answer preview: In early 2025, portfolio marks moved **down**. Q1 2025 says portfolio performance was negative for the quarter, with broad unrealised value erosion and a net deficit [4]. Q2 2025 also shows a modest decline in net asset value despite positive unrealized gains, due to a realized loss [3].
- Result: PASS
- Failed checks: None

### C07 - Clearly unsupported period

- Question: What was the fund's NAV in Q4 2018?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=[], source_period_any=[], answer_class=refusal
- Actual behavior: out_of_scope=True, answer_class=refusal, source_count=0, provider=none, source_periods=[]
- Actual answer preview: I couldn't find relevant information in the corpus for that question.
- Result: PASS
- Failed checks: None

### C08 - Off-topic weather question

- Question: Will it rain in London tomorrow?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=[], source_period_any=[], answer_class=refusal
- Actual behavior: out_of_scope=True, answer_class=refusal, source_count=0, provider=router:offtopic, source_periods=[]
- Actual answer preview: That seems outside the report corpus scope. I can help with finance/report questions tied to the provided quarterly summaries.
- Result: PASS
- Failed checks: None

### C09 - Future period outside corpus

- Question: What was the fund's NAV in Q2 2030?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=[], source_period_any=[], answer_class=refusal
- Actual behavior: out_of_scope=True, answer_class=refusal, source_count=0, provider=none, source_periods=[]
- Actual answer preview: I couldn't find relevant information in the corpus for that question.
- Result: PASS
- Failed checks: None

### C10 - Q3 2025 valuation direction

- Question: In Q3 2025, did portfolio fair value go up or down quarter over quarter?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['up', 'increase', 'increased', 'rose'], source_period_any=['Q3 2025', '2025'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=supported, source_count=4, provider=openai, source_periods=['Q3 2025', 'Q1 2025', 'Q3 2025', 'Q2 2025']
- Actual answer preview: In Q3 2025, portfolio fair value went **up** quarter over quarter. Source [1] says the portfolio fair value was “increasing quarter over quarter,” and source [3] says portfolio performance was “positive for the quarter overall” with “broad unrealised gains.”
- Result: PASS
- Failed checks: None
