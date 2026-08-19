
"""Shared colours and Plotly defaults so every chart in the app looks the same."""

INK = "#1a1a1a"
MUTED = "#6b6b6b"
GRID = "#e8e6e1"
PAPER = "rgba(0,0,0,0)"

RED = "#8b1a1a"
BLUE = "#2c5f8a"
AMBER = "#b8860b"
GREY = "#9a9a9a"

REGIME_COLOURS = {
    "pre": "#f2f0ec",
    "super_deduction": "#e6ddd0",
    "full_expensing": "#dce4ea",
}
REGIME_LABELS = {
    "pre": "18% writing-down allowance",
    "super_deduction": "130% super-deduction",
    "full_expensing": "100% full expensing",
}


def style(fig, height=420, legend=True):
    """Apply the house style to a Plotly figure."""
    fig.update_layout(
        height=height,
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(family="Georgia, serif", size=14, color=INK),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, ticks="outside",
                     tickcolor=GRID, color=MUTED)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=MUTED)
    return fig


def quarter_to_date(q):
    """'2021Q2' -> '2021-04-01' so Plotly puts it on a real time axis."""
    year, quarter = q.split("Q")
    return f"{year}-{(int(quarter) - 1) * 3 + 1:02d}-01"