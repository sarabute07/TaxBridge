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
# GLOBAL CSS — CLEAN + MINIMAL
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

/* ----------------------------------------------
    NEW FIXES: Remove top padding/margin from main container
---------------------------------------------- */
div.main[data-testid="stAppViewBlockContainer"] {
    padding-top: 0 !important;
}

div.block-container {
    padding-top: 2rem !important;
    /* Adjusted padding top for the main block to be 2rem, but let's reset it here 
       if the app view container is still imposing a margin. */
}
/* ----------------------------------------------
    END NEW FIXES
---------------------------------------------- */


/* Main background + font */
body {
    background-color: #ffffff !important;
    font-family: 'Inter', sans-serif;
}

/* Main boxed layout */
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

/* Divider */
.divider {
    height: 1px;
    background-color: #dedede;
    margin: 18px 0 28px 0;
}

/* Sub-heading */
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

/* ----------------------------------------------
    FIX: Combined selector for st.button and st.download_button 
    to ensure consistent gradient and override Streamlit's default red/blue.
---------------------------------------------- */

div[data-testid="stButton"] button, 
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #e9f1ff, #c7dcff) !important;
    color: #1a1a1a !important; /* Ensure text is dark */
    border: 1px solid #b7cef5 !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    background-color: transparent !important; 
}

div[data-testid="stButton"] button:hover, 
div[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, #dbe8ff, #b4d0ff) !important;
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
    "Upload PDF, CSV, or Excel",
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

        st.markdown(f"<h3>Total Spend: ₹ {total_spend:,.2f}</h3>", unsafe_allow_html=True)


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
        st.markdown("<br><div class='sub-header'>Monthly Expense Trend</div>", unsafe_allow_html=True)

        try:
            result_df["date"] = pd.to_datetime(result_df["date"])
            # Ensure proper date-time conversion before grouping
            result_df['month_period'] = result_df["date"].dt.to_period("M")
            monthly = result_df.groupby('month_period')["amount"].sum()
            monthly = monthly.reset_index()
            # Convert Period back to string for Altair/JSON serialization
            monthly["date"] = monthly["month_period"].astype(str)

            chart = (
                alt.Chart(monthly)
                .mark_line(point=True, strokeWidth=2, color="#4c78a8") # Added color for better visibility
                .encode(
                    x=alt.X("date:N", title="Month"),
                    y=alt.Y("amount:Q", title="Total Expense"),
                    # Correct format string to " ,.2f" (D3 format for currency/comma separation)
                    tooltip=["date:N", alt.Tooltip("amount:Q", format=",.2f")]
                )
                .properties(height=380)
                .interactive() # Allow zooming/panning
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