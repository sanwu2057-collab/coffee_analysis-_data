import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime  # <--- Essential for the time fix

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Afficionado Coffee Analytics Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fa;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 2px solid #38bdf8;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    }
    div[data-testid="metric-container"] label {
        color: #facc15 !important;
        font-size: 17px !important;
        font-weight: bold;
    }
    div[data-testid="metric-container"] div {
        color: white !important;
        font-size: 28px !important;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TITLE
# =========================================================

st.title("☕ Afficionado Coffee Roasters Dashboard")
st.markdown("### Product Optimization & Revenue Contribution Analytics")

# =========================================================
# LOAD DATA FUNCTION (REPAIRED)
# =========================================================

@st.cache_data
def load_data(uploaded_file):
    """Load data from uploaded file (CSV, XLSX, or ZIP)"""
    
    try:
        file_name = uploaded_file.name
        file_ext = file_name.split('.')[-1].lower()
        
        # 1. Read the file
        if file_ext == "zip":
            with zipfile.ZipFile(uploaded_file, "r") as z:
                data_file = next((f for f in z.namelist() if f.endswith((".csv", ".xlsx"))), None)
                if not data_file:
                    st.error("❌ No CSV or XLSX found in ZIP.")
                    st.stop()
                with z.open(data_file) as f:
                    if data_file.endswith(".csv"):
                        df = pd.read_csv(f)
                    else:
                        df = pd.read_excel(io.BytesIO(f.read()), engine="openpyxl")
        
        elif file_ext == "csv":
            df = pd.read_csv(uploaded_file)
        
        elif file_ext == "xlsx":
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        
        else:
            st.error("❌ Unsupported file format.")
            st.stop()

        # 2. THE FIX: Handle Excel datetime.time objects
        # We convert 'time' objects to strings so pd.to_datetime can process them
        if "transaction_time" in df.columns:
            df["transaction_time"] = df["transaction_time"].apply(
                lambda x: x.strftime('%H:%M:%S') if isinstance(x, datetime.time) else x
            )
        
        # 3. VALIDATE REQUIRED COLUMNS
        required_columns = [
            "product_category", "product_type", "product_detail",
            "transaction_qty", "unit_price", "transaction_time",
            "store_location", "product_id"
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            st.stop()
        
        # 4. CREATE DERIVED COLUMNS
        df["Revenue"] = df["transaction_qty"] * df["unit_price"]
        
        # Safe conversion to datetime, then extract hour
        df["Hour"] = pd.to_datetime(df["transaction_time"], errors='coerce').dt.hour
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.stop()

# =========================================================
# SIDEBAR FILE UPLOAD
# =========================================================

st.sidebar.header("📁 Data Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload your coffee sales data",
    type=["csv", "xlsx", "zip"],
    help="Upload CSV, XLSX, or ZIP file"
)

# =========================================================
# LOAD AND DISPLAY DASHBOARD
# =========================================================

if uploaded_file is None:
    st.info("📤 Please upload a data file to get started!")
    st.stop()

with st.spinner("📊 Loading and processing data..."):
    df = load_data(uploaded_file)

st.success("✅ Data loaded successfully!")

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Dashboard Filters")

category_filter = st.sidebar.multiselect(
    "Select Product Category",
    options=sorted(df["product_category"].dropna().unique()),
    default=sorted(df["product_category"].dropna().unique())
)

store_filter = st.sidebar.multiselect(
    "Select Store Location",
    options=sorted(df["store_location"].dropna().unique()),
    default=sorted(df["store_location"].dropna().unique())
)

product_type_filter = st.sidebar.multiselect(
    "Select Product Type",
    options=sorted(df["product_type"].dropna().unique()),
    default=sorted(df["product_type"].dropna().unique())
)

top_n = st.sidebar.slider("Top N Products", 5, 25, 10)

# Filter Logic
filtered_df = df[
    (df["product_category"].isin(category_filter)) &
    (df["store_location"].isin(store_filter)) &
    (df["product_type"].isin(product_type_filter))
]

# =========================================================
# KPIs
# =========================================================

st.markdown("---")
st.subheader("📊 Key Performance Indicators")

if not filtered_df.empty:
    total_revenue = filtered_df["Revenue"].sum()
    total_sales = filtered_df["transaction_qty"].sum()
    unique_products = filtered_df["product_id"].nunique()
    avg_price = filtered_df["unit_price"].mean()
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
    k2.metric("🛒 Sales Volume", f"{total_sales:,.0f}")
    k3.metric("📦 Unique Products", unique_products)
    k4.metric("💵 Avg Unit Price", f"${avg_price:.2f}")

    # =========================================================
    # VISUALIZATIONS
    # =========================================================

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Revenue Share by Category")
        category_rev = filtered_df.groupby("product_category")["Revenue"].sum().reset_index()
        fig1 = px.pie(category_rev, names="product_category", values="Revenue", hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("Top Products by Revenue")
        revenue_products = filtered_df.groupby("product_detail")["Revenue"].sum().sort_values(ascending=False).head(top_n).reset_index()
        fig2 = px.bar(revenue_products, x="product_detail", y="Revenue", color="Revenue")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("Hourly Revenue Trend")
    hourly_df = filtered_df.groupby("Hour")["Revenue"].sum().reset_index()
    fig3 = px.line(hourly_df, x="Hour", y="Revenue", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

    # =========================================================
    # DATA TABLE
    # =========================================================

    st.markdown("---")
    st.subheader("Detailed Performance Table")
    st.dataframe(filtered_df.head(100), use_container_width=True)
else:
    st.warning("⚠️ No data matches the selected filters.")
