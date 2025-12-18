import pandas as pd

def explode_peneliti(df):
    records = []

    for _, row in df.iterrows():
        for idx in [1, 2]:
            jk_col = f"jenis kelamin peneliti {idx}"
            kelas_col = f"kelas peneliti {idx}"

            if jk_col in df.columns and pd.notna(row[jk_col]):
                records.append({
                    "judul": row["judul penelitian"],
                    "bidang": row["bidang"],
                    "tahun": row["tahun"],
                    "provinsi": row["provinsi"],
                    "jenis_kelamin": row[jk_col],
                    "kelas": row[kelas_col] if kelas_col in df.columns else None
                })

    return pd.DataFrame(records)

