import re
import pandas as pd

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_columns(df):
    """Maps different CSV column names to standard ones."""
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]

    column_map = {
        "narration": "description",
        "details": "description",
        "particulars": "description",
        "transaction details": "description",
        "txn details": "description",

        "date": "date",
        "txn date": "date",
        "transaction date": "date",

        "amount": "amount",
        "debit": "amount",
        "withdrawal amt": "amount",
        "credit": "amount",
        "deposit amt": "amount"
    }

    for old, new in column_map.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]

    return df

def prepare_dataframe(df):
    df = normalize_columns(df)

    # Ensure required columns
    if "description" not in df.columns:
        raise ValueError("CSV must contain a description or narration column.")

    if "amount" not in df.columns:
        df["amount"] = 0.0  # default

    if "date" not in df.columns:
        df["date"] = None

    # Clean text field
    df["clean_desc"] = df["description"].apply(clean_text)
    return df
