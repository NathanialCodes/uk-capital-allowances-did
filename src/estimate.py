"""Primary specification. See PREREGISTRATION.md s7, s8."""
import pandas as pd
from linearmodels.panel import PanelOLS

panel = pd.read_csv("data/processed/panel.csv")
panel["quarter"] = pd.PeriodIndex(panel["quarter"], freq="Q").to_timestamp()
panel = panel.set_index(["industry", "quarter"])

mod = PanelOLS.from_formula("log_investment ~ treat + EntityEffects + TimeEffects", data=panel)
res = mod.fit(cov_type="clustered", cluster_entity=True)
print(res)


# interpretation, prereg s7
STEP = 0.0983
MFG, NONMFG = 0.501, 0.228
d_treat = STEP * (MFG - NONMFG)
b = res.params["treat"]
lo, hi = res.conf_int().loc["treat"]
print(f"\nApril 2021 step, mfg-mean vs non-mfg-mean exposure:")
print(f"  d(treat) = {d_treat:.4f}")
print(f"  effect   = {100*b*d_treat:+.2f}%   95% CI [{100*lo*d_treat:+.2f}%, {100*hi*d_treat:+.2f}%]")