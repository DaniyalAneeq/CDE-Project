# app_interactive.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ===============================
# 1 — PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Interactive Car Dataset Dashboard",
    layout="wide"
)

st.title("🚗 Interactive Car Dataset Analysis Dashboard")
st.markdown("Use filters to explore the car dataset interactively. All KPIs and plots update based on selected brands and years.")

# ===============================
# 2 — LOAD CSV
# ===============================
df = pd.read_csv('cleaned_data.csv').copy()

# ===============================
# 3 — DATA CLEANING
# ===============================
def clean_engine_capacity(value):
    if isinstance(value, str):
        v = value.lower().replace(" ", "")
        num = ''.join([c for c in v if c.isdigit()])
        if num == "":
            return np.nan
        num = int(num)
        if "cc" in v or "kwh" in v or "kw" in v:
            return num
    return value

df["engine_capacity"] = df["engine_capacity"].apply(clean_engine_capacity)
df["engine_capacity"] = pd.to_numeric(df["engine_capacity"], errors="coerce")
df["mileage"] = pd.to_numeric(df["mileage"], errors="coerce")

# Remove outliers
df = df[(df["mileage"] >= 0) & (df["mileage"] <= 800_000)].copy()
df = df[
    ((df["engine_capacity"] >= 600) & (df["engine_capacity"] <= 7000)) |
    ((df["engine_capacity"] >= 20) & (df["engine_capacity"] <= 150))
].copy()
df = df.dropna(subset=["engine_capacity"])

# Extract brand
df['brand'] = df['title'].str.split(' ').str[0]

# ===============================
# 4 — INTERACTIVE FILTERS
# ===============================
st.sidebar.header("Filters")

# Brand filter
brands = df['brand'].unique()
selected_brands = st.sidebar.multiselect("Select Brands", options=brands, default=list(brands))

# Year filter
if 'year' in df.columns:
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    selected_years = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))
else:
    selected_years = (df['year'].min(), df['year'].max()) if 'year' in df.columns else (0, 9999)

# Apply filters
df_filtered = df[df['brand'].isin(selected_brands)]
if 'year' in df.columns:
    df_filtered = df_filtered[(df_filtered['year'] >= selected_years[0]) & (df_filtered['year'] <= selected_years[1])]

# ===============================
# 5 — KPIs
# ===============================
st.subheader("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Cars", f"{df_filtered.shape[0]:,}")
col2.metric("Average Price (PKR)", f"{df_filtered['price'].mean():,.0f}" if 'price' in df_filtered.columns else "N/A")
col3.metric("Min Mileage", f"{df_filtered['mileage'].min():,.0f}")
col4.metric("Max Mileage", f"{df_filtered['mileage'].max():,.0f}")
col5.metric("Average Engine Capacity", f"{df_filtered['engine_capacity'].mean():,.0f}")

# ===============================
# 6 — DATA PREVIEW
# ===============================
st.subheader("Dataset Preview")
st.dataframe(df_filtered.head(10))

# ===============================
# 7 — ANALYSIS 1: Top 10 Brands
# ===============================
st.subheader("Top 10 Car Brands")
top_brands = df_filtered['brand'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    x=top_brands.index,
    y=top_brands.values,
    palette="viridis",
    ax=ax
)
ax.set_ylabel("Number of Cars")
ax.set_xlabel("Brand")
ax.set_title("Top 10 Car Brands (Filtered)")
ax.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(fig)

# ===============================
# 8 & 9 — ANALYSIS 2 & 3: Mileage & Engine Capacity
# ===============================
st.subheader("Mileage & Engine Capacity Analysis")
col1, col2 = st.columns(2)

with col1:
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.histplot(x=df_filtered['mileage'], bins=50, kde=True, color='skyblue', ax=ax2)
    ax2.set_xlabel("Mileage")
    ax2.set_ylabel("Count")
    ax2.set_title("Mileage Distribution (Filtered)")
    ax2.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig2)

with col2:
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.histplot(x=df_filtered['engine_capacity'], bins=50, kde=True, color='lightgreen', ax=ax3)
    ax3.set_xlabel("Engine Capacity")
    ax3.set_ylabel("Count")
    ax3.set_title("Engine Capacity Distribution (Filtered)")
    ax3.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig3)

# ===============================
# 10 — ANALYSIS 4: Price vs Mileage
# ===============================
if 'price' in df_filtered.columns:
    st.subheader("Price vs Mileage")
    fig4, ax4 = plt.subplots(figsize=(12, 6))
    sns.scatterplot(x='mileage', y='price', data=df_filtered, hue='brand', palette='tab10', ax=ax4, legend=False)
    ax4.set_xlabel("Mileage")
    ax4.set_ylabel("Price (PKR)")
    ax4.set_title("Price vs Mileage (Filtered)")
    ax4.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig4)

# ===============================
# 11 — ANALYSIS 5: Average Price Trend Over Years
# ===============================
if 'year' in df_filtered.columns and 'price' in df_filtered.columns:
    st.subheader("Average Car Price Trend Over Years")
    avg_price_per_year = df_filtered.groupby('year')['price'].mean().reset_index()

    fig5, ax5 = plt.subplots(figsize=(14, 6))
    sns.lineplot(data=avg_price_per_year, x='year', y='price', marker='o', color='red', ax=ax5)
    ax5.set_xlabel("Year")
    ax5.set_ylabel("Average Price (PKR)")
    ax5.set_title("Average Car Price Trend Over Years (Filtered)")
    ax5.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig5)

