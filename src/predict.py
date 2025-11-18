import joblib
import pandas as pd
from src.preprocess import prepare_dataframe

MODEL_PATH = "models/model.joblib"

# GST keyword rules
GST_KEYWORDS = {
    "5": ["food", "restaurant", "swiggy", "zomato", "meal"],
    "12": ["electronics", "printer", "ink", "office", "chair"],
    "18": ["software", "subscription", "google", "workspace", "canva", "internet", "wifi"]
}

def detect_gst(description):
    """Return GST % based on clean description keywords."""
    desc = str(description).lower()
    for rate, words in GST_KEYWORDS.items():
        if any(w in desc for w in words):
            return int(rate)
    return 0  # No GST identified

def classify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = prepare_dataframe(df)

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Model not found. Train it first. ({e})")

    # ML predictions
    predictions = model.predict(df["clean_desc"])
    df["predicted_category"] = predictions

    # Deductible logic
    deductible_cats = ["travel", "office", "fuel", "utilities"]
    df["deductible"] = df["predicted_category"].apply(
        lambda x: 1 if x in deductible_cats else 0
    )

    # GST calculation
    df["gst_rate"] = df["clean_desc"].apply(detect_gst)
    df["gst_input"] = df.apply(
        lambda row: round((row["amount"] * row["gst_rate"]) / 100, 2)
        if row["gst_rate"] > 0 else 0,
        axis=1
    )

    return df
