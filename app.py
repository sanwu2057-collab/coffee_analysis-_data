import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Afficionado Coffee Analytics Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    h1 {
        color: #0f172a;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.title("☕ Afficionado Coffee Roasters Dashboard")
st.markdown("### Product Optimization & Revenue Contribution Analytics"
@st.cache_data
def load_data(file_path="data/coffee.xlsx"):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xls"):
        df = pd.read_excel(file_path, engine="xlrd")
    else:  # assume .xlsx
        df = pd.read_excel(file_path, engine="openpyxl")
    return df




try:
    df = load_data()

except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

st.sidebar.header("Dashboard Filters")

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

filtered_df = df[
    (df["product_category"].isin(category_filter)) &
    (df["store_location"].isin(store_filter)) &
    (df["product_type"].isin(product_type_filter))
]

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
    total_revenue / unique_products
)

k1, k2, k3, k4 = st.columns(4)

k5, k6, k7, k8 = st.columns(4)

k1.metric(
    "💰 Total Revenue",
    f"${total_revenue:,.2f}"
)

k2.metric(
    "🛒 Total Sales Volume",
    f"{total_sales:,.0f}"
)

k3.metric(
    "📦 Unique Products",
    unique_products
)

k4.metric(
    "💵 Avg Unit Price",
    f"${avg_price:.2f}"
)

k5.metric(
    "📈 Avg Transaction Revenue",
    f"${avg_revenue:.2f}"
)

k6.metric(
    "⚠️ Revenue Concentration",
    f"{revenue_concentration_ratio:.2f}%"
)

k7.metric(
    "⭐ Product Efficiency",
    f"{product_efficiency_score:.2f}"
)

k8.metric(
    "🏆 Top Category",
    top_category
)

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

csv = product_table.to_csv(index=False)

st.download_button(
    label="Download Product Performance Report",
    data=csv,
    file_name="coffee_dashboard_report.csv",
    mime="text/csv"
)

st.markdown("---")
st.subheader("📌 Automated Business Insights")

best_product = revenue_products.iloc[0]["product_detail"]

best_category = category_rev.sort_values(
    by="Revenue",
    ascending=False
).iloc[0]["product_category"]

peak_hour = hourly_df.sort_values(
    by="Revenue",
    ascending=False
).iloc[0]["Hour"]

st.success(
    f"Top Revenue Product: {best_product}"
)

st.info(
    f"Highest Revenue Category: {best_category}"
)

st.warning(
    f"Peak Sales Hour: {peak_hour}:00"
)

st.markdown("---")

st.markdown(
    """
    ### Dashboard Features

    - Product Revenue Analysis
    - Product Popularity Analysis
    - Pareto Revenue Concentration
    - Hourly Sales Trends
    - Store-Level Performance
    - Category Revenue Distribution
    - Product Type Insights
    - Downloadable Reports
    - Interactive Filtering
    - KPI Monitoring
    """
)

st.caption(
    "Built using Streamlit, Pandas, NumPy, and Plotly"
)
