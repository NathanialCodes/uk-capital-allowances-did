
"""UK capital allowances explainer. Reads precomputed results, computes nothing."""
import json
import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).parent
sys.path.insert(0, str(APP_DIR))

from sections import policy, puzzle

st.set_page_config(page_title="UK Capital Allowances", page_icon="📊",
                   layout="centered", initial_sidebar_state="expanded")


@st.cache_data
def load():
    with open(APP_DIR / "data" / "results.json") as f:
        return json.load(f)


data = load()

PAGES = {
    "1. The puzzle": puzzle,
    "2. Measuring the policy": policy,
}

with st.sidebar:
    st.markdown("### UK capital allowances")
    st.caption("Did investment respond differently in industries that use more "
               "plant and machinery? A preregistered test, 2021 to 2025.")
    choice = st.radio("Contents", list(PAGES), label_visibility="collapsed")
    st.divider()
    st.caption(
        f"Panel: {data['meta']['panel']['industries']} industries, "
        f"{data['meta']['panel']['quarters']} quarters, "
        f"{data['meta']['panel']['n']} observations.  \n"
        f"ONS business investment, {data['meta']['vintages']['business_investment']} vintage."
    )
    st.caption("[Code and preregistration on GitHub]"
               "(https://github.com/NathanialCodes/uk-capital-allowances-did)")

PAGES[choice].render(data)