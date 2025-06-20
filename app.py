# app.py (UI versi dashboard layout seperti gambar dengan filter tanggal dan tooltip)

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Dashboard Kinerja ASDP", layout="wide")

# ---------- STYLE ----------
st.markdown("""
    <style>
        .card {
            background-color: #007bff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            color: white;
            text-align: center;
        }
        .section-label {
            background-color: #00bcd4;
            color: white;
            padding: 0.5rem 1rem;
            font-weight: bold;
            border-radius: 0.3rem;
            margin-bottom: 0.5rem;
            display: inline-block;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- FORMAT ----------
def format_number_custom(x):
    if pd.isna(x):
        return "-"
    if x >= 1_000_000:
        return f"{x/1_000_000:.1f} jt"
    elif x >= 1_000:
        return f"{x/1_000:.1f} rb"
    else:
        return f"{x:,.0f}"

# ---------- LOAD DATA ----------
def load_data(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        df_kinerja = pd.read_excel(xls, 'Kinerja_Keuangan')
        df_rasio = pd.read_excel(xls, 'Rasio_Keuangan')
        df_cashflow = pd.read_excel(xls, 'Cashflow_Forecast')
        df_cashflow['Tanggal'] = pd.to_datetime(df_cashflow['Tanggal'])
        df_debt = pd.read_excel(xls, 'Profil_Hutang')
        return df_kinerja, df_rasio, df_cashflow, df_debt
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None, None, None, None

# ---------- MAIN ----------
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/ASDP_Indonesia_Ferry_Logo.svg/2560px-ASDP_Indonesia_Ferry_Logo.svg.png", width=120)
st.markdown("<h2 style='margin-top: -1rem;'>DASHBOARD KINERJA</h2>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df_kinerja, df_rasio, df_cashflow, df_debt = load_data(uploaded_file)

    tahun_list = df_kinerja['Tahun'].unique()
    bulan_list = df_kinerja['Bulan'].unique()
    tahun = st.selectbox("Pilih Tahun", sorted(tahun_list, reverse=True))
    bulan_multi = st.multiselect("Pilih Bulan", bulan_list, default=bulan_list[:1])

    df_filtered = df_kinerja[(df_kinerja['Tahun'] == tahun) & (df_kinerja['Bulan'].isin(bulan_multi))]

    pendapatan = format_number_custom(df_filtered['Pendapatan'].sum())
    ebitda = format_number_custom(df_filtered['EBITDA'].sum())
    laba = format_number_custom(df_filtered['Laba_Bersih'].sum())
    cash = format_number_custom(df_cashflow['Saldo_Akhir'].iloc[-1])

    # KPI CARDS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class='card' title='Total pendapatan perusahaan dalam periode yang dipilih'>
            <h5>Pendapatan</h5>
            <h2>{pendapatan}</h2>
            <small>YTD vs RKAP<br>FY vs RKAP</small></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='card' title='Laba operasional sebelum depresiasi dan pajak'>
            <h5>EBITDA</h5>
            <h2>{ebitda}</h2>
            <small>YTD vs RKAP<br>FY vs RKAP</small></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='card' title='Laba bersih yang dihasilkan setelah biaya dan pajak'>
            <h5>Laba</h5>
            <h2>{laba}</h2>
            <small>YTD vs RKAP<br>FY vs RKAP</small></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class='card' title='Total kas dan setara kas saat ini'>
            <h5>Cash</h5>
            <h2>{cash}</h2>
            <small>YTD vs RKAP<br>FY vs RKAP</small></div>""", unsafe_allow_html=True)

    # LIKUIDITAS
    st.markdown("<div class='section-label'>Likuiditas</div>", unsafe_allow_html=True)
    tgl_min = df_cashflow['Tanggal'].min()
    tgl_max = df_cashflow['Tanggal'].max()
    start, end = st.date_input("Filter Rentang Tanggal", [tgl_min, tgl_max], format="YYYY-MM-DD")
    df_cash_filtered = df_cashflow[(df_cashflow['Tanggal'] >= pd.to_datetime(start)) & (df_cashflow['Tanggal'] <= pd.to_datetime(end))]
    fig_cash = px.line(df_cash_filtered, x='Tanggal', y='Saldo_Akhir', title="Kas dan Setara Kas")
    fig_cash.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_cash, use_container_width=True)

    # SOLVABILITAS
    st.markdown("<div class='section-label'>Solvabilitas</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    df_r = df_rasio[(df_rasio['Tahun'] == tahun) & (df_rasio['Bulan'].isin(bulan_multi))]
    with col1:
        st.metric("DSCR", f"{df_r['DSCR'].mean():.2f}", help="Kemampuan membayar utang dari operasional")
    with col2:
        st.metric("DER", f"{df_r['DER'].mean():.2f}", help="Rasio hutang terhadap ekuitas")
    with col3:
        st.metric("Current Ratio", f"{df_r['Current_Ratio'].mean():.2f}", help="Likuiditas jangka pendek")

    # PROFITABILITAS
    st.markdown("<div class='section-label'>Profitabilitas</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gross Profit Margin", "-", help="Margin kotor terhadap pendapatan")
    with col2:
        st.metric("EBITDA Margin", "-", help="EBITDA dibandingkan pendapatan")
    with col3:
        st.metric("Net Profit Margin", "-", help="Laba bersih dibandingkan pendapatan")
