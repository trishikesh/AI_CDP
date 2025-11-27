"""
AI-Powered Central Data Platform - Home Page
Elegant overview dashboard with key metrics from all domains
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from core_analysis.data_retriever import DataRetriever
from core_analysis.ai_engine import AIEngine

# Page configuration
st.set_page_config(
    page_title="AI-CDP Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Elegant and Minimal Design
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: none;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Headers */
    h1 {
        color: #1e293b;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    h2 {
        color: #475569;
        font-weight: 700;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        font-size: 1.8rem;
    }
    
    h3 {
        color: #64748b;
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    
    h4 {
        color: #475569;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
        padding: 2rem 1rem;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #e2e8f0 !important;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        background: white;
        padding: 12px;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 0.6rem 1.2rem;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    
    /* Date input */
    .stDateInput {
        border-radius: 10px;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_retriever' not in st.session_state:
    st.session_state.data_retriever = None
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'home_data' not in st.session_state:
    st.session_state.home_data = None

def initialize_connections():
    """Initialize database connections"""
    try:
        if st.session_state.data_retriever is None:
            st.session_state.data_retriever = DataRetriever()
        return True
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return False

def create_kpi_card(label, value, format_type="number", delta=None):
    """Create a styled KPI metric card"""
    if format_type == "currency":
        st.metric(label, f"${value:,.2f}", delta=delta)
    elif format_type == "percent":
        st.metric(label, f"{value:.2f}%", delta=delta)
    else:
        st.metric(label, f"{value:,.0f}", delta=delta)

# Main content
st.title("📊 Business Intelligence Dashboard")
st.markdown("##### Real-time insights across all business domains")

# Sidebar - Date Range Filter
with st.sidebar:
    st.markdown("## 📅 Date Range")
    date_range = st.date_input(
        "Select Period",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now(),
        key="home_date_range"
    )
    
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        with st.spinner("Loading data from MongoDB..."):
            if initialize_connections():
                try:
                    if len(date_range) == 2:
                        start_date = datetime.combine(date_range[0], datetime.min.time())
                        end_date = datetime.combine(date_range[1], datetime.max.time())
                    else:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=30)
                    
                    # Fetch all data
                    data_dict = st.session_state.data_retriever.get_all_data(start_date, end_date)
                    results = st.session_state.ai_engine.run_all_analyses(data_dict)
                    
                    st.session_state.home_data = {
                        'data_dict': data_dict,
                        'results': results,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                    st.session_state.data_loaded = True
                    st.success("✅ Data loaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 🧭 Quick Navigation")
    st.markdown("📄 Use pages in sidebar to explore:")
    st.markdown("- 💰 **Sales** - Revenue & Products")
    st.markdown("- 🔧 **Manufacturing** - Quality & Production")
    st.markdown("- 🧪 **Testing** - QA & Pass Rates")
    st.markdown("- 📦 **Inventory** - Stock & Alerts")
    st.markdown("- 🤖 **AI Assistant** - Ask Questions")

# Main Dashboard
if st.session_state.data_loaded and st.session_state.home_data:
    data_dict = st.session_state.home_data['data_dict']
    results = st.session_state.home_data['results']
    
    # KPI Row
    st.markdown("### 📈 Key Performance Indicators")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        create_kpi_card("Total Revenue", results['sales']['total_revenue'], "currency")
    
    with kpi_cols[1]:
        create_kpi_card("Defect Rate", results['quality']['avg_defect_rate'], "percent")
    
    with kpi_cols[2]:
        create_kpi_card("Inventory Level", results['inventory']['total_inventory'])
    
    with kpi_cols[3]:
        create_kpi_card("Test Pass Rate", results['testing']['pass_rate'], "percent")
    
    st.markdown("---")
    
    # Charts Grid
    st.markdown("### 📊 Domain Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Sales Revenue Trend")
        if not results['sales']['revenue_trend'].empty:
            fig = px.area(
                results['sales']['revenue_trend'],
                x='Date',
                y='Revenue',
                color_discrete_sequence=['#667eea'],
                template='plotly_white'
            )
            fig.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Revenue ($)",
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available for the selected period")
    
    with col2:
        st.markdown("#### 🔧 Quality Defect Rate")
        if not results['quality']['defect_trend'].empty:
            fig = px.line(
                results['quality']['defect_trend'],
                x='Date',
                y='Defect_Rate',
                color_discrete_sequence=['#f59e0b'],
                template='plotly_white'
            )
            fig.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Defect Rate (%)",
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.add_hline(y=5, line_dash="dash", line_color="red", opacity=0.4, annotation_text="Threshold")
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No quality data available for the selected period")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 📦 Inventory Levels")
        if not results['inventory']['inventory_trend'].empty:
            fig = px.bar(
                results['inventory']['inventory_trend'],
                x='Date',
                y='Inventory_Level',
                color_discrete_sequence=['#10b981'],
                template='plotly_white'
            )
            fig.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Inventory Level",
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No inventory data available for the selected period")
    
    with col4:
        st.markdown("#### 🧪 Top Products by Revenue")
        if not results['sales']['top_products'].empty:
            top_5 = results['sales']['top_products'].head(5)
            fig = px.bar(
                top_5,
                x='Revenue',
                y='SKU',
                orientation='h',
                color_discrete_sequence=['#8b5cf6'],
                template='plotly_white'
            )
            fig.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False,
                xaxis_title="Revenue ($)",
                yaxis_title="",
                hovermode='y unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product data available for the selected period")
    
    # Additional Insights
    st.markdown("---")
    st.markdown("### 🎯 Quick Insights")
    
    insight_cols = st.columns(3)
    
    with insight_cols[0]:
        st.info(f"**Profit Margin:** {results['sales']['profit_margin']:.2f}%")
        st.caption("Current profit margin from sales")
    
    with insight_cols[1]:
        anomaly_count = len(results['quality']['anomalies'])
        if anomaly_count > 0:
            st.warning(f"**Quality Alerts:** {anomaly_count} production lines")
            st.caption("Lines with defect rate > 5%")
        else:
            st.success("**Quality Status:** All lines performing well")
            st.caption("No critical quality issues")
    
    with insight_cols[2]:
        low_stock = results['inventory']['low_stock_alerts']
        if low_stock > 0:
            st.warning(f"**Low Stock Alerts:** {low_stock}")
            st.caption("Stores needing inventory replenishment")
        else:
            st.success("**Inventory Status:** All levels adequate")
            st.caption("No critical stock issues")

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        st.markdown("""
        Get Started
        
        1. **Select a date range** in the sidebar
        2. **Click 'Refresh Data'** to load real-time data from MongoDB
        3. **Explore insights** across all business domains
        
        Available Dashboards:
        - ** Sales:** Revenue trends, top products, profit analysis
        - ** Manufacturing:** Quality metrics, defect rates, production lines
        - ** Testing:** Pass rates, failed tests, quality assurance
        - ** Inventory:** Stock levels, low stock alerts, consumption trends
        - ** AI Assistant:** Ask questions and get instant insights
        
        Navigate using the sidebar to explore specific domains!
        """)

# Footer
st.markdown("---")
st.caption("AI-CDP Dashboard | Powered by MongoDB & Google Gemini AI")