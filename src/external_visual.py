import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.trend_analysis import (
    save_trend_yearly_final,
    load_trend_yearly
)

# ==============================
# VISUALISASI EKSTERNAL
# ==============================
def show_external_visual(
    df_filtered,
    years,
    keywords,
    fetch_trend_func
):
    st.subheader("🌐 Analisis Eksternal (Google Trends)")

    # ==========================
    # LOAD / SYNC DATA
    # ==========================
    trend_df = load_trend_yearly()

    for y in years:
        if trend_df.empty or y not in trend_df["year"].unique():
            with st.spinner(f"📡 Sinkronisasi Google Trends {y}..."):
                trend_df = save_trend_yearly_final(
                    year=y,
                    keywords=keywords,
                    df_judul=df_filtered[df_filtered["tahun"] == y],
                    fetch_trend_func=fetch_trend_func
                )

    # ==========================
    # FILTER YEAR
    # ==========================
    df_year = trend_df[trend_df["year"].isin(years)]

    # ==========================
    # TOP 100 TREND (GOOGLE ONLY)
    # ==========================
    top100 = (
        df_year
        .groupby("keyword")
        .agg({
            "google_total_score": "sum",
            "google_peak_value": "max"
        })
        .sort_values("google_total_score", ascending=False)
        .head(100)
        .reset_index()
    )

    st.subheader("🔥 Top 100 Trend Nasional")
    st.dataframe(top100)

    # ==========================
    # SCATTER: JUDUL vs TREND
    # ==========================
    st.subheader("📊 Kecocokan Judul vs Tren Global")

    scatter_df = (
        df_year
        .groupby("keyword")
        .agg({
            "google_total_score": "sum",
            "judul_mention_ratio": "mean"
        })
    )

    fig, ax = plt.subplots()
    ax.scatter(
        scatter_df["google_total_score"],
        scatter_df["judul_mention_ratio"]
    )
    ax.set_xlabel("Google Trend Total Score")
    ax.set_ylabel("Judul Mention Ratio (%)")

    st.pyplot(fig)

    # ==========================
    # LINE: IKUT TREND ATAU TIDAK
    # ==========================
    st.subheader("📈 Tren Mengikuti Topik Populer")

    line_df = (
        df_year
        .groupby("year")["judul_mention_ratio"]
        .mean()
    )

    fig, ax = plt.subplots()
    ax.plot(line_df.index, line_df.values, marker="o")
    ax.set_ylabel("Rata-rata % Judul Mengikuti Tren")

    st.pyplot(fig)
