from base64 import b64encode
from html import escape
import pandas as pd
import streamlit as st
from .config import COLORS, area, fmt


def h(value):
    return escape(str(value), quote=True)


def title(name, intro):
    st.html(
        f'<header class="titleblock"><div class="overline">IKPS Jawa Timur · 2024</div><h1>{h(name)}</h1><p>{h(intro)}</p></header>'
    )


def hero(scope, paths):
    regions = []
    if paths:
        ids = set(scope.group.ID_Wilayah)
        for r in scope.all.itertuples():
            color = COLORS[r.Klaster_ID - 1] if r.ID_Wilayah in ids else "#5D6D70"
            regions.append(
                f'<path d="{paths[r.ID_Wilayah]}" fill="{color}" stroke="#cedcd4" stroke-width=".5" fill-rule="evenodd"/>'
            )
    scale = "".join(f'<i style="background:{c}"></i>' for c in COLORS)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 185 405 206">'
        + "".join(regions)
        + "</svg>"
    )
    image = b64encode(svg.encode()).decode()
    art = (
        f'<div class="hero-art"><img src="data:image/svg+xml;base64,{image}" alt="Klaster AMPI di daratan utama Jawa Timur dan Madura"><div class="hero-scale">Klaster K1 {scale} K5</div></div>'
        if regions
        else '<div class="hero-art"><span class="hero-tag">5 dimensi IKPS · 9 indikator</span></div>'
    )
    st.html(
        '<header class="hero"><div class="hero-copy"><div class="hero-tag">Ringkasan eksekutif &nbsp; / &nbsp; 2024</div>'
        "<h1>Capaian IKPS<br>Jawa Timur</h1><p>Pemantauan lima dimensi dan prioritas intervensi stunting di 38 kabupaten dan kota.</p></div>"
        + art
        + "</header>"
    )


def section(name, detail=""):
    st.html(
        f'<div class="sectionhead"><h2>{h(name)}</h2>'
        + (f"<p>{h(detail)}</p>" if detail else "")
        + "</div>"
    )


def ribbon(items):
    st.html(
        '<div class="scoreline">'
        + "".join(
            f"<div><span>{h(l)}</span><strong>{h(v)}</strong><small>{h(u)}</small></div>"
            for l, v, u in items
        )
        + "</div>"
    )


def context(s, profile_visible=False):
    st.html(
        f'<div class="scope-line"><span>Kelompok pembanding &nbsp;<b>{h(s.label)}</b></span><span>{len(s.group)} dari 38 daerah</span></div>'
    )
    if s.focus is not None:
        f = s.focus
        suffix = (
            " · di luar kelompok" if f.ID_Wilayah not in set(s.group.ID_Wilayah) else ""
        )
        focus_label = (
            f"<b>{h(area(f.KabKota))}{suffix}</b><span>AMPI {fmt(f.Skor_AMPI)}</span>"
        )
        if profile_visible:
            focus_label = "<b>Fokus di luar kelompok</b>" if suffix else ""
        st.html(
            f'<div class="scope-line">{focus_label}<span>Median kelompok {fmt(s.group.Skor_AMPI.median())}</span><span>Median 38 daerah {fmt(s.all.Skor_AMPI.median())}</span></div>'
        )
    if s.group.empty:
        st.info(
            "Tidak ada wilayah dalam kombinasi filter ini. Ubah salah satu filter untuk mengisi kelompok pembanding."
        )


def map_table(rows, metric):
    out = rows.loc[:, ["KabKota", "Nilai"]].copy()
    out["KabKota"] = out.KabKota.map(area)
    pattern = "%.0f" if pd.api.types.is_integer_dtype(out.Nilai) else "%.2f"
    st.dataframe(
        out,
        hide_index=True,
        width="stretch",
        height=240,
        column_config={
            "KabKota": st.column_config.TextColumn("Kabupaten/kota"),
            "Nilai": st.column_config.NumberColumn(f"{metric} (poin)", format=pattern),
        },
        alt="Tabel data penelitian",
    )
