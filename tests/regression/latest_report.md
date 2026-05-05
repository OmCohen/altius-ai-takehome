# Regression Test Report

- Generated: 2026-05-05T14:43:59
- Mode: http
- Cases: 7
- Passed: 4
- Failed: 3

## Summary

| Case | Label | Result |
|---|---|---|
| C01 | Q1 2025 valuation commentary | FAIL |
| C02 | 2024 subscription facility usage | PASS |
| C03 | Strategy shift from 2022 to 2025 | PASS |
| C04 | Q3 2023 NAV with censored data | FAIL |
| C05 | Out-of-scope dividend policy | PASS |
| C06 | Paraphrased 2025 valuation question | FAIL |
| C07 | Clearly unsupported period | PASS |

## Expected vs Actual

### C01 - Q1 2025 valuation commentary

- Question: What was the fund's commentary on valuations in Q1 2025?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['valuation', 'markdown', 'net asset value', 'nav'], source_period_any=['Q1 2025', '2025'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=partial, source_count=4, provider=openai, source_periods=['Q1 2025', 'Q1 2025', 'Q2 2025', 'Q3 2025']
- Actual answer preview: The available evidence is partial, so this answer is directional rather than definitive. In Q1 2025, the fund said valuations were under pressure, with the quarter’s net deficit driven mainly by unrealised markdowns across the investment portfolio. [1] It also described portfolio performance as softer in the quarter, despite being broadly positive 
- Result: FAIL
- Failed checks: - answer_class: expected supported; actual partial

### C02 - 2024 subscription facility usage

- Question: How did the manager describe the use of the subscription credit facility across 2024?
- Expected behavior: out_of_scope=False, min_sources=2, required_terms_any=['subscription', 'credit facility', 'capital call', 'liquidity'], source_period_any=['2024'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=supported, source_count=4, provider=openai, source_periods=['Q2 2024', 'Q1 2024', 'Q3 2024', 'Q4 2024']
- Actual answer preview: Across 2024, the manager said the subscription credit facility was used as a revolving bridge to cover capital calls and to fund investments and expenses. In Q1, it supported rising cash balances through a draw on the facility; in Q2, the fund made use of it during accelerated capital call activity; in Q3, it was used to bridge capital calls and fu
- Result: PASS
- Failed checks: None

### C03 - Strategy shift from 2022 to 2025

- Question: Has the fund's strategy shifted between 2022 and 2025?
- Expected behavior: out_of_scope=False, min_sources=2, required_terms_any=['strategy', 'shift', 'no material', 'mandate'], source_period_any=['2022', '2025'], answer_class=supported
- Actual behavior: out_of_scope=False, answer_class=supported, source_count=4, provider=openai, source_periods=['Q2 2022', 'Q2 2025', 'Q4 2022', 'Q1 2025']
- Actual answer preview: The fund’s core strategy does not appear to have shifted materially between 2022 and 2025. In 2022, it was described as investing in a wide/broad range of equity and equity-related securities with an intent to resell for capital gain, typically within 3–5 years or when an exit is available [1][3]. In 2025, it is still described as pursuing a broad 
- Result: PASS
- Failed checks: None

### C04 - Q3 2023 NAV with censored data

- Question: What can we infer about NAV in Q3 2023 from the summaries?
- Expected behavior: out_of_scope=False, min_sources=1, required_terms_any=['nav', 'fair value', 'above cost', 'censor'], source_period_any=['Q3 2023', '2023'], answer_class=partial
- Actual behavior: out_of_scope=True, answer_class=refusal, source_count=4, provider=openai, source_periods=['Q3 2023', 'Q4 2023', 'Q2 2023', 'Q2 2022']
- Actual answer preview: I couldn't find relevant information in the corpus for that question.
- Result: FAIL
- Failed checks: - out_of_scope: expected False; actual True<br>- must_contain_any: expected nav OR fair value OR above cost OR censor; actual I couldn't find relevant information in the corpus for that question.<br>- answer_class: expected partial; actual refusal

### C05 - Out-of-scope dividend policy

- Question: What is the fund's dividend distribution policy?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=[], source_period_any=[], answer_class=refusal
- Actual behavior: out_of_scope=True, answer_class=refusal, source_count=4, provider=openai, source_periods=['Q1 2025', 'Q4 2023', 'Q3 2024', 'Q1 2023']
- Actual answer preview: I couldn't find relevant information in the corpus for that question.
- Result: PASS
- Failed checks: None

### C06 - Paraphrased 2025 valuation question

- Question: In early 2025, did portfolio marks move up or down?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=[], source_period_any=['2025'], answer_class=refusal
- Actual behavior: out_of_scope=False, answer_class=partial, source_count=4, provider=openai, source_periods=['Q3 2025', 'Q3 2025', 'Q2 2025', 'Q1 2025']
- Actual answer preview: The available evidence is partial, so this answer is directional rather than definitive. In early 2025, portfolio marks moved **down**. Q1 2025 says portfolio performance was negative for the quarter, with broad unrealised value erosion and a net deficit [4]. Q2 2025 also shows a modest decline in net asset value despite positive unrealized gains, 
- Result: FAIL
- Failed checks: - out_of_scope: expected True; actual False<br>- answer_class: expected refusal; actual partial

### C07 - Clearly unsupported period

- Question: What was the fund's NAV in Q4 2018?
- Expected behavior: out_of_scope=True, min_sources=0, required_terms_any=[], source_period_any=[], answer_class=refusal
- Actual behavior: out_of_scope=True, answer_class=refusal, source_count=0, provider=none, source_periods=[]
- Actual answer preview: I couldn't find relevant information in the corpus for that question.
- Result: PASS
- Failed checks: None
