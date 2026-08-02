"""Build quarterly allowance NPV series. See PREREGISTRATION.md s5."""
import pandas as pd

START, END = "2015Q1", "2026Q1"
BASE_R = 0.05

REGIMES = [
    ("pre",             None,     "2021Q1", 0.19, "wda", 0.18),
    ("super_deduction", "2021Q2", "2023Q1", 0.19, "fya", 1.30),
    ("full_expensing",  "2023Q2", None,     0.25, "fya", 1.00),   
]

def npv_allowance(kind, rate, tax_rate, r, discrete=False):
    if kind == "fya":
        pv = rate
    elif kind == "wda":
        pv = rate * (1 + r) / (r + rate) if discrete else rate / (r + rate)
    else: 
        raise ValueError(f"unknown allowance kind {kind}")
    return tax_rate * pv


def build(r=BASE_R, discrete=False):
    quarters = pd.period_range(START, END, freq="Q")
    df = pd.DataFrame(index=quarters)
    df.index.name = "quarter"
    df["regime"] = pd.NA
    df["npv"] = float("nan")
    for name, lo, hi, tax_rate, kind, rate in REGIMES:
        lo = quarters[0] if lo is None else pd.Period(lo, freq="Q")
        hi = quarters[-1] if hi is None else pd.Period(hi, freq="Q")
        mask = (df.index >= lo) & (df.index <= hi)
        df.loc[mask, "regime"] = name
        df.loc[mask, "npv"] = npv_allowance(kind, rate, tax_rate, r, discrete)
    assert df["npv"].notna().all(), "some quarters have no regime"
    return df

df = build()
df["r"] = BASE_R
df["discrete"] = False
df.to_csv("data/processed/treatment.csv")

print(df.groupby("regime", sort=False)["npv"].agg(["first", "count"]).round(4).to_string())
print("\nApril 2021 step: %+.4f" % (df.loc[pd.Period("2021Q2","Q"),"npv"] - df.loc[pd.Period("2021Q1","Q"),"npv"]))
print("April 2023 step: %+.4f" % (df.loc[pd.Period("2023Q2","Q"),"npv"] - df.loc[pd.Period("2023Q1","Q"),"npv"]))

print("\nrobustness — NPV by discount rate and timing convention:")
for r in (0.03, 0.05, 0.07):
    for disc in (False, True):
        d = build(r, disc)
        step = d.loc[pd.Period("2021Q2","Q"),"npv"] - d.loc[pd.Period("2021Q1","Q"),"npv"]
        print(f"  r={r:.2f} discrete={str(disc):5s}  pre={d['npv'].iloc[0]:.4f}  Apr21 step={step:+.4f}")



