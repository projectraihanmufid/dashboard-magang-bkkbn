import streamlit as st
from . import charts as ch
from .components import context, hero, section, ribbon
from .config import OCHRE, TEAL, area, fmt


def render(d, s, paths):
    hero(s, paths)
    context(s)
    if s.group.empty:
        return
    g = s.group
    ribbon(
        [
            ("Median AMPI", fmt(g.Skor_AMPI.median()), "poin · antarwilayah"),
            ("Rerata penalti", fmt(g.Penalti_AMPI.mean()), "poin · lima dimensi"),
            (
                "Peringkat berubah",
                str(g.Geser_Peringkat_AMPI.ne(0).sum()),
                f"dari {len(g)} daerah",
            ),
            ("Klaster terendah", str(g.Klaster_ID.eq(5).sum()), "daerah di K5"),
        ]
    )
    a, b = st.columns([1.12, 1], gap="large")
    dim = (
        s.rows(d["Skor_Dimensi"])
        .groupby("Dimensi_IKPS")
        .Skor_Dimensi.mean()
        .sort_values()
    )
    with a:
        section("Capaian lima dimensi", "Rerata kelompok · poin")
        ch.bars(
            dim.index,
            dim,
            "Skor dimensi (poin)",
            colors=[OCHRE] + [TEAL] * 4,
            limit=111,
            height=245,
        )
    with b:
        section("Sebaran klaster", "K1 tertinggi · K5 terendah")
        ch.clusters(g, sorted(s.all.Klaster.unique()))
    section(
        "Daerah di kedua ujung peringkat",
        "Skor AMPI kelompok pembanding",
    )
    c, e = st.columns(2, gap="large")
    for col, asc, label, color in [
        (c, False, "Skor tertinggi", TEAL),
        (e, True, "Skor terendah", OCHRE),
    ]:
        with col:
            st.markdown(f"**{label}**")
            rows = g.sort_values(["Skor_AMPI", "KabKota"], ascending=[asc, True]).head(
                5
            )
            ch.bars(
                rows.KabKota.map(area),
                rows.Skor_AMPI,
                "AMPI (poin)",
                colors=color,
                limit=111,
                height=230,
            )
    section(
        "Indikator yang sering menjadi prioritas",
        "Frekuensi dalam tiga prioritas daerah",
    )
    ch.prior_frequency(s.rows(d["Gap_Prioritas"]), d["Referensi_Indikator"])
