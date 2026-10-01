"""RetailPulse: a dynamic Power BI-style local dashboard replica."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"

st.set_page_config(page_title="RetailPulse Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3, [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #f7f8fc; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #260b10 0%, #4d0d18 100%); }
[data-testid="stSidebar"] * { color: #fff !important; }
.brand { display:flex; align-items:center; gap:12px; margin:4px 0 18px; }
.brand-mark { background:#d90429; color:white; border-radius:10px; padding:7px 10px; font-weight:700; font-size:20px; }
.brand-name { font-family:'Space Grotesk'; color:#fff; font-size:22px; font-weight:700; }
.hero { background:linear-gradient(120deg,#490914 0%,#d90429 62%,#ef233c 100%); color:white; border-radius:18px; padding:22px 28px; margin-bottom:15px; box-shadow:0 10px 25px rgba(90,0,15,.16); }
.hero h1 { margin:0; font-size:31px; letter-spacing:-1px; }
.hero p { margin:5px 0 0; opacity:.88; }
.report-bar { background:#fff; border:1px solid #e4e7ef; border-radius:10px; padding:10px 15px; color:#4b5563; margin-bottom:14px; }
.report-bar b { color:#b00020; }
.section-title { color:#4b0a14; border-left:5px solid #d90429; padding-left:11px; margin:18px 0 10px; }
[data-testid="stMetric"] { background:#fff; border:1px solid #e4e7ef; border-radius:11px; padding:10px 13px; box-shadow:0 3px 10px rgba(35,42,60,.04); }
[data-testid="stMetricLabel"] { color:#6b7280; font-size:12px; }
[data-testid="stMetricValue"] { color:#3b0710; font-size:22px; }
div[data-baseweb="tab-list"] { gap:5px; background:#fff; padding:7px; border:1px solid #e4e7ef; border-radius:11px; }
button[data-baseweb="tab"] { height:38px; border-radius:7px; font-weight:600; }
button[data-baseweb="tab"][aria-selected="true"] { background:#d90429; color:#fff; }
.small-note { color:#6b7280; font-size:12px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    path = OUTPUTS / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def money(value: float) -> str:
    return f"£{value:,.0f}"


def chart_layout(fig, height: int = 330):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=55, b=10), plot_bgcolor="white", paper_bgcolor="white", font=dict(family="DM Sans", color="#374151"), xaxis_title=None, yaxis_title=None)
    return fig


def metric_row(kpi: pd.Series) -> None:
    columns = st.columns(5)
    metrics = [
        ("Total Revenue", money(kpi["total_revenue"]), "Valid sales"),
        ("Total Orders", f"{kpi['total_orders']:,.0f}", "Distinct invoices"),
        ("Total Units", f"{kpi['total_units_sold']:,.0f}", "Items sold"),
        ("Unique Customers", f"{kpi['unique_customers']:,.0f}", "Identifiable buyers"),
        ("Average Order Value", money(kpi["average_order_value"]), "Revenue per order"),
    ]
    for column, (label, value, help_text) in zip(columns, metrics):
        with column:
            st.metric(label, value, help=help_text)


def sales_page(kpi, monthly, products, countries, selected_countries, period, top_n):
    st.markdown('<h3 class="section-title">Sales Overview</h3>', unsafe_allow_html=True)
    metric_row(kpi)
    st.markdown("<div class='small-note'>Interactive local replica · values are loaded from the Spark SQL outputs</div>", unsafe_allow_html=True)
    monthly_view = monthly[(monthly["month"].dt.date >= period[0]) & (monthly["month"].dt.date <= period[1])]
    country_view = countries[countries["country"].isin(selected_countries)] if selected_countries else countries
    left, right = st.columns([1.45, 1])
    with left:
        fig = px.line(monthly_view, x="month", y="revenue", markers=True, title="Monthly Revenue Trend")
        fig.update_traces(line_color="#1683ff", line_width=3, hovertemplate="%{x|%b %Y}<br>£%{y:,.0f}<extra></extra>")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    with right:
        view = country_view.nlargest(10, "revenue").sort_values("revenue")
        fig = px.bar(view, x="revenue", y="country", orientation="h", title="Country-wise Revenue")
        fig.update_traces(marker_color="#1683ff", hovertemplate="%{y}<br>£%{x:,.0f}<extra></extra>")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    product_view = products.head(top_n).sort_values("revenue")
    fig = px.bar(product_view, x="revenue", y="description", orientation="h", title="Top Products by Revenue")
    fig.update_traces(marker_color="#d90429", hovertemplate="%{y}<br>£%{x:,.0f}<extra></extra>")
    st.plotly_chart(chart_layout(fig, 390), use_container_width=True)


def customer_page(customer_analysis, segments):
    st.markdown('<h3 class="section-title">Customer Behaviour</h3>', unsafe_allow_html=True)
    customers = int(segments["customers"].sum()) if not segments.empty else 0
    repeat = int(segments.loc[segments["customer_segment"] != "One-time Customer", "customers"].sum()) if not segments.empty else 0
    average_spend = float((segments["average_customer_spend"] * segments["customers"]).sum() / customers) if customers else 0
    columns = st.columns(4)
    values = [f"{customers:,}", f"{repeat:,}", f"{repeat / customers:.1%}" if customers else "0%", money(average_spend)]
    for column, label, value in zip(columns, ["Identifiable Customers", "Repeat Customers", "Repeat Rate", "Weighted Avg Spend"], values):
        with column:
            st.metric(label, value)
    left, right = st.columns([1, 1.25])
    with left:
        fig = px.pie(segments, names="customer_segment", values="customers", hole=.58, title="Customer Segment Mix")
        fig.update_traces(marker=dict(colors=["#d90429", "#ef233c", "#ffb3c1"]), textinfo="percent+label")
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
    with right:
        spend = segments.sort_values("average_customer_spend")
        fig = px.bar(spend, x="average_customer_spend", y="customer_segment", orientation="h", title="Average Spend by Segment")
        fig.update_traces(marker_color="#b00020", hovertemplate="%{y}<br>£%{x:,.0f}<extra></extra>")
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
    if not customer_analysis.empty:
        st.markdown("#### Highest-value customers")
        st.dataframe(customer_analysis.head(12), use_container_width=True, hide_index=True)


def cancellation_page(cancellations):
    st.markdown('<h3 class="section-title">Cancellation Analysis</h3>', unsafe_allow_html=True)
    columns = st.columns(3)
    values = [money(cancellations["cancellation_value"].sum()), f"{cancellations['cancellation_invoices'].sum():,.0f}", f"{cancellations['cancelled_units'].sum():,.0f}"]
    for column, label, value in zip(columns, ["Cancellation Value", "Cancellation Invoices", "Cancelled Units"], values):
        with column:
            st.metric(label, value)
    left, right = st.columns([1.35, 1])
    with left:
        fig = px.line(cancellations, x="month", y="cancellation_value", markers=True, title="Cancellation Value Trend")
        fig.update_traces(line_color="#d90429", line_width=3, hovertemplate="%{x|%b %Y}<br>£%{y:,.0f}<extra></extra>")
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
    with right:
        fig = px.bar(cancellations, x="month", y="cancellation_invoices", title="Cancellation Invoices by Month")
        fig.update_traces(marker_color="#6a040f")
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
    st.dataframe(cancellations, use_container_width=True, hide_index=True)


st.markdown('<div class="hero"><h1>RetailPulse Dashboard</h1><p>Interactive retail intelligence · Power BI-style local experience</p></div>', unsafe_allow_html=True)
st.markdown('<div class="report-bar">📊 <b>RetailPulse_Dashboard</b> &nbsp;|&nbsp; Local analytical report &nbsp;|&nbsp; Data refreshed from project outputs</div>', unsafe_allow_html=True)

kpi = load_csv("kpi_summary.csv")
monthly = load_csv("monthly_sales.csv")
products = load_csv("top_products.csv")
countries = load_csv("country_sales.csv")
segments = load_csv("customer_segments.csv")
customer_analysis = load_csv("customer_analysis.csv")
cancellations = load_csv("cancellation_analysis.csv")

if kpi.empty or monthly.empty:
    st.error("Dashboard data is missing. Run the project pipeline first with `python src/run_project.py`.")
    st.stop()

monthly["month"] = pd.to_datetime(monthly["month"])
cancellations["month"] = pd.to_datetime(cancellations["month"])
month_values = monthly["month"]

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">RP</span><span class="brand-name">RetailPulse</span></div>', unsafe_allow_html=True)
    st.markdown("### Dashboard filters")
    selected_countries = st.multiselect("Country", sorted(countries["country"].dropna().unique()), placeholder="All countries")
    period = st.slider("Invoice date", min_value=month_values.min().date(), max_value=month_values.max().date(), value=(month_values.min().date(), month_values.max().date()))
    top_n = st.slider("Top products", min_value=5, max_value=10, value=10)
    st.markdown("---")
    st.success("Data loaded")
    st.caption("No Power BI URL required. This report is powered by the project's real Spark/Pandas outputs.")

pages = st.tabs(["Sales Overview", "Customer Behaviour", "Cancellation Analysis"])
with pages[0]:
    sales_page(kpi.iloc[0], monthly, products, countries, selected_countries, period, top_n)
with pages[1]:
    customer_page(customer_analysis, segments)
with pages[2]:
    cancellation_page(cancellations)

st.caption("RetailPulse · Power BI-style local replica · Source: Spark SQL analytical CSV outputs")
