
"""Page 1: the puzzle."""
import plotly.graph_objects as go
import streamlit as st

from theme import BLUE, GREY, RED, quarter_to_date, style


def render(data):
    d = data["puzzle"]
    mfg = d["series"]["manufacturing"]
    non = d["series"]["non_manufacturing"]

    st.title("Generous capital allowances, and a sector that shrank anyway")

    st.markdown("""
Between 2021 and 2025 the UK ran the most generous capital allowances in decades.
From April 2021 a company could deduct £1.30 from taxable profit for every £1 it spent
on plant and machinery. From April 2023 it could deduct the full cost immediately, and
from November 2023 that became permanent.

Among businesses that claim capital allowances, HMRC found 74% of manufacturers
had invested in machinery and tools against an average of 38%, so on any standard
model of investment they stood to gain the most.

Here is what happened.
""")

    x = [quarter_to_date(q) for q in mfg["quarters"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=non["index"], name="Non-manufacturing",
                             line=dict(color=BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=x, y=mfg["index"], name="Manufacturing",
                             line=dict(color=RED, width=2.5)))
    fig.add_hline(y=100, line=dict(color=GREY, width=1, dash="dot"))
    fig.add_vline(x=quarter_to_date("2021Q2"), line=dict(color=GREY, width=1))
    fig.add_annotation(x=quarter_to_date("2021Q2"), y=133, text="  super-deduction begins",
                       showarrow=False, xanchor="left", font=dict(size=12, color=GREY))
    fig.update_yaxes(title="Real business investment, 2021Q1 = 100")
    st.plotly_chart(style(fig), use_container_width=True)

    a, b = st.columns(2)
    a.metric("Manufacturing, 2021 to 2025", "-20.1%")
    b.metric("Non-manufacturing, 2021 to 2025", "+21.6%")

    st.markdown("""
The two lines separate almost exactly when the policy starts, and they separate the
wrong way. The sector that stood to gain the most is the one that fell.

The obvious reading is that the policy failed. That reading is too quick, because
almost everything else moved at the same time.

The Bank of England's Decision Maker Panel recorded firms' effective borrowing rate
rising from 4.8% in November 2022 to a peak of 7.1% in 2024, and successive Monetary
Policy Reports attributed weak business investment to the higher Bank Rate. That works
through the cost of capital, which is the same channel the allowances were operating
on, in the opposite direction.

Energy prices spiked in 2022 and hit some subsectors far harder than others. Textiles
and oil refining, the two most energy-exposed, fell by 38.9% and 38.2% over the period,
roughly twice the manufacturing average.

And UK manufacturing had been shrinking as a share of business investment for thirty
years, from 18.6% in 1997 to 10.3% in 2025, well before any of this began.

Any of those could produce the picture above on its own. So the chart raises the
question and cannot answer it.
""")

    st.markdown("### Finding something the policy did not touch")

    st.markdown("""
To isolate the allowances you need a comparison. Something that was exposed to the tax
change and something that was not, moving through the same economy at the same time,
so that everything else cancels out.

The allowances give you one. They applied to qualifying plant and machinery. Other
assets a business buys, such as buildings and intellectual property, were treated
differently and were not affected by these changes. Industries differ enormously in how
much of their capital is plant and machinery: it is 70% of the capital stock in food
and drink manufacturing and under 4% in education. A machinery-heavy industry was
heavily exposed to the change. A buildings-heavy industry was barely exposed at all.
Both faced the same borrowing costs and the same energy prices.

That is the lever, and it narrows the question considerably:

> Did industries that use more plant and machinery invest differently from industries
> that use less, once you account for everything hitting all industries at once?

Worth being clear about what that leaves out. It is not a test of whether the
allowances lifted UK investment overall. A policy change that affected every industry
in the same quarter is indistinguishable from anything else happening in that quarter,
so the aggregate effect is not recoverable from this data by this method. What is
recoverable is the difference between more exposed and less exposed industries, and
that is what the rest of this app estimates.

Three things are needed. A measure of how generous the policy was, quarter by quarter.
A measure of how exposed each industry was. And a comparison that holds everything else
constant.

The next two pages build the first two. The interesting problem turns up in the second
one, before any statistics appear.
""")