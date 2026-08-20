
"""Page 4: the estimate, and why it is not a causal one."""
import plotly.graph_objects as go
import streamlit as st

from theme import GREY, RED, quarter_to_date, style


def render(data):
    r = data["result"]
    es = data["event_study"]
    r1 = data["rule1"]

    st.title("The estimate, and why it does not mean what it looks like")

    st.markdown("""
The three pieces are now in place. A quarterly measure of how generous the allowances
were, an industry measure of exposure to them, and 840 industry-quarter observations
covering twenty industries from 2015 to 2026.

The regression multiplies the two measures together and asks whether investment moved
with that product, after absorbing everything permanently different about each industry
and everything that hit all industries in a given quarter.

Those two absorptions are worth pausing on, because they define what is left. Industry
fixed effects remove anything constant about an industry, including its exposure, which
never changes. Quarter fixed effects remove anything common to all industries in a
quarter, including the allowance regime, which was the same for everyone. So neither
ingredient survives on its own. Only their interaction does, and it answers one narrow
question: when generosity rose, did high exposure industries move differently from low
exposure ones, relative to their own norms and to that quarter's common shock.
""")

    a, b, c = st.columns(3)
    a.metric("Coefficient", f"{r['beta']:.3f}")
    b.metric("Standard error", f"{r['se']:.3f}")
    c.metric("p-value", f"{r['p']:.3f}")

    st.markdown(f"""
The coefficient is negative, and the standard error is two and a half times its size.
Converted into something interpretable, the April 2021 reform is associated with
investment about **{abs(r['effect_pct']):.1f}% lower** at manufacturing-average exposure
than at non-manufacturing-average exposure, with a confidence interval running from
{r['effect_ci_pct'][0]:.1f}% to +{r['effect_ci_pct'][1]:.1f}%.

That interval spans a moderate fall and a moderate rise. This is not a small effect
measured precisely. It is an effect the data cannot measure at all. A wild cluster
bootstrap, which I preregistered because twenty clusters is few enough for standard
errors to be unreliable, gives p = {r['bootstrap_p']} against the {r['p']:.3f} above.
It confirms the result rather than rescuing it.
""")

    st.markdown("### Testing the assumption the design depends on")

    st.markdown("""
A difference-in-differences estimate is causal only if the treated and control groups
would have followed parallel paths in the absence of the policy. That assumption
concerns the treated group's outcome after April 2021 under no treatment, which is
never observed for any unit, so the assumption itself cannot be tested directly.

What can be tested is an implication of it. If the two groups were already diverging
before the policy, the assumption that they would have stayed parallel afterwards is
much harder to sustain. The chart below estimates a separate coefficient for every
quarter rather than one for the whole period, with 2021Q1 set to zero as the reference.
Under the assumption, the pre-April-2021 coefficients should sit flat around zero.

Passing that test would not prove the assumption holds. Failing it is strong evidence
against.
""")

    pre = [(q, b_, l, h) for q, b_, l, h in
           zip(es["quarters"], es["beta"], es["lo"], es["hi"]) if q <= "2020Q1"]
    post = [(q, b_, l, h) for q, b_, l, h in
            zip(es["quarters"], es["beta"], es["lo"], es["hi"]) if q >= "2021Q1"]

    fig = go.Figure()
    for seg, show in [(pre, True), (post, False)]:
        xs = [quarter_to_date(q) for q, _, _, _ in seg]
        fig.add_trace(go.Scatter(x=xs + xs[::-1],
                                 y=[h for _, _, _, h in seg] + [l for _, _, l, _ in seg][::-1],
                                 fill="toself", fillcolor="rgba(139,26,26,0.15)",
                                 line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=xs, y=[b_ for _, b_, _, _ in seg],
                                 mode="lines+markers", line=dict(color=RED, width=2.5),
                                 marker=dict(size=4), name="Coefficient",
                                 showlegend=show,
                                 hovertemplate="%{x|%YQ%q}<br>%{y:.2f}<extra></extra>"))
    fig.add_hline(y=0, line=dict(color="black", width=0.8))
    fig.add_vrect(x0=quarter_to_date("2020Q2"), x1=quarter_to_date("2021Q1"),
                  fillcolor="grey", opacity=0.12, line_width=0,
                  annotation_text="2020 excluded", annotation_position="top left",
                  annotation_font=dict(size=11, color=GREY))
    fig.add_vline(x=quarter_to_date(es["treatment_start"]),
                  line=dict(color="black", width=1, dash="dash"))
    fig.update_yaxes(title="Coefficient on exposure x quarter")
    st.plotly_chart(style(fig, height=430), use_container_width=True)

    st.markdown(f"""
They do not sit flat. They drift steadily upward from 2018 to the reference point, and
a joint test of the five pre-treatment coefficients rejects the null of no pre-trend
with **p = {es['wald_p']:.3f}**.

My preregistration set p below 0.05 as the threshold at which the coefficient stops
being reportable as a causal estimate. This clears that threshold by 0.002, which is a
margin worth stating openly rather than reporting as though it were decisive. But the
rule was fixed in advance, and it applies as written.

The direction of the drift is the interesting part, and it is the opposite of what I
expected. High exposure industries were *gaining* ground on low exposure ones before
the policy started. That is the approach to 2021 being the highest year for
manufacturing investment in the ONS series since 1997.

Which explains where the negative coefficient comes from. The design takes the
pre-period slope as its counterfactual. That slope points upward, so the model expects
continued gains, and when investment falls after 2021 the whole gap is attributed to the
policy. What it is actually measuring is the combination of the energy shock, higher
borrowing costs, and a fall back from a record peak. A temporary incentive that pulls
investment forward is expected to produce exactly that pattern afterwards.

Worth noting that no individual quarter is significant. Every confidence interval on the
chart contains zero, before and after. Only the joint test rejects, because five
coefficients lean the same way rather than because any one is precise.

One caveat in the other direction. A pre-trend test has limited power, so passing one
would not have licensed much confidence either. And the test only looks at 2015 to 2020.
It cannot detect a violation that begins with treatment, which is precisely what the
2022 energy shock would be if it hit high exposure industries harder than low exposure
ones. The failed test is evidence against the design, but a passed test would not have
been strong evidence for it.
""")

    st.markdown("### The second test")

    st.markdown("""
Page 3 showed that exposure is close to a manufacturing indicator. The preregistered
test for that was to throw away the seven manufacturing industries and re-estimate on
the remaining thirteen, where exposure still varies by a factor of fourteen. If the
allowance channel is real and separable, it should still be there.
""")

    t1, t2 = st.columns(2)
    t1.metric("All 20 industries", f"{r1['full_beta']:.3f}", f"SE {r1['full_se']:.3f}",
              delta_color="off")
    t2.metric("13 non-manufacturing only", f"+{r1['nonmfg_beta']:.3f}",
              f"SE {r1['nonmfg_se']:.3f}", delta_color="off")

    st.markdown(f"""
The sign flips, from {r1['full_beta']:.3f} to +{r1['nonmfg_beta']:.3f}. Under the
preregistered rule, a sign flip is a failure.

The standard error also triples, to {r1['nonmfg_se']:.2f}. With thirteen clusters the
estimate is so imprecise that the sign is close to arbitrary, so the flip should not be
read as evidence of a positive effect either. Both facts point the same way: outside
manufacturing, this data cannot identify anything.

Two preregistered tests, both failed, for the same underlying reason. Exposure and
manufacturing status are nearly the same variable in UK industry data, so a comparison
built on exposure cannot be separated from everything else that was happening to
manufacturing.
""")
