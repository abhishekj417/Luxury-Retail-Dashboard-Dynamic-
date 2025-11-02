import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Luxury Retail Financial Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 🔑 API CONFIGURATION - UPDATE THIS SECTION WITH YOUR API KEY
# ==============================================================================
# Get your FREE API key from: https://site.financialmodelingprep.com/developer/docs
# Sign up takes 2 minutes - Free tier gives you 250 API calls per day
FMP_API_KEY = "YOUR API KEY"  # ← REPLACE THIS with your actual API key

# ==============================================================================
# COMPANY CONFIGURATIONS
# ==============================================================================
COMPANIES = {
    "LVMH": {
        "name": "LVMH Moët Hennessy Louis Vuitton",
        "ticker_yahoo": "MC.PA",
        "ticker_fmp": "MC.PA",
        "exchange": "Euronext Paris",
        "currency": "EUR"
    },
    "Hermès": {
        "name": "Hermès International",
        "ticker_yahoo": "RMS.PA",
        "ticker_fmp": "RMS.PA",
        "exchange": "Euronext Paris",
        "currency": "EUR"
    },
    "Richemont": {
        "name": "Compagnie Financière Richemont",
        "ticker_yahoo": "CFR.SW",
        "ticker_fmp": "CFR.SW",
        "exchange": "SIX Swiss Exchange",
        "currency": "CHF"
    },
    "Watches of Switzerland": {
        "name": "Watches of Switzerland Group",
        "ticker_yahoo": "WOSG.L",
        "ticker_fmp": "WOSG.L",
        "exchange": "London Stock Exchange",
        "currency": "GBP",
        "manual_data": {
            "Revenue": 1652000000,
            "EBITDA": 150000000,
            "PBT": None,
            "PAT": None,
            "Free_Cash_Flow": 98000000,
            "Period": "FY25 (52 weeks to April 27, 2025)",
            "Store_Count": 194,
            "Same_Store_Sales": "-6%",
            "Geographic_Mix": "UK: 45%, US: 55%",
            "Gross_Margin": "27.2%",
            "Operating_Margin": "9.1%"
        }
    },
    "The Hour Glass": {
        "name": "The Hour Glass Limited",
        "ticker_yahoo": "AGS.SI",
        "ticker_fmp": "AGS.SI",
        "exchange": "Singapore Exchange",
        "currency": "SGD",
        "manual_data": {
            "Revenue": 1162874000,
            "EBITDA": None,
            "PBT": 175432000,
            "PAT": 136083000,
            "Free_Cash_Flow": None,
            "Period": "FY25 (Year ended March 31, 2025)",
            "Store_Count": 52,
            "Same_Store_Sales": "-14%",
            "Geographic_Mix": "Singapore: 45%, Australia: 25%, SEA: 30%",
            "Gross_Margin": "35.8%",
            "Operating_Margin": "15.1%"
        }
    }
}

# Title and description
st.title("💎 Luxury Retail Companies Financial Dashboard")
st.markdown("**Top 5 Luxury Retail Companies - Live Financial Metrics (Auto-Updated)**")
st.markdown("---")

# ==============================================================================
# FINANCIAL MODELING PREP API FUNCTIONS (Most Accurate)
# ==============================================================================

@st.cache_data(ttl=3600)
def get_fmp_financial_data(ticker, company_key):
    """Fetch financial data from Financial Modeling Prep API - Most Accurate Source"""

    if FMP_API_KEY == "YOUR_API_KEY_HERE":
        return None

    try:
        base_url = "https://financialmodelingprep.com/api/v3"

        income_url = f"{base_url}/income-statement/{ticker}?limit=1&apikey={FMP_API_KEY}"
        income_response = requests.get(income_url, timeout=10)

        cashflow_url = f"{base_url}/cash-flow-statement/{ticker}?limit=1&apikey={FMP_API_KEY}"
        cashflow_response = requests.get(cashflow_url, timeout=10)

        metrics_url = f"{base_url}/key-metrics/{ticker}?limit=1&apikey={FMP_API_KEY}"
        metrics_response = requests.get(metrics_url, timeout=10)

        data = {
            "Company": COMPANIES[company_key]["name"],
            "Exchange": COMPANIES[company_key]["exchange"],
            "Currency": COMPANIES[company_key]["currency"],
            "Revenue": None,
            "EBITDA": None,
            "PBT": None,
            "PAT": None,
            "Free_Cash_Flow": None,
            "Period": "Latest Annual",
            "Store_Count": None,
            "Same_Store_Sales": None,
            "Geographic_Mix": None,
            "Gross_Margin": None,
            "Operating_Margin": None
        }

        if income_response.status_code == 200:
            income_data = income_response.json()
            if income_data and len(income_data) > 0:
                latest = income_data[0]
                data["Revenue"] = latest.get("revenue")
                data["EBITDA"] = latest.get("ebitda")
                data["PBT"] = latest.get("incomeBeforeTax")
                data["PAT"] = latest.get("netIncome")
                data["Period"] = f"Annual - {latest.get('date', 'Latest')}"

                if data["Revenue"] and data["Revenue"] > 0:
                    gross_profit = latest.get("grossProfit")
                    operating_income = latest.get("operatingIncome")

                    if gross_profit:
                        data["Gross_Margin"] = f"{(gross_profit / data['Revenue']) * 100:.1f}%"
                    if operating_income:
                        data["Operating_Margin"] = f"{(operating_income / data['Revenue']) * 100:.1f}%"

        if cashflow_response.status_code == 200:
            cashflow_data = cashflow_response.json()
            if cashflow_data and len(cashflow_data) > 0:
                latest_cf = cashflow_data[0]
                data["Free_Cash_Flow"] = latest_cf.get("freeCashFlow")

        if metrics_response.status_code == 200:
            metrics_data = metrics_response.json()
            if metrics_data and len(metrics_data) > 0:
                latest_metrics = metrics_data[0]
                if not data["Gross_Margin"]:
                    gm = latest_metrics.get("grossProfitMargin")
                    if gm:
                        data["Gross_Margin"] = f"{gm * 100:.1f}%"
                if not data["Operating_Margin"]:
                    om = latest_metrics.get("operatingProfitMargin")
                    if om:
                        data["Operating_Margin"] = f"{om * 100:.1f}%"

        return data

    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def get_yfinance_fallback(ticker, company_key):
    """Fallback to Yahoo Finance if FMP fails"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        cashflow = stock.cashflow

        data = {
            "Company": COMPANIES[company_key]["name"],
            "Exchange": COMPANIES[company_key]["exchange"],
            "Currency": COMPANIES[company_key]["currency"],
            "Revenue": None,
            "EBITDA": None,
            "PBT": None,
            "PAT": None,
            "Free_Cash_Flow": None,
            "Period": "Latest Annual",
            "Store_Count": None,
            "Same_Store_Sales": None,
            "Geographic_Mix": None,
            "Gross_Margin": None,
            "Operating_Margin": None
        }

        if not financials.empty:
            if 'Total Revenue' in financials.index:
                data["Revenue"] = financials.loc['Total Revenue'].iloc[0]
            if 'EBITDA' in financials.index:
                data["EBITDA"] = financials.loc['EBITDA'].iloc[0]
            if 'Pretax Income' in financials.index:
                data["PBT"] = financials.loc['Pretax Income'].iloc[0]
            if 'Net Income' in financials.index:
                data["PAT"] = financials.loc['Net Income'].iloc[0]

        if not cashflow.empty and 'Free Cash Flow' in cashflow.index:
            data["Free_Cash_Flow"] = cashflow.loc['Free Cash Flow'].iloc[0]

        data["Gross_Margin"] = f"{info.get('grossMargins', 0) * 100:.1f}%" if info.get('grossMargins') else None
        data["Operating_Margin"] = f"{info.get('operatingMargins', 0) * 100:.1f}%" if info.get('operatingMargins') else None

        return data
    except:
        return None

def merge_with_manual_data(api_data, company_key):
    """Merge API data with manual data for operational metrics"""
    if "manual_data" in COMPANIES[company_key]:
        manual = COMPANIES[company_key]["manual_data"]
        for key, value in manual.items():
            if value is not None and (api_data.get(key) is None or pd.isna(api_data.get(key))):
                api_data[key] = value
    return api_data

def format_number(value, currency="USD"):
    """Format numbers in millions/billions"""
    if value is None or pd.isna(value):
        return "N/A"

    try:
        value = float(value)
        if abs(value) >= 1e9:
            return f"{currency} {value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"{currency} {value/1e6:.2f}M"
        else:
            return f"{currency} {value:,.0f}"
    except:
        return str(value)

# Sidebar
st.sidebar.header("🎛️ Dashboard Controls")
st.sidebar.markdown("### Data Source")
api_choice = st.sidebar.radio(
    "Select Data Source:",
    ["Financial Modeling Prep (Most Accurate)", "Yahoo Finance (Fallback)", "Manual Data Only"],
    index=0
)

st.sidebar.markdown("### Display Options")
show_operational = st.sidebar.checkbox("Show Operational Metrics", value=True)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh All Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 API Status")
if FMP_API_KEY == "YOUR_API_KEY_HERE":
    st.sidebar.error("❌ API Key Not Set")
    st.sidebar.markdown("[Get Free API Key](https://site.financialmodelingprep.com/developer/docs)")
else:
    st.sidebar.success("✅ API Key Configured")

# Fetch data
with st.spinner("Loading financial data from live APIs..."):
    all_data = []

    for key, company in COMPANIES.items():
        data = None

        if api_choice == "Financial Modeling Prep (Most Accurate)":
            data = get_fmp_financial_data(company["ticker_fmp"], key)
            if not data or all(data[k] is None for k in ["Revenue", "EBITDA", "PAT"]):
                data = get_yfinance_fallback(company["ticker_yahoo"], key)
        elif api_choice == "Yahoo Finance (Fallback)":
            data = get_yfinance_fallback(company["ticker_yahoo"], key)
        elif api_choice == "Manual Data Only":
            if "manual_data" in company:
                data = {
                    "Company": company["name"],
                    "Exchange": company["exchange"],
                    "Currency": company["currency"],
                    **company["manual_data"]
                }

        if data:
            data = merge_with_manual_data(data, key)
            all_data.append(data)

if all_data:
    df = pd.DataFrame(all_data)

    st.header("📊 Financial Metrics")
    financial_cols = ["Company", "Exchange", "Currency", "Revenue", "EBITDA", "PBT", "PAT", "Free_Cash_Flow", "Period"]
    financial_df = df[financial_cols].copy()

    for col in ["Revenue", "EBITDA", "PBT", "PAT", "Free_Cash_Flow"]:
        financial_df[col] = financial_df.apply(
            lambda row: format_number(row[col], row["Currency"]) if col in row else "N/A", axis=1
        )

    st.dataframe(financial_df, use_container_width=True, hide_index=True)

    if show_operational:
        st.header("🏪 Operational Metrics")
        operational_cols = ["Company", "Store_Count", "Same_Store_Sales", "Geographic_Mix", "Gross_Margin", "Operating_Margin"]
        operational_df = df[operational_cols].copy().fillna("N/A")
        st.dataframe(operational_df, use_container_width=True, hide_index=True)

    st.header("💡 Key Insights")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Companies", len(df))
    with col2:
        total_rev = df["Revenue"].apply(lambda x: x if pd.notna(x) else 0).sum()
        st.metric("Combined Revenue", format_number(total_rev, "Mixed"))
    with col3:
        st.metric("Stock Exchanges", df["Exchange"].nunique())

    st.header("📥 Export Data")
    export_df = pd.concat([financial_df, operational_df.drop(columns=["Company"])], axis=1)
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button("📊 Download as CSV", csv, f"luxury_retail_dashboard_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
else:
    st.error("Unable to load data. Please check API configuration.")

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Luxury Retail Financial Dashboard</strong> | <em>Powered by Financial Modeling Prep API</em></p>
    <p style='font-size: 0.8em; color: gray;'>Data refreshes hourly. For informational purposes only.</p>
</div>
""", unsafe_allow_html=True)
