
"""Post hoc specification curve for the explainer app. See PREREGISTRATION.md s13.

NOT a robustness check. The growth-rate outcome was never preregistered; s4 fixes
the outcome as log real investment. This grid exists to show how many defensible
looking specifications a researcher could have tried, and what they would have found.
"""
import itertools
import warnings

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

warnings.filterwarnings("ignore")

INVESTMENT_FILE = "data/raw/businessinvestmentbyindustryandasset_2026-06-30.xlsx"
COVID_DROP = ["2020Q2", "2020Q3", "2020Q4"]

SAMPLES = {
    "2015-, drop 2020Q2-Q4": ("2015Q1", "2026Q1", COVID_DROP),
    "2015-, keep 2020":      ("2015Q1", "2026Q1", []),
    "2015-, drop to 2021Q1": ("2015Q1", "2026Q1", COVID_DROP + ["2021Q1"]),
    "1997- full":            ("1997Q1", "2026Q1", []),
}
EXPOSURES = {"net stock": "pm_share_net", "gross stock": "pm_share_gross",
             "flow": "pm_share_flow"}
OUTCOMES = {"log level": "log_investment", "growth": "growth"}
TREATMENTS = ["continuous", "binary"]

PREREG = ("2015-, drop 2020Q2-Q4", "net stock", "log level", "continuous")

exposure = pd.read_csv("data/processed/exposure.csv")
flow = pd.read_csv("data/processed/exposure_flow.csv")
treatment = pd.read_csv("data/processed/treatment.csv")
treatment["q"] = pd.PeriodIndex(treatment["quarter"], freq="Q")

inv = pd.read_excel(INVESTMENT_FILE, sheet_name="Table_4_CVM_SA", skiprows=3)
inv = inv.rename(columns={inv.columns[0]: "quarter"})
inv = inv[inv["quarter"].astype(str).str.match(r"^\d{4}Q[1-4]$")]
base = inv.melt(id_vars="quarter", var_name="industry", value_name="investment")
base["q"] = pd.PeriodIndex(base["quarter"], freq="Q")
base["investment"] = pd.to_numeric(base["investment"], errors="coerce")
base = base[base["industry"].isin(exposure["industry"])]
base = (base.merge(exposure, on="industry", validate="many_to_one")
            .merge(flow, on="industry", validate="many_to_one")
            .merge(treatment[["q", "npv"]], on="q", validate="many_to_one"))
base = base.dropna(subset=["investment"])
base = base[base["investment"] > 0]
base = base.sort_values(["industry", "q"]).reset_index(drop=True)
base["log_investment"] = np.log(base["investment"])


def add_growth(df):
    """Quarter-on-quarter log growth, in percent.

    Any observation whose predecessor is not the immediately preceding quarter
    is set to NaN. Without this, diff() silently spans the dropped COVID
    quarters and labels a four-quarter change as a one-quarter change.
    """
    df = df.sort_values(["industry", "q"]).copy()
    df["growth"] = df.groupby("industry")["log_investment"].diff() * 100
    prev_q = df.groupby("industry")["q"].shift(1)
    contiguous = (df["q"] - prev_q).apply(lambda x: getattr(x, "n", np.nan)) == 1
    df.loc[~contiguous, "growth"] = np.nan
    return df


rows = []
for (s_name, (start, end, drop)), (e_name, e_col), (o_name, o_col), t_form in \
        itertools.product(SAMPLES.items(), EXPOSURES.items(), OUTCOMES.items(), TREATMENTS):

    d = base[(base["q"] >= pd.Period(start, "Q")) & (base["q"] <= pd.Period(end, "Q"))]
    d = d[~d["q"].isin([pd.Period(x, "Q") for x in drop])]
    d = add_growth(d)

    if t_form == "continuous":
        d["T"] = d["npv"] * d[e_col]
    else:
        median = d.groupby("industry")[e_col].first().median()
        d["T"] = d["npv"] * (d[e_col] > median).astype(float)

    d = d.dropna(subset=[o_col, "T"]).copy()
    d["quarter"] = d["q"].dt.to_timestamp()
    r = PanelOLS.from_formula(f"{o_col} ~ T + EntityEffects + TimeEffects",
                              data=d.set_index(["industry", "quarter"])
                              ).fit(cov_type="clustered", cluster_entity=True)
    ci = r.conf_int().loc["T"]
    rows.append(dict(sample=s_name, exposure=e_name, outcome=o_name, treat=t_form,
                     beta=r.params["T"], se=r.std_errors["T"], p=r.pvalues["T"],
                     ci_lo=ci["lower"], ci_hi=ci["upper"], n=int(r.nobs),
                     preregistered=(s_name, e_name, o_name, t_form) == PREREG))

curve = pd.DataFrame(rows).sort_values("beta").reset_index(drop=True)
curve.to_csv("output/tables/spec_curve.csv", index=False)

sig = curve["p"] < 0.05
print(f"{len(curve)} specifications, {sig.sum()} significant at 5%")
print(f"of those, {(sig & (curve.outcome == 'growth')).sum()} are growth-rate forms "
      f"and {(sig & (curve.outcome == 'log level')).sum()} are log-level forms")
print()
print(curve.groupby("outcome").agg(n=("p", "size"), min_p=("p", "min"),
                                   sig_5pct=("p", lambda x: (x < 0.05).sum()),
                                   median_beta=("beta", "median")).round(4).to_string())
print("\npreregistered specification:")
print(curve[curve.preregistered][["sample", "exposure", "outcome", "treat",
                                  "beta", "se", "p", "n"]].to_string(index=False))
print("\nmost significant 3:")
print(curve.nsmallest(3, "p")[["sample", "exposure", "outcome", "treat",
                               "beta", "se", "p"]].to_string(index=False))




