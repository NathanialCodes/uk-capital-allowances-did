# Working notes

## 2026-08-02 - exposure built

- Net and gross P&M shares correlate 0.971 (prereg robustness item 2, settled).
- Gross reorders the top two: metals overtakes food. Gross ignores depreciation, machinery depreciates faster than buildings, so machinery gets more weight.
- 970 of 5,915 cells suppressed (16.4%), almost entirely dwellings and cultivated assets, both excluded from the denominator anyway.

## 2026-08-02 - treatment built
- April 2021 step +0.0983; April 2023 step +0.0030. The second boundary is 1/33 the size of the first - justifies the single continuous NPV over regime dummies.
- Apr 2021 step ranges 0.0793–0.1102 across r in {.03,05,.07} x {continuous, discrete}. Scales beta inversely, cannot change sign or significance.
Prereg robustness 6 and 7 settled.

