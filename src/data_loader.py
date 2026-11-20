"""Membaca dan memeriksa tujuh tabel baseline yang dipakai aplikasi."""

import pandas as pd
import streamlit as st

from .config import DIMS, WORKBOOK

REGION = "ID_Wilayah"
CODE = "Kode_Indikator"

# Jumlah baris, kunci unik, dan kolom yang dibutuhkan tampilan atau validasi.
TABLES = {
    "Wilayah": (38, [REGION], "KabKota Tipe Bakorwil Tahun"),
    "Indeks_Wilayah": (
        38,
        [REGION],
        "KabKota Tipe Bakorwil Klaster Klaster_ID Skor_AMPI Rank_AMPI "
        "Penalti_AMPI Geser_Peringkat_AMPI Prioritas_Intervensi",
    ),
    "Referensi_Indikator": (9, [CODE], "Indikator Dimensi_IKPS Target"),
    "Capaian_Indikator": (
        342,
        [REGION, CODE],
        "KabKota Indikator Dimensi_IKPS Nilai_Mentah Nilai_Analisis Target "
        "Skor_Normalisasi Flag_Imputasi Flag_Estimasi",
    ),
    "Skor_Dimensi": (190, [REGION, "Dimensi_IKPS"], "KabKota Skor_Dimensi"),
    "Gap_Prioritas": (
        342,
        [REGION, CODE],
        "KabKota Indikator Rank_Prioritas Flag_Top3",
    ),
    "MasterPlan_Klaster": (
        5,
        ["Klaster"],
        "Jumlah_Daerah Fase_Intervensi Target_Skor_AMPI Indikator_Prioritas",
    ),
}


def validate(data):
    for name, (count, key, fields) in TABLES.items():
        table = data[name]
        missing = (set(key) | set(fields.split())) - set(table)
        if missing:
            raise ValueError(f"{name} kehilangan kolom {', '.join(sorted(missing))}.")
        if (
            len(table) != count
            or table[key].isna().any().any()
            or table.duplicated(key).any()
        ):
            raise ValueError(
                f"{name} memerlukan {count} baris dengan kunci unik {', '.join(key)}."
            )

    regions = data["Wilayah"].set_index(REGION)
    ref = data["Referensi_Indikator"].set_index(CODE)
    if (
        regions.Tipe.value_counts().to_dict() != {"Kabupaten": 29, "Kota": 9}
        or not regions.Tahun.eq(2024).all()
        or not regions.KabKota.is_unique
    ):
        raise ValueError("Identitas 38 wilayah pada baseline 2024 tidak cocok.")
    for name, table in data.items():
        if (
            REGION in table
            and not table[REGION].map(regions.KabKota).eq(table.KabKota).all()
        ):
            raise ValueError(f"Relasi wilayah pada {name} tidak cocok.")
        if (
            CODE in table
            and not table[CODE].map(ref.Indikator).eq(table.Indikator).all()
        ):
            raise ValueError(f"Relasi indikator pada {name} tidak cocok.")
        if "Dimensi_IKPS" in table and set(table.Dimensi_IKPS) != set(DIMS):
            raise ValueError(f"Lima dimensi IKPS pada {name} tidak cocok.")

    idx = data["Indeks_Wilayah"]
    for col in ("Tipe", "Bakorwil"):
        if not idx[REGION].map(regions[col]).eq(idx[col]).all():
            raise ValueError(f"{col} berbeda antara tabel indeks dan wilayah.")
    codes = idx.Klaster.str.extract(r"^K([1-5])\b", expand=False)
    if (
        set(idx.Klaster_ID) != set(range(1, 6))
        or not codes.eq(idx.Klaster_ID.astype(str)).all()
    ):
        raise ValueError("ID dan label klaster K1–K5 tidak cocok.")
    if (
        not idx.Skor_AMPI.between(0, 100).all()
        or not idx.Rank_AMPI.between(1, 38).all()
    ):
        raise ValueError("Skor atau peringkat AMPI di luar rentang baseline.")
    plan = data["MasterPlan_Klaster"]
    if not plan.Klaster.map(idx.Klaster.value_counts()).eq(plan.Jumlah_Daerah).all():
        raise ValueError("Jumlah anggota klaster berbeda dari master plan.")

    obs = data["Capaian_Indikator"]
    for col in ("Dimensi_IKPS", "Target"):
        if not obs[CODE].map(ref[col]).eq(obs[col]).all():
            raise ValueError(f"{col} berbeda antara capaian dan referensi indikator.")
    if not obs.Nilai_Mentah.isna().eq(obs.Flag_Imputasi).all():
        raise ValueError("Penanda imputasi tidak sesuai dengan nilai mentah kosong.")
    gaps = data["Gap_Prioritas"]
    if (
        not gaps.Flag_Top3.eq(gaps.Rank_Prioritas.between(1, 3)).all()
        or not gaps.groupby(REGION).Flag_Top3.sum().eq(3).all()
    ):
        raise ValueError("Tiga prioritas per wilayah tidak konsisten.")


@st.cache_data(show_spinner="Membaca workbook IKPS…", max_entries=2)
def read(path, stamp, size):
    # Waktu modifikasi dan ukuran menjadi bagian dari kunci cache Streamlit.
    data = pd.read_excel(path, sheet_name=list(TABLES), engine="openpyxl")
    validate(data)
    return data


def load():
    stat = WORKBOOK.stat()
    return read(WORKBOOK, stat.st_mtime_ns, stat.st_size)
