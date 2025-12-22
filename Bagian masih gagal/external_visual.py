import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.trend_analysis import (
    save_trend_yearly_final,
    load_trend_yearly
)

# =====================================================
# VISUALISASI EKSTERNAL (GOOGLE TRENDS)
# =====================================================
def show_external_visual(
    df_filtered,
    years,
    keywords,
    fetch_trend_func
):
    st.subheader("🌐 Analisis Eksternal (Google Trends)")

    # =================================================
    # PRE-SYNC GATE (WAJIB LOLOS)
    # =================================================
    if df_filtered is None or df_filtered.empty:
        st.warning("⚠️ Data kosong setelah filter. Analisis eksternal dibatalkan.")
        return

    if not keywords or len(keywords) < 3:
        st.warning("⚠️ Keyword tidak cukup untuk analisis tren.")
        return

    if not years:
        st.warning("⚠️ Tahun analisis belum dipilih.")
        return

    try:
        years = sorted([int(y) for y in years])
    except Exception:
        st.error("❌ Format tahun tidak valid.")
        st.stop()

    # =================================================
    # LOAD DATA TREN (TANPA AUTO SYNC)
    # =================================================
    trend_df = load_trend_yearly()

    # Pastikan struktur kolom aman
    required_cols = {
        "keyword",
        "year",
        "google_peak",
        "google_mean",
        "google_sum",
        "google_rank"
    }

    if not trend_df.empty:
        missing_cols = required_cols - set(trend_df.columns)
        if missing_cols:
            st.error(
                f"❌ File trend_yearly.csv rusak / tidak sesuai.\n"
                f"Kolom hilang: {missing_cols}"
            )
            st.stop()

    # =================================================
    # SINKRONISASI (HANYA JIKA DIPERLUKAN)
    # =================================================
    need_sync_years = []

    if trend_df.empty:
        need_sync_years = years
    else:
        existing_years = trend_df["year"].unique().tolist()
        need_sync_years = [y for y in years if y not in existing_years]

    if need_sync_years:
        with st.spinner(f"📡 Sinkronisasi Google Trends {need_sync_years}..."):
            trend_df = save_trend_yearly_final(
                keywords=keywords,
                years=need_sync_years,
                fetch_trend_func=fetch_trend_func
            )

    if trend_df.empty:
        st.warning("⚠️ Data Google Trends belum tersedia.")
        return

    # =================================================
    # FILTER TAHUN
    # =================================================
    df_year = trend_df[trend_df["year"].isin(years)]

    if df_year.empty:
        st.warning("⚠️ Tidak ada data tren untuk tahun terpilih.")
        return

    # =================================================
    # TOP 100 TREND (GOOGLE ONLY)
    # =================================================
    st.subheader("🔥 Top 100 Tren Nasional (Google Trends)")

    top100 = (
        df_year
        .groupby("keyword", as_index=False)
        .agg(
            google_total_score=("google_sum", "sum"),
            google_peak_value=("google_peak", "max")
        )
        .sort_values("google_total_score", ascending=False)
        .head(100)
    )

    st.dataframe(top100, use_container_width=True)

    # =================================================
    # SCATTER: JUDUL vs TREN GLOBAL
    # =================================================
    st.subheader("📊 Kecocokan Judul vs Tren Global")

    # hitung rasio mention judul
    judul_count = (
        df_filtered["judul"]
        .str.lower()
        .str.contains("|".join(keywords), regex=True)
        .mean() * 100
    )

    scatter_df = (
        df_year
        .groupby("keyword", as_index=False)
        .agg(google_total_score=("google_sum", "sum"))
    )

    scatter_df["judul_mention_ratio"] = judul_count

    fig, ax = plt.subplots()
    ax.scatter(
        scatter_df["google_total_score"],
        scatter_df["judul_mention_ratio"]
    )
    ax.set_xlabel("Google Trend Total Score")
    ax.set_ylabel("Judul Mention Ratio (%)")
    ax.grid(True)

    st.pyplot(fig)

    # =================================================
    # LINE CHART: IKUT TREN ATAU TIDAK
    # =================================================
    st.subheader("📈 Rata-rata Kesesuaian Judul terhadap Tren")

    line_df = (
        df_year
        .groupby("year", as_index=False)
        .agg(avg_google_trend=("google_mean", "mean"))
    )

    fig, ax = plt.subplots()
    ax.plot(
        line_df["year"],
        line_df["avg_google_trend"],
        marker="o"
    )
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Rata-rata Skor Google Trends")
    ax.grid(True)

    st.pyplot(fig)
