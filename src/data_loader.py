import pandas as pd

def load_data(path, sheet_name="GABUNGAN"):
    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=0,
        engine="openpyxl"
    )
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return df