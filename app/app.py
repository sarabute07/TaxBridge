import sys
import os

import streamlit as st
import pandas as pd
import io
import altair as alt

# ---------------- MOCK IMPORTS (Replace with your real ones) ----------------
def classify_dataframe(df):
    if "category" not in df.columns:
        df["category"] = ["Travel", "Office Supplies", "Utilities", "Travel", "Meals"] * (
            len(df) // 5
        ) + (["Travel"] * (len(df) % 5))

    if "gst_rate" not in df.columns:
        df["gst_rate"] = [0.18, 0.12, 0.05, 0.18, 0.00] * (
            len(df) // 5
        ) + ([0.18] * (len(df) % 5))

    if "gst_input" not in df.columns:
        df["gst_input"] = df["amount"].astype(float) * df["gst_rate"]

    return df


def save_transactions(df):
    print(f"Saving {len(df)} transactions…")
    pass


def read_pdf_bank_statement(file):
    data = {
        "date": [
            "2024-05-01",
            "2024-05-02",
            "2024-05-03",
            "2024-05-04",
            "2024-05-05",
        ],
        "description": [
            "UBER RIDE 1234",
            "AMAZON PRINTER INK",
            "ELECTRIC BILL",
            "FLIGHT INDIGO",
            "LOCAL CAFE COFFEE",
        ],
        "amount": [500.00, 2500.00, 1800.50, 8500.00, 300.00],
    }
    return pd.DataFrame(data)


# ----------------------------- PAGE CONFIG -----------------------------
st.set_page_config(
    page_title="TaxBridge — Tax Automation and Expense Classification System",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------- GLOBAL CSS -----------------------------
st.markdown(
    """
<style>

/* ----------------------------------------------------------------------
   🔥 FORCE LIGHT MODE (Works EVEN on Streamlit Cloud Dark Mode)
---------------------------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #ffffff !important;
    filter: invert(0) !important;
}

html.dark, body.dark, [data-testid="stAppViewContainer"].dark {
    background-color: #ffffff !important;
}

:root {
    color-scheme: light !important;
}

/* ----------------------------------------------------------------------
   REMOVE STREAMLIT DEFAULT TOP HEADER + TOOLBAR
---------------------------------------------------------------------- */
header[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}

section[data-testid="stToolbar"] {
    display: none !important;
}

/* Adjust spacing */
.block-container {
    padding-top: 2rem !important;
}

/* Main layout */
body {
    font-family: 'Inter', sans-serif;
}

.main-container {
    padding: 30px 40px;
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e6e6e6;
    box-shadow: 0px 0px 14px rgba(0,0,0,0.03);
}

/* Title */
.app-title {
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: #1e1e1e;
}

.divider {
    height: 1px;
    background-color: #dedede;
    margin: 18px 0 28px 0;
}

/* Subheaders */
.sub-header {
    font-size: 18px;
    font-weight: 600;
    color: #444;
    margin-bottom: 8px;
}

/* Summary cards */
.summary-card {
    padding: 18px;
    border-radius: 12px;
    background: #f8f9fc;
    border: 1px solid #e3e6ee;
}

.summary-title {
    font-size: 14px;
    font-weight: 600;
    color: #666;
}

.summary-value {
    font-size: 22px;
    font-weight: 700;
    color: #222;
    margin-top: 4px;
}

/* Buttons + Download Buttons (Unified Gradient) */
div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #e9f1ff, #c7dcff) !important;
    color: #1a1a1a !important;
    border: 1px solid #b7cef5 !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

div[data-testid="stButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, #dbe8ff, #b4d0ff) !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------- MAIN UI BOX -----------------------------
st.markdown("<div class='main-container'>", unsafe_allow_html=True)


# ----------------------------- TITLE -----------------------------
st.markdown(
    "<div class='app-title'>TaxBridge — Tax Automation and Expense Classification System</div>",
    unsafe_allow_html=True,
)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.write(
    "Upload your bank statements and classify expenses with GST applicability for compliance and reporting."
)


# ----------------------------- FILE UPLOAD -----------------------------
st.markdown("<div class='sub-header'>Upload Bank Statement</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload PDF, CSV, or Excel", type=["pdf", "csv", "xlsx"]
)

if uploaded_file is not None:

    # ---- Read File ----
    if uploaded_file.name.endswith(".pdf"):
        df = read_pdf_bank_statement(uploaded_file)
        st.success("PDF parsed successfully.")
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---- Validate ----
    required_cols = ["date", "description", "amount"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(f"Your file is missing required columns: {', '.join(missing)}")
        st.stop()

    # ---- Preview ----
    st.markdown("<div class='sub-header'>Preview</div>", unsafe_allow_html=True)
    st.dataframe(df.head(), use_container_width=True)

    # ---- Classify ----
    if st.button("Classify Expenses", use_container_width=True):

        result_df = classify_dataframe(df)
        st.success("Classification complete.")

        # Sort by date
        try:
            result_df["date"] = pd.to_datetime(result_df["date"])
            result_df = result_df.sort_values("date")
        except:
            pass

        st.markdown("<div class='sub-header'>Classified Output</div>", unsafe_allow_html=True)
        st.dataframe(result_df, use_container_width=True)

        # Save
        try:
            save_transactions(result_df)
            st.info("Saved to database.")
        except:
            st.warning("Could not save to database.")

        # ---- Total Spend ----
        total_spend = result_df["amount"].astype(float).sum()
        st.markdown(
            f"<h3>Total Spend: ₹ {total_spend:,.2f}</h3>", unsafe_allow_html=True
        )

        # ---------------- GST SUMMARY ----------------
        st.markdown("<div class='sub-header'>GST Summary</div>", unsafe_allow_html=True)

        gst_input_total = result_df["gst_input"].sum()
        gst_applicable = result_df[result_df["gst_rate"] > 0].shape[0]
        gst_not_applicable = result_df[result_df["gst_rate"] == 0].shape[0]
        taxable_spend = result_df[result_df["gst_rate"] > 0]["amount"].sum()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
            <div class='summary-card'>
                <div class='summary-title'>Total GST Input</div>
                <div class='summary-value'>₹ {gst_input_total:,.2f}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class='summary-card'>
                <div class='summary-title'>GST Applicable</div>
                <div class='summary-value'>{gst_applicable}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
            <div class='summary-card'>
                <div class='summary-title'>GST Not Applicable</div>
                <div class='summary-value'>{gst_not_applicable}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"""
            <div class='summary-card'>
                <div class='summary-title'>Taxable Spend</div>
                <div class='summary-value'>₹ {taxable_spend:,.2f}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # ---------------- MONTHLY TREND ----------------
        st.markdown(
            "<br><div class='sub-header'>Monthly Expense Trend</div>",
            unsafe_allow_html=True,
        )

        result_df["date"] = pd.to_datetime(result_df["date"])
        result_df["month_period"] = result_df["date"].dt.to_period("M")

        monthly = result_df.groupby("month_period")["amount"].sum().reset_index()
        monthly["date"] = monthly["month_period"].astype(str)

        chart = (
            alt.Chart(monthly)
            .mark_line(point=True, strokeWidth=2, color="#4c78a8")
            .encode(
                x=alt.X("date:N", title="Month"),
                y=alt.Y("amount:Q", title="Total Expense"),
                tooltip=["date:N", alt.Tooltip("amount:Q", format=",.2f")],
            )
            .properties(height=380)
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)

        # ---------------- DOWNLOADS ----------------
        st.markdown("<div class='sub-header'>Download Results</div>", unsafe_allow_html=True)

        buffer = io.BytesIO()
        result_df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="Download Excel",
            data=buffer,
            file_name="taxbridge_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )

        csv_data = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="taxbridge_output.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )


# ----------------------------- END -----------------------------
st.markdown("</div>", unsafe_allow_html=True)
