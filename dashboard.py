import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(layout="wide", page_title="📊 Sales Dashboard")

st.title("📊 Sales Dashboard")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("sales.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
region = st.sidebar.selectbox("Select Region", options=["All"] + sorted(df["region"].unique().tolist()))
product = st.sidebar.selectbox("Select Product", options=["All"] + sorted(df["product"].unique().tolist()))
date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=df["date"].min().date(),
    max_value=df["date"].max().date(),
    value=(df["date"].min().date(), df["date"].max().date())
)

# Apply filters
filtered_df = df.copy()
if region != "All":
    filtered_df = filtered_df[filtered_df["region"] == region]
if product != "All":
    filtered_df = filtered_df[filtered_df["product"] == product]
filtered_df = filtered_df[(filtered_df["date"].dt.date >= date_range[0]) & (filtered_df["date"].dt.date <= date_range[1])]

# Summary metrics
st.subheader("📈 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Units Sold", f"{int(filtered_df['units_sold'].sum()):,}")
col2.metric("Total Revenue", f"${filtered_df['revenue'].sum():,.2f}")
col3.metric("Avg Revenue per Unit", f"${(filtered_df['revenue'].sum() / filtered_df['units_sold'].sum()):,.2f}")

# Line chart: Revenue over Time
st.subheader("📅 Revenue Over Time")
revenue_trend = filtered_df.groupby("month")["revenue"].sum().reset_index()
line_chart = alt.Chart(revenue_trend).mark_line(point=True).encode(
    x="month:T", y="revenue:Q"
).properties(width=800, height=300)
st.altair_chart(line_chart, use_container_width=True)

# Bar chart: Top 10 Products by Units Sold
st.subheader("🔥 Top 10 Products by Units Sold")
top_products = filtered_df.groupby("product")["units_sold"].sum().nlargest(10).reset_index()
st.bar_chart(top_products.set_index("product"))

# Pie chart: Revenue by Region
st.subheader("🗺️ Revenue Distribution by Region")
region_revenue = filtered_df.groupby("region")["revenue"].sum().reset_index()
st.plotly_chart(px.pie(region_revenue, names="region", values="revenue", title="Revenue by Region"), use_container_width=True)

# Heatmap: Revenue by Region and Product
st.subheader("📊 Revenue Heatmap by Region and Product")
heatmap_data = filtered_df.groupby(["region", "product"])["revenue"].sum().unstack(fill_value=0)
st.dataframe(heatmap_data.style.background_gradient(cmap="YlGnBu"))

# Area chart: Revenue Over Time by Product
st.subheader("📈 Revenue Over Time by Product")
monthly_product = filtered_df.groupby(["month", "product"])["revenue"].sum().reset_index()
area_chart = alt.Chart(monthly_product).mark_area().encode(
    x="month:T", y="revenue:Q", color="product:N"
).properties(height=300)
st.altair_chart(area_chart, use_container_width=True)

# Box Plot: Revenue Distribution by Product
st.subheader("📦 Revenue Distribution by Product")
box_data = filtered_df[["product", "revenue"]]
st.plotly_chart(
    px.box(box_data, x="product", y="revenue", title="Revenue Distribution per Product"),
    use_container_width=True
)

# Line chart: Revenue + Units Sold over time
st.subheader("📊 Revenue and Units Sold Over Time")
time_data = filtered_df.groupby("date")[["revenue", "units_sold"]].sum().reset_index()
fig = px.line(time_data, x="date", y=["revenue", "units_sold"], markers=True, title="Daily Revenue and Units Sold")
st.plotly_chart(fig, use_container_width=True)

# Filtered data table
st.markdown("---")
st.subheader("🧾 Filtered Sales Data")
st.dataframe(filtered_df.sort_values("date", ascending=False), use_container_width=True)