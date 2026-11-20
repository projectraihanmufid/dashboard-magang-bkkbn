from pathlib import Path
import pandas as pd


def test_project_files_and_modules_exist():
    required_paths = [
        "streamlit_app.py",
        "requirements.txt",
        "data/ikps_jatim_2024.xlsx",
        "assets/geometri/jatim.shp",
        "assets/geometri/jatim.dbf",
        "assets/geometri/jatim.shx",
        "src/config.py",
        "src/data_loader.py",
        "src/geo.py",
        "src/filters.py",
        "src/charts.py",
        "src/map_view.py",
        "src/overview.py",
        "src/plans.py",
        "src/profiles.py",
        "src/ranks.py",
        "src/components.py",
    ]
    for file_path in required_paths:
        assert Path(file_path).exists(), f"File {file_path} tidak ditemukan"


def test_dataset_ikps_readable():
    df = pd.read_excel("data/ikps_jatim_2024.xlsx")
    assert not df.empty, "Dataset ikps_jatim_2024.xlsx kosong"
    assert len(df.columns) > 1, "Kolom dataset tidak valid"
