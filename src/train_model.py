import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from src.preprocess import prepare_dataframe

def main():
    print("Loading training data...")
    try:
        df = pd.read_csv("data/training.csv")
        print("Data loaded. Rows:", len(df))
    except Exception as e:
        print("ERROR loading data:", e)
        return

    df = prepare_dataframe(df)

    if "category" not in df.columns:
        print("ERROR: 'category' column missing in training.csv")
        return

    if df.empty:
        print("ERROR: training.csv is empty or not loaded correctly")
        return

    X = df["clean_desc"]
    y = df["category"]

    print("Training model...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("model", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X, y)
    print("Training complete.")

    joblib.dump(pipeline, "models/model.joblib")
    print("Model saved to models/model.joblib")

if __name__ == "__main__":
    main()
