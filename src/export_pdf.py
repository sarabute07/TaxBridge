from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime

def generate_pdf_report(df, file_path="taxbridge_report.pdf"):
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30
    )

    elements = []

    # ----------------------------
    # Title
    # ----------------------------
    title = Paragraph("TaxBridge — Expense Summary Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # ----------------------------
    # Date
    # ----------------------------
    date = Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y')}", normal_style)
    elements.append(date)
    elements.append(Spacer(1, 20))

    # ----------------------------
    # Summary Numbers
    # ----------------------------
    total_exp = df["amount"].sum()
    total_gst = df["gst_input"].sum()
    total_deductible = df["deductible"].sum()

    summary_data = [
        ["Total Expense", f"₹ {total_exp:,.2f}"],
        ["GST Input Credit", f"₹ {total_gst:,.2f}"],
        ["Deductible Transactions", str(total_deductible)]
    ]

    summary_table = Table(summary_data, colWidths=[180, 180])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E8EEF9")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # ----------------------------
    # Detailed table
    # ----------------------------
    table_data = [
        ["Date", "Description", "Amount", "Category", "GST %", "GST Input", "Deductible"]
    ]

    for _, row in df.iterrows():
        table_data.append([
            row["date"],
            row["description"],
            f"₹ {row['amount']}",
            row["predicted_category"].capitalize(),
            str(row["gst_rate"]),
            f"₹ {row['gst_input']}",
            "Yes" if row["deductible"] == 1 else "No"
        ])

    detail_table = Table(table_data, colWidths=[70, 160, 60, 75, 50, 70, 60])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E3F2FD")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
    ]))

    elements.append(detail_table)

    # Build the PDF
    doc.build(elements)

    return file_path
