import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "taxbridge.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        description TEXT,
        amount REAL,
        predicted_category TEXT,
        deductible INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def save_transactions(df: pd.DataFrame):
    init_db()
    conn = sqlite3.connect(DB_PATH)

    # Make sure the columns exist before saving
    required_cols = ["date", "description", "amount", "predicted_category", "deductible"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    df_to_save = df[required_cols].copy()
    df_to_save.to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()
