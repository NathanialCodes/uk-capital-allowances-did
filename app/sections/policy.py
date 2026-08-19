
"""Page 2: measuring the policy."""
import plotly.graph_objects as go
import streamlit as st

from theme import (GREY, REGIME_COLOURS, REGIME_LABELS, RED,
                   quarter_to_date, style)


def render(data):
    d = data["policy"]

    st.title("How generous was it, really?")

    st.markdown("""
The three allowance regimes look like three different policies, and they are usually
described that way, including in my own earlier report on this question. But a company
does not respond to the headline rate. It responds to how much tax it saves, in today's
money, for every pound it spends.

That is one number, and it can be calculated.

Under a writing-down allowance you deduct 18% of the remaining balance each year,
indefinitely. Those deductions form a geometric series which collapses to a simple
fraction, and multiplying by the corporation tax rate turns a deduction into cash.
Under a first-year allowance you deduct everything immediately, so there is nothing
to discount.
""")

    st.markdown("""
| Period | Allowance | Corporation tax | Tax saved per £1 spent |
|---|---|---|---|
| to March 2021 | 18% writing-down | 19% | **0.149** |
| April 2021 to March 2023 | 130% super-deduction | 19% | **0.247** |
| April 2023 onward | 100% full expensing | 25% | **0.250** |
""")

    x = [quarter_to_date(q) for q in d["quarters"]]
    fig = go.Figure()
    for regime in ["pre", "super_deduction", "full_expensing"]:
        idx = [i for i, r in enumerate(d["regime"]) if r == regime]
        if not idx:
            continue
        fig.add_vrect(x0=x[min(idx)], x1=x[max(idx)],
                      fillcolor=REGIME_COLOURS[regime], opacity=1, line_width=0,
                      layer="below", annotation_text=REGIME_LABELS[regime],
                      annotation_position="top left",
                      annotation_font=dict(size=11, color=GREY))
    fig.add_trace(go.Scatter(x=x, y=d["npv"], line=dict(color=RED, width=3,
                                                        shape="hv"), name="NPV"))
    fig.update_yaxes(title="Tax saved per £1 of qualifying spend", range=[0.10, 0.30])
    st.plotly_chart(style(fig, height=380, legend=False), use_container_width=True)

    a, b = st.columns(2)
    a.metric("April 2021 change", f"+{d['step_2021']:.4f}",
             help="Nearly 10p per £1 spent. A large change in the cost of investing.")
    b.metric("April 2023 change", f"+{d['step_2023']:.4f}",
             help="Three tenths of a penny per £1. Close to no change at all.")

    st.markdown("""
This is the first thing the arithmetic changes.

April 2021 is a genuine event. The cost of investing in machinery fell by nearly ten
pence in the pound.

April 2023 is not an event at all. It is a change of about a third of a penny. The
super-deduction had been designed as a bridge to the corporation tax rise, so cutting
the allowance from 130% to 100% while raising the tax rate from 19% to 25% leaves the
present value almost exactly where it was. The two changes offset, by construction.

My earlier report treated those two dates as comparable policy changes and looked for
different responses in each period. Once you work out the present value it is clear
that only one of the two can be identified at all. Everything that follows uses this
single continuous measure rather than three regime dummies, because two of the three
regimes are the same regime under a different name.
""")

    st.markdown("### Does the answer depend on the assumptions?")
    st.markdown("""
The calculation needs a discount rate, and there is no single correct choice. It also
needs a convention about whether the first year's allowance is claimed straight away
or a year later. Neither is obvious, so the honest thing is to show the whole plausible
range rather than defend one number.
""")

    r = st.select_slider("Discount rate", options=[0.03, 0.05, 0.07], value=0.05,
                         format_func=lambda v: f"{v:.0%}")
    discrete = st.toggle("Claim the first year's allowance immediately", value=False)
    row = next(s for s in d["sensitivity"]
               if abs(s["r"] - r) < 1e-9 and s["discrete"] == discrete)

    c1, c2 = st.columns(2)
    c1.metric("Pre-2021 value per £1", f"{row['pre']:.4f}")
    c2.metric("April 2021 step", f"+{row['step_2021']:.4f}")

    st.markdown("""
Notice what moves and what does not. The discount rate only affects the pre-2021
figure, because a first-year allowance has nothing left to discount. So the April 2021
step ranges from 0.079 to 0.110 across the six combinations, and the April 2023 step
stays near zero in all of them.

That range mostly changes the units the treatment is measured in, which rescales the
coefficient reported later without changing what it means. Re-estimating the main
specification under all six combinations moves the p-value between 0.680 and 0.703,
and the coefficient stays negative throughout.

Worth knowing before the result appears, because it closes off one objection in
advance. Whatever the estimate turns out to be, it is not an artefact of the discount
rate.
""")