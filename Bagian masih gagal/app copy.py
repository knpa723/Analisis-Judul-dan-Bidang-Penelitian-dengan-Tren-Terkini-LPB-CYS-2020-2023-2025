import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_data
from src.preprocessing import explode_peneliti
from src.keyword_extraction import extract_keywords
from src.trend_analysis import get_trend, extract_trend_peak, save_trend_peak

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
    df_raw = load_data("data\Data Clean.xlsx")
    df_peneliti = explode_peneliti(df_raw)
    return df_raw, df_peneliti

df_raw, df_peneliti = load_all_data()


# ==============================
# CACHE GOOGLE TRENDS
# ==============================
@st.cache_data(show_spinner=False)
def load_trend_cached(keyword):
    return get_trend(keyword)


# ==============================
# SIDEBAR FILTER
# ==============================
st.sidebar.header("⚙️ Filter Data")

mode = st.sidebar.radio(
    "Pilih Jenis Analisis",
    ["Internal", "Eksternal"],
    horizontal=False
)

# Helper agar multiselect tidak boleh kosong
def safe_multiselect(label, options):
    selected = st.sidebar.multiselect(label, options, default=options)
    if len(selected) == 0:
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
# KPI CARD (INTERNAL)
# ==============================
def show_internal_kpi(df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Peneliti", df.shape[0])

    with col2:
        top_bidang = df["bidang"].value_counts().idxmax()
        st.metric("Bidang Dominan", top_bidang)

    with col3:
        gender_ratio = df["jenis_kelamin"].value_counts(normalize=True) * 100
        st.metric("Gender Dominan", gender_ratio.idxmax())

    with col4:
        top_year = df["tahun"].value_counts().idxmax()
        st.metric("Tahun Teraktif", int(top_year))


# ==============================
# VISUALISASI INTERNAL
# ==============================
def show_internal_visual(df):
    st.subheader("📌 Analisis Internal")

    col1, col2 = st.columns(2)

    # Distribusi Bidang
    with col1:
        st.markdown("**Distribusi Bidang Penelitian**")
        fig, ax = plt.subplots()
        df["bidang"].value_counts().plot(kind="bar", ax=ax)
        ax.set_xlabel("Bidang")
        ax.set_ylabel("Jumlah Peneliti")
        st.pyplot(fig)

    # Gender vs Bidang
    with col2:
        st.markdown("**Gender vs Bidang**")
        pivot = pd.crosstab(df["bidang"], df["jenis_kelamin"])
        fig, ax = plt.subplots()
        pivot.plot(kind="bar", stacked=True, ax=ax)
        ax.set_xlabel("Bidang")
        ax.set_ylabel("Jumlah")
        st.pyplot(fig)

    # Tren Tahunan
    st.markdown("**Tren Jumlah Peneliti per Tahun**")
    fig, ax = plt.subplots()
    df.groupby("tahun").size().plot(marker="o", ax=ax)
    ax.set_ylabel("Jumlah Peneliti")
    st.pyplot(fig)


# ==============================
# VISUALISASI EKSTERNAL
# ==============================
def show_external_visual(df):
    st.subheader("Analisis Eksternal (Google Trends)")

    if df.empty:
        st.warning("Data kosong setelah filter.")
        return

    # ==========================
    # KEYWORD EXTRACTION
    # ==========================
    keywords = extract_keywords(
        df["judul"].dropna().unique(),
        top_n=10
    )

    if len(keywords) == 0:
        st.info("Tidak ada keyword yang dapat diekstrak.")
        return

    keyword_df = pd.DataFrame(keywords, columns=["Keyword", "Score"])

    col1, col2 = st.columns(2)

    # ==========================
    # TOP KEYWORD BAR CHART
    # ==========================
    with col1:
        st.markdown("**Top Keyword Judul Penelitian**")
        fig, ax = plt.subplots()
        ax.barh(keyword_df["Keyword"], keyword_df["Score"])
        ax.set_xlabel("TF-IDF Score")
        ax.invert_yaxis()
        st.pyplot(fig)

    # ==========================
    # GOOGLE TRENDS
    # ==========================
    with col2:
        st.markdown("**Trend Alignment (Google Trends)**")

        keyword = keyword_df.iloc[0]["Keyword"]

        try:
            trend = load_trend_cached(keyword)

            if trend.empty:
                st.info("Google Trends tidak mengembalikan data.")
                return

            # Line chart
            st.line_chart(trend.iloc[:, 0])

            # ==========================
            # SIMPAN DATA TREND
            # ==========================
            os.makedirs("data/trends", exist_ok=True)

            trend_file = f"data/trends/trend_{keyword.replace(' ', '_')}.csv"
            trend.to_csv(trend_file)

            # ==========================
            # PEAK EXTRACTION
            # ==========================
            peak_value = int(trend.iloc[:, 0].max())
            peak_date = trend.iloc[:, 0].idxmax()

            peak_df = pd.DataFrame([{
                "keyword": keyword,
                "peak_value": peak_value,
                "peak_date": peak_date
            }])

            peak_file = "data/trends/trend_peak_summary.csv"

            if os.path.exists(peak_file):
                old = pd.read_csv(peak_file)
                peak_df = (
                    pd.concat([old, peak_df])
                    .drop_duplicates(subset=["keyword"], keep="last")
                )

            peak_df.to_csv(peak_file, index=False)

            # ==========================
            # INFO BOX
            # ==========================
            st.success(
                f" Peak trend **{keyword}** terjadi pada "
                f"**{peak_date.date()}** dengan nilai **{peak_value}**"
            )

        except Exception as e:
            st.error("Gagal mengambil data Google Trends")
            st.caption(str(e))


# ==============================
# MAIN LOGIC
# ==============================
if mode == "Internal":
    show_internal_kpi(df_filtered)
    show_internal_visual(df_filtered)

else:
    show_external_visual(df_filtered)

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("© Dashboard Analisis LPB | NLP & Trend Analytics")
