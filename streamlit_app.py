import base64
from functools import partial
from pathlib import Path
from struct import error as StructError
from zipfile import BadZipFile
import shapefile
from pyproj.exceptions import CRSError
from shapely.errors import GEOSException
import streamlit as st

from src import map_view, overview, plans
from src.config import ROOT, TITLE
from src.data_loader import load
from src.filters import filters
from src.geo import read_map

st.set_page_config(
    page_title=TITLE,
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="auto",
)
st.html((ROOT / "assets" / "style.css").read_text(encoding="utf-8"))
try:
    data = load()
except (OSError, ValueError, TypeError, KeyError, BadZipFile) as exc:
    st.error(
        f"Workbook belum dapat digunakan. Periksa berkas, kolom, atau kunci relasinya. {exc}"
    )
    st.stop()
try:
    paths = read_map(data["Wilayah"])
    geo_error = ""
except (
    OSError,
    ValueError,
    KeyError,
    StructError,
    CRSError,
    GEOSException,
    shapefile.ShapefileException,
) as exc:
    paths = None
    geo_error = (
        f"Periksa SHP, SHX, DBF, PRJ WGS 84 dan CPG dalam assets/geometri. {exc}"
    )

LOGOS = [
    (("jatim",), "Provinsi Jawa Timur"),
    (("bkkbn",), "BKKBN"),
    (("upnvjt", "upnvj", "upn"), "UPN Veteran Jawa Timur"),
]
LOGO_EXT = {".png", ".svg", ".jpg", ".jpeg", ".webp"}


def find_logo(stems):
    folder = ROOT / "assets" / "logo"
    if not folder.exists():
        return None
    for p in sorted(folder.iterdir()):
        if p.stem.lower() in stems and p.suffix.lower() in LOGO_EXT:
            return p
    return None


@st.cache_resource
def encode_logo(path, mtime):
    p = Path(path)
    ext = p.suffix.lower().lstrip(".")
    mime = {"svg": "image/svg+xml", "jpg": "image/jpeg"}.get(ext, f"image/{ext}")
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def brand_html():
    imgs = ""
    for stems, alt in LOGOS:
        p = find_logo(stems)
        if p:
            uri = encode_logo(str(p), p.stat().st_mtime)
            imgs += f'<img src="{uri}" alt="Logo {alt}">'
    return (
        '<div class="brand-lock">'
        f'<div class="logo-row">{imgs}</div>'
        "<div><strong>IKPS Jatim</strong><small>Pemantauan wilayah</small></div>"
        "</div>"
    )


with st.sidebar:
    with st.container(key="brand"):
        st.html(brand_html())

routes = [
    ("Ringkasan eksekutif", "space_dashboard", "ringkasan", overview.render),
    ("Peta sebaran & profil daerah", "map", "peta", map_view.render),
    ("Peringkat, klaster & master plan", "leaderboard", "peringkat", plans.render),
]


def show(func):
    args = [data, scope]
    if func in (overview.render, map_view.render):
        args.append(paths)
    if func is map_view.render:
        args.append(geo_error)
    func(*args)


pages = [
    st.Page(
        partial(show, func),
        title=label,
        icon=f":material/{icon}:",
        url_path=url,
        default=i == 0,
    )
    for i, (label, icon, url, func) in enumerate(routes)
]
current = st.navigation(pages, position="hidden")
with st.sidebar:
    for page in pages:
        st.page_link(page, width="stretch")
    st.divider()
scope = filters(data["Indeks_Wilayah"])
current.run()
st.divider()
st.caption(
    "IKPS eksperimental Jawa Timur · Baseline 2024 · Rekonstruksi penelitian dengan sembilan indikator padanan lokal."
)
