import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

# ----------------------------
# PAGE CONFIG
# ----------------------------

st.set_page_config(
    page_title="Xeno Transaction Intelligence Platform",
    page_icon="🚀",
    layout="wide"
)
st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
}

h1 {
    color: #1f2937;
}

[data-testid="stMetric"] {
    border: 1px solid #e5e7eb;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)
def generate_pdf_report(
    total_records,
    valid_count,
    invalid_count,
    quality_score,
    invalid_phone_count,
    invalid_date_count,
    invalid_payment_count,
    missing_value_count,
    top_country,
    top_payment,
    avg_amount,
    invalid_records_df
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    title = Paragraph(
        "Xeno Transaction Intelligence Platform",
        styles["Title"]
    )

    content.append(title)

    content.append(
        Paragraph(
            "Operational Data Quality Assessment Report",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"Generated On: {datetime.now()}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 12))

    summary_table = Table([
        ["Metric", "Value"],
        ["Dataset Status",
         "PASS" if quality_score >= 95
         else "REVIEW REQUIRED" if quality_score >= 80
         else "FAILED"],
        ["Quality Score", f"{quality_score}%"],
        ["Total Records", total_records],
        ["Valid Records", valid_count],
        ["Invalid Records", invalid_count]
    ])

    summary_table.setStyle(
        TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ])
    )

    content.append(
        Paragraph(
            "Executive Summary",
            styles["Heading2"]
        )
    )

    content.append(summary_table)

    content.append(Spacer(1, 15))

    findings_table = Table([
        ["Validation Check", "Count"],
        ["Invalid Phone Numbers", invalid_phone_count],
        ["Invalid Dates", invalid_date_count],
        ["Invalid Payment Modes", invalid_payment_count],
        ["Missing Values", missing_value_count]
    ])

    findings_table.setStyle(
        TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ])
    )

    content.append(
        Paragraph(
            "Validation Findings",
            styles["Heading2"]
        )
    )

    content.append(findings_table)

    content.append(Spacer(1, 15))

    content.append(
        Paragraph(
            "Key Business Insights",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"• Most transactions originate from {top_country}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"• Most used payment mode is {top_payment}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"• Average transaction value is ₹{avg_amount}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"• Data quality score is {quality_score}%",
            styles["Normal"]
        )
    )
    risk_level = (
        "LOW RISK"
        if quality_score >= 95
        else "MEDIUM RISK"
        if quality_score >= 80
        else "HIGH RISK"
    )

    content.append(
        Paragraph(
            "Risk Assessment",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"Risk Level: {risk_level}",
            styles["Normal"]
        )
    )

    if quality_score >= 95:
        recommendation = "Dataset is suitable for downstream processing."

    elif quality_score >= 80:
        recommendation = "Review validation exceptions before processing."

    else:
        recommendation = "Dataset requires remediation before processing."

    content.append(
        Paragraph(
            f"Recommendation: {recommendation}",
            styles["Normal"]
        )
    )


    content.append(Spacer(1, 15))

    content.append(
        Paragraph(
            "Validation Exceptions",
            styles["Heading2"]
        )
    )

    sample_exceptions = invalid_records_df.head(5)

    exception_data = [["Order ID", "Failure Reason"]]

    for _, row in sample_exceptions.iterrows():

        exception_data.append([
            str(row["order_id"]),
            str(row["failure_reason"])
        ])

    exception_table = Table(exception_data)

    exception_table.setStyle(
        TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ])
    )

    content.append(exception_table)

    content.append(Spacer(1, 15))

    content.append(
        Paragraph(
            "Generated by Xeno Transaction Intelligence Platform",
            styles["Italic"]
        )
    )

    doc.build(content)

    buffer.seek(0)

    return buffer
# ----------------------------
# SIDEBAR
# ----------------------------


st.sidebar.markdown("---")

st.sidebar.header("⚙️ Settings")

chunk_size = st.sidebar.number_input(
    "Chunk Size",
    min_value=10,
    value=100,
    step=10
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
Transaction Validation & Intelligence

Version 1.0
""")
# ----------------------------
# HEADER
# ----------------------------

st.title("Xeno Transaction Intelligence Platform")
st.markdown("""
---
""")
st.markdown("""
Enterprise-grade transaction validation, quality monitoring,
and reporting platform for operational datasets.
""")

# ----------------------------
# FILE UPLOAD
# ----------------------------

uploaded_file = st.file_uploader(
    "Upload Transaction CSV",
    type=["csv"]
)
st.sidebar.title("Xeno Platform")

if uploaded_file is not None:
    st.sidebar.success("Dataset Uploaded")

# ----------------------------
# MAIN APP
# ----------------------------

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    required_columns = [
        "order_id",
        "product_id",
        "customer_name",
        "country",
        "phone",
        "payment_mode",
        "transaction_date",
        "amount"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        st.error(
            f"Missing Required Columns: {', '.join(missing_columns)}"
        )
        st.stop()

    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head())

    validate = st.button("🔍 Validate Dataset")

    if validate:

        valid_payment_modes = [
            "UPI",
            "Card",
            "Cash",
            "Net Banking"
        ]

        df["phone_valid"] = True
        df["date_valid"] = True
        df["payment_valid"] = True
        df["failure_reason"] = ""

        invalid_phone_count = 0
        invalid_date_count = 0
        invalid_payment_count = 0

        # ----------------------------
        # VALIDATION
        # ----------------------------

        for index, row in df.iterrows():

            phone = str(row["phone"])
            country = str(row["country"])

            phone_ok = False

            if country == "India":
                phone_ok = (
                    len(phone) == 10
                    and phone.isdigit()
                )

            elif country == "Singapore":
                phone_ok = (
                    len(phone) == 8
                    and phone.isdigit()
                )

            if not phone_ok:
                df.at[index, "phone_valid"] = False
                df.at[index, "failure_reason"] += "Invalid Phone; "
                invalid_phone_count += 1

            try:
                pd.to_datetime(row["transaction_date"])
            except:
                df.at[index, "date_valid"] = False
                df.at[index, "failure_reason"] += "Invalid Date; "
                invalid_date_count += 1

            if row["payment_mode"] not in valid_payment_modes:
                df.at[index, "payment_valid"] = False
                df.at[index, "failure_reason"] += "Invalid Payment Mode; "
                invalid_payment_count += 1

        missing_value_count = int(
            df.isnull().sum().sum()
        )

        valid_records = df[
            (df["phone_valid"])
            &
            (df["date_valid"])
            &
            (df["payment_valid"])
        ]

        invalid_records_df = df[
            (~df["phone_valid"])
            |
            (~df["date_valid"])
            |
            (~df["payment_valid"])
        ]

        total_records = len(df)

        valid_count = len(valid_records)

        invalid_count = total_records - valid_count

        quality_score = round(
            (valid_count / total_records) * 100,
            2
        )

        # ----------------------------
        # DASHBOARD
        # ----------------------------

        st.subheader("📊 Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Records",
            total_records
        )

        col2.metric(
            "Valid Records",
            valid_count
        )

        col3.metric(
            "Invalid Records",
            invalid_count
        )

        col4.metric(
            "Quality Score",
            f"{quality_score}%"
        )

        st.progress(quality_score / 100)
        
        st.subheader("📋 Executive Summary")

        if quality_score >= 95:
            st.success(
                "Dataset Status: PASS ✅\n\nReady for downstream processing."
            )

        elif quality_score >= 80:
            st.warning(
                "Dataset Status: REVIEW REQUIRED ⚠️\n\nMinor issues detected."
            )

        else:
            st.error(
                "Dataset Status: FAILED ❌\n\nSignificant data quality issues found."
            )
        # ----------------------------
        # VALIDATION SUMMARY
        # ----------------------------

        st.subheader("⚠ Validation Summary")

        st.write(
            f"📱 Invalid Phones: {invalid_phone_count}"
        )

        st.write(
            f"📅 Invalid Dates: {invalid_date_count}"
        )

        st.write(
            f"💳 Invalid Payment Modes: {invalid_payment_count}"
        )

        st.write(
            f"❗ Missing Values: {missing_value_count}"
        )

        # ----------------------------
        # AI INSIGHTS
        # ----------------------------

        st.subheader("AI Insights")

        top_country = (
            df["country"]
            .value_counts()
            .idxmax()
        )

        st.success(
            f"Most transactions originate from {top_country}."
        )

        top_payment = (
            df["payment_mode"]
            .value_counts()
            .idxmax()
        )

        st.info(
            f"Most used payment mode is {top_payment}."
        )

        avg_amount = round(
            pd.to_numeric(
                df["amount"],
                errors="coerce"
            ).mean(),
            2
        )

        st.info(
            f"Average transaction value is ₹{avg_amount}."
        )

        if quality_score < 90:
            st.warning(
                "Data quality issues detected. Review invalid records before processing."
            )
        india_percentage = round(
            ((df["country"] == "India").sum() / len(df)) * 100,2)

        st.info(
            f"India contributes {india_percentage}% of total transactions.")

        st.info(
            f"Current data quality score is {quality_score}%."
     )
        # ----------------------------
        # ANALYTICS
        # ----------------------------

        st.subheader("📈 Analytics")

        country_df = (
            df["country"]
            .value_counts()
            .reset_index()
        )

        country_df.columns = [
            "Country",
            "Count"
        ]

        country_chart = px.bar(
            country_df,
            x="Country",
            y="Count",
            title="Country Distribution"
        )

        st.plotly_chart(
            country_chart,
            use_container_width=True
        )

        payment_chart = px.pie(
            df,
            names="payment_mode",
            title="Payment Mode Distribution"
        )

        st.plotly_chart(
            payment_chart,
            use_container_width=True
        )

        amount_chart = px.histogram(
            df,
            x="amount",
            title="Transaction Amount Distribution"
        )

        st.plotly_chart(
            amount_chart,
            use_container_width=True
        )
        st.subheader("📅 Transaction Trend")

        trend_df = df.copy()

        trend_df["transaction_date"] = pd.to_datetime(
            trend_df["transaction_date"],
            errors="coerce"
        )

        trend_df = (
            trend_df.groupby("transaction_date")
            .size()
            .reset_index(name="Transactions")
        )

        trend_chart = px.line(
            trend_df,
            x="transaction_date",
            y="Transactions",
            title="Transaction Trend"
        )

        st.plotly_chart(
            trend_chart,
            use_container_width=True
        )
        # ----------------------------
        # INVALID RECORDS
        # ----------------------------

        st.subheader("❌ Invalid Records")
        st.caption(
            "Failure reasons are provided for each invalid record."
        )
        st.dataframe(
            invalid_records_df,
            use_container_width=True
        )

        # ----------------------------
        # VALID RECORDS
        # ----------------------------

        st.subheader("✅ Clean Records")

        st.dataframe(
            valid_records,
            use_container_width=True
        )

        # ----------------------------
        # DOWNLOADS
        # ----------------------------

        st.subheader("📥 Export Center")

        clean_csv = valid_records.to_csv(
            index=False
        )

        st.download_button(
            "⬇ Download Clean CSV",
            clean_csv,
            "cleaned_transactions.csv",
            "text/csv"
        )

        invalid_csv = invalid_records_df.to_csv(
            index=False
        )

        st.download_button(
            "⬇ Download Invalid Records",
            invalid_csv,
            "invalid_transactions.csv",
            "text/csv"
        )

        

        pdf_buffer = generate_pdf_report(
            total_records,
            valid_count,
            invalid_count,
            quality_score,
            invalid_phone_count,
            invalid_date_count,
            invalid_payment_count,
            missing_value_count,
            top_country,
            top_payment,
            avg_amount,
            invalid_records_df
        )

        st.download_button(
            "Download Validation Report (PDF)",
            data=pdf_buffer,
            file_name=f"Xeno_Data_Quality_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

        # ----------------------------
        # CHUNKING
        # ----------------------------

        st.subheader("🗂 CSV Chunking")

        if len(valid_records) > chunk_size:

            chunks = np.array_split(
                valid_records,
                int(
                    np.ceil(
                        len(valid_records)
                        / chunk_size
                    )
                )
            )

            for i, chunk in enumerate(chunks):

                chunk_csv = chunk.to_csv(
                    index=False
                )

                st.download_button(
                    f"Download Chunk {i+1}",
                    chunk_csv,
                    f"chunk_{i+1}.csv",
                    "text/csv"
                )

        else:
            st.success(
                f"No chunking required. Dataset contains only {len(valid_records)} valid records."
            )