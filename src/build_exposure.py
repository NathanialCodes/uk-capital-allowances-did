"""Build P&M exposure by industry from ONS capital stocks. See PREREGISTRATION.md s6."""
import pandas as pd

STOCK_FILE = "data/raw/grossandnetcapitalstock_2025-11-27.xlsx"
YEARS = [2015, 2016, 2017, 2018, 2019]

QUALIFYING = ["Other machinery, equipment and weapons systems", "ICT equipment"]
OTHER = ["Other buildings and structures", "Transport equipment",
         "Research & development", "Computer software and databases"]
DENOMINATOR = QUALIFYING + OTHER


GROUPS = {
    "Solid fuels & oil refining":              ["C19"],
    "Chemicals and man made fibres":           ["C20", "C21"],
    "Metals and metal goods":                  ["C24", "C25"],
    "Engineering and vehicles":                ["C26", "C27", "C28", "C29", "C30"],
    "Food, drink and tobacco":                 ["C10T12"],
    "Textiles, clothing, leather and footwear":["C13T15"],
    "Other manufacturing":                     ["C16T18", "C22_23", "C31_32", "C33"],
    "Agriculture, forestry and fishing":       ["A"],
    "Mining and Quarrying":                    ["B"],
    "Electricity, gas and water":              ["D", "E"],
    "Construction":                            ["F"],
    "Distribution Services":                   ["G"],
    "Transportation and storage":              ["H"],
    "Hotels and restaurants":                  ["I"],
    "Information and communication":           ["J"],
    "Financial intermediation":                ["K"],
    "Real estate, renting and business":       ["L", "M", "N"],
    "Education":                               ["P"],
    "Health and social work":                  ["Q"],
    "Other services":                          ["O", "R", "S", "T"],
}
MANUFACTURING = list(GROUPS)[:7]

def load_stocks(measure):
    df = pd.read_excel(STOCK_FILE, sheet_name="Current prices", skiprows=4)
    df = df[df["Measure"] == measure].copy()
    for y in YEARS:
        df[y] = pd.to_numeric(df[y], errors="coerce")
    n_suppressed = int(df[YEARS].isna().sum().sum())
    df["avg"] = df[YEARS].mean(axis=1)
    piv = df.pivot_table(index="Industry code", columns="Asset", values="avg")
    return piv, n_suppressed

def exposure(piv):
    out = {}
    for name, codes in GROUPS.items():
        missing = [c for c in codes if c not in piv.index]
        assert not missing, f"{name}: codes not found: {missing}"
        rows = piv.loc[codes]
        out[name] = rows[QUALIFYING].sum().sum() / rows[DENOMINATOR].sum().sum()  
    return pd.Series(out)

net, n_supp_net = load_stocks("Net capital stocks")
gross, n_supp_gross = load_stocks("Gross capital stocks")

result = pd.DataFrame({
    "pm_share_net": exposure(net),
    "pm_share_gross": exposure(gross),
})
result.index.name = "industry"
result["is_manufacturing"] = result.index.isin(MANUFACTURING)
result = result.sort_values("pm_share_net", ascending=False)
result.to_csv("data/processed/exposure.csv")

print (f"suppressed cells: net {n_supp_net}, gross {n_supp_gross}")
print (result.round(3).to_string())

print("\nmfg mean %.3f | non-mfg mean %.3f" % (
    result.loc[result.is_manufacturing, "pm_share_net"].mean(),
    result.loc[~result.is_manufacturing, "pm_share_net"].mean()))
print("corr(net, gross) = %.4f" % result["pm_share_net"].corr(result["pm_share_gross"]))

