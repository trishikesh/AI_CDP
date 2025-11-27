"""
Sales Analytics Dashboard
Connected to 'Sales' MongoDB collection
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
    page_title="Sales Analytics",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Same elegant styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    
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
    
    .js-plotly-plot {
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        background: white;
        padding: 12px;
    }
    
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
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
    
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
    
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_retriever' not in st.session_state:
    st.session_state.data_retriever = None
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'sales_data_loaded' not in st.session_state:
    st.session_state.sales_data_loaded = False
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = None

def initialize_connections():
    """Initialize database connections"""
    try:
        if st.session_state.data_retriever is None:
            st.session_state.data_retriever = DataRetriever()
        return True
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return False

# Main content
st.title("💰 Sales Analytics")
st.markdown("##### Revenue trends, top products, and profit analysis")

# Sidebar - Filters
with st.sidebar:
    st.markdown("## 📅 Date Range")
    date_range = st.date_input(
        "Select Period",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now(),
        key="sales_date_range"
    )
    
    st.markdown("## 🔍 Filters")
    
    # SKU Filter (will populate after data load)
    sku_filter = st.multiselect(
        "Filter by SKU",
        options=st.session_state.get('available_skus', []),
        default=[],
        key="sales_sku_filter"
    )
    
    if st.button("🔄 Load Sales Data", use_container_width=True, type="primary"):
        with st.spinner("Loading sales data from MongoDB..."):
            if initialize_connections():
                try:
                    if len(date_range) == 2:
                        start_date = datetime.combine(date_range[0], datetime.min.time())
                        end_date = datetime.combine(date_range[1], datetime.max.time())
                    else:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=30)
                    
                    # Fetch Sales data from 'Sales' collection
                    sales_df = st.session_state.data_retriever.get_sales_data(start_date, end_date)
                    
                    if not sales_df.empty:
                        # Analyze sales data
                        results = st.session_state.ai_engine.analyze_sales(sales_df)
                        
                        st.session_state.sales_data = {
                            'df': sales_df,
                            'results': results,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                        st.session_state.sales_data_loaded = True
                        
                        # Populate SKU options
                        if 'SKU' in sales_df.columns:
                            st.session_state.available_skus = sorted(sales_df['SKU'].unique().tolist())
                        
                        st.success(f"✅ Loaded {len(sales_df):,} sales records!")
                        st.rerun()
                    else:
                        st.warning("No sales data found for the selected period")
                        
                except Exception as e:
                    st.error(f"Error loading sales data: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📊 Connected Collection")
    st.info("**MongoDB Collection:** Sales")
    st.caption("Real-time data from Sales collection")

# Main Dashboard
if st.session_state.sales_data_loaded and st.session_state.sales_data:
    sales_df = st.session_state.sales_data['df']
    results = st.session_state.sales_data['results']
    
    # Apply SKU filter
    filtered_df = sales_df.copy()
    if sku_filter:
        filtered_df = filtered_df[filtered_df['SKU'].isin(sku_filter)]
        # Recalculate results for filtered data
        results = st.session_state.ai_engine.analyze_sales(filtered_df)
    
    # KPI Row
    st.markdown("### 📈 Key Sales Metrics")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        st.metric("Total Revenue", f"${results['total_revenue']:,.2f}")
    
    with kpi_cols[1]:
        st.metric("Total Profit", f"${results['total_profit']:,.2f}")
    
    with kpi_cols[2]:
        st.metric("Profit Margin", f"{results['profit_margin']:.2f}%")
    
    with kpi_cols[3]:
        total_orders = len(filtered_df)
        st.metric("Total Orders", f"{total_orders:,}")
    
    st.markdown("---")
    
    # Revenue Trend Chart
    st.markdown("### 📊 Revenue Trend Over Time")
    if not results['revenue_trend'].empty:
        fig = px.area(
            results['revenue_trend'],
            x='Date',
            y='Revenue',
            color_discrete_sequence=['#667eea'],
            template='plotly_white',
            labels={'Revenue': 'Revenue ($)', 'Date': ''}
        )
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data available")
    
    # Top Products and Profit Trend
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 10 Products by Revenue")
        if not results['top_products'].empty:
            top_10 = results['top_products'].head(10)
            fig = px.bar(
                top_10,
                x='Revenue',
                y='SKU',
                orientation='h',
                color='Revenue',
                color_continuous_scale='Viridis',
                template='plotly_white',
                labels={'Revenue': 'Revenue ($)', 'SKU': 'Product SKU'}
            )
            fig.update_layout(
                height=500,
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No product data available")
    
    with col2:
        st.markdown("#### 💵 Daily Profit Trend")
        if not results['revenue_trend'].empty:
            fig = px.line(
                results['revenue_trend'],
                x='Date',
                y='Profit',
                color_discrete_sequence=['#10b981'],
                template='plotly_white',
                labels={'Profit': 'Profit ($)', 'Date': ''}
            )
            fig.update_layout(
                height=500,
                margin=dict(l=10, r=10, t=30, b=10),
                showlegend=False,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No profit trend data available")
    
    # Revenue Distribution
    st.markdown("---")
    st.markdown("### 📊 Revenue Distribution by Product")
    
    if not results['top_products'].empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            top_5 = results['top_products'].head(5)
            fig = px.pie(
                top_5,
                values='Revenue',
                names='SKU',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Purples_r,
                template='plotly_white'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Product performance table
            st.markdown("#### 📋 Product Performance")
            display_df = results['top_products'].head(10)[['SKU', 'Revenue', 'Quantity', 'Profit']].copy()
            display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"${x:,.2f}")
            display_df['Profit'] = display_df['Profit'].apply(lambda x: f"${x:,.2f}")
            display_df['Quantity'] = display_df['Quantity'].apply(lambda x: f"{x:,.0f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Detailed Data View
    st.markdown("---")
    st.markdown("### 📋 Detailed Sales Records")
    
    with st.expander("View Raw Data", expanded=False):
        # Display columns selection
        display_cols = st.multiselect(
            "Select columns to display",
            options=filtered_df.columns.tolist(),
            default=['timestamp', 'SKU', 'Revenue', 'Quantity', 'Profit'] if all(col in filtered_df.columns for col in ['timestamp', 'SKU', 'Revenue', 'Quantity', 'Profit']) else filtered_df.columns.tolist()[:5],
            key="sales_display_cols"
        )
        
        if display_cols:
            st.dataframe(
                filtered_df[display_cols].sort_values('timestamp', ascending=False).head(100),
                use_container_width=True,
                hide_index=True
            )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Sales Data (CSV)",
            data=csv,
            file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("📊 **Sales Analytics Dashboard**")
        st.markdown("""
        ### Get Started
        
        1. **Select a date range** in the sidebar
        2. **Click 'Load Sales Data'** to fetch data from MongoDB
        3. **Apply filters** to analyze specific products
        
        #### Available Metrics:
        - **Revenue Trends:** Daily/weekly revenue patterns
        - **Top Products:** Best performing SKUs
        - **Profit Analysis:** Profit margins and trends
        - **Order Volume:** Transaction counts
        
        #### Data Source:
        This page is connected to the **Sales** MongoDB collection and displays real-time sales data.
        """)

# Footer
st.markdown("---")
st.caption("Sales Analytics | Connected to MongoDB 'Sales' Collection")