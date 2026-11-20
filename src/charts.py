import plotly.graph_objects as go
import streamlit as st
from .config import (
    COLORS,
    LINE,
    NAVY,
    RED,
    TEAL,
    fmt,
    indicator,
)


def finish(fig, label, height=300):
    left_margin = 8
    if len(fig.data) and fig.data[0].y is not None:
        names = [v for v in fig.data[0].y if isinstance(v, str)]
        if names:
            left_margin = min(152, max(30, max(len(v) for v in names) * 7 + 9))
    fig.update_layout(
        height=height,
        margin=dict(l=left_margin, r=18, t=12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans 3, Arial, sans-serif", size=13, color=NAVY),
        separators=",.",
        showlegend=False,
        hoverlabel=dict(bgcolor=NAVY, font_color="white", align="left"),
        legend=dict(orientation="h", y=1.02, x=0, yanchor="bottom", font_size=12),
    )
    fig.update_xaxes(
        automargin=True, gridcolor=LINE, zerolinecolor=LINE, fixedrange=True
    )
    fig.update_yaxes(
        automargin=True, gridcolor=LINE, zerolinecolor=LINE, fixedrange=True
    )
    st.plotly_chart(
        fig,
        theme=None,
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
        alt=label,
    )


def bars(labels, values, axis, *, colors=TEAL, height=None, limit=None, precision=1):
    y = list(labels)
    x = list(values)
    fig = go.Figure(
        go.Bar(
            x=x,
            y=y,
            orientation="h",
            marker_color=colors,
            text=[fmt(v, precision) for v in x],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>"
            + axis
            + ": %{x:."
            + str(precision)
            + "f}<extra></extra>",
        )
    )
    fig.update_yaxes(
        type="category", categoryorder="array", categoryarray=y[::-1], showgrid=False
    )
    right = limit if limit is not None else max([abs(v) for v in x] + [1]) * 1.20
    fig.update_xaxes(title_text=axis, range=[min([0, *x]) * 1.18, right])
    fig.update_layout(bargap=0.44)
    finish(fig, axis, height or max(225, 65 + len(x) * 27))


def clusters(group, all_clusters):
    counts = group.Klaster.value_counts().reindex(all_clusters, fill_value=0)
    fig = go.Figure(
        go.Bar(
            x=[s.split(" ")[0] for s in counts.index],
            y=counts.tolist(),
            customdata=counts.index,
            marker_color=COLORS,
            text=counts.tolist(),
            textposition="outside",
            hovertemplate="%{customdata}<br>%{y} daerah<extra></extra>",
        )
    )
    fig.update_xaxes(title_text="Klaster AMPI", showgrid=False)
    fig.update_yaxes(
        title_text="Jumlah daerah",
        range=[0, max(counts.max() * 1.25, 1.6)],
        dtick=1 if counts.max() < 7 else None,
    )
    fig.update_layout(bargap=0.38)
    finish(fig, "Jumlah daerah dalam setiap klaster AMPI", 245)


def prior_frequency(gaps, ref):
    freq = (
        gaps.groupby("Indikator")
        .Flag_Top3.sum()
        .reindex(ref.Indikator, fill_value=0)
        .sort_values(ascending=False, kind="stable")
    )
    bars(
        [indicator(i) for i in freq.index],
        freq,
        "Jumlah daerah",
        precision=0,
        colors=[RED if v == freq.max() and v else "#78A69A" for v in freq],
    )
