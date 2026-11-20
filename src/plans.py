import plotly.graph_objects as go
import streamlit as st

from . import charts
from .components import context, h, section, title
from .config import COLORS, DIMS, SCALE, fmt, indicator
from .ranks import ranking


def cluster_profile(data, scope):
    members = scope.group[["ID_Wilayah", "Klaster"]]
    dim = scope.rows(data["Skor_Dimensi"]).merge(
        members, on="ID_Wilayah", validate="many_to_one"
    )
    scores = dim.pivot_table(
        index="Klaster", columns="Dimensi_IKPS", values="Skor_Dimensi"
    ).reindex(columns=DIMS)
    scores.insert(0, "AMPI", scope.group.groupby("Klaster").Skor_AMPI.median())
    short = [v.split(" ")[0] for v in scores.index]
    fig = go.Figure(
        go.Heatmap(
            x=scores.columns.tolist(),
            y=short,
            z=scores.to_numpy().tolist(),
            text=[[fmt(n, 1) for n in row] for row in scores.to_numpy()],
            texttemplate="%{text}",
            textfont_size=12,
            zmin=0,
            zmax=100,
            colorscale=SCALE,
            xgap=2,
            ygap=2,
            colorbar=dict(
                title="Poin",
                orientation="h",
                len=0.7,
                thickness=8,
                y=-0.04,
                yanchor="top",
                nticks=4,
            ),
            hovertemplate="%{y} · %{x}<br>%{z:.2f} poin<extra></extra>",
        )
    )
    fig.update_xaxes(
        side="top",
        tickangle=-58,
        tickmode="array",
        tickvals=scores.columns.tolist(),
        ticktext=[
            c.replace("Perlindungan sosial", "Perlindungan<br>sosial")
            for c in scores.columns
        ],
    )
    fig.update_yaxes(autorange="reversed", type="category")
    charts.finish(fig, "Median AMPI dan rerata lima dimensi per klaster", 320)


def roadmap(data, scope):
    phases = data["MasterPlan_Klaster"].sort_values("Klaster")
    visible = set(scope.group.Klaster)
    parts = ['<div class="phase-list roadmap">']
    for phase, frame in phases.groupby("Fase_Intervensi", sort=True):
        name, _, period = phase.partition(" (")
        parts.append(
            f'<article><b>{h(name)}</b><strong>{h(period.rstrip(")"))}</strong>'
        )
        current = frame[frame.Klaster.isin(visible)]
        if current.empty:
            parts.append('<span class="phase-empty">0 daerah dalam filter</span>')
        for r in current.itertuples():
            code = r.Klaster.split(" ")[0]
            color = COLORS[int(code[1:]) - 1]
            priorities = " · ".join(
                indicator(i.strip()) for i in r.Indikator_Prioritas.split(",")
            )
            parts.append(
                f'<div class="phase-cluster"><div><i style="background:{color}"></i>'
                f"<b>{h(code)}</b><span>Target AMPI {fmt(r.Target_Skor_AMPI)}</span></div>"
                f"<p>{h(priorities)}</p></div>"
            )
        parts.append("</article>")
    st.html("".join(parts) + "</div>")


def render(d, s):
    title(
        "Peringkat, klaster & master plan",
        "Skor AMPI, profil kelompok dan fase intervensi.",
    )
    context(s)
    if s.group.empty:
        return
    ranking(s)
    a, b = st.columns([0.85, 1.15], gap="large")
    with a:
        section("Distribusi klaster", "Jumlah daerah dalam filter")
        charts.clusters(s.group, sorted(s.all.Klaster.unique()))
    with b:
        section("Profil klaster", "Median AMPI · rerata lima dimensi")
        cluster_profile(d, s)
    section(
        "Master plan intervensi",
        "Target skor dan indikator prioritas klaster · baseline 2024",
    )
    roadmap(d, s)
