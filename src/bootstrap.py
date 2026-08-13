"""Wild cluster bootstrap. See PREREGISTRATION.md s8."""
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

B = 9999
SEED = 1

panel = pd.read_csv("data/processed/panel.csv")
panel["quarter"] = pd.PeriodIndex(panel["quarter"], freq="Q").to_timestamp()

res = PanelOLS.from_formula("log_investment ~ treat + EntityEffects + TimeEffects",
                            data=panel.set_index(["industry", "quarter"])
                            ).fit(cov_type="clustered", cluster_entity=True)
t_obs = res.params["treat"] / res.std_errors["treat"]
print(f"observed: beta={res.params['treat']:+.4f}  t={t_obs:+.4f}  "
      f"analytic p={res.pvalues['treat']:.4f}")

d = panel.copy()
for col in ["log_investment", "treat"]:
    x = d[col].values.copy()
    for _ in range(60):
        x = x - pd.Series(x).groupby(d["industry"].values).transform("mean").values
        x = x - pd.Series(x).groupby(d["quarter"].values).transform("mean").values
    d[col + "_dm"] = x


y = d["log_investment_dm"].values
X = d["treat_dm"].values
g = pd.factorize(d["industry"])[0]
G = g.max() + 1
n = len(y)
k = 1 + (d["industry"].nunique() - 1) + (d["quarter"].nunique() - 1)

def ols_t(yv):
    XtX = X @ X
    bh = (X @ yv) / XtX
    e = yv - X * bh
    meat = sum((X[g == j] @ e[g == j]) ** 2 for j in range(G))
    c = (G / (G - 1)) * ((n - 1) / (n - k - 1))
    V = c * meat / XtX ** 2
    return bh, bh / np.sqrt(V)

b_hat, t_check = ols_t(y)
print(f"demeaned check: beta={b_hat:+.4f}  t={t_check:+.4f}")

rng = np.random.default_rng(SEED)
resid_null = y                      # beta imposed at 0, so residual is y itself
t_star = np.empty(B)
for i in range(B):
    w = rng.choice([-1.0, 1.0], size=G)[g]
    t_star[i] = ols_t(resid_null * w)[1]


p_boot = np.mean(np.abs(t_star) >= np.abs(t_check))
lo, hi = np.quantile(t_star, [0.025, 0.975])
print(f"\nWILD CLUSTER BOOTSTRAP, B={B}, {G} clusters, seed {SEED}")
print(f"  p = {p_boot:.4f}   (analytic p = {res.pvalues['treat']:.4f})")
print(f"  bootstrap t distribution 2.5/97.5 pct: {lo:+.3f}, {hi:+.3f}")
print(f"  normal reference: -1.960, +1.960")
