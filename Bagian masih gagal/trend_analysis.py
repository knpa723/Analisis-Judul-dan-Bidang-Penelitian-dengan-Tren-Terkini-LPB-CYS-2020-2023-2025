import pandas as pd
import os
from datetime import datetime
from pytrends.request import TrendReq


def get_trend(keyword, year):
    pytrends = TrendReq(hl="id-ID", tz=360)

    start = f"{year}-01-01"
    end = f"{year}-12-01"

    pytrends.build_payload(
        [keyword],
        timeframe=f"{start} {end}",
        geo="ID"
    )

    df = pytrends.interest_over_time()

    if df.empty:
        return df

    return df.drop(columns=["isPartial"], errors="ignore")

# ==============================
# SAVE TREND PER TAHUN (FINAL)
# ==============================
def save_trend_yearly_final(
    keywords,
    years,
    fetch_trend_func,
    path="data/trends/trend_yearly.csv"
):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        df_all = pd.read_csv(path)
    else:
        df_all = pd.DataFrame()

    records = []

    for year in years:
        for kw in keywords:
            if (
                not df_all.empty
                and ((df_all["keyword"] == kw) & (df_all["year"] == year)).any()
            ):
                continue

            try:
                trend = fetch_trend_func(kw, year)
                if trend.empty:
                    continue

                series = trend.iloc[:, 0]

                records.append({
                    "keyword": kw,
                    "year": int(year),
                    "google_peak": int(series.max()),
                    "google_mean": float(series.mean()),
                    "google_sum": int(series.sum())
                })

            except:
                continue

    if records:
        df_new = pd.DataFrame(records)
        df_all = pd.concat([df_all, df_new], ignore_index=True)

        # ranking per tahun
        df_all["google_rank"] = (
            df_all
            .groupby("year")["google_peak"]
            .rank(method="dense", ascending=False)
        )

        df_all.to_csv(path, index=False)

    return df_all



# ==============================
# LOAD SAJA (TANPA SINKRON)
# ==============================
def load_trend_yearly(path="data/trends/trend_yearly.csv"):
    if not os.path.exists(path):
        return pd.DataFrame()

    return pd.read_csv(path)
