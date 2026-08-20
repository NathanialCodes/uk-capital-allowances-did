
"""Power analysis for the primary specification. Post hoc, see PREREGISTRATION.md s13.

Asks what effect sizes this design could have detected, given its realised precision.
Two approaches: an analytical minimum detectable effect from the estimated standard
error, and a simulation that imposes known effects on the actual panel and counts how
often they are recovered.
"""
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy import stats

warnings.filterwarnings("ignore")

ALPHA = 0.05
TARGET_POWER = 0.80
N_SIMS = 2000
SEED = 42

STEP_2021 = 0.0983
MFG_MEAN, NONMFG_MEAN = 0.501, 0.228
D_TREAT = STEP_2021 * (MFG_MEAN - NONMFG_MEAN)

BENCHMARKS = {
    "Maffini, Xing and Devereux (2019), UK": 2.3,
    "DMP net-additional, Budget 2021": 4.1,
    "OBR (2021) ex ante": 10.0,
    "Zwick and Mahon (2017), US, window 1": 10.4,
    "Zwick and Mahon (2017), US, window 2": 16.9,
}

panel = pd.read_csv("data/processed/panel.csv")
panel["quarter"] = pd.PeriodIndex(panel["quarter"], freq="Q").to_timestamp()
G = panel["industry"].nunique()

res = PanelOLS.from_formula("log_investment ~ treat + EntityEffects + TimeEffects",
                            data=panel.set_index(["industry", "quarter"])
                            ).fit(cov_type="clustered", cluster_entity=True)
se = float(res.std_errors["treat"])
beta_hat = float(res.params["treat"])

# ---- analytical MDE -----------------------------------------------------
z_crit, z_pow = stats.norm.ppf(1 - ALPHA / 2), stats.norm.ppf(TARGET_POWER)
t_crit, t_pow = stats.t.ppf(1 - ALPHA / 2, G - 1), stats.t.ppf(TARGET_POWER, G - 1)
mde_normal = (z_crit + z_pow) * se
mde_t = (t_crit + t_pow) * se

def to_pct(b):
    return 100 * b * D_TREAT

print(f"beta = {beta_hat:.4f}, clustered SE = {se:.4f}, G = {G}")
print(f"\nMinimum detectable effect at {TARGET_POWER:.0%} power, {ALPHA:.0%} two-sided:")
print(f"  normal reference:      beta {mde_normal:.3f}  ->  {to_pct(mde_normal):.1f}%")
print(f"  t({G-1}) reference:      beta {mde_t:.3f}  ->  {to_pct(mde_t):.1f}%")

# ---- simulation ---------------------------------------------------------
d = panel.copy()
for col in ["log_investment", "treat"]:
    x = d[col].values.copy()
    for _ in range(60):
        x = x - pd.Series(x).groupby(d["industry"].values).transform("mean").values
        x = x - pd.Series(x).groupby(d["quarter"].values).transform("mean").values
    d[col + "_dm"] = x

y, X = d["log_investment_dm"].values, d["treat_dm"].values
g = pd.factorize(d["industry"])[0]
n, k = len(y), 1 + (G - 1) + (panel["quarter"].nunique() - 1)
resid = y - X * beta_hat


def ols_t(yv):
    XtX = X @ X
    b = (X @ yv) / XtX
    e = yv - X * b
    meat = sum((X[g == j] @ e[g == j]) ** 2 for j in range(G))
    c = (G / (G - 1)) * ((n - 1) / (n - k - 1))
    return b, b / np.sqrt(c * meat / XtX ** 2)


rng = np.random.default_rng(SEED)
crit = stats.t.ppf(1 - ALPHA / 2, G - 1)
targets = np.arange(0, 21, 1.0)
rows = []
for pct in targets:
    b_true = pct / (100 * D_TREAT)
    rejects = 0
    for _ in range(N_SIMS):
        w = rng.choice([-1.0, 1.0], size=G)[g]
        _, t_stat = ols_t(X * b_true + resid * w)
        rejects += abs(t_stat) > crit
    rows.append({"effect_pct": pct, "beta_true": b_true, "power": rejects / N_SIMS})

power = pd.DataFrame(rows)
power.to_csv("output/tables/power.csv", index=False)

sim_mde = np.interp(TARGET_POWER, power["power"], power["effect_pct"])
print(f"\nSimulation ({N_SIMS} draws, Rademacher weights by cluster):")
print(f"  size at true effect 0: {power.loc[0, 'power']:.3f}  (should be near {ALPHA})")
print(f"  effect reaching {TARGET_POWER:.0%} power: {sim_mde:.1f}%")

print(f"\nPower against effect sizes reported in the literature:")
for label, pct in BENCHMARKS.items():
    pw = np.interp(pct, power["effect_pct"], power["power"])
    verdict = "detectable" if pw >= TARGET_POWER else "underpowered"
    print(f"  {label:40s} {pct:5.1f}%   power {pw:.2f}   {verdict}")

# ---- figure -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(power["effect_pct"], power["power"], color="#8b1a1a", lw=2.5)
ax.axhline(TARGET_POWER, color="grey", ls="--", lw=1)
ax.axhline(ALPHA, color="grey", ls=":", lw=1)
ax.text(20.3, TARGET_POWER, "80%", va="center", fontsize=9, color="grey")
ax.text(20.3, ALPHA, "5%", va="center", fontsize=9, color="grey")
for label, pct in BENCHMARKS.items():
    pw = np.interp(pct, power["effect_pct"], power["power"])
    ax.plot([pct], [pw], "o", color="#2c5f8a", ms=6)
    ax.annotate(label.split(" (")[0], (pct, pw), textcoords="offset points",
                xytext=(6, -10), fontsize=8, color="#2c5f8a")
ax.set_xlabel("True differential effect of the April 2021 reform (%)")
ax.set_ylabel("Probability of rejecting the null at 5%")
ax.set_title("What this design could have detected", fontsize=11)
ax.set_xlim(0, 21)
ax.set_ylim(0, 1)
fig.tight_layout()
fig.savefig("output/figures/power_curve.png", dpi=150)
print("\nsaved output/figures/power_curve.png")