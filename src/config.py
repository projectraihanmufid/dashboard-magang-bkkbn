from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = ROOT / "data" / "ikps_jatim_2024.xlsx"
GEO = ROOT / "assets" / "geometri"
TITLE = (
    "Dashboard Pemantauan IKPS & Prioritas Intervensi Stunting Provinsi Jawa Timur 2024"
)
ALL = "Semua"
DIMS = ["Kesehatan", "Gizi", "Perumahan", "Pendidikan", "Perlindungan sosial"]
IND = {
    "ASI": "ASI eksklusif",
    "KB": "KB modern",
    "Air_Layak": "Air minum layak",
    "Bantuan_Pangan": "Bantuan pangan",
    "Persalinan": "Persalinan di faskes",
}
NAVY, TEAL, OCHRE, RED = "#23364D", "#267F7A", "#AB742F", "#AF5544"
LINE = "#D9DDD5"
COLORS = ["#195E5C", "#59958A", "#B6B4A0", "#CA9562", "#A64E40"]
SCALE = ["#F1E1C9", "#C3C9AF", "#8AB3A2", "#508E85", "#185D5C"]


def fmt(x, places=2):
    import pandas as pd

    return (
        "—" if pd.isna(x) else f"{x:,.{places}f}".translate(str.maketrans(",.", ".,"))
    )


def area(x):
    return str(x).title()


def indicator(x):
    return IND.get(x, str(x).replace("_", " "))


def bak(x):
    return str(x).partition("(")[2].rstrip(")") or str(x)
