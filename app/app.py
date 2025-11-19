import sys
import os

# Ensure root path is available
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import io
import altair as alt

# Mock imports since the original files are not provided.
# You will need to ensure these modules (src.predict, src.db, src.read_pdf) are available.
def classify_dataframe(df):
    # Mock implementation for classification
    if 'category' not in df.columns:
        df['category'] = ['Travel', 'Office Supplies', 'Utilities', 'Travel', 'Meals'] * (len(df) // 5) + (['Travel'] * (len(df) % 5))
    if 'gst_rate' not in df.columns:
        df['gst_rate'] = [0.18, 0.12, 0.05, 0.18, 0.00] * (len(df) // 5) + ([0.18] * (len(df) % 5))
    if 'gst_input' not in df.columns:
        df['gst_input'] = df['amount'].astype(float) * df['gst_rate']
    return df

def save_transactions(df):
    # Mock implementation for database saving
    print(f"Saving {len(df)} transactions to database...")
    pass

def read_pdf_bank_statement(file):
    # Mock implementation for PDF reading - create a dummy DataFrame
    data = {
        'date': ['2024-05-01', '2024-05-02', '2024-05-03', '2024-05-04', '2024-05-05'],
        'description': ['UBER RIDE 1234', 'AMAZON PRINTER INK', 'ELECTRIC BILL', 'FLIGHT INDIGO', 'LOCAL CAFE COFFEE'],
        'amount': [500.00, 2500.00, 1800.50, 8500.00, 300.00]
    }
    return pd.DataFrame(data)

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(
    page_title="TaxBridge — Tax Automation and Expense Classification System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# GLOBAL CSS — BLUE-NAVY GLASSMORPHISM
# --------------------------------------------------
st.markdown("""
<style>

:root {
    color-scheme: light !important;
}

/* Remove Streamlit header */
header[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}

section[data-testid="stToolbar"] {
    display: none !important;
}

/* Page container spacing */
.block-container {
    padding-top: 2rem !important;
}

/* Background gradient - Navy to Blue */
div.main[data-testid="stAppViewBlockContainer"] {
    padding-top: 0 !important;
    background: linear-gradient(135deg, #0f1729 0%, #1a2847 50%, #2d5a8c 100%) !important;
    min-height: 100vh;
}

div.block-container {
    padding-top: 2rem !important;
}

/* Main background + font */
body {
    background: linear-gradient(135deg, #0f1729 0%, #1a2847 50%, #2d5a8c 100%) !important;
    font-family: 'Inter', -apple-system, sans-serif;
}

html {
    background: linear-gradient(135deg, #0f1729 0%, #1a2847 50%, #2d5a8c 100%) !important;
}

/* Streamlit app wrapper */
.stApp {
    background: linear-gradient(135deg, #0f1729 0%, #1a2847 50%, #2d5a8c 100%) !important;
}

/* Main boxed layout - Glassmorphism Effect */
.main-container {
    padding: 40px 50px;
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
    margin: 20px;
}

/* Title */
.app-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -0.8px;
    background: linear-gradient(135deg, #60a5ff, #a5d6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 30px rgba(96, 165, 255, 0.2);
}

/* Divider */
.divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(165, 214, 255, 0.5), transparent);
    margin: 24px 0 32px 0;
}

/* Sub-heading */
.sub-header {
    font-size: 20px;
    font-weight: 700;
    background: linear-gradient(135deg, #90caf9, #64b5f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
    margin-top: 24px;
}

/* Summary cards - Glassmorphism */
.summary-card {
    padding: 22px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 8px 20px rgba(45, 90, 140, 0.25);
    transition: all 0.3s ease;
}

.summary-card:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(96, 165, 255, 0.4) !important;
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(96, 165, 255, 0.35);
}

.summary-title {
    font-size: 14px;
    font-weight: 600;
    color: rgba(165, 214, 255, 0.8);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.summary-value {
    font-size: 26px;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5ff, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-top: 8px;
}

/* Buttons - Glass effect with gradient */
div[data-testid="stButton"] button, 
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, rgba(96, 165, 255, 0.3), rgba(147, 197, 253, 0.2)) !important;
    color: #e0f2ff !important;
    border: 1.5px solid rgba(96, 165, 255, 0.6) !important;
    padding: 12px 24px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    width: 100% !important;
    background-color: transparent !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(96, 165, 255, 0.2) !important;
}

div[data-testid="stButton"] button:hover, 
div[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, rgba(96, 165, 255, 0.5), rgba(147, 197, 253, 0.4)) !important;
    border: 1.5px solid rgba(96, 165, 255, 0.8) !important;
    box-shadow: 0 6px 20px rgba(96, 165, 255, 0.4) !important;
    transform: translateY(-2px);
}

/* File uploader styling */
div[data-testid="stFileUploadDropzone"] {
    background: rgba(45, 90, 140, 0.25) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 2px dashed rgba(96, 165, 255, 0.6) !important;
    border-radius: 16px !important;
    padding: 30px !important;
}

div[data-testid="stFileUploadDropzone"] * {
    color: #60a5ff !important;
}

div[data-testid="stFileUploadDropzone"] button {
    background: linear-gradient(135deg, rgba(96, 165, 255, 0.4), rgba(147, 197, 253, 0.3)) !important;
    color: #60a5ff !important;
}

/* File uploader text */
[data-testid="stFileUploadDropzone"] p, 
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] div {
    color: #60a5ff !important;
}

/* Dataframe styling */
div[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    overflow: hidden;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
}

.stDataFrame, [data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.08) !important;
}

/* Dataframe table text */
[data-testid="stDataFrame"] tbody td,
[data-testid="stDataFrame"] thead th {
    color: #1a1a1a !important;
    background: rgba(255, 255, 255, 0.95) !important;
}

[data-testid="stDataFrame"] table {
    background: rgba(255, 255, 255, 0.95) !important;
}

/* Tabs styling - Glass effect */
div[data-testid="stTabs"] {
    background: transparent !important;
}

[role="tablist"] {
    background: rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border-radius: 16px !important;
    padding: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

button[role="tab"] {
    background: transparent !important;
    color: rgba(165, 214, 255, 0.7) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    padding: 10px 20px !important;
}

button[role="tab"]:hover {
    background: rgba(96, 165, 255, 0.15) !important;
    color: #60a5ff !important;
}

button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(96, 165, 255, 0.3), rgba(147, 197, 253, 0.2)) !important;
    color: #e0f2ff !important;
    border: 1px solid rgba(96, 165, 255, 0.5) !important;
}

/* Success/Info/Warning/Error messages */
div[data-testid="stAlert"] {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
}

/* Text color adjustments */
p, label, span {
    color: #60a5ff !important;
}

/* Input styling */
input, textarea, select {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #e0f2ff !important;
    border: 1px solid rgba(96, 165, 255, 0.3) !important;
    border-radius: 8px !important;
}

/* Metric value styling */
.metric-value {
    color: #60a5ff !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(96, 165, 255, 0.5), rgba(45, 90, 140, 0.5));
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, rgba(96, 165, 255, 0.7), rgba(45, 90, 140, 0.7));
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# MAIN WRAPPER BOX
# --------------------------------------------------
st.markdown("<div class='main-container'>", unsafe_allow_html=True)


# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.markdown("<div class='app-title'>TaxBridge — Tax Automation and Expense Classification System</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

st.write("Upload your bank statements and classify expenses with GST applicability for compliance and reporting.")


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
st.markdown("<div class='sub-header'>Upload Bank Statement</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose PDF, CSV, or Excel",
    type=["pdf", "csv", "xlsx"]
)

if uploaded_file is not None:

    # --------------------------------------------------
    # READ FILE
    # --------------------------------------------------
    if uploaded_file.name.endswith(".pdf"):
        try:
            df = read_pdf_bank_statement(uploaded_file)
            st.success("PDF parsed successfully.")
        except Exception as e:
            st.error(f"PDF extraction failed: {e}")
            st.stop()

    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        # Check if the uploaded file is a mock PDF for the demo
        if uploaded_file.name.endswith(".xlsx"):
             df = pd.read_excel(uploaded_file)
        else:
             # Fallback/Default for unknown files, assuming Excel
             df = pd.read_excel(uploaded_file)

    # --------------------------------------------------
    # 1. VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------
    required_cols = ["date", "description", "amount"]
    # Check if a mock DataFrame needs to be generated for non-PDF files for the demo
    if df.empty and uploaded_file.name != 'taxbridge_output.xlsx':
        st.warning("Generating mock data since the uploaded file is empty or missing data for the demo.")
        data = {
            'date': ['2024-05-01', '2024-05-02', '2024-05-03', '2024-05-04', '2024-05-05'],
            'description': ['UBER RIDE 1234', 'AMAZON PRINTER INK', 'ELECTRIC BILL', 'FLIGHT INDIGO', 'LOCAL CAFE COFFEE'],
            'amount': [500.00, 2500.00, 1800.50, 8500.00, 300.00]
        }
        df = pd.DataFrame(data)

    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(f"Your file is missing required columns: {', '.join(missing)}")
        st.stop()


    # --------------------------------------------------
    # PREVIEW TABLE (plain, no gradient)
    # --------------------------------------------------
    st.markdown("<div class='sub-header'>Preview</div>", unsafe_allow_html=True)
    st.dataframe(df.head(), use_container_width=True)


    # --------------------------------------------------
    # CLASSIFY BUTTON
    # --------------------------------------------------
    # This st.button is now styled by the global CSS rule targeting div[data-testid="stButton"] > button
    if st.button("Classify Expenses", use_container_width=True):

        try:
            result_df = classify_dataframe(df)
            st.success("Classification complete.")
        except Exception as e:
            st.error(f"Classification error: {e}")
            st.stop()

        # --------------------------------------------------
        # 2. SORT BY DATE
        # --------------------------------------------------
        try:
            result_df["date"] = pd.to_datetime(result_df["date"])
            result_df = result_df.sort_values("date")
        except:
            pass


        # --------------------------------------------------
        # CLASSIFIED TABLE (plain)
        # --------------------------------------------------
        st.markdown("<div class='sub-header'>Classified Output</div>", unsafe_allow_html=True)
        st.dataframe(result_df, use_container_width=True)


        # SAVE TO DATABASE
        try:
            save_transactions(result_df)
            st.info("Saved to database.")
        except:
            st.warning("Could not save to database.")


        # --------------------------------------------------
        # TOTAL SPEND
        # --------------------------------------------------
        try:
            total_spend = result_df["amount"].astype(float).sum()
        except:
            total_spend = 0

        st.markdown(f"<h3 style='color: #60a5ff; text-align: center; font-weight: 800; font-size: 28px; margin-top: 40px;'>Total Spend: ₹ {total_spend:,.2f}</h3>", unsafe_allow_html=True)


        # --------------------------------------------------
        # GST SUMMARY CARDS
        # --------------------------------------------------
        st.markdown("<div class='sub-header'>GST Summary</div>", unsafe_allow_html=True)

        try:
            gst_input_total = result_df["gst_input"].astype(float).sum()
            gst_applicable = result_df[result_df["gst_rate"] > 0].shape[0]
            gst_not_applicable = result_df[result_df["gst_rate"] == 0].shape[0]
            taxable_spend = result_df[result_df["gst_rate"] > 0]["amount"].astype(float).sum()
        except:
            gst_input_total = gst_applicable = gst_not_applicable = taxable_spend = 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div class='summary-card'>
                    <div class='summary-title'>Total GST Input</div>
                    <div class='summary-value'>₹ {gst_input_total:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class='summary-card'>
                    <div class='summary-title'>GST Applicable</div>
                    <div class='summary-value'>{gst_applicable}</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class='summary-card'>
                    <div class='summary-title'>GST Not Applicable</div>
                    <div class='summary-value'>{gst_not_applicable}</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class='summary-card'>
                    <div class='summary-title'>Taxable Spend</div>
                    <div class='summary-value'>₹ {taxable_spend:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)


        # --------------------------------------------------
        # MONTHLY EXPENSE — ALTAIR CHART
        # --------------------------------------------------
        # --------------------------------------------------
        # MONTHLY EXPENSE — ALTAIR CHART (FIXED)
        # --------------------------------------------------
        st.markdown("<br><div class='sub-header'>Monthly Expense Trend</div>", unsafe_allow_html=True)

        try:
            # Convert date column properly
            result_df["date"] = pd.to_datetime(result_df["date"])

            # Create monthly groups
            monthly = (
                result_df
                .groupby(result_df["date"].dt.to_period("M"))["amount"]
                .sum()
                .reset_index()
            )

            # Convert period → string for Altair
            monthly["month"] = monthly["date"].astype(str)

            # Altair chart
            chart = (
                alt.Chart(monthly)
                .mark_line(point=alt.OverlayMarkDef(filled=True, size=60))
                .encode(
                    x=alt.X("month:N", title="Month"),
                    y=alt.Y("amount:Q", title="Total Expense"),
                    tooltip=["month:N", alt.Tooltip("amount:Q", format=",.2f")]
                )
                .properties(height=380)
                .interactive()
            )

            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.warning(f"Unable to generate monthly chart: {e}")

        # --------------------------------------------------
        # DOWNLOAD FILES — with gradient buttons (using type="primary" for styling)
        # --------------------------------------------------
        st.markdown("<div class='sub-header'>Download Results</div>", unsafe_allow_html=True)

        buffer = io.BytesIO()
        result_df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        # The st.download_button is styled via the global CSS rule targeting primary buttons.
        st.download_button(
            label="Download Excel",
            data=buffer,
            file_name="taxbridge_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="excel_download",
            help="Download Excel",
            type="primary",
        )

        csv_data = result_df.to_csv(index=False).encode("utf-8")
        # The st.download_button is styled via the global CSS rule targeting primary buttons.
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="taxbridge_output.csv",
            mime="text/csv",
            use_container_width=True,
            key="csv_download",
            help="Download CSV",
            type="primary",
        )


# END MAIN CONTAINER
st.markdown("</div>", unsafe_allow_html=True)
