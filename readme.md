# 📊 Dashboard Kinerja Keuangan ASDP

Aplikasi dashboard interaktif berbasis [Streamlit](https://streamlit.io/) untuk menyajikan kinerja keuangan ASDP secara visual dan real-time kepada BOD.

## 🚀 Fitur Utama

- 📈 Ringkasan KPI: Pendapatan, EBITDA, Fixed Cost, Laba Bersih, Debt
- 📊 Rasio Keuangan: DSCR, DER, Current Ratio
- 💰 Cashflow Forecast: Proyeksi saldo kas 2 minggu ke depan
- 📄 Profil & Jatuh Tempo Hutang dengan Gantt Chart
- 📌 Rekomendasi strategi otomatis berdasarkan skor performa
- ⬆️ Upload file Excel (template disediakan)
- 📤 Export data ke Excel

## 🧱 Struktur Tab

1. **Ringkasan Kinerja**
2. **Rasio Keuangan**
3. **Cashflow Forecast**
4. **Profil Hutang**
5. **Strategi Perusahaan**
6. **Export Data**

## 📂 Cara Penggunaan

1. Clone atau upload project ini ke [Streamlit Cloud](https://streamlit.io/cloud)
2. Pastikan file `app.py` dan `requirements.txt` berada di root repository
3. Upload file Excel sesuai format `template.xlsx` saat menjalankan aplikasi

## 📥 Template Input Data

Gunakan file `template.xlsx` yang tersedia di repo ini. Format data terdiri dari 4 sheet:

- `Kinerja_Keuangan`
- `Rasio_Keuangan`
- `Cashflow_Forecast`
- `Profil_Hutang`

## 📦 Requirements

Install dependencies secara lokal:
```bash
pip install -r requirements.txt
