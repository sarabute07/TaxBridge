import pdfplumber
import pandas as pd

def safe_float(value):
    """
    Safely convert a value to float.
    Handles: '', None, '--', spaces, ',', '₹', etc.
    """
    if value is None:
        return 0.0

    try:
        value = str(value)
        value = value.replace(",", "").replace("₹", "").strip()

        if value == "" or value == "-" or value.lower() == "nan":
            return 0.0

        return float(value)
    except:
        return 0.0


def read_pdf_bank_statement(pdf_file):
    """
    Extracts tables from a PDF bank statement and returns a clean DataFrame.
    Safe for messy PDFs, blank cells, extra rows, and missing numbers.
    """

    final_rows = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            try:
                table = page.extract_table()
            except:
                table = None

            if table:
                for row in table:
                    if row and any(str(x).strip() for x in row):  # skip empty rows
                        final_rows.append(row)

    if not final_rows:
        raise ValueError("No table found inside PDF. PDF might be scanned or unstructured.")

    # Convert to DataFrame
    df = pd.DataFrame(final_rows)

    # First row = header
    df.columns = df.iloc[0].astype(str).str.strip().str.lower()
    df = df.drop(0, axis=0)

    # Clean column names
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Normalize column names (common cases)
    rename_map = {
        "narration": "description",
        "details": "description",
        "particulars": "description",
        "transaction details": "description",

        "date": "date",
        "value date": "date",
        "txn date": "date",

        "withdrawal amt": "debit",
        "withdrawal amount": "debit",
        "withdrawal": "debit",

        "deposit amt": "credit",
        "deposit amount": "credit",
        "deposit": "credit",

        "amount": "amount",
        "amt": "amount",
    }

    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

    # Fill missing cols
    if "description" not in df.columns:
        df["description"] = ""

    # Create amount column safely
    if "amount" not in df.columns:
        if "debit" in df.columns and "credit" in df.columns:
            df["amount"] = df.apply(
                lambda r: safe_float(r.get("debit")) - safe_float(r.get("credit")),
                axis=1,
            )
        elif "debit" in df.columns:
            df["amount"] = df["debit"].apply(safe_float)
        elif "credit" in df.columns:
            df["amount"] = df["credit"].apply(safe_float)
        else:
            df["amount"] = 0.0
    else:
        df["amount"] = df["amount"].apply(safe_float)

    # Convert debit/credit columns safely
    if "debit" in df.columns:
        df["debit"] = df["debit"].apply(safe_float)
    if "credit" in df.columns:
        df["credit"] = df["credit"].apply(safe_float)

    # Clean NA values
    df = df.fillna("")

    return df
