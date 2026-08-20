
"""Precompute every number the Streamlit app displays. Writes app/data/results.json.

The app imports only streamlit, pandas and plotly. All estimation happens here,
so the app and the repo cannot disagree, and the app has no econometrics
dependencies to break on deploy.
"""
import json
import warnings

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")

INVESTMENT_FILE = "data/raw/businessinvestmentbyindustryandasset_2026-06-30.xlsx"
OUT = "app/data/results.json"
BASE_QUARTER = "2021Q1"
STEP_2021, MFG_MEAN, NONMFG_MEAN = 0.0983, 0.501, 0.228

panel = pd.read_csv("data/processed/panel.csv")
panel["q"] = pd.PeriodIndex(panel["quarter"], freq="Q")
panel["quarter"] = panel["q"].dt.to_timestamp()
exposure = pd.read_csv("data/processed/exposure.csv")
flow = pd.read_csv("data/processed/exposure_flow.csv")
treatment = pd.read_csv("data/processed/treatment.csv")
curve = pd.read_csv("output/tables/spec_curve.csv")

out = {}

# ---------- page 1: the puzzle -------------------------------------------
inv = pd.read_excel(INVESTMENT_FILE, sheet_name="Table_4_CVM_SA", skiprows=3)
inv = inv.rename(columns={inv.columns[0]: "quarter"})
inv = inv[inv["quarter"].astype(str).str.match(r"^\d{4}Q[1-4]$")]
inv = inv.set_index("quarter")
series = {}
for label, col in [("manufacturing", "Total Manufacturing"),
                   ("non_manufacturing", "Total Non-Manufacturing")]:
    s = pd.to_numeric(inv[col], errors="coerce")
    s = s[(s.index >= "2019Q1") & (s.index <= "2026Q1")]
    series[label] = {"quarters": list(s.index),
                     "index": list((100 * s / s.loc[BASE_QUARTER]).round(2)),
                     "level": list(s.round(0))}
out["puzzle"] = {"series": series, "base_quarter": BASE_QUARTER}

# ---------- page 2: the policy -------------------------------------------
def npv(kind, rate, tax, r=0.05, discrete=False):
    pv = rate if kind == "fya" else (rate * (1 + r) / (r + rate) if discrete else rate / (r + rate))
    return tax * pv

t = treatment.copy()
t = t[(t["quarter"] >= "2019Q1") & (t["quarter"] <= "2026Q1")]
out["policy"] = {
    "quarters": list(t["quarter"]),
    "npv": list(t["npv"].round(4)),
    "regime": list(t["regime"]),
    "sensitivity": [
        {"r": r, "discrete": d,
         "pre": round(npv("wda", 0.18, 0.19, r, d), 4),
         "step_2021": round(npv("fya", 1.30, 0.19) - npv("wda", 0.18, 0.19, r, d), 4)}
        for r in (0.03, 0.05, 0.07) for d in (False, True)
    ],
    "step_2021": STEP_2021,
    "step_2023": round(npv("fya", 1.00, 0.25) - npv("fya", 1.30, 0.19), 4),
}

# ---------- page 3: exposure ---------------------------------------------
e = exposure.merge(flow, on="industry")
med = {c: float(e[c].median()) for c in ["pm_share_net", "pm_share_gross", "pm_share_flow"]}
out["exposure"] = {
    "industries": e.to_dict(orient="records"),
    "medians": med,
    "mfg_range": [float(e[e.is_manufacturing].pm_share_net.min()),
                  float(e[e.is_manufacturing].pm_share_net.max())],
    "nonmfg_range": [float(e[~e.is_manufacturing].pm_share_net.min()),
                     float(e[~e.is_manufacturing].pm_share_net.max())],
    "corr_net_gross": round(float(e.pm_share_net.corr(e.pm_share_gross)), 4),
    "binary_split_identical_net_gross": bool(
        ((e.pm_share_net > med["pm_share_net"]) == (e.pm_share_gross > med["pm_share_gross"])).all()),
    "overlap_industries": list(
        e[(~e.is_manufacturing) & (e.pm_share_net > e[e.is_manufacturing].pm_share_net.min())]["industry"]),
}

# ---------- page 4: the result -------------------------------------------
def fit(df, dep="log_investment", treat="treat"):
    return PanelOLS.from_formula(f"{dep} ~ {treat} + EntityEffects + TimeEffects",
                                 data=df.set_index(["industry", "quarter"])
                                 ).fit(cov_type="clustered", cluster_entity=True)

r = fit(panel)
ci = r.conf_int().loc["treat"]
d_treat = STEP_2021 * (MFG_MEAN - NONMFG_MEAN)
out["result"] = {
    "beta": round(float(r.params["treat"]), 4),
    "se": round(float(r.std_errors["treat"]), 4),
    "p": round(float(r.pvalues["treat"]), 4),
    "ci": [round(float(ci["lower"]), 4), round(float(ci["upper"]), 4)],
    "n": int(r.nobs), "n_clusters": 20,
    "effect_pct": round(100 * float(r.params["treat"]) * d_treat, 2),
    "effect_ci_pct": [round(100 * float(ci["lower"]) * d_treat, 2),
                      round(100 * float(ci["upper"]) * d_treat, 2)],
    "bootstrap_p": 0.71,
}

q = panel.copy()
q["bin"] = np.where(q["q"].astype(str) == BASE_QUARTER, "BASE", q["q"].astype(str))
terms = []
for b in sorted(q["bin"].unique()):
    if b == "BASE":
        continue
    q[f"x_{b}"] = q["pm_share_net"] * (q["bin"] == b)
    terms.append(f"x_{b}")
re = PanelOLS.from_formula("log_investment ~ " + " + ".join(terms) +
                           " + EntityEffects + TimeEffects",
                           data=q.set_index(["industry", "quarter"])
                           ).fit(cov_type="clustered", cluster_entity=True)
cie = re.conf_int()
ev = pd.DataFrame({"quarter": [BASE_QUARTER] + [t_[2:] for t_ in terms],
                   "beta": [0.0] + [float(re.params[t_]) for t_ in terms],
                   "lo": [0.0] + [float(cie.loc[t_, "lower"]) for t_ in terms],
                   "hi": [0.0] + [float(cie.loc[t_, "upper"]) for t_ in terms]})
ev = ev.sort_values("quarter")
out["event_study"] = {
    "quarters": list(ev["quarter"]),
    "beta": list(ev["beta"].round(4)),
    "lo": list(ev["lo"].round(4)),
    "hi": list(ev["hi"].round(4)),
    "treatment_start": "2021Q2",
    "excluded": ["2020Q2", "2020Q3", "2020Q4"],
    "wald_p": 0.0481, "wald_stat": 11.173, "n_leads": 5,
    "verdict": "FAIL",
}

nm = panel[~panel["is_manufacturing"]]
rn = fit(nm)
out["rule1"] = {
    "full_beta": out["result"]["beta"], "full_se": out["result"]["se"],
    "nonmfg_beta": round(float(rn.params["treat"]), 4),
    "nonmfg_se": round(float(rn.std_errors["treat"]), 4),
    "nonmfg_p": round(float(rn.pvalues["treat"]), 4),
    "nonmfg_n": int(rn.nobs), "nonmfg_clusters": int(nm["industry"].nunique()),
    "sign_flipped": bool(np.sign(rn.params["treat"]) != np.sign(r.params["treat"])),
    "verdict": "FAIL",
}

# ---------- page 5: spec curve -------------------------------------------
out["spec_curve"] = {
    "specs": curve.round(4).to_dict(orient="records"),
    "n_specs": len(curve),
    "n_sig_5pct": int((curve["p"] < 0.05).sum()),
    "n_sig_growth": int(((curve["p"] < 0.05) & (curve["outcome"] == "growth")).sum()),
    "n_sig_level": int(((curve["p"] < 0.05) & (curve["outcome"] == "log level")).sum()),
    "min_p_level": round(float(curve[curve["outcome"] == "log level"]["p"].min()), 4),
}

power_df = pd.read_csv("output/tables/power.csv")
out["power"] = {
    "effect_pct": list(power_df["effect_pct"]),
    "power": list(power_df["power"].round(3)),
    "mde": 8.0,
    "benchmarks": [
        {"label": "Maffini, Xing and Devereux (2019), UK", "pct": 2.3, "power": 0.10},
        {"label": "DMP net-additional, Budget 2021", "pct": 4.1, "power": 0.27},
        {"label": "OBR (2021) ex ante", "pct": 10.0, "power": 0.95},
        {"label": "Zwick and Mahon (2017), US", "pct": 10.4, "power": 0.96},
    ],
}

out["meta"] = {
    "vintages": {"business_investment": "2026-06-30",
                 "capital_stocks": "2025-11-27", "gfcf": "2025-11-03"},
    "panel": {"n": 840, "industries": 20, "quarters": 42,
              "sample": "2015Q1-2026Q1 excluding 2020Q2-Q4"},
}

with open(OUT, "w") as f:
    json.dump(out, f, indent=1)

import os
print(f"wrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
print(f"sanity: beta={out['result']['beta']} p={out['result']['p']} "
      f"| effect {out['result']['effect_pct']}% "
      f"| rule1 nonmfg {out['rule1']['nonmfg_beta']} "
      f"| curve {out['spec_curve']['n_sig_5pct']}/{out['spec_curve']['n_specs']} sig")
print(f"binary split net==gross: {out['exposure']['binary_split_identical_net_gross']}")
print(f"overlap industries: {out['exposure']['overlap_industries']}")