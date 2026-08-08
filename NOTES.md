# Working notes

## 2026-08-02 - exposure built

- Net and gross P&M shares correlate 0.971 (prereg robustness item 2, settled).
- Gross reorders the top two: metals overtakes food. Gross ignores depreciation, machinery depreciates faster than buildings, so machinery gets more weight.
- 970 of 5,915 cells suppressed (16.4%), almost entirely dwellings and cultivated assets, both excluded from the denominator anyway.

## 2026-08-02 - treatment built

- April 2021 step +0.0983; April 2023 step +0.0030. The second boundary is 1/33 the size of the first - justifies the single continuous NPV over regime dummies.
- Apr 2021 step ranges 0.0793-0.1102 across r in {.03,05,.07} x {continuous, discrete}. Scales beta inversely, cannot change sign or significance.
Prereg robustness 6 and 7 settled.

## 2026-08-05 - panel assembled

- 840 rows = 20 industries x 42 quarters. Balanced, zero missing values.
- Sample 2015Q1-2026Q1 excluding 2020Q2-Q4, per prereg s3.
- treat (npv x pm_share_net) ranges 0.0051 to 0.1753. Floor is Education pre-2021; ceiling is Food/drink/tobacco post-2023. That interval is the entire identifying variation.
- Investment ranges 44 to 18,030 (£m/quarter) - roughly 400x across industries, which is why the outcome is in logs.

## 2026-08-07 - primary specification

- beta = -0.3977, clustered SE 1.0168, p = 0.696, CI [-2.394, 1.598].
- In units: April 2021 step, mfg-mean vs non-mfg-mean exposure = -1.07%, CI [-6.42%, +4.29%]. 
Imprecisely estimated zero, wrong sign.
- Consistent with prior report (channel small) and OBR Nov 2023 (no apparent aggregate boost). 
Decision rules s9 not yet run - not a conclusion yet.
- F-test poolability 402.25: FE jointly hugely significant.
- Model confirms spec s7: 20 entities x 42 periods, balanced, F(1,778) so only the interaction is identified. Entity FE absorbs pm_share, time FE absorbs npv.

## 2026-08-08 - event study and Rule 2 (event_study.py, prereg s9, s13)

### The amendment

- Rule 2 as preregistered was infeasible. With G=20 clusters the cluster-robust
covariance matrix has rank 18. The quarterly event study has 41 parameters and
Rule 2 asked for a joint test of 21 restrictions. The Wald statistic came back
as 7.8e14 from an effectively singular matrix - undefined, not significant, and
it would have printed p = 0.0000 without erroring.
- Amended in s13 to annual bins: 5 leads, 6 lags, 2020Q1 and 2021Q1 pooled as the
omitted base. Amendment committed and pushed before the amended test was run,
with the p-value already known. Thresholds unchanged.
- Lesson worth keeping: a Wald test on more restrictions than the rank of the
cluster-robust covariance matrix returns a number without raising. Always print
np.linalg.matrix_rank(np.asarray(res.cov)) alongside any joint test.

### The result

- Amended test: cov rank 11, 11 params, 5 leads. Wald = 11.173, p = 0.0481.
- Rule 2 verdict: FAIL (p < 0.05). Parallel trends rejected. Beta is NOT reported
as a causal estimate - descriptive association only, and the README must state
that the identifying assumption fails.
- Margin is 0.002. State this openly in the write-up rather than reporting
"p < 0.05" as though it were decisive. The rule was fixed in advance and
applies as written, but a reader is entitled to know how close it was. (Same
discipline as the symmetric-framing correction on the EPU correlations in the
prior report.)
- Verdict is provisional until the wild cluster bootstrap has been run on it -
s8 makes the bootstrap primary, and with 20 clusters it can move 0.048 either
way.

### What the figure shows

- A steady drift, not an outlier. Coefficients sit near -1.0 through 2015-2017,
then rise more or less monotonically from 2018 to the 2021Q1 base.
- Direction is the surprise: high-exposure industries were gaining relative
ground on low-exposure ones through the pre-period. That is the opposite of the
secular-decline story, and is consistent with 2021 being the highest annual
manufacturing investment in the ONS series since 1997 (prior report s3.1). The
pre-trend is the run-up to a cyclical peak, not a long decline.
- The path is tent-shaped, peaking at the base period and falling steadily to
about -1.5 by 2026Q1. The shape is invariant to the choice of base period -
changing the base shifts every coefficient by a constant.
- This is where the wrong-signed beta comes from. A parallel-trends design takes
the pre-period slope as the counterfactual. That slope is upward, so the
counterfactual keeps rising while the actual path falls, and the gap is read as
a negative treatment effect. Economically it is not allowances depressing
investment: it is the four competing channels from the prior report (2022
energy shock, Bank Rate 2022-24, Brexit, secular share decline) arriving after
2021, plus House and Shapiro payback from a record 2021 base. The prior report
said exactly this descriptively - "the 2021 baseline was the highest ever
achieved under stimulus... it was inevitable for some drop-off to occur
post-2021". The event study shows it mechanically.
- Every individual coefficient's 95% CI contains zero, pre and post. Only the
joint test rejects - five coefficients leaning the same way, not one precise
estimate. Say so plainly; the plot looks dramatic until you notice the shading
spans two full log points throughout.
- Plotting fix applied: the line and ribbon are broken across the dropped
2020Q2-Q4 quarters and the window shaded grey. Before the fix, matplotlib
interpolated across three quarters that are not in the sample, producing the
most visually striking feature of the chart out of nothing.

---

## Outstanding

- Rule 1 - non-manufacturing subsample (13 industries, exposure range
0.035-0.486). Determines whether the story is "no detectable effect" or "the
design cannot separate the allowance channel from manufacturing status".
Sharpened by the event study: if the pre-trend is a run-up to a manufacturing
investment peak, it should be materially weaker among non-manufacturing.
- Wild cluster bootstrap (s8) - primary inference, on both beta and the Rule 2
test.
- Remaining robustness - items 1, 3, 4, 5, 8, 9, 10, 11 of s10.
- README - week 4. Must include, per s11: the null reported at headline
prominence, the Rule 2 failure, and the correction to the prior report's claim
that engineering and vehicles was the most machinery-intensive subsector
(measured: 4th of 7 on stocks, 6th of 7 on flows).