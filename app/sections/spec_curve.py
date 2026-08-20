
"""Page 5: the specification curve, and what preregistration is for."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from theme import AMBER, BLUE, GREY, INK, style


def render(data):
    sc = data["spec_curve"]
    df = pd.DataFrame(sc["specs"])

    st.title("Try to find an effect")

    st.markdown(f"""
Everything so far followed one specification, fixed in a document committed to GitHub
before any estimation code existed. This page shows why that mattered.

Nothing about that specification was forced. I chose a sample window, a way of measuring
exposure, an outcome variable and a form for the treatment. Each choice had a defensible
alternative. Combining them gives {sc['n_specs']} specifications, all of which a
reasonable person could have run.

Below you can run any of them. Change the settings and watch the result move.
""")

    c1, c2 = st.columns(2)
    sample = c1.selectbox("Sample window", sorted(df["sample"].unique()), index=1)
    exposure = c2.selectbox("Exposure measure", sorted(df["exposure"].unique()), index=2)
    c3, c4 = st.columns(2)
    outcome = c3.selectbox("Outcome variable", ["log level", "growth"])
    treat = c4.selectbox("Treatment form", sorted(df["treat"].unique()), index=1)

    row = df[(df["sample"] == sample) & (df["exposure"] == exposure)
             & (df["outcome"] == outcome) & (df["treat"] == treat)].iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Coefficient", f"{row['beta']:,.3f}")
    m2.metric("Standard error", f"{row['se']:,.3f}")
    m3.metric("p-value", f"{row['p']:.4f}",
              "significant at 5%" if row["p"] < 0.05 else "not significant",
              delta_color="off")

    if row["preregistered"]:
        st.info("This is the preregistered specification. It is the one reported on page 4.")
    elif row["p"] < 0.05:
        st.warning("Significant, and not the preregistered specification. "
                   "Read on before believing it.")

    st.markdown("### All 48, at once")

    st.markdown("""
Each dot is one specification, sorted by the size of its coefficient. Filled dots are
significant at 5%. The circled dot is the one I committed to in advance.
""")

    plot = df.sort_values("beta").reset_index(drop=True)
    plot["x"] = plot.index
    fig = go.Figure()
    for is_growth, colour, label in [(True, AMBER, "Growth rate outcome"),
                                     (False, BLUE, "Log level outcome")]:
        sub = plot[(plot["outcome"] == "growth") == is_growth]
        sig, non = sub[sub["p"] < 0.05], sub[sub["p"] >= 0.05]
        fig.add_trace(go.Scatter(
            x=sig["x"], y=sig["beta"], mode="markers", name=label + ", significant",
            marker=dict(color=colour, size=9),
            customdata=sig[["sample", "exposure", "treat", "p"]],
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}, %{customdata[2]}"
                          "<br>beta %{y:,.2f}, p %{customdata[3]:.4f}<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=non["x"], y=non["beta"], mode="markers", name=label + ", not significant",
            marker=dict(color=colour, size=9, opacity=0.25),
            customdata=non[["sample", "exposure", "treat", "p"]],
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}, %{customdata[2]}"
                          "<br>beta %{y:,.2f}, p %{customdata[3]:.4f}<extra></extra>"))
    pre = plot[plot["preregistered"]]
    fig.add_trace(go.Scatter(
        x=pre["x"], y=pre["beta"], mode="markers", name="Preregistered",
        marker=dict(color="rgba(0,0,0,0)", size=20, line=dict(color=INK, width=2)),
        hovertemplate="preregistered specification<extra></extra>"))
    fig.add_hline(y=0, line=dict(color=GREY, width=1))
    fig.update_xaxes(title="Specifications, ordered by coefficient", showticklabels=False)
    fig.update_yaxes(title="Coefficient")
    st.plotly_chart(style(fig, height=460), use_container_width=True)

    st.markdown(f"""
{sc['n_sig_5pct']} of the {sc['n_specs']} specifications are significant at 5%. Every one
of them is negative, meaning more exposed industries did worse.

Someone who ran this grid and reported the best result could write that capital
allowances reduced investment in machinery-intensive industries, significant at
p below 0.001. It would survive changes of sample and changes of exposure measure. It
would look robust.
""")

    st.markdown("### The split is not random")

    a, b = st.columns(2)
    a.metric("Growth rate outcome", f"{sc['n_sig_growth']} of 24 significant")
    b.metric("Log level outcome", f"{sc['n_sig_level']} of 24 significant")

    st.markdown(f"""
Every significant result uses the growth rate as the outcome. Not one of the twenty-four
log level specifications reaches 5%, and the closest gets to
p = {sc['min_p_level']:.3f}. The split is total, and it does not depend on the sample or
the exposure measure at all. One choice is doing all the work.

That choice is not a technical detail. It changes the economic question.

Regressing the growth rate on the level of the treatment asks whether exposed industries
grew faster in every quarter the policy was switched on, meaning a permanently higher
growth rate for as long as the allowances existed. No theory of capital allowances
predicts that. The user cost model predicts a level shift: investment jumps to a higher
level, then growth returns to normal.

And there is a reason those coefficients come out negative. A temporary incentive brings
investment forward, so the period afterwards shows payback. Starting from a record 2021,
a measure of average growth across the treated window picks up the fall from that peak.
The growth specification is correctly computed, significant, and answering a question
nobody asked.

Which is the point. It is not obviously wrong from the outside. It fits the data better
than the specification I used. Anyone hunting for significance would have found it, and
could have justified it afterwards.
""")

    st.markdown("### What stopped it")

    st.markdown("""
Only the order of events.

The outcome variable was fixed as the log of real investment in a document committed on
2 August, before any regression had been run. The specification curve on this page was
built afterwards, and the amendment recording it as post hoc was pushed before these
results were published. The commit history is timestamped by GitHub and I cannot edit it.

That is the whole mechanism. Not honesty as a personality trait, which is unverifiable,
but a sequence of commits a stranger can check.

The result reported on page 4 is the circled dot: a coefficient indistinguishable from
zero, in a design whose identifying assumption fails. It is a worse headline than
p below 0.001. It is also the one I am able to defend.
""")

    with st.expander("See all 48 specifications"):
        show = df.sort_values("p")[["sample", "exposure", "outcome", "treat",
                                    "beta", "se", "p", "n", "preregistered"]]
        st.dataframe(show, use_container_width=True, hide_index=True)
        