import streamlit as st
import pandas as pd

from src.data_loader import load_data
from src.preprocessing import explode_peneliti
from src.internal_visual import show_internal_kpi, show_internal_visual


# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="Dashboard Analisis LPB (Internal)",
    layout="wide"
)

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1rem;   /* ubah ke 0rem kalau mau mentok */
    }

    section[data-testid="stSidebar"] {
        background-color: #54bf00;  /* hijau muda netral */
    }

    span[data-baseweb="tag"] {
        background-color: #f7a300 !important; /* kuning muda netral */
        color: #4A4A4A !important;
        border-radius: 6px !important;
        font-weight: 500;
    }

    span[data-baseweb="tag"] svg {
        color: #6B5E1E !important;
    }

    span[data-baseweb="tag"]:hover {
        background-color: #F1DB7A !important;
    }

    div[data-baseweb="select"] > div {
        background-color: white !important;
    }

    .sidebar-logo-wrapper {
    display: flex;
    justify-content: center;
    margin-top: -25px;   /* NAIKKAN POSISI */
    margin-bottom: 12px;
}

/* Lingkaran putih */
.sidebar-logo-circle {
    background-color: white;
    width: 130px;
    height: 130px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Logo image */
.sidebar-logo-circle img {
    width: 90px;
    height: auto;
    object-fit: contain;
}

    </style>
    """,
    unsafe_allow_html=True
)



st.title("📊 Dashboard Analisis Topik Judul Penelitian LPB 2020-2023, 2025")
st.markdown("<br><br>", unsafe_allow_html=True)


# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_all_data():
    df_raw = load_data("data/Data Clean.xlsx")
    df_peneliti = explode_peneliti(df_raw)
    return df_peneliti

df_peneliti = load_all_data()

if df_peneliti.empty:
    st.error("❌ Data hasil preprocessing kosong. Cek explode_peneliti.")
    st.stop()

df_all = df_peneliti.copy() 

# ==============================
# SIDEBAR FILTER (INTERNAL ONLY)
# ==============================
import base64

with open("Asset/Logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.sidebar.markdown(f"""
<div class="sidebar-logo-wrapper">
    <div class="sidebar-logo-circle">
        <img src="data:image/png;base64,{logo_base64}">
    </div>
</div>
""", unsafe_allow_html=True)

df_peneliti["kelas"] = (
    df_peneliti["kelas"]
    .dropna()
    .astype(int)
)

def safe_multiselect(label, options):
    selected = st.sidebar.multiselect(label, options, default=options)
    if not selected:
        st.warning(f"{label} minimal 1 dipilih")
        st.stop()
    return selected

provinsi = safe_multiselect(
    "Provinsi",
    sorted(df_peneliti["provinsi"].dropna().unique())
)

gender = safe_multiselect(
    "Jenis Kelamin",
    sorted(df_peneliti["jenis_kelamin"].dropna().unique())
)

bidang = safe_multiselect(
    "Bidang",
    sorted(df_peneliti["bidang"].dropna().unique())
)

tahun = safe_multiselect(
    "Tahun",
    sorted(df_peneliti["tahun"].dropna().unique())
)


kelas = safe_multiselect(
    "Kelas",
    sorted(df_peneliti["kelas"].dropna().unique())
)


# ==============================
# FILTER DATA
# ==============================
df_filtered = df_peneliti[
    (df_peneliti["provinsi"].isin(provinsi)) &
    (df_peneliti["jenis_kelamin"].isin(gender)) &
    (df_peneliti["bidang"].isin(bidang)) &
    (df_peneliti["tahun"].isin(tahun)) &
    (df_peneliti["kelas"].isin(kelas))
]

if df_filtered.empty:
    st.warning("⚠️ Data kosong setelah filter")
    st.stop()


# ==============================
# INTERNAL KPI & VISUAL
# ==============================
show_internal_kpi(df_filtered)
st.markdown("<br>", unsafe_allow_html=True)
show_internal_visual(
    df_filtered,
    df_all
)



st.markdown("---")
st.caption("© Dashboard Analisis LPB CYS")
