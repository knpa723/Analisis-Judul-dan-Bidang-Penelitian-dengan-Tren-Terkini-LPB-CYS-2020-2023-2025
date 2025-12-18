import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_data
from src.preprocessing import explode_peneliti
from src.keyword_extraction import extract_keywords
from src.external_visual import show_external_visual
from src.trend_analysis import get_trend


# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="Dashboard Analisis LPB",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Analisis Penelitian LPB")
st.markdown("Analisis Internal & Eksternal berbasis Judul Penelitian")


# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_all_data():
    df_raw = load_data("data/Data Clean.xlsx")
    df_peneliti = explode_peneliti(df_raw)
    return df_raw, df_peneliti

df_raw, df_peneliti = load_all_data()


# ==============================
# CACHE GOOGLE TRENDS
# ==============================
@st.cache_data(show_spinner=False)
def load_trend_cached(keyword, year):
    return get_trend(keyword, year)


# ==============================
# SIDEBAR FILTER
# ==============================
st.sidebar.header("⚙️ Filter Data")

mode = st.sidebar.radio(
    "Pilih Jenis Analisis",
    ["Internal", "Eksternal"]
)

def safe_multiselect(label, options):
    selected = st.sidebar.multiselect(label, options, default=options)
    if not selected:
        st.sidebar.warning(f"⚠️ {label} minimal 1 pilihan")
        st.stop()
    return selected


provinsi = safe_multiselect(
    "Asal LPB",
    sorted(df_peneliti["provinsi"].dropna().unique())
)

gender = safe_multiselect(
    "Jenis Kelamin",
    sorted(df_peneliti["jenis_kelamin"].dropna().unique())
)

bidang = safe_multiselect(
    "Bidang Penelitian",
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
# FILTER DATAFRAME
# ==============================
df_filtered = df_peneliti[
    (df_peneliti["provinsi"].isin(provinsi)) &
    (df_peneliti["jenis_kelamin"].isin(gender)) &
    (df_peneliti["bidang"].isin(bidang)) &
    (df_peneliti["tahun"].isin(tahun)) &
    (df_peneliti["kelas"].isin(kelas))
]


# ==============================
# INTERNAL
# ==============================
def show_internal_kpi(df):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Peneliti", df.shape[0])
    col2.metric("Bidang Dominan", df["bidang"].value_counts().idxmax())
    col3.metric("Gender Dominan", df["jenis_kelamin"].value_counts().idxmax())
    col4.metric("Tahun Teraktif", int(df["tahun"].value_counts().idxmax()))


def show_internal_visual(df):
    st.subheader("📌 Analisis Internal")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        df["bidang"].value_counts().plot(kind="bar", ax=ax)
        st.pyplot(fig)

    with col2:
        pivot = pd.crosstab(df["bidang"], df["jenis_kelamin"])
        fig, ax = plt.subplots()
        pivot.plot(kind="bar", stacked=True, ax=ax)
        st.pyplot(fig)

    fig, ax = plt.subplots()
    df.groupby("tahun").size().plot(marker="o", ax=ax)
    st.pyplot(fig)


# ==============================
# MAIN LOGIC
# ==============================
if mode == "Internal":
    show_internal_kpi(df_filtered)
    show_internal_visual(df_filtered)

else:
    keywords = extract_keywords(
        df_filtered["judul"].dropna().unique(),
        top_n=1000
    )

    keyword_list = [k[0] for k in keywords]

    show_external_visual(
        df_filtered=df_filtered,
        years=tahun,
        keywords=keyword_list,
        fetch_trend_func=load_trend_cached
    )


# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("© Dashboard Analisis LPB CYS | Muhammad Zidan Rizki ZUlfazli | TI '22")
