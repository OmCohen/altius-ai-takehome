# Regression Test Report

- Generated: 2026-05-05T08:55:24
- Mode: http
- Cases: 7
- Passed: 4
- Failed: 3

## Summary

| Case | Label | Result |
|---|---|---|
| C01 | Q1 2025 valuation commentary | PASS |
| C02 | 2024 subscription facility usage | PASS |
| C03 | Strategy shift from 2022 to 2025 | PASS |
| C04 | Q3 2023 NAV with censored data | PASS |
| C05 | Out-of-scope dividend policy | FAIL |
| C06 | Paraphrased 2025 valuation question | FAIL |
| C07 | Clearly unsupported period | FAIL |

## Expected vs Actual

### C01 - Q1 2025 valuation commentary

- Question: What was the fund's commentary on valuations in Q1 2025?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['valuation', 'markdown', 'net asset value', 'nav'], source_period_any=['Q1 2025', '2025']
- Actual behavior: out_of_scope=False, source_count=4, provider=openai, source_periods=['Q1 2025', 'Q1 2025', 'Q2 2025', 'Q3 2025']
- Actual answer preview: In Q1 2025, the fund said valuations were slightly softer: overall fair value declined quarter over quarter, but the portfolio was still valued above cost. The quarter’s NAV decline was driven mainly by unrealised markdowns across the portfolio. [1][2]
- Result: PASS
- Failed checks: None

### C02 - 2024 subscription facility usage

- Question: How did the manager describe the use of the subscription credit facility across 2024?
- Expected behavior: out_of_scope=False, min_sources=2, required_terms_any=['subscription', 'credit facility', 'capital call', 'liquidity'], source_period_any=['2024']
- Actual behavior: out_of_scope=False, source_count=4, provider=openai, source_periods=['Q2 2022', 'Q3 2025', 'Q2 2024', 'Q1 2024']
- Actual answer preview: The sources provided do not mention a subscription credit facility or describe how it was used across 2024, so I can’t support a factual answer from them. [3][4]
- Result: PASS
- Failed checks: None

### C03 - Strategy shift from 2022 to 2025

- Question: Has the fund's strategy shifted between 2022 and 2025?
- Expected behavior: out_of_scope=False, min_sources=2, required_terms_any=['strategy', 'shift', 'no material', 'mandate'], source_period_any=['2022', '2025']
- Actual behavior: out_of_scope=False, source_count=4, provider=openai, source_periods=['Q2 2022', 'Q2 2025', 'Q4 2022', 'Q1 2025']
- Actual answer preview: No clear strategy shift is supported by the sources. In 2022, the fund described its strategy as investing in a broad range of equity and equity-related securities with the goal of reselling for capital gain, typically within 3–5 years or upon exit [1][3]. In 2025, it is still described as pursuing broad private equity investing across equity and e
- Result: PASS
- Failed checks: None

### C04 - Q3 2023 NAV with censored data

- Question: What can we infer about NAV in Q3 2023 from the summaries?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['nav', 'fair value', 'above cost', 'censor'], source_period_any=['Q3 2023', '2023']
- Actual behavior: out_of_scope=False, source_count=4, provider=openai, source_periods=['Q2 2022', 'Q3 2023', 'Q4 2023', 'Q2 2023']
- Actual answer preview: In Q3 2023, NAV increased versus year-end, and the main driver was unrealised appreciation across the investment portfolio. The fund was still actively investing, with additional capital deployed during the quarter. [2]
- Result: PASS
- Failed checks: None

### C05 - Out-of-scope dividend policy

- Question: What is the fund's dividend distribution policy?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=["couldn't find", 'not found', 'not in the corpus', 'no relevant information'], source_period_any=[]
- Actual behavior: out_of_scope=False, source_count=4, provider=openai, source_periods=['Q1 2025', 'Q4 2023', 'Q3 2024', 'Q1 2023']
- Actual answer preview: The provided sources do not state the fund’s dividend distribution policy. They discuss valuation, strategy, and governance, but do not mention any dividend policy or distribution terms. [1][2][3][4]
- Result: FAIL
- Failed checks: - out_of_scope: expected True; actual False<br>- must_contain_any: expected couldn't find OR not found OR not in the corpus OR no relevant information; actual The provided sources do not state the fund’s dividend distribution policy. They discuss valuation, strategy, and governance, but do not mention any dividend policy or distribution terms. [1][2][3][4]

### C06 - Paraphrased 2025 valuation question

- Question: In early 2025, did portfolio marks move up or down?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['down', 'markdown', 'decline', 'net deficit'], source_period_any=['2025']
- Actual behavior: out_of_scope=False, source_count=4, provider=openai, source_periods=['Q1 2023', 'Q1 2023', 'Q3 2025', 'Q3 2025']
- Actual answer preview: The sources do not support an answer for **early 2025** specifically. The only 2025 source provided is for **Q3 2025**, which says portfolio fair value increased quarter over quarter and overall value rose, so marks moved **up** in that quarter [3][4].
- Result: FAIL
- Failed checks: - must_contain_any: expected down OR markdown OR decline OR net deficit; actual The sources do not support an answer for **early 2025** specifically. The only 2025 source provided is for **Q3 2025**, which says portfolio fair value increased quarter over quarter and overall value rose, so marks move

### C07 - Clearly unsupported period

- Question: What was the fund's NAV in Q4 2018?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=["couldn't find", 'not found', 'not in the corpus', 'no relevant information'], source_period_any=[]
- Actual behavior: out_of_scope=False, source_count=4, provider=openai, source_periods=['Q4 2021', 'Q4 2022', 'Q4 2024', 'Q4 2023']
- Actual answer preview: The fund’s NAV in Q4 2018 is not stated in the provided sources, so I can’t determine it from these documents. [1][2][3][4]
- Result: FAIL
- Failed checks: - out_of_scope: expected True; actual False<br>- must_contain_any: expected couldn't find OR not found OR not in the corpus OR no relevant information; actual The fund’s NAV in Q4 2018 is not stated in the provided sources, so I can’t determine it from these documents. [1][2][3][4]
