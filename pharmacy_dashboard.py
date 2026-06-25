"""
Pharmacy Sales Dashboard
=========================
Streamlit app showing:
  1. Sales by Region
  2. Sales by Representative
  3. Sales Trends over Time
  4. Before vs After Data-Unification comparison
     (raw multi-warehouse export  ->  entity-resolved / cleaned dataset)

Run:
    streamlit run pharmacy_dashboard.py

Inputs (sidebar uploaders, or auto-detected in the working directory):
  - AFTER  (cleaned/unified) : e.g. updated16_file.csv  (output of the entity-resolution pipeline)
  - BEFORE (raw)             : e.g. supplier_sales.csv   (original multi-warehouse export)

Column names are auto-detected with fallbacks, so slightly different headers still work.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Pharmacy Sales Dashboard", layout="wide", page_icon="💊")

# --------------------------------------------------------------------------------------
# Column resolution
# --------------------------------------------------------------------------------------
COLUMN_CANDIDATES = {
    "sales":    ["total_amount", "sales", "amount", "revenue", "net_amount"],
    "qty":      ["quantity", "qty"],
    "region":   ["region", "city", "governorate"],
    "rep":      ["employee_name", "user_name", "representative", "sales_rep", "rep_name"],
    "date":     ["creation_date", "created_at", "date", "invoice_date"],
    "account":  ["account_id", "account_name"],
    "product":  ["product_name", "prod_id"],
    "supplier": ["supplier_id", "supplier_name"],
}


def resolve(df, key):
    for c in COLUMN_CANDIDATES[key]:
        if c in df.columns:
            return c
    return None


@st.cache_data(show_spinner=False)
def load_csv(file):
    return pd.read_csv(file)


def prep(df):
    df = df.copy()
    date_col = resolve(df, "date")
    df["_date"] = pd.to_datetime(df[date_col], errors="coerce") if date_col else pd.NaT

    sales_col = resolve(df, "sales")
    df["_sales"] = pd.to_numeric(df[sales_col], errors="coerce") if sales_col else np.nan

    region_col = resolve(df, "region")
    df["_region"] = df[region_col] if region_col else np.nan

    rep_col = resolve(df, "rep")
    df["_rep"] = df[rep_col] if rep_col else np.nan

    return df


def autodetect(paths):
    for p in paths:
        if Path(p).exists():
            return p
    return None


# --------------------------------------------------------------------------------------
# Sidebar — data loading
# --------------------------------------------------------------------------------------
st.sidebar.title("💊 Data Sources")

after_file = st.sidebar.file_uploader("AFTER unification (cleaned)", type="csv", key="after")
before_file = st.sidebar.file_uploader("BEFORE unification (raw)", type="csv", key="before")

after_path = autodetect(["updated16_file.csv", "updated_file.csv", "after.csv"])
before_path = autodetect(["supplier_sales.csv", "before.csv"])

df_after_raw = load_csv(after_file) if after_file is not None else (load_csv(after_path) if after_path else None)
df_before_raw = load_csv(before_file) if before_file is not None else (load_csv(before_path) if before_path else None)

st.title("💊 Pharmacy Sales Dashboard")
st.caption("Multi-warehouse pharmacy sales — unified view")

if df_after_raw is None:
    st.warning(
        "Upload the unified (cleaned) sales CSV in the sidebar to get started. "
        "Optionally also upload the raw/before file to unlock the Before vs After comparison."
    )
    st.stop()

df_after = prep(df_after_raw)
df_before = prep(df_before_raw) if df_before_raw is not None else None

# --------------------------------------------------------------------------------------
# Sidebar — filters (applied to the AFTER / unified dataset)
# --------------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

min_d, max_d = df_after["_date"].min(), df_after["_date"].max()
date_range = None
if pd.notna(min_d) and pd.notna(max_d):
    date_range = st.sidebar.date_input(
        "Date range", value=(min_d.date(), max_d.date()),
        min_value=min_d.date(), max_value=max_d.date(),
    )

regions = sorted(df_after["_region"].dropna().unique().tolist())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions) if regions else []

reps = sorted(df_after["_rep"].dropna().unique().tolist())
sel_reps = st.sidebar.multiselect("Representative", reps, default=[])

f = df_after.copy()
if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    f = f[f["_date"].isna() | ((f["_date"] >= start) & (f["_date"] <= end))]
if sel_regions:
    f = f[f["_region"].isin(sel_regions) | f["_region"].isna()]
if sel_reps:
    f = f[f["_rep"].isin(sel_reps)]

# --------------------------------------------------------------------------------------
# KPIs
# --------------------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"{f['_sales'].sum():,.0f}")
k2.metric("Rows / Invoices", f"{len(f):,}")
k3.metric("Active Regions", f"{f['_region'].nunique():,}")
k4.metric("Representatives", f"{f['_rep'].nunique():,}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(
    ["🗺️ Sales by Region", "🧑‍💼 Sales by Representative", "📈 Sales Trends", "🔄 Before vs After Unification"]
)

# --------------------------------------------------------------------------------------
# Tab 1 — Sales by Region
# --------------------------------------------------------------------------------------
with tab1:
    if f["_region"].notna().any():
        reg_sales = (
            f.groupby("_region")["_sales"].sum().reset_index()
            .sort_values("_sales", ascending=False)
            .rename(columns={"_region": "Region", "_sales": "Sales"})
        )
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.bar(reg_sales, x="Region", y="Sales", color="Region",
                         text_auto=".2s", title="Total Sales by Region")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.pie(reg_sales, names="Region", values="Sales", title="Region Share", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(reg_sales, use_container_width=True, hide_index=True)
    else:
        st.info("No region data available in the current dataset / filters.")

# --------------------------------------------------------------------------------------
# Tab 2 — Sales by Representative
# --------------------------------------------------------------------------------------
with tab2:
    if f["_rep"].notna().any():
        top_n = st.slider("Show top N representatives", 5, 50, 15)
        rep_sales = (
            f.groupby("_rep")["_sales"].sum().reset_index()
            .sort_values("_sales", ascending=False).head(top_n)
            .rename(columns={"_rep": "Representative", "_sales": "Sales"})
        )
        fig = px.bar(rep_sales, x="Sales", y="Representative", orientation="h",
                     text_auto=".2s", title=f"Top {top_n} Representatives by Sales")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(rep_sales, use_container_width=True, hide_index=True)
    else:
        st.info("No representative data available in the current dataset / filters.")

# --------------------------------------------------------------------------------------
# Tab 3 — Sales Trends over Time
# --------------------------------------------------------------------------------------
with tab3:
    if f["_date"].notna().any():
        granularity = st.radio("Granularity", ["Day", "Week", "Month"], horizontal=True, index=2)
        freq_map = {"Day": "D", "Week": "W", "Month": "M"}
        freq = freq_map[granularity]

        ts = (
            f.dropna(subset=["_date"]).set_index("_date")
            .resample(freq)["_sales"].sum().reset_index()
            .rename(columns={"_date": "Date", "_sales": "Sales"})
        )
        fig = px.line(ts, x="Date", y="Sales", markers=True, title=f"Sales Trend ({granularity})")
        st.plotly_chart(fig, use_container_width=True)

        if len(sel_regions) > 1:
            ts_region = (
                f.dropna(subset=["_date"])
                .groupby([pd.Grouper(key="_date", freq=freq), "_region"])["_sales"].sum()
                .reset_index().rename(columns={"_date": "Date", "_region": "Region", "_sales": "Sales"})
            )
            fig2 = px.line(ts_region, x="Date", y="Sales", color="Region", markers=True,
                           title=f"Sales Trend by Region ({granularity})")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No valid date column found to plot trends.")

# --------------------------------------------------------------------------------------
# Tab 4 — Before vs After Data Unification
# --------------------------------------------------------------------------------------
with tab4:
    st.subheader("Impact of the Data-Unification / Entity-Resolution Pipeline")
    if df_before is None:
        st.info("Upload the BEFORE (raw) CSV in the sidebar to unlock this comparison.")
    else:
        b, a = df_before, df_after

        acc_col_b = resolve(b, "account") or "account_id"
        acc_col_a = "Global_Account_ID" if "Global_Account_ID" in a.columns else (resolve(a, "account") or "account_id")

        rows_b, rows_a = len(b), len(a)
        acc_b = b[acc_col_b].nunique() if acc_col_b in b.columns else np.nan
        acc_a = a[acc_col_a].nunique() if acc_col_a in a.columns else np.nan
        region_fill_b = b["_region"].notna().mean() * 100
        region_fill_a = a["_region"].notna().mean() * 100
        rep_fill_b = b["_rep"].notna().mean() * 100
        rep_fill_a = a["_rep"].notna().mean() * 100
        sales_b = b["_sales"].sum()
        sales_a = a["_sales"].sum()

        comp = pd.DataFrame({
            "Metric": ["Rows", "Unique Accounts / Entities", "Region Filled %", "Representative Filled %", "Total Sales"],
            "Before (raw)": [f"{rows_b:,}", f"{acc_b:,.0f}" if pd.notna(acc_b) else "—",
                              f"{region_fill_b:.1f}%", f"{rep_fill_b:.1f}%", f"{sales_b:,.0f}"],
            "After (unified)": [f"{rows_a:,}", f"{acc_a:,.0f}" if pd.notna(acc_a) else "—",
                                 f"{region_fill_a:.1f}%", f"{rep_fill_a:.1f}%", f"{sales_a:,.0f}"],
        })
        st.dataframe(comp, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            if pd.notna(acc_b) and pd.notna(acc_a):
                dedup_fig = px.bar(
                    x=["Before (raw entities)", "After (unified entities)"],
                    y=[acc_b, acc_a], color=["Before", "After"],
                    text=[acc_b, acc_a], title="Duplicate Pharmacy Entities Merged",
                )
                dedup_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Unique Accounts")
                st.plotly_chart(dedup_fig, use_container_width=True)
                st.caption(f"➡️ {acc_b - acc_a:,.0f} duplicate entities consolidated by entity resolution.")
        with c2:
            fill_fig = px.bar(
                x=["Region", "Representative"],
                y=[region_fill_a - region_fill_b, rep_fill_a - rep_fill_b],
                text=[f"+{region_fill_a - region_fill_b:.1f}pp", f"+{rep_fill_a - rep_fill_b:.1f}pp"],
                title="Data Completeness Gained (percentage points)",
            )
            fill_fig.update_layout(yaxis_title="Percentage points gained", xaxis_title="")
            st.plotly_chart(fill_fig, use_container_width=True)

        if b["_region"].notna().any() and a["_region"].notna().any():
            st.markdown("#### Sales by Region — Before vs After")
            rb = b.groupby("_region")["_sales"].sum().reset_index(); rb["View"] = "Before"
            ra = a.groupby("_region")["_sales"].sum().reset_index(); ra["View"] = "After"
            both = pd.concat([rb, ra], ignore_index=True).rename(columns={"_region": "Region", "_sales": "Sales"})
            fig3 = px.bar(both, x="Region", y="Sales", color="View", barmode="group",
                          title="Sales by Region: Before vs After Unification")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info(
                "Region was not populated in the raw data — region/area assignment is itself "
                "produced by the unification pipeline, so only the AFTER view has a regional breakdown."
            )
