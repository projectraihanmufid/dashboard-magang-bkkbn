import plotly.graph_objects as go
import streamlit as st

from .charts import finish
from .components import section
from .config import RED, TEAL, area, fmt


def ranking(scope):
    section("Peringkat AMPI", "Peringkat baseline dari 38 daerah")
    view = st.segmented_control(
        "Cakupan peringkat",
        ["Top 10", "Bottom 10", "Semua"],
        default="Top 10",
        required=True,
        key="cakupan_peringkat",
        label_visibility="collapsed",
    )
    rows = scope.group.sort_values(
        ["Skor_AMPI", "Rank_AMPI", "KabKota"], ascending=[False, True, True]
    )
    if view == "Top 10":
        rows = rows.head(10)
    elif view == "Bottom 10":
        rows = rows.tail(10)
    focus_id = None if scope.focus is None else scope.focus.ID_Wilayah
    names = rows.KabKota.map(area).tolist()
    dense = len(rows) > 10
    bars = go.Bar(
        x=names,
        y=rows.Skor_AMPI.tolist(),
        orientation="v",
        marker_color=[RED if i == focus_id else TEAL for i in rows.ID_Wilayah],
        text=[fmt(v) for v in rows.Skor_AMPI],
        textposition="inside",
        insidetextanchor="middle",
        textangle=-90 if dense else None,
        textfont=dict(color="white", size=12),
        cliponaxis=False,
        customdata=rows[["Rank_AMPI", "Klaster"]].to_numpy().tolist(),
        hovertemplate="%{x}<br>AMPI %{y:.2f} poin<br>Peringkat %{customdata[0]} dari 38<br>%{customdata[1]}<extra></extra>",
    )
    fig = go.Figure(bars)
    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=names,
        tickmode="array",
        tickvals=names,
        ticktext=names,
        tickangle=-65,
        tickfont_size=12,
        showgrid=False,
    )
    fig.update_yaxes(title_text="AMPI (poin)", range=[0, 100], dtick=25)
    fig.update_layout(bargap=0.22, uniformtext_minsize=11, uniformtext_mode="show")
    # Scrolling stays inside this figure, so long names remain readable on narrow screens.
    minimum = 58 + 27 * len(rows)
    st.html(f"<style>.st-key-ranking_canvas{{min-width:{minimum}px}}</style>")
    with st.container(key="ranking_scroll"):
        with st.container(key="ranking_canvas"):
            finish(
                fig,
                "Peringkat daerah menurut skor AMPI dari tertinggi ke terendah",
                338,
            )
