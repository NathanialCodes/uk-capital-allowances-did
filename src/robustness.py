"""Pre-specified robustness table. See PREREGISTRATION.md s10."""
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

INVESTMENT_FILE = "data/raw/businessinvestmentbyindustryandasset_2026-06-30.xlsx"

panel = pd.read_csv("data/processed/panel.csv")
panel["q"] = pd.PeriodIndex(panel["quarter"], freq="Q")
panel["quarter"] = panel["q"].dt.to_timestamp()

exposure = pd.read_csv("data/processed/exposure.csv")
exposure_flow = pd.read_csv("data/processed/exposure_flow.csv")
treatment = pd.read_csv("data/processed/treatment.csv")
treatment["q"] = pd.PeriodIndex(treatment["quarter"], freq="Q")


def fit(df, treat_col="treat"):
    est = df.set_index(["industry", "quarter"])
    r = PanelOLS.from_formula(
        f"log_investment ~ {treat_col} + EntityEffects + TimeEffects", data=est
    ).fit(cov_type="clustered", cluster_entity=True)
    return dict(beta=r.params[treat_col], se=r.std_errors[treat_col],
                p=r.pvalues[treat_col], n=int(r.nobs), G=df["industry"].nunique())


rows = []
def add(label, df, treat_col="treat"):
    rows.append({"spec": label, **fit(df, treat_col)})


def build_long(start, end, drop):
    """Rebuild the panel over an arbitrary sample window."""
    inv = pd.read_excel(INVESTMENT_FILE, sheet_name="Table_4_CVM_SA", skiprows=3)
    inv = inv.rename(columns={inv.columns[0]: "quarter"})
    inv = inv[inv["quarter"].astype(str).str.match(r"^\d{4}Q[1-4]$")]
    long = inv.melt(id_vars="quarter", var_name="industry", value_name="investment")
    long["q"] = pd.PeriodIndex(long["quarter"], freq="Q")
    long["investment"] = pd.to_numeric(long["investment"], errors="coerce")
    long = long[long["industry"].isin(exposure["industry"])]
    keep = (long["q"] >= pd.Period(start, "Q")) & (long["q"] <= pd.Period(end, "Q"))
    long = long[keep & ~long["q"].isin([pd.Period(x, "Q") for x in drop])]
    long = long.merge(exposure, on="industry", how="left", validate="many_to_one")
    long = long.merge(treatment[["q", "npv"]], on="q", how="left", validate="many_to_one")
    long = long.dropna(subset=["investment", "npv"])
    long = long[long["investment"] > 0]
    long["log_investment"] = np.log(long["investment"])
    long["treat"] = long["npv"] * long["pm_share_net"]
    long["quarter"] = long["q"].dt.to_timestamp()
    return long


add("0. Primary (prereg s7)", panel)

# 1. flow-based exposure
p1 = panel.merge(exposure_flow, on="industry", how="left", validate="many_to_one")
p1["treat_flow"] = p1["npv"] * p1["pm_share_flow"]
add("1. Flow-based exposure", p1, "treat_flow")

# 2. gross capital stocks
p2 = panel.copy()
p2["treat_gross"] = p2["npv"] * p2["pm_share_gross"]
add("2. Gross capital stocks", p2, "treat_gross")

# 3, 4, 5. sample variants
add("3. Full sample 1997Q1-2026Q1", build_long("1997Q1", "2026Q1", []))
add("4. No COVID exclusion", build_long("2015Q1", "2026Q1", []))
add("5. COVID exclusion incl 2021Q1",
    build_long("2015Q1", "2026Q1", ["2020Q2", "2020Q3", "2020Q4", "2021Q1"]))

# 8. binary treatment, above/below median exposure
p8 = panel.copy()
med = p8.groupby("industry")["pm_share_net"].first().median()
p8["treat_bin"] = p8["npv"] * (p8["pm_share_net"] > med).astype(float)
add("8. Binary above/below median", p8, "treat_bin")

# 9. exposure terciles - two coefficients from one regression
p9 = panel.copy()
ind_exp = p9.groupby("industry")["pm_share_net"].first()
tercile = pd.qcut(ind_exp, 3, labels=[0, 1, 2]).astype(int)
p9["tercile"] = p9["industry"].map(tercile)
p9["treat_mid"] = p9["npv"] * (p9["tercile"] == 1).astype(float)
p9["treat_high"] = p9["npv"] * (p9["tercile"] == 2).astype(float)
r9 = PanelOLS.from_formula(
    "log_investment ~ treat_mid + treat_high + EntityEffects + TimeEffects",
    data=p9.set_index(["industry", "quarter"])
).fit(cov_type="clustered", cluster_entity=True)
for term, label in [("treat_mid", "9a. Tercile mid (vs low)"),
                    ("treat_high", "9b. Tercile high (vs low)")]:
    rows.append({"spec": label, "beta": r9.params[term], "se": r9.std_errors[term],
                 "p": r9.pvalues[term], "n": int(r9.nobs), "G": 20})

out = pd.DataFrame(rows)
out.to_csv("output/tables/robustness.csv", index=False)
print(out.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
print(f"\nsign: {(out['beta'] < 0).sum()} negative, {(out['beta'] > 0).sum()} positive")
print(f"p range {out['p'].min():.3f} to {out['p'].max():.3f}, "
      f"beta range {out['beta'].min():+.3f} to {out['beta'].max():+.3f}")

# 11. pyfixest cross-check
try:
    import pyfixest as pf
    chk = pf.feols("log_investment ~ treat | industry + quarter",
                   data=panel, vcov={"CRV1": "industry"})
    b_pf = chk.coef()["treat"]
    print(f"\n11. pyfixest cross-check: beta={b_pf:+.6f} vs "
          f"linearmodels {rows[0]['beta']:+.6f}  diff={abs(b_pf - rows[0]['beta']):.2e}")
except ImportError:
    print("\n11. pyfixest not installed - cross-check skipped")