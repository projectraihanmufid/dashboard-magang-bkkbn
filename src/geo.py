"""Geometri kartografis lokal. Tidak menyimpan skor atau label klaster."""

import re
from pathlib import Path

import shapefile
from pyproj import CRS
from shapely.geometry import shape
import streamlit as st

from .config import GEO


def key(kind, name):
    return kind.upper(), re.sub(
        r"^(KABUPATEN|KAB\.?|KOTA)\s+", "", name.strip().upper()
    )


def svg_path(geometry):
    # Local equirectangular display centered around latitude 7° S, north up.
    polygons = [geometry] if geometry.geom_type == "Polygon" else geometry.geoms
    parts = []
    for poly in polygons:
        for ring in [poly.exterior, *poly.interiors]:
            xy = [
                f"{(lon-110.80)*99.25:.2f},{(-lat-4.95)*100:.2f}"
                for lon, lat in ring.coords
            ]
            parts.append("M" + " ".join(xy) + "Z")
    return "".join(parts)


@st.cache_data(max_entries=2, show_spinner=False)
def _read(folder, stamp, regions):
    folder = Path(folder)
    crs = CRS.from_wkt((folder / "jatim.prj").read_text().strip())
    if not crs.equals(CRS.from_epsg(4326), ignore_axis_order=True):
        raise ValueError("CRS geometri harus WGS 84 geografis.")
    lookup = {key(t, n): i for i, n, t in regions}
    boundaries = {}
    encoding = (folder / "jatim.cpg").read_text().strip()
    with shapefile.Reader(str(folder / "jatim.shp"), encoding=encoding) as reader:
        required_fields = {"NAME_1", "TYPE_2", "NAME_2"}
        if not required_fields.issubset({f[0] for f in reader.fields}):
            raise ValueError("Kolom NAME_1, TYPE_2 dan NAME_2 diperlukan pada DBF.")
        if reader.numShapes != 38 or len(reader) != 38:
            raise ValueError("Jumlah rekaman SHP/SHX/DBF harus 38.")
        for rec in reader.iterShapeRecords():
            attr = rec.record
            ident = lookup.get(key(attr.TYPE_2, attr.NAME_2))
            geometry = shape(rec.shape.__geo_interface__)
            if not ident or ident in boundaries or attr.NAME_1 != "Jawa Timur":
                raise ValueError(
                    f"Relasi batas wilayah tidak unik atau tidak cocok: {attr.NAME_2}."
                )
            if (
                geometry.geom_type not in {"Polygon", "MultiPolygon"}
                or geometry.is_empty
                or not geometry.is_valid
            ):
                raise ValueError(f"Poligon tidak valid: {attr.NAME_2}.")
            west, south, east, north = geometry.bounds
            if not (110 < west <= east < 117 and -10 < south <= north < -4):
                raise ValueError("Koordinat berada di luar cakupan Jawa Timur.")
            display = geometry.simplify(0.0008, preserve_topology=True)
            if display.is_empty or not display.is_valid:
                raise ValueError(f"Geometri tampilan tidak valid: {attr.NAME_2}.")
            boundaries[ident] = svg_path(display)
    if set(boundaries) != set(lookup.values()) or len(boundaries) != 38:
        raise ValueError("ID peta dan workbook tidak berpasangan 1:1.")
    return boundaries


def read_map(w, folder=GEO):
    files = [folder / ("jatim." + ext) for ext in ["shp", "shx", "dbf", "prj", "cpg"]]
    stamp = tuple((p.stat().st_mtime_ns, p.stat().st_size) for p in files)
    return _read(
        str(folder),
        stamp,
        tuple(w[["ID_Wilayah", "KabKota", "Tipe"]].itertuples(index=False, name=None)),
    )
