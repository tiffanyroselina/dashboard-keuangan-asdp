# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Dashboard Kinerja ASDP", layout="wide")

# ---------- LOAD DATA ----------
def load_data(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        df_kinerja = pd.read_excel(xls, 'Kinerja_Keuangan')
        df_rasio = pd.read_excel(xls, 'Rasio_Keuangan')
        df_cashflow = pd.read_excel(xls, 'Cashflow_Forecast')
        df_debt = pd.read_excel(xls, 'Profil_Hutang')
        return df_kinerja, df_rasio, df_cashflow, df_debt
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None, None, None, None

# ---------- FILTER ----------
def apply_filter(df, tahun, bulan_list):
    return df[(df['Tahun'] == tahun) & (df['Bulan'].isin(bulan_list))]

# ---------- SCORING STRATEGI ----------
def generate_rekomendasi(kinerja, rasio, cashflow):
    skor = 0
    if kinerja['Pendapatan'].mean() > 100000: skor += 1
    if kinerja['Laba_Bersih'].mean() > 10000: skor += 1
    if rasio['DSCR'].mean() >= 1.2: skor += 1
    if rasio['Current_Ratio'].mean() >= 1.1: skor += 1
    if rasio['DER'].mean() <= 1.5: skor += 1
    if cashflow['Saldo_Akhir'].mean() > 0: skor += 1

    if skor >= 5:
        return "Strategi Ekspansi"
    elif skor >= 3:
        return "Strategi Efisiensi"
    else:
        return "Strategi Konservatif / Restrukturisasi"

# ---------- HIGHLIGHT CELL ----------
def highlight_rasio(val, threshold, reverse=False):
    if reverse:
        return 'background-color: red' if val > threshold else ''
    else:
        return 'background-color: red' if val < threshold else ''

# ---------- MAIN ----------
st.title("📊 Dashboard Kinerja Keuangan ASDP")

uploaded_file = st.sidebar.file_uploader("Upload file Excel", type=["xlsx"])
if uploaded_file:
    df_kinerja, df_rasio, df_cashflow, df_debt = load_data(uploaded_file)

    tahun_list = df_kinerja['Tahun'].unique()
    bulan_list = df_kinerja['Bulan'].unique()

    tahun = st.sidebar.selectbox("Pilih Tahun", sorted(tahun_list, reverse=True))
    bulan_multi = st.sidebar.multiselect("Pilih Bulan", bulan_list, default=bulan_list[:1])

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Ringkasan Kinerja", "Rasio Keuangan", "Cashflow Forecast",
        "Profil Hutang", "Strategi", "Export"
    ])

    with tab1:
        st.header("📈 Ringkasan Kinerja")
        df_filtered = apply_filter(df_kinerja, tahun, bulan_multi)
        st.dataframe(df_filtered)
        for col in ['Pendapatan','EBITDA','Fixed_Cost','Laba_Bersih','Debt']:
            fig = px.bar(df_filtered, x='Bulan', y=col, title=f"Perbandingan {col} per Bulan")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("📊 Rasio Keuangan")
        df_filtered = apply_filter(df_rasio, tahun, bulan_multi)

        styled_df = df_filtered.style\
            .applymap(lambda v: highlight_rasio(v, 1.2), subset=['DSCR'])\
            .applymap(lambda v: highlight_rasio(v, 1.1), subset=['Current_Ratio'])\
            .applymap(lambda v: highlight_rasio(v, 1.5, reverse=True), subset=['DER'])

        st.dataframe(styled_df)

        for col in ['DSCR', 'Current_Ratio', 'DER']:
            fig = px.bar(df_filtered, x='Bulan', y=col, title=f"Perbandingan {col} per Bulan",
                         color='Bulan', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("💰 Cashflow Forecast (2 Minggu)")
        st.dataframe(df_cashflow)
        fig = px.line(df_cashflow, x='Tanggal', y='Saldo_Akhir', title='Proyeksi Saldo Harian')
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("📄 Profil & Jatuh Tempo Hutang")
        st.dataframe(df_debt)
        df_debt['Jatuh_Tempo'] = pd.to_datetime(df_debt['Jatuh_Tempo'])
        df_gantt = df_debt.copy()
        df_gantt['Start'] = datetime.today()
        df_gantt['Finish'] = df_gantt['Jatuh_Tempo']
        fig = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Nama_Pinjaman", color="Institusi")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.header("📌 Rekomendasi Strategi Perusahaan")
        df_k = apply_filter(df_kinerja, tahun, bulan_multi)
        df_r = apply_filter(df_rasio, tahun, bulan_multi)
        rekomendasi = generate_rekomendasi(df_k, df_r, df_cashflow)
        st.success(f"Hasil Analisis: **{rekomendasi}**")

    with tab6:
        st.header("📄 Export Laporan")

        def convert_df_to_excel(dfs: dict):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for name, df in dfs.items():
                    df.to_excel(writer, index=False, sheet_name=name[:31])
            return output.getvalue()

        excel_data = convert_df_to_excel({
            "Kinerja_Keuangan": df_kinerja,
            "Rasio_Keuangan": df_rasio,
            "Cashflow_Forecast": df_cashflow,
            "Profil_Hutang": df_debt
        })

        st.download_button(
            label="📂 Download Laporan Excel",
            data=excel_data,
            file_name=f"Laporan_Kinerja_{'_'.join(bulan_multi)}_{tahun}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
