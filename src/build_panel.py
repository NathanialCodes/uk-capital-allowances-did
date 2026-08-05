"""Assemble the estimation panel. See PREREGISTRATION.md s3, s4, s7."""
import numpy as np
import pandas as pd

INVESTMENT_FILE = "data/raw/businessinvestmentbyindustryandasset_2026-06-30.xlsx"
SAMPLE_START, SAMPLE_END = "2015Q1", "2026Q1"
COVID_DROP = ["2020Q2", "2020Q3", "2020Q4"]

def load_investment():
    df = pd.read_excel(INVESTMENT_FILE, sheet_name="Table_4_CVM_SA", skiprows=3)
    df = df.rename(columns={df.columns[0]: "quarter"})
    df = df[df["quarter"].astype(str).str.match(r"^\d{4}Q[1-4]$")]
    long = df.melt(id_vars="quarter", var_name="industry", value_name="investment")
    long["quarter"] = pd.PeriodIndex(long["quarter"], freq="Q")
    long["investment"] = pd.to_numeric(long["investment"], errors="coerce")
    return long

exposure = pd.read_csv("data/processed/exposure.csv")
treatment = pd.read_csv("data/processed/treatment.csv")
treatment["quarter"] = pd.PeriodIndex(treatment["quarter"], freq="Q")

panel = load_investment()
panel = panel[panel["industry"].isin(exposure["industry"])]


# --- sample selection, prereg s3
keep = (panel["quarter"] >= pd.Period(SAMPLE_START, "Q")) & (panel["quarter"] <= pd.Period(SAMPLE_END, "Q"))
panel = panel[keep & ~panel["quarter"].isin([pd.Period(q, "Q") for q in COVID_DROP])]

panel = panel.merge(exposure, on="industry", how="left", validate="many_to_one")
panel = panel.merge(treatment, on="quarter", how="left", validate="many_to_one")

# --- derived columns, prereg s4 and s7
panel["log_investment"] = np.log(panel["investment"])
panel["treat"] = panel["npv"] * panel["pm_share_net"]


assert panel.notna().all().all(), "panel contains missing values"
n_i, n_t = panel["industry"].nunique(), panel["quarter"].nunique()
assert len(panel) == n_i * n_t, f"unbalanced: {len(panel)} != {n_i}x{n_t}"

panel = panel.sort_values(["industry", "quarter"]).reset_index(drop=True)
panel.to_csv("data/processed/panel.csv", index=False)

print(f"panel: {len(panel)} rows = {n_i} industries x {n_t} quarters")
print(f"\ninvestment  min {panel['investment'].min():,.0f}  max {panel['investment'].max():,.0f}")
print(f"treat       min {panel['treat'].min():.4f}  max {panel['treat'].max():.4f}")
print("\n", panel.head(3).to_string(), sep="")

