# Pre-Analysis Plan

**Project:** UK capital allowances and industry-level business investment, 2021–2025
**Author:** Nathanial (GitHub: NathanialCodes)
**Date committed:** 2 August 2026
**Status:** Locked prior to estimation. No regression involving the outcome variable has been run at the time of this commit.

This document fixes the specification before results are seen. Any analysis not described here, if run later, is reported as post hoc. Amendments are recorded in Section 13 with dates, not made silently.

---

## 1. Research question

Did increases in the generosity of UK capital allowances between 2021 and 2025 raise business investment by more in industries whose capital stock is more intensive in qualifying plant and machinery?

**Scope limit.** This tests the *level* channel — allowance generosity operating through the user cost of capital, in the tradition of Hall and Jorgenson (1967). It does **not** test the *instability* or credibility channel — whether frequent policy change independently depressed investment through option value. That is a distinct question, addressed in the prior descriptive report (§3.4) using Decision Maker Panel evidence, and it is out of scope here. The distinction is stated because the prior report's title asks about the "unstable" regime, and this extension answers only half of that.

**Prior.** The descriptive report concluded the allowance channel was directionally real but small relative to three competing channels (monetary tightening, the 2022 energy shock, Brexit and secular decline). A small or statistically insignificant coefficient is therefore an expected and reportable result, not a failed analysis.

---

## 2. Data sources

All files are committed to `data/raw/` at the vintages below. ONS revises quarterly; results are reproducible only against these vintages.

| File | Release | Supplies |
|---|---|---|
| `businessinvestmentbyindustryandasset_2026-06-30.xlsx` | 30 Jun 2026 | Outcome. Table 4 (CVM, seasonally adjusted), 20 leaf industries, 1997Q1–2026Q1 |
| `grossandnetcapitalstock_2025-11-27.xlsx` | 27 Nov 2025 | Exposure. Net and gross capital stocks by asset and industry, current prices |
| `gfcfbyindustryandasset_2025-11-03.xlsx` | 3 Nov 2025 | Robustness only. Annual GFCF by industry and asset, flow-based exposure |

**Known data properties, recorded in advance:**

- In the business investment dataset, industry-level series are seasonally adjusted and then aggregated, whereas the headline ONS Business Investment release adjusts asset-level series first. The panel therefore **will not reconcile** to the headline release. This is a property of the source, not an error.
- Chained volume measures are non-additive. No aggregate is ever constructed by summing industry series.
- CVM reference year is 2023.
- ONS asset deflators for machinery, transport and ICT are built from import price indices of materials and fuels rather than product price indices. This is a known weakness during the 2022 energy shock and is noted as a limitation, not corrected.

---

## 3. Sample

**Units.** The 20 private-sector leaf industries in the business investment dataset: seven manufacturing subsectors (solid fuels and oil refining; metals and metal goods; chemicals and man-made fibres; engineering and vehicles; food, drink and tobacco; textiles, clothing, leather and footwear; other manufacturing) and thirteen non-manufacturing (agriculture, forestry and fishing; mining and quarrying; electricity, gas and water; construction; distribution services; hotels and restaurants; transportation and storage; information and communication; financial intermediation; real estate, renting and business; education; health and social work; other services).

Aggregate columns and the two public-corporation series are excluded: the former are sums of the leaves, the latter carry no industry detail. The panel is private sector only.

**Period.** 2015Q1–2026Q1, **excluding 2020Q2–2020Q4**. This yields 42 quarters × 20 industries = 840 industry-quarters, balanced.

**Justification for the COVID exclusion.** Quarter fixed effects absorb shocks common to all industries. They do not absorb COVID hitting industries *differentially*, and that differential is correlated with treatment exposure: hotels and restaurants (exposure 0.119) and transportation and storage (0.051) collapsed in 2020 and rebounded sharply through 2021–22, while manufacturing (0.342–0.701) fell far less. A recovery-driven divergence between low- and high-exposure industries would coincide in time with the super-deduction while having no tax content. Dropping 2020Q2–Q4 removes the acute phase; retaining 2021Q1 preserves an anchor quarter immediately before treatment for the event study.

**Justification for the 2015 start.** Twenty-one pre-treatment quarters are sufficient to estimate pre-trends while avoiding the global financial crisis and the 2016 referendum period, over which the industry composition of investment shifted for reasons unrelated to tax.

**Pre-specified alternatives** (Section 10): full sample 1997Q1–2026Q1; no COVID exclusion; exclusion extended to 2021Q1.

**Verified:** zero missing or non-positive values across all 900 industry-quarter cells in 2015Q1–2026Q1.

---

## 4. Outcome variable

`log(I_it)` — natural log of real business investment for industry *i* in quarter *t*, chained volume measure, seasonally adjusted, from Table 4.

Logs are used so the coefficient reads as a proportional response and so that industries differing by three orders of magnitude in scale (textiles ≈ £70m/quarter; real estate ≈ £15bn/quarter) contribute comparably rather than being dominated by the largest.

No transformation for non-positive values is required; none occur in the estimation sample.

---

## 5. Treatment variable

`NPV_t` — the present value of capital allowances per £1 of qualifying main-rate plant and machinery expenditure, varying over time and common to all industries.

**Construction.** Under a writing-down allowance at declining-balance rate δ, deductions form the geometric series δ, δ(1−δ), δ(1−δ)², … discounted at r, with present value δ/(r+δ). Under a first-year allowance the full amount is deducted immediately, so the present value is the FYA rate itself. Multiplying by the corporation tax rate τ converts a deduction into cash.

| Period | Regime | Formula | Value |
|---|---|---|---|
| to 2021Q1 | 18% WDA, CT 19% | 0.19 × [0.18 / (0.05 + 0.18)] | 0.1487 |
| 2021Q2–2023Q1 | 130% super-deduction, CT 19% | 0.19 × 1.30 | 0.2470 |
| 2023Q2 onward | 100% full expensing, CT 25% | 0.25 × 1.00 | 0.2500 |

**Baseline discount rate:** r = 0.05.

**Timing convention.** δ/(r+δ) is the continuous-time form, in which the first year's allowance is discounted. The discrete alternative δ(1+r)/(r+δ), in which the first allowance is claimed immediately, gives 0.1561 and reduces the April 2021 step from 9.83pp to 9.09pp. The continuous form is adopted as primary because it is the standard presentation in the user-cost literature; the discrete form is a pre-specified robustness. Neither is more correct; the choice is recorded so it is checkable.

**Recorded in advance: the April 2023 boundary is close to a non-event.** The super-deduction was designed as a bridge to the corporation tax rise, so 130% at 19% and 100% at 25% are near-identical in present value — a 0.3pp step against 9.8pp in April 2021. Identification therefore comes almost entirely from the April 2021 change. The three-regime structure of the prior report is not used, because two of its regimes are indistinguishable in the quantity that matters. No attempt is made to estimate separate super-deduction and full-expensing effects.

**Normalisation is irrelevant, by construction.** Subtracting a constant *c* gives (NPV − c) × PM = NPV×PM − c×PM, and the second term is time-invariant within industry, hence absorbed by industry fixed effects. Levels are used.

---

## 6. Exposure variable

`PM_i` = (other machinery, equipment and weapons systems + ICT equipment) ÷ (that sum + other buildings and structures + transport equipment + research & development + computer software and databases), from net capital stocks, current prices, 2015–2019 mean of levels, then the ratio. Time-invariant.

Dwellings and cultivated biological resources are excluded from the denominator: both are ~88% suppressed and neither is business investment. All six assets are leaf nodes of the ONS asset hierarchy; parent categories are excluded to avoid exact double-counting.

**Aggregation rule.** Where an industry maps to several ONS codes (e.g. metals = C24 + C25), pound values are pooled across codes and the ratio taken once — ratio of sums, not mean of ratios. For metals these give 0.6506 and 0.7048 respectively; the mean-of-ratios version wrongly weights a small code equally with one holding 2.5× the capital.

**Transport equipment is excluded from the numerator.** Cars do not qualify for the super-deduction or full expensing, and assets provided for leasing are excluded from both. Including transport equipment moves transportation and storage from 19th to 9th of 20 on exposure (0.051 → 0.355), assigning high exposure to an industry that is substantially untreated. This is a classification decision with a material effect and is recorded as such.

**Why stocks, not investment flows.** Two measurement grounds, decided before any correlation was computed. (i) In the annual GFCF-by-industry-and-asset file, ICT is suppressed in 49.2% of industry-years 2015–19 and *selectively* so — entirely suppressed for chemicals, textiles and metals, available for information and communication — which would build industry-correlated error into the treatment variable. The equivalent figure in the capital stock file is 3.3%. (ii) A flow-based share shares its denominator with the outcome, so transitory investment spikes in the baseline window generate mean reversion biasing the interaction negative.

**Audit note.** Before locking this definition I computed the bivariate rank correlation between both exposure measures and the seven manufacturing subsectors' 2021–25 investment changes reported in Table 1 of the prior descriptive report (stock ρ = +0.32, flow ρ = −0.11, both p > 0.4, n = 7). The definition above was chosen on the measurement grounds in (i) and (ii), not on that result, but the inspection preceded the lock and is recorded here. Both measures are reported in the results table regardless of outcome.

---

## 7. Primary specification

```
log(I_it) = α_i + λ_t + β·(NPV_t × PM_i) + ε_it
```

- `α_i` — industry fixed effects. Absorb everything permanently different about an industry, **including PM_i itself**, which is why exposure cannot enter alone.
- `λ_t` — quarter fixed effects. Absorb everything common to all industries in a quarter, **including NPV_t**, which does not vary across industries. No allowance-regime main effect is separately identified, by construction.
- `β` — the parameter of interest. Reads: when allowance generosity rose, did high-exposure industries move differently from low-exposure ones, relative to their own norms and to that quarter's common shock?

`β` is a semi-elasticity per unit of NPV × exposure. Interpretation is reported as the predicted effect of the April 2021 step (ΔNPV = 0.0983) for an industry at the manufacturing mean exposure (0.501) relative to one at the non-manufacturing mean (0.228).

**Estimator:** `linearmodels.PanelOLS` with `entity_effects=True, time_effects=True`. Cross-checked against `pyfixest`; both are reported if they disagree beyond floating-point tolerance.

**Secondary specification (event study).** `PM_i` interacted with a full set of quarter dummies, normalised to zero in 2021Q1 (the last pre-treatment quarter). Used to test pre-trends and to display dynamics. Reported as a figure with 95% confidence intervals regardless of what it shows.

---

## 8. Inference

Standard errors clustered by industry (20 clusters).

Cluster-robust standard errors are biased downward when the number of clusters is small, and 20 is within the range where this bites. **Wild cluster bootstrap (Rademacher weights, 9,999 replications, null imposed) is the primary inference.** Analytic cluster-robust errors are reported alongside for comparison, not instead.

Where the two disagree materially, the bootstrap is reported as the headline and the discrepancy is stated explicitly.

---

## 9. Decision rules

Each rule is written so that a reader holding the output table can apply it and reach the same verdict without consulting the author.

**Rule 1 — Separability from the manufacturing decline.**
`PM_i` correlates strongly with manufacturing status (manufacturing mean 0.501, range 0.342–0.701; non-manufacturing mean 0.228, range 0.035–0.486). If β is driven entirely by manufacturing versus non-manufacturing, it cannot be distinguished from the secular manufacturing decline the prior report identifies as a separate channel.

β is therefore re-estimated on the 13 non-manufacturing industries alone, where exposure still varies by a factor of 14.

- **Survives** — non-manufacturing β has the same sign as full-sample β *and* lies within one full-sample standard error of it.
- **Inconclusive** — same sign, between one and two full-sample standard errors away. Reported as inconclusive; the README states the design cannot separate the two explanations.
- **Fails** — sign flips, or the estimate lies more than two full-sample standard errors away. Conclusion: the full-sample estimate is not separable from the manufacturing-specific decline. **This becomes the headline finding**, reported with the same prominence a positive result would receive.

**Rule 2 — Pre-trends.**
From the event-study specification, a Wald test of joint significance of all pre-treatment interaction coefficients (2015Q1–2020Q1, excluding the dropped quarters, normalised at 2021Q1).

- **p ≥ 0.10** — parallel trends not rejected; β reported as the primary estimate.
- **0.05 ≤ p < 0.10** — reported with an explicit caveat in both the results section and the README.
- **p < 0.05** — parallel trends rejected. β is **not** reported as a causal estimate. It is reported as a descriptive association, and the README states the identifying assumption fails.

**Rule 3 — Exposure measure disagreement.**
If stock-based and flow-based exposure produce β estimates of opposite sign, no causal claim is made from either. Both are reported side by side and the conclusion is that the result is not robust to a defensible change in the exposure definition.

---

## 10. Robustness list (closed)

Fixed at commit. Anything run later and not on this list is labelled post hoc in the write-up.

1. Flow-based exposure from the annual GFCF file
2. Gross capital stocks in place of net
3. Full sample 1997Q1–2026Q1
4. No COVID exclusion (2020 retained in full)
5. COVID exclusion extended through 2021Q1
6. Discrete NPV timing convention, δ(1+r)/(r+δ)
7. Discount rate r = 0.03 and r = 0.07
8. Binary treatment: above/below median exposure, in place of continuous
9. Exposure terciles, to test whether the dose–response is monotonic
10. Analytic cluster-robust standard errors alongside the wild bootstrap
11. `pyfixest` cross-check of the `linearmodels` point estimates

---

## 11. Reporting commitment

Null, small, or wrong-signed results are reported as the headline finding, with the same prominence a large and significant result would receive.

The full robustness table is published whatever it shows. No specification is dropped from the write-up for being inconvenient.

The prior descriptive report claimed engineering and vehicles was the most machinery-intensive manufacturing subsector. Measurement places it fourth of seven on capital stock and sixth of seven on flows. **This correction is reported in the README regardless of whether the regression supports the allowance channel**, because it is a finding about the prior work independent of the new estimate.

---

## 12. What would change my mind

Conditions under which the conclusion is that this design cannot answer the question:

1. Pre-treatment interaction coefficients jointly significant at 5% (Rule 2) — the parallel-trends assumption fails and no causal reading survives.
2. β changes sign between stock-based and flow-based exposure (Rule 3) — the result is an artefact of a definitional choice.
3. The non-manufacturing subsample fails Rule 1 — exposure is not separable from manufacturing status, and the design reduces to the descriptive comparison the prior report already made.
4. The wild bootstrap interval admits economically absurd magnitudes (e.g. implying the April 2021 change moved manufacturing investment by more than 50%) — the design lacks the precision to be informative.
5. Fewer than 15 of 20 industries have complete exposure data after suppression handling — the panel is too thin for 20-cluster inference.

None of these is a reason not to publish. Each is a specific, reportable finding about what industry-level data can and cannot identify, which is precisely the limitation the prior report asserted without evidence.

---

## 13. Amendments

Any deviation from the above is recorded here with a date and a reason, in a commit separate from the analysis it affects.

*(none at time of commit)*

**2026-08-07 - Rule 2 test statistic**

Rule 2 specified a Wald test on all 21 pre-treatment interaction coefficients.
This is infeasible: with G=20 clusters the cluster-robust covariance matrix has
rank 18, so a joint test of 21 restrictions is not defined. The quarterly event
study produced a Wald statistic of 7.8e14 from an effectively singular matrix.

Amendment: the pre-trends test is conducted on annual bins rather than
individual quarters. Quarters are grouped by calendar year, with 2020Q1 and
2021Q1 pooled as the omitted base period, giving 5 pre-treatment lead
coefficients and 6 post-treatment lags. This is within the rank of the
covariance matrix.

The quarterly event study is retained as a figure, since plotting individual
coefficients requires no joint test. Only the Wald test uses annual bins.

The thresholds in Rule 2 (p>=0.10 pass, 0.05-0.10 caveat, <0.05 fail) are
unchanged. The amendment changes the granularity of the test, not its
decision rule.

**2026-08-18 - Specification curve added post hoc for exposition**

A specification curve of 48 estimates is added to support a public explainer app. It crosses four sample windows, three exposure measures, two outcome forms (log level, quarter-on-quarter growth) and two treatment forms (continuous, binary above/below median).

This is POST HOC and outside the s10 robustness list. In particular, the growth-rate outcome was never preregistered: s4 fixes the outcome as the log of real investment, and that remains the specification of record.

Results from the curve are reported as an illustration of researcher degrees of freedom, not as findings. No estimate from the curve revises the conclusion
in s9 or s11. The primary estimate remains beta = -0.398, p = 0.696, with both decision rules failed.

I have already computed the curve before writing this amendment, so its content is known: 23 of 48 specifications are significant at 5%, all of them growth-rate forms, all wrong-signed. The amendment is recorded before the results are published rather than before they were computed, and that sequence is stated
here rather than implied otherwise.
