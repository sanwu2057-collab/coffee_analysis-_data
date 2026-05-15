import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import zipfile
import io
import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="☕ Afficionado Coffee Dashboard",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Afficionado Coffee Roasters Dashboard")
st.markdown("### Product Optimization & Revenue Analytics")

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data(file):

    try:

        # Load CSV/XLSX
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)

        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)

        elif file.name.endswith(".zip"):

            with zipfile.ZipFile(file) as z:

                for f in z.namelist():

                    if f.endswith(".csv"):

                        with z.open(f) as x:
                            df = pd.read_csv(x)

                        break

                    elif f.endswith(".xlsx"):

                        with z.open(f) as x:
                            df = pd.read_excel(
                                io.BytesIO(x.read())
                            )

                        break
        else:
            st.error("Unsupported file format")
            st.stop()

        # ==================================================
        # FIX datetime.time ERROR
        # ==================================================

        for col in df.columns:

            if df[col].dtype == 'object':

                sample = (
                    df[col]
                    .dropna()
                    .iloc[0]
                    if not df[col].dropna().empty
                    else None
                )

                if isinstance(sample, datetime.time):
                    df[col] = df[col].astype(str)

        # ==================================================
        # REQUIRED COLUMNS
        # ==================================================

        required_columns = [
            "product_category",
            "product_type",
            "product_detail",
            "transaction_qty",
            "unit_price",
            "transaction_time",
            "store_location",
            "product_id"
        ]

        missing = [
            c for c in required_columns
            if c not in df.columns
        ]

        if missing:

            st.error(
                f"Missing columns: {missing}"
            )

            st.stop()

        # ==================================================
        # DATE + TIME PROCESSING
        # ==================================================

        time_data = pd.to_datetime(
            df["transaction_time"],
            errors="coerce"
        )

        df["Hour"] = time_data.dt.hour
        df["Minute"] = time_data.dt.minute
        df["Day"] = time_data.dt.day
        df["Month"] = time_data.dt.month
        df["Year"] = time_data.dt.year
        df["Date"] = time_data.dt.date

        # important:
        # string not datetime.time object

        df["Time"] = time_data.dt.strftime(
            "%H:%M:%S"
        )

        df["AM_PM"] = time_data.dt.strftime(
            "%p"
        )

        df["Time_Period"] = pd.cut(
            df["Hour"],
            bins=[0,6,12,17,21,24],
            labels=[
                "Night",
                "Morning",
                "Afternoon",
                "Evening",
                "Late Night"
            ],
            include_lowest=True
        )

        # ==================================================
        # REVENUE
        # ==================================================

        df["Revenue"] = (
            df["transaction_qty"]
            * df["unit_price"]
        )

        return df

    except Exception as e:

        st.error(
            f"Error processing file: {str(e)}"
        )

        st.stop()


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded = st.sidebar.file_uploader(
    "Upload file",
    type=["csv","xlsx","zip"]
)

if uploaded is None:
    st.info("Upload data file")
    st.stop()

df = load_data(uploaded)

# =========================================================
# FILTERS
# =========================================================

st.sidebar.header("Filters")

category = st.sidebar.multiselect(
    "Category",
    df["product_category"].unique(),
    default=df["product_category"].unique()
)

store = st.sidebar.multiselect(
    "Store",
    df["store_location"].unique(),
    default=df["store_location"].unique()
)

filtered_df = df[
    (df["product_category"].isin(category))
    &
    (df["store_location"].isin(store))
]

# =========================================================
# KPI CARDS
# =========================================================

st.subheader("📊 KPI Dashboard")

c1,c2,c3,c4=st.columns(4)

c1.metric(
    "Revenue",
    f"${filtered_df['Revenue'].sum():,.2f}"
)

c2.metric(
    "Sales Volume",
    f"{filtered_df['transaction_qty'].sum():,.0f}"
)

c3.metric(
    "Products",
    filtered_df["product_id"].nunique()
)

c4.metric(
    "Avg Price",
    f"${filtered_df['unit_price'].mean():.2f}"
)

# =========================================================
# CATEGORY PIE
# =========================================================

cat=filtered_df.groupby(
    "product_category"
)["Revenue"].sum().reset_index()

fig1=px.pie(
    cat,
    names="product_category",
    values="Revenue",
    hole=.45
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =========================================================
# HOURLY TREND
# =========================================================

hourly=filtered_df.groupby(
    "Hour"
)["Revenue"].sum().reset_index()

fig2=px.line(
    hourly,
    x="Hour",
    y="Revenue",
    markers=True
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================================
# TOP PRODUCTS
# =========================================================

top=filtered_df.groupby(
    "product_detail"
)["Revenue"].sum().sort_values(
    ascending=False
).head(10).reset_index()

fig3=px.bar(
    top,
    x="product_detail",
    y="Revenue",
    color="Revenue"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================================
# HEATMAP
# =========================================================

heat=filtered_df.pivot_table(
    values="Revenue",
    index="store_location",
    columns="product_category",
    aggfunc="sum"
)

fig4=px.imshow(
    heat,
    text_auto=True
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =========================================================
# DATA TABLE
# =========================================================

st.subheader(
    "Detailed Table"
)

st.dataframe(
    filtered_df
)

st.success(
    "Dashboard loaded successfully"
)
