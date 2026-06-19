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
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime

# ============================================================
# CONSTANTS
# ============================================================

REQUIRED_COLUMNS = [
    "order_id", "product_id", "customer_name", "country",
    "phone", "payment_mode", "transaction_date", "amount"
]

VALID_PAYMENT_MODES = ["UPI", "Card", "Cash", "Net Banking"]

BRAND_COLORS = ["#4F46E5", "#7C3AED", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Xeno Transaction Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1300px;
}

#MainMenu, footer {visibility: hidden;}

/* Hero header */
.xeno-hero {
    background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%);
    padding: 2.2rem 2.5rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 1.6rem;
    box-shadow: 0 10px 30px rgba(79, 70, 229, 0.25);
}
.xeno-hero h1 {
    color: white !important;
    font-weight: 800;
    font-size: 1.9rem;
    margin-bottom: 0.3rem;
}
.xeno-hero p {
    color: rgba(255,255,255,0.88);
    font-size: 1rem;
    margin: 0;
}

/* KPI cards */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.kpi-label {
    color: #6B7280;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.kpi-value {
    color: #1F2937;
    font-size: 1.7rem;
    font-weight: 800;
    margin-top: 0.2rem;
}

/* Status badge */
.status-badge {
    display: inline-block;
    padding: 0.45rem 1.1rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.88rem;
}

[data-testid="stMetric"] {
    border: 1px solid #E5E7EB;
    padding: 15px;
    border-radius: 12px;
    background: white;
}

[data-testid="stSidebar"] {
    background-color: #F9FAFB;
}

div[data-testid="stExpander"] {
    border: 1px solid #E5E7EB;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# PDF REPORT GENERATION
# ============================================================

def generate_pdf_report(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Xeno Transaction Intelligence Platform", styles["Title"]))
    content.append(Paragraph("Operational Data Quality Assessment Report", styles["Heading2"]))
    content.append(Paragraph(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    content.append(Spacer(1, 12))

    quality_score = results["quality_score"]
    status = "PASS" if quality_score >= 95 else "REVIEW REQUIRED" if quality_score >= 80 else "FAILED"

    summary_table = Table([
        ["Metric", "Value"],
        ["Dataset Status", status],
        ["Quality Score", f"{quality_score}%"],
        ["Total Records", results["total_records"]],
        ["Valid Records", results["valid_count"]],
        ["Invalid Records", results["invalid_count"]],
    ])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(Paragraph("Executive Summary", styles["Heading2"]))
    content.append(summary_table)
    content.append(Spacer(1, 15))

    findings_table = Table([
        ["Validation Check", "Count"],
        ["Invalid Phone Numbers", results["invalid_phone_count"]],
        ["Invalid Dates", results["invalid_date_count"]],
        ["Invalid Payment Modes", results["invalid_payment_count"]],
        ["Missing Values", results["missing_value_count"]],
    ])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(Paragraph("Validation Findings", styles["Heading2"]))
    content.append(findings_table)
    content.append(Spacer(1, 15))

    content.append(Paragraph("Key Business Insights", styles["Heading2"]))
    content.append(Paragraph(f"- Most transactions originate from {results['top_country']}", styles["Normal"]))
    content.append(Paragraph(f"- Most used payment mode is {results['top_payment']}", styles["Normal"]))
    content.append(Paragraph(f"- Average transaction value is Rs. {results['avg_amount']}", styles["Normal"]))
    content.append(Paragraph(f"- Data quality score is {quality_score}%", styles["Normal"]))

    risk_level = "LOW RISK" if quality_score >= 95 else "MEDIUM RISK" if quality_score >= 80 else "HIGH RISK"
    content.append(Paragraph("Risk Assessment", styles["Heading2"]))
    content.append(Paragraph(f"Risk Level: {risk_level}", styles["Normal"]))

    if quality_score >= 95:
        recommendation = "Dataset is suitable for downstream processing."
    elif quality_score >= 80:
        recommendation = "Review validation exceptions before processing."
    else:
        recommendation = "Dataset requires remediation before processing."
    content.append(Paragraph(f"Recommendation: {recommendation}", styles["Normal"]))
    content.append(Spacer(1, 15))

    content.append(Paragraph("Validation Exceptions (sample)", styles["Heading2"]))
    invalid_records_df = results["invalid_records_df"]
    sample_exceptions = invalid_records_df.head(5)
    exception_data = [["Order ID", "Failure Reason"]]
    for _, row in sample_exceptions.iterrows():
        exception_data.append([str(row["order_id"]), str(row["failure_reason"])])
    exception_table = Table(exception_data)
    exception_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(exception_table)
    content.append(Spacer(1, 15))
    content.append(Paragraph("Generated by Xeno Transaction Intelligence Platform", styles["Italic"]))

    doc.build(content)
    buffer.seek(0)
    return buffer


# ============================================================
# VALIDATION LOGIC
# ============================================================

@st.cache_data(show_spinner=False)
def load_csv(file):
    return pd.read_csv(file)


def validate_phone(phone, country):
    """Validate phone format. India/Singapore use strict length rules,
    any other country falls back to a sane generic digit-length check
    instead of being marked invalid by default."""
    phone = str(phone).strip()
    country = str(country).strip()
    country_rules = {"India": 10, "Singapore": 8}
    if country in country_rules:
        return phone.isdigit() and len(phone) == country_rules[country]
    return phone.isdigit() and 7 <= len(phone) <= 15


def run_validation(df_raw, valid_payment_modes):
    df = df_raw.copy()

    # Missing values measured on the original required columns only,
    # so the count isn't diluted/inflated by helper columns added below.
    missing_value_count = int(df[REQUIRED_COLUMNS].isnull().sum().sum())

    df["phone_valid"] = df.apply(
        lambda r: validate_phone(r["phone"], r["country"]), axis=1
    )

    parsed_dates = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["date_valid"] = parsed_dates.notna()

    df["payment_valid"] = df["payment_mode"].isin(valid_payment_modes)

    df["failure_reason"] = ""
    df.loc[~df["phone_valid"], "failure_reason"] += "Invalid Phone; "
    df.loc[~df["date_valid"], "failure_reason"] += "Invalid Date; "
    df.loc[~df["payment_valid"], "failure_reason"] += "Invalid Payment Mode; "

    invalid_phone_count = int((~df["phone_valid"]).sum())
    invalid_date_count = int((~df["date_valid"]).sum())
    invalid_payment_count = int((~df["payment_valid"]).sum())

    valid_mask = df["phone_valid"] & df["date_valid"] & df["payment_valid"]
    drop_cols = ["phone_valid", "date_valid", "payment_valid"]
    valid_records = df[valid_mask].drop(columns=drop_cols)
    invalid_records_df = df[~valid_mask].drop(columns=drop_cols)

    total_records = len(df)
    valid_count = len(valid_records)
    invalid_count = total_records - valid_count
    quality_score = round((valid_count / total_records) * 100, 2) if total_records else 0.0

    amount_numeric = pd.to_numeric(df["amount"], errors="coerce")

    if total_records:
        top_country = df["country"].value_counts().idxmax()
        top_payment = df["payment_mode"].value_counts().idxmax()
        india_percentage = round(((df["country"] == "India").sum() / total_records) * 100, 2)
    else:
        top_country, top_payment, india_percentage = "N/A", "N/A", 0.0

    avg_amount = round(amount_numeric.mean(), 2) if amount_numeric.notna().any() else 0.0

    return {
        "df": df,
        "valid_records": valid_records,
        "invalid_records_df": invalid_records_df,
        "total_records": total_records,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "quality_score": quality_score,
        "invalid_phone_count": invalid_phone_count,
        "invalid_date_count": invalid_date_count,
        "invalid_payment_count": invalid_payment_count,
        "missing_value_count": missing_value_count,
        "top_country": top_country,
        "top_payment": top_payment,
        "avg_amount": avg_amount,
        "india_percentage": india_percentage,
        "amount_numeric": amount_numeric,
        "parsed_dates": parsed_dates,
    }


# ============================================================
# UI: SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🚀 Xeno Platform")
    st.caption("Transaction Validation & Intelligence — v1.1")
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    chunk_size = st.number_input("Chunk Size", min_value=10, value=100, step=10)
    st.markdown("---")
    with st.expander("ℹ️ About this tool"):
        st.write(
            "Upload a transaction CSV to validate phone numbers, dates and "
            "payment modes against business rules, explore analytics, and "
            "export clean data plus a PDF audit report."
        )
    with st.expander("📋 Required columns"):
        st.code("\n".join(REQUIRED_COLUMNS))

# ============================================================
# UI: HERO HEADER
# ============================================================

st.markdown("""
<div class="xeno-hero">
    <h1>🚀 Xeno Transaction Intelligence Platform</h1>
    <p>Enterprise-grade transaction validation, quality monitoring and reporting for operational datasets.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader("📁 Upload Transaction CSV", type=["csv"])

if uploaded_file is not None:
    st.sidebar.success("✅ Dataset Uploaded")

    df_raw = load_csv(uploaded_file)

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df_raw.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.stop()

    with st.expander("📄 Dataset Preview", expanded=True):
        st.dataframe(df_raw.head(), use_container_width=True)
        st.caption(f"{len(df_raw):,} rows × {len(df_raw.columns)} columns")

    col_a, _ = st.columns([1, 4])
    with col_a:
        validate_clicked = st.button("🔍 Validate Dataset", type="primary", use_container_width=True)

    # A unique fingerprint for this exact upload (name + size). Used so the
    # dashboard below is rebuilt only when a NEW file is uploaded, but
    # otherwise survives reruns triggered by download buttons / widgets.
    current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"

    if validate_clicked:
        with st.spinner("Validating dataset..."):
            st.session_state["xeno_results"] = run_validation(df_raw, VALID_PAYMENT_MODES)
            st.session_state["xeno_file_id"] = current_file_id

    has_results = (
        "xeno_results" in st.session_state
        and st.session_state.get("xeno_file_id") == current_file_id
    )

    if has_results:
        results = st.session_state["xeno_results"]

        total_records = results["total_records"]
        valid_count = results["valid_count"]
        invalid_count = results["invalid_count"]
        quality_score = results["quality_score"]

        if quality_score >= 95:
            status_label, status_color, status_bg = "PASS", "#15803D", "#DCFCE7"
        elif quality_score >= 80:
            status_label, status_color, status_bg = "REVIEW REQUIRED", "#B45309", "#FEF3C7"
        else:
            status_label, status_color, status_bg = "FAILED", "#B91C1C", "#FEE2E2"

        st.markdown(
            f'<span class="status-badge" style="background:{status_bg}; color:{status_color};">'
            f'{status_label}</span>',
            unsafe_allow_html=True
        )
        st.write("")

        # ---------------- KPI ROW ----------------
        k1, k2, k3, k4 = st.columns(4)
        for col, label, value in [
            (k1, "Total Records", f"{total_records:,}"),
            (k2, "Valid Records", f"{valid_count:,}"),
            (k3, "Invalid Records", f"{invalid_count:,}"),
            (k4, "Quality Score", f"{quality_score}%"),
        ]:
            with col:
                st.markdown(
                    f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                    f'<div class="kpi-value">{value}</div></div>',
                    unsafe_allow_html=True
                )

        st.write("")
        st.progress(min(quality_score / 100, 1.0))
        st.write("")

        tab_summary, tab_validation, tab_analytics, tab_records, tab_export = st.tabs(
            ["📋 Summary", "⚠️ Validation", "📈 Analytics", "🗂 Records", "📥 Export"]
        )

        # ---------------- SUMMARY TAB ----------------
        with tab_summary:
            if quality_score >= 95:
                st.success("Dataset Status: PASS ✅ — Ready for downstream processing.")
            elif quality_score >= 80:
                st.warning("Dataset Status: REVIEW REQUIRED ⚠️ — Minor issues detected.")
            else:
                st.error("Dataset Status: FAILED ❌ — Significant data quality issues found.")

            st.markdown("#### AI Insights")
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"🌍 Most transactions originate from **{results['top_country']}**.")
                st.info(f"💳 Most used payment mode is **{results['top_payment']}**.")
            with c2:
                st.info(f"💰 Average transaction value is **₹{results['avg_amount']}**.")
                st.info(f"🇮🇳 India contributes **{results['india_percentage']}%** of total transactions.")

            if quality_score < 90:
                st.warning("Data quality issues detected. Review invalid records before processing.")

        # ---------------- VALIDATION TAB ----------------
        with tab_validation:
            st.markdown("#### Validation Findings")
            v1, v2, v3, v4 = st.columns(4)
            v1.metric("📱 Invalid Phones", results["invalid_phone_count"])
            v2.metric("📅 Invalid Dates", results["invalid_date_count"])
            v3.metric("💳 Invalid Payment Modes", results["invalid_payment_count"])
            v4.metric("❗ Missing Values", results["missing_value_count"])

            st.markdown("#### Risk Assessment")
            risk_level = (
                "LOW RISK" if quality_score >= 95
                else "MEDIUM RISK" if quality_score >= 80
                else "HIGH RISK"
            )
            st.write(f"**Risk Level:** {risk_level}")

        # ---------------- ANALYTICS TAB ----------------
        with tab_analytics:
            df_full = results["df"]

            country_df = df_full["country"].value_counts().reset_index()
            country_df.columns = ["Country", "Count"]
            country_chart = px.bar(
                country_df, x="Country", y="Count", title="Country Distribution",
                color_discrete_sequence=BRAND_COLORS, template="plotly_white"
            )
            country_chart.update_layout(font_family="Inter")
            st.plotly_chart(country_chart, use_container_width=True)

            payment_chart = px.pie(
                df_full, names="payment_mode", title="Payment Mode Distribution",
                color_discrete_sequence=BRAND_COLORS, template="plotly_white", hole=0.45
            )
            payment_chart.update_layout(font_family="Inter")
            st.plotly_chart(payment_chart, use_container_width=True)

            amount_df = df_full.assign(amount_numeric=results["amount_numeric"])
            amount_chart = px.histogram(
                amount_df, x="amount_numeric", title="Transaction Amount Distribution",
                color_discrete_sequence=BRAND_COLORS, template="plotly_white"
            )
            amount_chart.update_layout(font_family="Inter", xaxis_title="Amount")
            st.plotly_chart(amount_chart, use_container_width=True)

            trend_df = pd.DataFrame({"transaction_date": results["parsed_dates"]}).dropna()
            trend_df = trend_df.groupby("transaction_date").size().reset_index(name="Transactions")
            trend_chart = px.line(
                trend_df, x="transaction_date", y="Transactions", title="Transaction Trend",
                color_discrete_sequence=BRAND_COLORS, template="plotly_white"
            )
            trend_chart.update_layout(font_family="Inter")
            st.plotly_chart(trend_chart, use_container_width=True)

        # ---------------- RECORDS TAB ----------------
        with tab_records:
            st.markdown("#### ❌ Invalid Records")
            st.caption("Failure reasons are provided for each invalid record.")
            st.dataframe(results["invalid_records_df"], use_container_width=True)

            st.markdown("#### ✅ Clean Records")
            st.dataframe(results["valid_records"], use_container_width=True)

        # ---------------- EXPORT TAB ----------------
        with tab_export:
            st.markdown("#### 📥 Export Center")

            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                st.download_button(
                    "⬇ Clean CSV",
                    results["valid_records"].to_csv(index=False),
                    "cleaned_transactions.csv",
                    "text/csv",
                    use_container_width=True,
                    key="dl_clean_csv"
                )
            with ec2:
                st.download_button(
                    "⬇ Invalid Records CSV",
                    results["invalid_records_df"].to_csv(index=False),
                    "invalid_transactions.csv",
                    "text/csv",
                    use_container_width=True,
                    key="dl_invalid_csv"
                )
            with ec3:
                pdf_buffer = generate_pdf_report(results)
                st.download_button(
                    "⬇ PDF Report",
                    data=pdf_buffer,
                    file_name=f"Xeno_Data_Quality_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf_report"
                )

            st.markdown("---")
            st.markdown("#### 🗂 CSV Chunking")

            valid_records = results["valid_records"]
            if len(valid_records) > chunk_size:
                n_chunks = int(np.ceil(len(valid_records) / chunk_size))
                chunks = np.array_split(valid_records, n_chunks)
                st.caption(f"Split into {n_chunks} chunk(s) of up to {chunk_size} records each.")
                cols = st.columns(3)
                for i, chunk in enumerate(chunks):
                    with cols[i % 3]:
                        st.download_button(
                            f"Chunk {i + 1} ({len(chunk)} rows)",
                            chunk.to_csv(index=False),
                            f"chunk_{i + 1}.csv",
                            "text/csv",
                            use_container_width=True,
                            key=f"dl_chunk_{i}"
                        )
            else:
                st.success(f"No chunking required. Dataset contains only {len(valid_records)} valid records.")

else:
    st.info("👋 Upload a transaction CSV file above to begin.")

st.markdown(
    "<p style='text-align:center; color:#9CA3AF; font-size:0.8rem; margin-top:2rem;'>"
    "Xeno Transaction Intelligence Platform · Internal Tool</p>",
    unsafe_allow_html=True
)
