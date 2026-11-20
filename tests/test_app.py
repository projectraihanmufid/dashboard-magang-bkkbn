from pathlib import Path
import pandas as pd
import geopandas as gpd


def test_required_files_exist():
    assert Path("streamlit_app.py").exists()
    assert Path("requirements.txt").exists()
    assert Path("data/ikps_jatim_2024.xlsx").exists()
    assert Path("assets/geometri/jatim.shp").exists()


def test_dataset_and_shapefile_readable():
    df = pd.read_excel("data/ikps_jatim_2024.xlsx")
    gdf = gpd.read_file("assets/geometri/jatim.shp")
    assert not df.empty, "Dataset ikps_jatim_2024.xlsx kosong"
    assert not gdf.empty, "Shapefile jatim.shp kosong"
