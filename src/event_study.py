"""Event study and pre-trends test. See PREREGISTRATION.md s7 (secondary), s9 Rule 2, s13."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

BASE_QUARTERS = ["2020Q1", "2021Q1"]
TREAT_START = "2021Q2"

panel = pd.read_csv("data/processed/panel.csv")
panel["q"] = pd.PeriodIndex(panel["quarter"], freq="Q")
panel["quarter"] = panel["q"].dt.to_timestamp()


def make_terms(df, bin_col):
    terms = []
    for b in sorted(df[bin_col].unique()):
        if b == "BASE":
            continue
        col = f"x_{b}"
        df[col] = df["pm_share_net"] * (df[bin_col] == b)
        terms.append(col)
    return terms

def fit(df, terms):
    formula = "log_investment ~ " + " + ".join(terms) + " + EntityEffects + TimeEffects"
    return PanelOLS.from_formula(formula, data=df.set_index(["industry", "quarter"])
                                 ).fit(cov_type="clustered", cluster_entity=True)


annual = panel.copy()
annual["bin"] = np.where(annual["q"].astype(str).isin(BASE_QUARTERS),
                         "BASE", annual["q"].dt.year.astype(str))
terms_a = make_terms(annual, "bin")
res_a = fit(annual, terms_a)

pre = [t for t in terms_a if t[2:] < "2021"]
R = np.zeros((len(pre), len(res_a.params)))
idx = {n: i for i, n in enumerate(res_a.params.index)}
for i, t in enumerate(pre):
    R[i, idx[t]] = 1
wald = res_a.wald_test(restriction=R, value=np.zeros(len(pre)))

print(f"cov rank {np.linalg.matrix_rank(np.asarray(res_a.cov))}, "
      f"{len(terms_a)} params, testing {len(pre)} leads")
print(f"RULE 2: Wald = {wald.stat:.3f}, p = {wald.pval:.4f}")


quarterly = panel.copy()
quarterly["bin"] = np.where(quarterly["q"].astype(str) == "2021Q1",
                            "BASE", quarterly["q"].astype(str))
terms_q = make_terms(quarterly, "bin")
res_q = fit(quarterly, terms_q)

ci = res_q.conf_int()
plot = pd.DataFrame({
    "q": [pd.Period("2021Q1", "Q")] + [pd.Period(t[2:], "Q") for t in terms_q],
    "b": [0.0] + [res_q.params[t] for t in terms_q],
    "lo": [0.0] + [ci.loc[t, "lower"] for t in terms_q],
    "hi": [0.0] + [ci.loc[t, "upper"] for t in terms_q],
}).sort_values("q")

# two segments either side of the dropped COVID quarters, prereg s3
pre = plot[plot["q"] <= pd.Period("2020Q1", "Q")]
post = plot[plot["q"] >= pd.Period("2021Q1", "Q")]

fig, ax = plt.subplots(figsize=(11, 5))
for seg in (pre, post):
    xs = seg["q"].dt.to_timestamp()
    ax.fill_between(xs, seg["lo"], seg["hi"], alpha=0.2, color="#8b1a1a")
    ax.plot(xs, seg["b"], marker="o", ms=3, color="#8b1a1a")

ax.axvspan(pd.Period("2020Q2", "Q").to_timestamp(),
           pd.Period("2021Q1", "Q").to_timestamp(), color="grey", alpha=0.12,
           label="2020Q2-Q4 excluded (COVID)")
ax.axhline(0, color="black", lw=0.8)
ax.axvline(pd.Period("2021Q2", "Q").to_timestamp(), color="black", ls="--", lw=0.8,
           label="Apr 2021: super-deduction begins")
ax.legend(loc="lower left", fontsize=9, framealpha=0.9)

ax.set_ylabel("coefficient on exposure × period")
ax.set_title("Exposure × quarter coefficients, base 2021Q1", fontsize=11)
ax.text(0.5, -0.16,
        f"Pre-trend Wald test on annual bins: p = {wald.pval:.3f}. "
        "Bands are 95% CIs, clustered by industry (20 clusters).",
        transform=ax.transAxes, ha="center", fontsize=9, color="#444")

fig.tight_layout()
fig.savefig("output/figures/event_study.png", dpi=150)
print("\nsaved output/figures/event_study.png")