"""Rule 1: non-manufacturing subsample. See PREREGISTRATION.md s9 Rule 1."""
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

panel = pd.read_csv("data/processed/panel.csv")
panel["quarter"] = pd.PeriodIndex(panel["quarter"], freq="Q").to_timestamp()

def fit(df):
    est = df.set_index(["industry", "quarter"])
    return PanelOLS.from_formula(
        "log_investment ~ treat + EntityEffects + TimeEffects", data=est
    ).fit(cov_type="clustered", cluster_entity=True)

full = fit(panel)
nonmfg_df = panel[~panel["is_manufacturing"]]
nonmfg = fit(nonmfg_df)

b_full, se_full = full.params["treat"], full.std_errors["treat"]
b_non = nonmfg.params["treat"]
dist = abs(b_non - b_full) / se_full

print(f"full sample     n={full.nobs:4d}  G={panel['industry'].nunique():2d}  "
      f"beta={b_full:+.4f}  SE={se_full:.4f}  p={full.pvalues['treat']:.4f}")
print(f"non-mfg only    n={nonmfg.nobs:4d}  G={nonmfg_df['industry'].nunique():2d}  "
      f"beta={b_non:+.4f}  SE={nonmfg.std_errors['treat']:.4f}  p={nonmfg.pvalues['treat']:.4f}")
print(f"\nsame sign: {np.sign(b_non) == np.sign(b_full)}")
print(f"distance from full-sample beta: {dist:.2f} full-sample SE")

if np.sign(b_non) != np.sign(b_full) or dist > 2:
    verdict = "FAIL - not separable from the manufacturing decline"
elif dist <= 1:
    verdict = "SURVIVES"
else:
    verdict = "INCONCLUSIVE"
print(f"RULE 1 VERDICT: {verdict}")

e = nonmfg_df.groupby("industry")["pm_share_net"].first()
print(f"\nnon-mfg exposure: min {e.min():.3f} max {e.max():.3f} "
      f"mean {e.mean():.3f} sd {e.std():.3f}")
mfg_e = panel[panel["is_manufacturing"]].groupby("industry")["pm_share_net"].first()
print(f"mfg exposure:     min {mfg_e.min():.3f} max {mfg_e.max():.3f} "
      f"mean {mfg_e.mean():.3f} sd {mfg_e.std():.3f}")