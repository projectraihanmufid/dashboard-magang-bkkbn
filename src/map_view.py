from bisect import bisect_right

import streamlit as st

from .components import context, map_table, ribbon, section, title
from .config import DIMS, ROOT, SCALE, area, fmt, indicator
from .filters import select_filter
from .profiles import indicator_profile

assets = ROOT / "assets"
map_widget = st.components.v2.component(
    "ikps_atlas",
    html=(assets / "map.html").read_text(encoding="utf-8"),
    css=(assets / "map.css").read_text(encoding="utf-8"),
    js=(assets / "map.js").read_text(encoding="utf-8"),
)


def set_focus(names):
    ident = st.session_state.get("atlas", {}).get("picked")
    if ident in names:
        select_filter("fokus", names[ident])


def metric_values(data, scope):
    family = st.segmented_control(
        "Metrik peta",
        ["AMPI", "Dimensi", "Indikator"],
        default="AMPI",
        required=True,
        key="jenis_peta",
    )
    if family == "Dimensi":
        metric = st.selectbox("Dimensi IKPS", DIMS, key="peta_dimensi")
        scores = data["Skor_Dimensi"]
        return (
            metric,
            scores.loc[scores.Dimensi_IKPS.eq(metric)]
            .set_index("ID_Wilayah")
            .Skor_Dimensi,
        )
    if family == "Indikator":
        ref = data["Referensi_Indikator"]
        metric = st.selectbox(
            "Indikator",
            ref.Indikator.tolist(),
            format_func=indicator,
            key="peta_indikator",
        )
        scores = data["Capaian_Indikator"]
        return (
            indicator(metric),
            scores.loc[scores.Indikator.eq(metric)]
            .set_index("ID_Wilayah")
            .Skor_Normalisasi,
        )
    return "Skor AMPI", scope.all.set_index("ID_Wilayah").Skor_AMPI


def atlas(scope, paths, name, values):
    ids = set(scope.group.ID_Wilayah)
    focus = scope.focus.ID_Wilayah if scope.focus is not None else None
    legend = list(zip(["0–<65", "65–<75", "75–<85", "85–<95", "95–100"], SCALE))
    if len(ids) < len(scope.all):
        legend.append(("Di luar kelompok", "#D3D9D2"))
    rows = []
    for r in scope.all.itertuples():
        value = values.at[r.ID_Wilayah]
        active = r.ID_Wilayah in ids
        color = SCALE[bisect_right([65, 75, 85, 95], value)]
        priorities = ", ".join(
            indicator(i.strip()) for i in r.Prioritas_Intervensi.split(",")
        )
        rows.append(
            dict(
                id=r.ID_Wilayah,
                path=paths[r.ID_Wilayah],
                name=area(r.KabKota),
                metric=f"{name}: {fmt(value)} poin",
                detail=(
                    r.Klaster
                    if name == "Skor AMPI"
                    else f"AMPI {fmt(r.Skor_AMPI)} poin · {r.Klaster}"
                ),
                priority="Prioritas: " + priorities,
                active=active,
                focus=r.ID_Wilayah == focus,
                color=color if active else "#D3D9D2",
            )
        )
    names = scope.all.set_index("ID_Wilayah").KabKota.to_dict()
    map_widget(
        key="atlas",
        data={
            "rows": sorted(rows, key=lambda r: r["focus"]),
            "legend": legend,
            "title": f"{name} (poin)",
        },
        on_picked_change=lambda: set_focus(names),
    )


def render(d, s, paths, geo_error):
    title(
        "Peta sebaran & profil daerah", "Skor wilayah dan capaian sembilan indikator."
    )
    context(s, profile_visible=True)
    left, right = st.columns([1.12, 1], gap="large")
    with left:
        name, values = metric_values(d, s)
        if paths:
            atlas(s, paths, name, values)
        else:
            st.warning("Peta belum dapat ditampilkan. " + geo_error)
            fallback = s.group[["KabKota", "ID_Wilayah"]].copy()
            fallback["Nilai"] = fallback.ID_Wilayah.map(values)
            map_table(fallback.sort_values("Nilai", ascending=False), name)
    with right:
        if s.focus is not None:
            r = s.focus
            section(area(r.KabKota))
            with st.container(key="profil_angka"):
                ribbon(
                    [
                        ("AMPI", fmt(r.Skor_AMPI), "poin"),
                        ("Peringkat", str(r.Rank_AMPI), "dari 38 daerah"),
                        (
                            "Klaster",
                            f"K{r.Klaster_ID}",
                            r.Klaster.split("(", 1)[-1].rstrip(")"),
                        ),
                    ]
                )
        indicator_profile(d, s)
