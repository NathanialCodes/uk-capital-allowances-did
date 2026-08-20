
"""Page 3: measuring exposure, and the problem inside it."""
import plotly.graph_objects as go
import streamlit as st

from theme import BLUE, RED, style

MEASURES = {
    "Net capital stock": "pm_share_net",
    "Gross capital stock": "pm_share_gross",
    "Investment flows": "pm_share_flow",
}


def render(data):
    d = data["exposure"]
    rows = d["industries"]

    st.title("Which industries were actually exposed?")

    st.markdown("""
The allowances applied to plant and machinery. So the question is how much of each
industry's capital is plant and machinery, and that is answerable from ONS capital
stock data, which reports the stock of every asset type for every industry.

I take the share of machinery and ICT equipment in each industry's capital stock,
averaged over 2015 to 2019 so it reflects the industry's technology rather than
anything happening during the policy window.

One decision needs explaining, because it changes the answer. Transport equipment is
not in the numerator, even though it sounds like machinery. The legislation excludes
cars, second-hand assets and assets bought for leasing from these reliefs. Counting
transport equipment as qualifying would move transportation and storage from 19th to
9th out of 20 on exposure, treating an industry that was largely outside the policy as
one of the most exposed to it.
""")

    measure = st.radio("Exposure measure", list(MEASURES), horizontal=True)
    col = MEASURES[measure]

    ordered = sorted(rows, key=lambda r: r[col])
    fig = go.Figure()
    for is_mfg, name, colour in [(True, "Manufacturing", RED),
                                 (False, "Non-manufacturing", BLUE)]:
        sub = [r for r in ordered if r["is_manufacturing"] == is_mfg]
        fig.add_trace(go.Bar(
            y=[r["industry"] for r in sub], x=[r[col] for r in sub],
            orientation="h", name=name, marker_color=colour,
            hovertemplate="%{y}<br>%{x:.1%}<extra></extra>"))
    fig.update_xaxes(title="Share of capital stock in plant and machinery",
                     tickformat=".0%")
    fig.update_layout(barmode="stack")
    st.plotly_chart(style(fig, height=560), use_container_width=True)

    mlo, mhi = d["mfg_range"]
    nlo, nhi = d["nonmfg_range"]
    a, b = st.columns(2)
    a.metric("Manufacturing range", f"{mlo:.0%} to {mhi:.0%}")
    b.metric("Non-manufacturing range", f"{nlo:.0%} to {nhi:.0%}")

    st.markdown(f"""
The spread is real. Food and drink manufacturing holds {mhi:.0%} of its capital in
machinery, education holds {nlo:.1%}. That is a factor of twenty, and it is the
variation the whole study rests on.

But look at the colours rather than the lengths.
""")

    st.markdown("### The problem")

    st.markdown(f"""
The seven manufacturing industries occupy almost the entire top of the chart. Their
exposure runs from {mlo:.0%} to {mhi:.0%}. Non-manufacturing runs from {nlo:.1%} to
{nhi:.0%}, and only two non-manufacturing industries reach into the manufacturing
range at all: {" and ".join(d["overlap_industries"])}.

So exposure is not really an independent measure. It is close to a manufacturing
indicator with extra decimal places.

That matters because of what the comparison is supposed to do. The design compares
more exposed industries with less exposed ones and attributes the difference to the
allowances. If exposure and manufacturing status are nearly the same variable, then
the comparison is really manufacturing against everything else, and it will pick up
anything else that was happening to manufacturing at the time. Which, as page 1
showed, is quite a lot: the energy shock, higher borrowing costs, and a thirty year
decline in manufacturing's share of investment.

This is the central weakness of the design, and it is visible here, before any
regression has been run. I wrote a test for it into the preregistration in advance:
re-estimate on the thirteen non-manufacturing industries alone, where exposure still
varies from {nlo:.1%} to {nhi:.0%}, and see whether the result survives. Page 4 reports
what happened.
""")

    st.markdown("### Two things worth noticing about the measure itself")

    st.markdown(f"""
Switch the radio button above between net and gross capital stock and almost nothing
moves. The two correlate at {d['corr_net_gross']}, which is reassuring: the choice
between them is not doing any work.

Switch to investment flows and more changes, because that measure comes from a
different ONS release where ICT is suppressed for around half of industry-years,
including entirely for chemicals, textiles and metals. That is why the capital stock
measure is the one used in the main specification, and it is a decision recorded in
the preregistration rather than made after seeing results.

There is also a curiosity in the data. Net and gross capital stock produce the exact
same split of all twenty industries into above and below median. Two measures that
disagree enough to flip the sign of the final coefficient produce identical results
the moment you reduce them to a binary. Reducing a continuous measure to above or
below median throws away precisely the variation on which they disagree.
""")