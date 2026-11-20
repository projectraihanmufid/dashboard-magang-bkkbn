# Dashboard Pemantauan IKPS & Prioritas Intervensi Stunting Provinsi Jawa Timur 2024

Aplikasi penelitian untuk membandingkan capaian penanganan stunting pada 29 kabupaten dan 9 kota di Jawa Timur. Indeks eksperimental ini menggunakan sembilan indikator padanan lokal dalam lima dimensi. IKPS resmi diterbitkan oleh BPS.

| Halaman | Yang dapat ditelaah |
| --- | --- |
| Ringkasan eksekutif | Median AMPI, rerata penalti, perubahan peringkat, jumlah daerah di K5, capaian lima dimensi, kedua ujung peringkat, dan frekuensi prioritas. |
| Peta sebaran & profil daerah | Sebaran skor AMPI, lima dimensi, atau sembilan indikator. Pilih daerah di peta untuk membandingkan capaian indikator (%) dengan targetnya. |
| Peringkat, klaster & master plan | Peringkat AMPI, anggota dan profil lima klaster, target skor, serta indikator prioritas pada tiga fase intervensi. |

Filter tipe wilayah, Bakorwil, dan klaster menentukan kelompok pembanding. Fokus kabupaten/kota menyorot satu daerah. Median 38 wilayah tetap tersedia saat fokus dipilih.

## Menjalankan aplikasi

Gunakan Python **3.12**. Buka terminal di folder yang memuat `streamlit_app.py`. Buat dan aktifkan lingkungan sesuai sistem operasi.

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux atau macOS**

```sh
python3.12 -m venv .venv
. .venv/bin/activate
```

Kemudian pasang dependensi dan jalankan server dari folder yang sama.

```sh
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Buka alamat lokal yang ditampilkan di terminal. Aplikasi memakai Streamlit dan Plotly untuk antarmuka, Pandas dan OpenPyXL untuk Excel, serta PyShp, Shapely, dan pyproj untuk peta. Data dan geometri dibaca dari repositori. Peta dapat digunakan tanpa layanan peta eksternal atau kunci API.

Untuk Streamlit Community Cloud setelah persetujuan publikasi, pilih repositori dan cabang rilis, isi **Main file path** dengan `streamlit_app.py`, lalu pilih **Python 3.12** di *Advanced settings*. Tema ada di `.streamlit/config.toml`. [Panduan deployment Streamlit](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

## Data dan interpretasi

| Berkas | Isi dan kegunaan |
| --- | --- |
| `data/ikps_jatim_2024.xlsx` | Ekstrak tujuh tabel dari workbook penelitian 2024. Mencakup wilayah, referensi dan capaian indikator, skor dimensi, indeks wilayah, prioritas gap, serta master plan klaster. |
| `assets/geometri/jatim.*` | Batas 38 kabupaten/kota dari lampiran proyek. Kelima komponen SHP, SHX, DBF, PRJ, dan CPG dipasangkan. Geometri dicocokkan ke workbook melalui tipe dan nama wilayah. |

Skor utama memakai normalisasi terhadap target pada skala 0–100. Rerata lima dimensi berbobot setara menjadi skor aritmetik. AMPI menguranginya dengan penalti sebesar varians populasi antardimensi dibagi rerata tersebut. PCA digunakan untuk bobot prioritas gap. Aplikasi membaca hasil analisis yang tersimpan dan hanya menghitung ringkasan kelompok untuk tampilan. Winsorization digunakan pada analisis sensitivitas penelitian.

Data indikator berasal dari `Data_Kesehatan_Jatim_2024.xlsx`. Capaian Persalinan merupakan estimasi. Satu nilai mentah Persalinan Kabupaten Pasuruan kosong dan nilai analisisnya memakai median 78%. Observasi Imunisasi yang diestimasi belum teridentifikasi. Median wilayah memakai bobot setara per daerah. Pengelompokan Bakorwil mengikuti notebook dan masih memerlukan verifikasi resmi. Roadmap merupakan usulan penelaahan intervensi.

Cakupan indikator menggunakan definisi lokal dan belum mencakup MP-ASI maupun dimensi pangan resmi. Analisis hanya mencakup tahun 2024. **Status publikasi** masih menunggu konfirmasi hak redistribusi data penelitian dan batas wilayah, termasuk ketentuan atribusinya. Metadata asal belum mencantumkan lisensi yang dapat digunakan sebagai dasar publikasi.
