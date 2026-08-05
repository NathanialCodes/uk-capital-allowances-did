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