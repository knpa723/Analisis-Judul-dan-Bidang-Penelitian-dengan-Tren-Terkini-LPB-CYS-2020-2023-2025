import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from src.keyword_extraction import extract_keywords


# ==============================
# KPI INTERNAL
# ==============================
def show_internal_kpi(df):
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👩‍🔬 Total Penelitian", df.shape[0])
    c2.metric("📚 Bidang Dominan", df["bidang"].value_counts().idxmax())
    c3.metric("⚧ Gender Dominan", df["jenis_kelamin"].value_counts().idxmax())
    c4.metric("📅 Tahun Teraktif", int(df["tahun"].value_counts().idxmax()))


# ==============================
# VISUAL INTERNAL
# ==============================
def show_internal_visual(df, df_all):
    # =====================================================
    # ROW 1 — STACKED BAR + 2 PIE (SEBARIS)
    # =====================================================
    col1, col2, col3 = st.columns([2, 1.2, 1.2])

    # ---------- STACKED BAR ----------
    with col1:
        st.markdown("### Gender vs Bidang")

        pivot = pd.crosstab(df["bidang"], df["jenis_kelamin"])

        fig = px.bar(
            pivot,
            x=pivot.index,
            y=pivot.columns,
            title="Distribusi Gender per Bidang",
            labels={"value": "Jumlah Peneliti", "variable": "Gender"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- PIE 1: TOPIK (KEYWORD EXTRACTION) ----------
    with col2:
        st.markdown("### Topik Penelitian (Judul)")

        keywords = extract_keywords(
            df["judul"].dropna().unique(),
            top_n=10
        )

        topic_df = pd.DataFrame(
            keywords,
            columns=["topik", "jumlah"]
        )

        fig = px.pie(
            topic_df,
            names="topik",
            values="jumlah",
            hole=0.45
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- PIE 2: BIDANG ----------
    with col3:
        st.markdown("### Distribusi Bidang")

        bidang_count = (
            df["bidang"]
            .value_counts()
            .reset_index()
        )
        bidang_count.columns = ["bidang", "jumlah"]

        fig = px.pie(
            bidang_count,
            names="bidang",
            values="jumlah",
            hole=0.45
        )
        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # ROW 2 — BAR PROVINSI
    # =====================================================
    st.markdown("### Topik Penelitian Terfavorit per Provinsi")

    records = []

    for prov, df_p in df.groupby("provinsi"):
        judul_list = df_p["judul"].dropna().unique()

        # guard aman
        if len(judul_list) < 2:
            continue

        keywords = extract_keywords(judul_list, top_n=1)

        if not keywords:
            continue

        topik, skor = keywords[0]

        records.append({
            "provinsi": prov,
            "topik": topik,
            "jumlah": len(judul_list)
        })

    prov_topic_df = pd.DataFrame(records)

    if prov_topic_df.empty:
        st.warning("⚠️ Tidak cukup data untuk analisis topik per provinsi.")
    else:
        prov_topic_df = prov_topic_df.sort_values("jumlah", ascending=False)

        fig = px.bar(
            prov_topic_df,
            x="provinsi",
            y="jumlah",
            color="topik",  
            hover_data={
                "topik": True,
                "jumlah": True,
                "provinsi": False
            },
            labels={
                "jumlah": "Jumlah Judul",
                "provinsi": "Provinsi",
                "topik": "Topik Terfavorit"
            },
            title="Topik Penelitian Terfavorit per Provinsi"
        )

        fig.update_layout(
            legend_title_text="Topik Penelitian",
            xaxis_tickangle=-45,
            bargap=0.25
        )

        st.plotly_chart(fig, use_container_width=True)


    # =====================================================
    # ROW 3 — TREN JUDUL
    # =====================================================
    st.markdown("### Tren Jumlah Penelitian per Tahun")


    all_years = sorted(df_all["tahun"].dropna().unique())


    trend_all = (
        df_all.groupby("tahun")["judul"]
        .nunique()
        .reindex(all_years, fill_value=0)
        .reset_index()
    )


    trend_selected = (
        df.groupby("tahun")["judul"]
        .nunique()
        .reindex(all_years, fill_value=0)
        .reset_index()
    )


    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(
        trend_all["tahun"],
        trend_all["judul"],
        linestyle="--",
        marker="o",
        linewidth=3,
        color="green",
        alpha=0.9,
        zorder=1,
        label="Total LPB (Semua Provinsi)"
    )

    ax.plot(
        trend_selected["tahun"],
        trend_selected["judul"],
        linestyle="-",
        marker="o",
        linewidth=2,
        color="tab:orange",
        zorder=2,
        label="Provinsi Terpilih"
    )

    ax.set_xlabel("Tahun")
    ax.set_ylabel("Jumlah Judul Penelitian")
    ax.set_title("Tren Jumlah Penelitian per Tahun")

    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)

    st.pyplot(fig)

    if trend_all["judul"].equals(trend_selected["judul"]):
        st.info(
            "ℹ️ Tren provinsi terpilih sama dengan total LPB karena semua provinsi masih dipilih di sidebar."
        )



    # =====================================================
    # ROW 4 — AKURASI EKSTRAKSI TOPIK
    # =====================================================
    # st.markdown("### ✅ Evaluasi Akurasi Ekstraksi Topik")

    # correct = 0
    # total = 0

    # for _, row in df.iterrows():
    #     judul = row["judul"].lower()
    #     bidang = row["bidang"].lower()
    #     total += 1
    #     if bidang in judul:
    #         correct += 1

    # accuracy = round((correct / total) * 100, 2)

    # st.metric(
    #     label="Akurasi Topik (Judul vs Bidang)",
    #     value=f"{accuracy} %"
    # )
