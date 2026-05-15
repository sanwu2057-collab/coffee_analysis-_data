import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



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
# LOAD DATA FUNCTION
# =========================================================

@st.cache_data

def load_data(uploaded_file):
    """Load data from uploaded file (CSV, XLSX, or ZIP)"""
    
    try:
        # Get file extension
        file_name = uploaded_file.name
        file_ext = file_name.split('.')[-1].lower()
        
        # Case 1: ZIP archive
        if file_ext == "zip":
            if not zipfile.is_zipfile(uploaded_file):
                st.error("❌ Provided file is not a valid ZIP file.")
                st.stop()
            
            with zipfile.ZipFile(uploaded_file, "r") as z:
                file_list = z.namelist()
                data_file = None
                
                # Find first CSV or XLSX inside
                for file in file_list:
                    if file.endswith(".csv") or file.endswith(".xlsx"):
                        data_file = file
                        break
                
                if data_file is None:
                    st.error("❌ No CSV or XLSX file found inside ZIP.")
                    st.stop()
                
                with z.open(data_file) as f:
                    if data_file.endswith(".csv"):
                        df = pd.read_csv(f)
                    else:
                        df = pd.read_excel(io.BytesIO(f.read()), engine="openpyxl")
        
        # Case 2: CSV directly
        elif file_ext == "csv":
            df = pd.read_csv(uploaded_file)
        
        # Case 3: Excel directly
        elif file_ext == "xlsx":
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        
        else:
            st.error("❌ Unsupported file format. Use .zip, .csv, or .xlsx")
            st.stop()
        
        # =====================================================
        # VALIDATE REQUIRED COLUMNS
        # =====================================================
        required_columns = [
            "product_category", "product_type", "product_detail",
            "transaction_qty", "unit_price", "transaction_time",
            "store_location", "product_id"
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            st.error(f"Your file has these columns: {', '.join(df.columns.tolist())}")
            st.stop()
        
        # =====================================================
        # CREATE REQUIRED COLUMNS
        # =====================================================
        df["Revenue"] = df["transaction_qty"] * df["unit_price"]
        df["Hour"] = pd.to_datetime(df["transaction_time"]).dt.hour
        
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
    help="Upload CSV, XLSX, or ZIP file with your coffee sales data"
)

# =========================================================
# LOAD AND DISPLAY DASHBOARD
# =========================================================

if uploaded_file is None:
    st.info("📤 Please upload a data file to get started!")
    st.markdown("""
    ### Expected File Format:
    Your data file should contain these columns:
    - `product_category` - Category of the product
    - `product_type` - Type of product
    - `product_detail` - Detailed product name
    - `transaction_qty` - Quantity sold
    - `unit_price` - Price per unit
    - `transaction_time` - Timestamp of transaction
    - `store_location` - Store location
    - `product_id` - Product identifier
    """)
    st.stop()

# Load data
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

top_n = st.sidebar.slider(
    "Top N Products",
    min_value=5,
    max_value=25,
    value=10
)

# =========================================================
# FILTER DATA
# =========================================================

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

total_revenue = filtered_df["Revenue"].sum()
total_sales = filtered_df["transaction_qty"].sum()
unique_products = filtered_df["product_id"].nunique()
avg_price = filtered_df["unit_price"].mean()
avg_revenue = filtered_df["Revenue"].mean()

top_category = (
    filtered_df.groupby("product_category")["Revenue"]
    .sum()
    .idxmax()
)

revenue_concentration = (
    filtered_df.groupby("product_detail")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

revenue_concentration_ratio = (
    revenue_concentration.head(10).sum()
    / revenue_concentration.sum()
) * 100

product_efficiency_score = (
    total_revenue / unique_products if unique_products > 0 else 0
)

k1, k2, k3, k4 = st.columns(4)
k5, k6, k7, k8 = st.columns(4)

k1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
k2.metric("🛒 Total Sales Volume", f"{total_sales:,.0f}")
k3.metric("📦 Unique Products", unique_products)
k4.metric("💵 Avg Unit Price", f"${avg_price:.2f}")

k5.metric("📈 Avg Transaction Revenue", f"${avg_revenue:.2f}")
k6.metric("⚠️ Revenue Concentration", f"{revenue_concentration_ratio:.2f}%")
k7.metric("⭐ Product Efficiency", f"${product_efficiency_score:.2f}")
k8.metric("🏆 Top Category", top_category)

# =========================================================
# CATEGORY REVENUE PIE
# =========================================================

st.markdown("---")
st.subheader("Revenue Share by Product Category")

category_rev = (
    filtered_df.groupby("product_category")["Revenue"]
    .sum()
    .reset_index()
)

fig1 = px.pie(
    category_rev,
    names="product_category",
    values="Revenue",
    hole=0.45,
    title="Category Revenue Distribution"
)

st.plotly_chart(fig1, use_container_width=True)

# =========================================================
# TOP PRODUCTS BY REVENUE
# =========================================================

st.markdown("---")
st.subheader("Top Products by Revenue")

revenue_products = (
    filtered_df.groupby("product_detail")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)

fig2 = px.bar(
    revenue_products,
    x="product_detail",
    y="Revenue",
    color="Revenue",
    text_auto=True,
    title="Top Revenue Generating Products"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# TOP PRODUCTS BY VOLUME
# =========================================================

st.markdown("---")
st.subheader("Top Products by Sales Volume")

volume_products = (
    filtered_df.groupby("product_detail")["transaction_qty"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)

fig3 = px.bar(
    volume_products,
    x="product_detail",
    y="transaction_qty",
    color="transaction_qty",
    text_auto=True,
    title="Most Popular Products"
)

st.plotly_chart(fig3, use_container_width=True)

# =========================================================
# SCATTER PLOT
# =========================================================

st.markdown("---")
st.subheader("Popularity vs Revenue Analysis")

scatter_df = (
    filtered_df.groupby("product_detail")
    .agg({
        "transaction_qty": "sum",
        "Revenue": "sum"
    })
    .reset_index()
)

fig4 = px.scatter(
    scatter_df,
    x="transaction_qty",
    y="Revenue",
    hover_name="product_detail",
    size="Revenue",
    color="Revenue",
    title="Popularity vs Revenue"
)

st.plotly_chart(fig4, use_container_width=True)

# =========================================================
# PARETO ANALYSIS
# =========================================================

st.markdown("---")
st.subheader("Pareto Analysis (80/20 Rule)")

pareto_df = (
    filtered_df.groupby("product_detail")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

pareto_df["Cumulative Revenue"] = (
    pareto_df["Revenue"].cumsum()
)

pareto_df["Cumulative Percentage"] = (
    pareto_df["Cumulative Revenue"] /
    pareto_df["Revenue"].sum()
) * 100

fig5 = make_subplots(specs=[[{"secondary_y": True}]])

fig5.add_trace(
    go.Bar(
        x=pareto_df["product_detail"],
        y=pareto_df["Revenue"],
        name="Revenue"
    ),
    secondary_y=False
)

fig5.add_trace(
    go.Scatter(
        x=pareto_df["product_detail"],
        y=pareto_df["Cumulative Percentage"],
        mode="lines+markers",
        name="Cumulative %"
    ),
    secondary_y=True
)

fig5.update_layout(
    title="Pareto Revenue Analysis"
)

st.plotly_chart(fig5, use_container_width=True)

# =========================================================
# HOURLY REVENUE TREND
# =========================================================

st.markdown("---")
st.subheader("Hourly Revenue Trend")

hourly_df = (
    filtered_df.groupby("Hour")["Revenue"]
    .sum()
    .reset_index()
)

fig6 = px.line(
    hourly_df,
    x="Hour",
    y="Revenue",
    markers=True,
    title="Revenue by Hour"
)

st.plotly_chart(fig6, use_container_width=True)

# =========================================================
# STORE REVENUE
# =========================================================

st.markdown("---")
st.subheader("Store-Level Revenue Analysis")

store_df = (
    filtered_df.groupby("store_location")["Revenue"]
    .sum()
    .reset_index()
)

fig7 = px.bar(
    store_df,
    x="store_location",
    y="Revenue",
    color="Revenue",
    text_auto=True,
    title="Revenue by Store Location"
)

st.plotly_chart(fig7, use_container_width=True)

# =========================================================
# PRODUCT TYPE ANALYSIS
# =========================================================

st.markdown("---")
st.subheader("Product Type Revenue Analysis")

ptype_df = (
    filtered_df.groupby("product_type")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)

fig8 = px.bar(
    ptype_df,
    x="product_type",
    y="Revenue",
    color="Revenue",
    title="Revenue by Product Type"
)

st.plotly_chart(fig8, use_container_width=True)

# =========================================================
# HEATMAP
# =========================================================

st.markdown("---")
st.subheader("Store vs Category Revenue Heatmap")

heatmap_df = filtered_df.pivot_table(
    values="Revenue",
    index="store_location",
    columns="product_category",
    aggfunc="sum"
)

fig9 = px.imshow(
    heatmap_df,
    text_auto=True,
    aspect="auto",
    title="Store vs Product Category Revenue"
)

st.plotly_chart(fig9, use_container_width=True)

# =========================================================
# PRODUCT TABLE
# =========================================================

st.markdown("---")
st.subheader("Detailed Product Performance Table")

product_table = (
    filtered_df.groupby([
        "product_category",
        "product_type",
        "product_detail"
    ])
    .agg({
        "transaction_qty": "sum",
        "Revenue": "sum",
        "unit_price": "mean"
    })
    .reset_index()
)

product_table.columns = [
    "Category",
    "Product Type",
    "Product Detail",
    "Total Quantity Sold",
    "Total Revenue",
    "Average Unit Price"
]

st.dataframe(
    product_table,
    use_container_width=True,
    height=600
)

# =========================================================
# DOWNLOAD BUTTON
# =========================================================

csv = product_table.to_csv(index=False)

st.download_button(
    label="📥 Download Product Performance Report",
    data=csv,
    file_name="coffee_dashboard_report.csv",
    mime="text/csv"
)

# =========================================================
# BUSINESS INSIGHTS
# =========================================================

st.markdown("---")
st.subheader("📌 Automated Business Insights")

best_product = revenue_products.iloc[0]["product_detail"] if len(revenue_products) > 0 else "N/A"

best_category = category_rev.sort_values(
    by="Revenue",
    ascending=False
).iloc[0]["product_category"] if len(category_rev) > 0 else "N/A"

peak_hour = hourly_df.sort_values(
    by="Revenue",
    ascending=False
).iloc[0]["Hour"] if len(hourly_df) > 0 else "N/A"

st.success(
    f"💎 Top Revenue Product: {best_product}"
)

st.info(
    f"🏆 Highest Revenue Category: {best_category}"
)

st.warning(
    f"⏰ Peak Sales Hour: {peak_hour}:00" if peak_hour != "N/A" else "⏰ Peak Sales Hour: N/A"
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    ### Dashboard Features

    - 📊 Product Revenue Analysis
    - 🛍️ Product Popularity Analysis
    - 📈 Pareto Revenue Concentration
    - ⏱️ Hourly Sales Trends
    - 🏪 Store-Level Performance
    - 🎯 Category Revenue Distribution
    - 📦 Product Type Insights
    - 📥 Downloadable Reports
    - 🎛️ Interactive Filtering
    - 📌 KPI Monitoring
    """
)

st.caption(
    "Built using Streamlit, Pandas, NumPy, and Plotly"
)
