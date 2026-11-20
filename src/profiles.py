"""Capaian sembilan indikator dan target dalam persen."""

from math import ceil

import pandas as pd
import streamlit as st

from .components import h, section
from .config import DIMS, fmt, indicator


def indicator_profile(data, scope):
    obs = data["Capaian_Indikator"]
    if scope.focus is None:
        obs = scope.rows(obs)
        subtitle = f"Rerata kelompok · {len(scope.group)} daerah"
    else:
        obs = obs.loc[obs.ID_Wilayah.eq(scope.focus.ID_Wilayah)]
        subtitle = ""
    if obs.empty:
        return

    section("Capaian indikator terhadap target", subtitle)
    aggregate = obs.groupby("Kode_Indikator").agg(
        actual=("Nilai_Analisis", "mean"),
        raw=("Nilai_Mentah", "mean"),
        score=("Skor_Normalisasi", "mean"),
        imputed=("Flag_Imputasi", "sum"),
        estimated=("Flag_Estimasi", "max"),
    )
    items = data["Referensi_Indikator"].join(
        aggregate, on="Kode_Indikator", validate="one_to_one"
    )
    ceiling = max(100, ceil(items.actual.max() / 25) * 25)
    prefix = "Rerata " if scope.focus is None else ""
    parts = [
        '<div class="indicator-profile"><div class="indicator-head"><span>Indikator</span>'
        '<span class="rail-key">Skala 0–' + str(ceiling) + "%</span>"
        "<span>Capaian</span><span>Target</span></div>"
    ]
    for dimension in DIMS:
        parts.append(f'<div class="indicator-dimension">{h(dimension)}</div>')
        for r in items[items.Dimensi_IKPS.eq(dimension)].itertuples():
            label = indicator(r.Indikator)
            raw = "kosong" if pd.isna(r.raw) else fmt(r.raw) + "%"
            details = [
                f"{prefix}capaian mentah {raw}",
                f"{prefix}skor normalisasi {fmt(r.score)} poin",
            ]
            if r.imputed:
                details.append(f"Imputasi median pada {int(r.imputed)} observasi")
            if pd.isna(r.estimated):
                details.append("Observasi estimasi belum teridentifikasi")
            elif r.estimated == 1:
                details.append("Capaian menggunakan estimasi")
            tip = " · ".join(details)
            parts.append(
                f'<div class="indicator-row" tabindex="0" data-code="{h(r.Kode_Indikator)}" '
                f'aria-label="{h(label)}, capaian {fmt(r.actual)}%, target {fmt(r.Target,0)}%. {h(tip)}">'
                f'<span class="indicator-name">{h(label)}</span>'
                f'<span class="indicator-rail" aria-hidden="true"><i style="width:{100*r.actual/ceiling:.4f}%"></i>'
                f'<b style="left:{100*r.Target/ceiling:.4f}%"></b></span>'
                f'<strong>{fmt(r.actual)}%</strong><span class="target-number">{fmt(r.Target,0)}%</span>'
                f'<span class="indicator-tip" role="tooltip">{h(tip)}</span></div>'
            )
    st.html("".join(parts) + "</div>")
