"""
Inventory Management Dashboard
Connected to 'Field' MongoDB collection
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
    page_title="Inventory Management",
    page_icon="📦",
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
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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
    
    /* Alert badges */
    .alert-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .alert-critical {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .alert-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .alert-good {
        background-color: #d1fae5;
        color: #065f46;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_retriever' not in st.session_state:
    st.session_state.data_retriever = None
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'inventory_data_loaded' not in st.session_state:
    st.session_state.inventory_data_loaded = False
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = None

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
st.title("📦 Inventory Management")
st.markdown("##### Stock levels, low stock alerts, and consumption trends")

# Sidebar - Filters
with st.sidebar:
    st.markdown("## 📅 Date Range")
    date_range = st.date_input(
        "Select Period",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        min_value=datetime(1950, 1, 1),
        max_value=datetime(2025, 12, 31),
        key="inventory_date_range"
    )
    
    st.markdown("## 🔍 Filters")
    
    # Store ID Filter
    store_filter = st.multiselect(
        "Filter by Store ID",
        options=st.session_state.get('available_stores', []),
        default=[],
        key="inventory_store_filter"
    )
    
    # Low Stock Alert Filter
    show_low_stock_only = st.checkbox(
        "Show Low Stock Only",
        value=False,
        key="show_low_stock"
    )
    
    if st.button("🔄 Load Inventory Data", use_container_width=True, type="primary"):
        with st.spinner("Loading inventory data from MongoDB..."):
            if initialize_connections():
                try:
                    if len(date_range) == 2:
                        start_date = datetime.combine(date_range[0], datetime.min.time())
                        end_date = datetime.combine(date_range[1], datetime.max.time())
                    else:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=30)
                    
                    # Fetch Field data from 'Field' collection
                    field_df = st.session_state.data_retriever.get_field_data(start_date, end_date)
                    
                    if not field_df.empty:
                        # Analyze inventory data
                        results = st.session_state.ai_engine.analyze_inventory(field_df)
                        
                        st.session_state.inventory_data = {
                            'df': field_df,
                            'results': results,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                        st.session_state.inventory_data_loaded = True
                        
                        # Populate filter options
                        if 'Store_ID' in field_df.columns:
                            st.session_state.available_stores = sorted(field_df['Store_ID'].unique().tolist())
                        
                        st.success(f"✅ Loaded {len(field_df):,} inventory records!")
                        st.rerun()
                    else:
                        st.warning("No inventory data found for the selected period")
                        
                except Exception as e:
                    st.error(f"Error loading inventory data: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📊 Connected Collection")
    st.info("**MongoDB Collection:** Field")
    st.caption("Real-time inventory data")

# Main Dashboard
if st.session_state.inventory_data_loaded and st.session_state.inventory_data:
    field_df = st.session_state.inventory_data['df']
    results = st.session_state.inventory_data['results']
    
    # Apply filters
    filtered_df = field_df.copy()
    if store_filter:
        filtered_df = filtered_df[filtered_df['Store_ID'].isin(store_filter)]
    
    if show_low_stock_only and 'Low_Stock_Alerts' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Low_Stock_Alerts'] > 0]
    
    # Recalculate results for filtered data
    if store_filter or show_low_stock_only:
        results = st.session_state.ai_engine.analyze_inventory(filtered_df)
    
    # KPI Row
    st.markdown("### 📈 Key Inventory Metrics")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        st.metric("Total Inventory", f"{results['total_inventory']:,.0f}")
    
    with kpi_cols[1]:
        st.metric("Low Stock Alerts", f"{results['low_stock_alerts']:,.0f}")
    
    with kpi_cols[2]:
        avg_days = results['avg_days_to_depletion']
        st.metric("Avg Days to Depletion", f"{avg_days:.1f}" if avg_days > 0 else "N/A")
    
    with kpi_cols[3]:
        critical_stores = len(results['critical_stores'])
        st.metric("Critical Stores", f"{critical_stores}")
    
    # Inventory Status Alert
    st.markdown("---")
    if results['low_stock_alerts'] > 10:
        st.markdown('<div class="alert-badge alert-critical">⚠️ CRITICAL: High number of low stock alerts</div>', unsafe_allow_html=True)
    elif results['low_stock_alerts'] > 5:
        st.markdown('<div class="alert-badge alert-warning">⚡ WARNING: Multiple low stock alerts</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-badge alert-good">✅ GOOD: Inventory levels adequate</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Inventory Trend
    st.markdown("### 📊 Inventory Level Trend")
    if not results['inventory_trend'].empty:
        fig = px.area(
            results['inventory_trend'],
            x='Date',
            y='Inventory_Level',
            color_discrete_sequence=['#10b981'],
            template='plotly_white',
            labels={'Inventory_Level': 'Inventory Level', 'Date': ''}
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
    
    # Store Analysis
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏪 Top Stores by Inventory Level")
        if 'Store_ID' in filtered_df.columns and 'Inventory_Level' in filtered_df.columns:
            store_inv = filtered_df.groupby('Store_ID')['Inventory_Level'].mean().reset_index()
            store_inv = store_inv.sort_values('Inventory_Level', ascending=False).head(10)
            
            fig = px.bar(
                store_inv,
                x='Store_ID',
                y='Inventory_Level',
                color='Inventory_Level',
                color_continuous_scale='Greens',
                template='plotly_white',
                labels={'Inventory_Level': 'Avg Inventory Level', 'Store_ID': 'Store ID'}
            )
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No store inventory data available")
    
    with col2:
        st.markdown("### 📉 Daily Consumption Trend")
        if 'timestamp' in filtered_df.columns and 'Daily_Consumption' in filtered_df.columns:
            cons_df = filtered_df.copy()
            cons_df['Date'] = pd.to_datetime(cons_df['timestamp']).dt.date
            daily_cons = cons_df.groupby('Date')['Daily_Consumption'].sum().reset_index()
            daily_cons = daily_cons.sort_values('Date')
            
            fig = px.line(
                daily_cons,
                x='Date',
                y='Daily_Consumption',
                color_discrete_sequence=['#f59e0b'],
                template='plotly_white',
                labels={'Daily_Consumption': 'Total Consumption', 'Date': ''}
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
            st.info("No consumption data available")
    
    # Critical Stores Alert
    st.markdown("---")
    st.markdown("### ⚠️ Critical Inventory Alerts")
    
    if not results['critical_stores'].empty:
        st.warning(f"**{len(results['critical_stores'])} stores** have less than 7 days of inventory remaining")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🚨 Critical Stores (< 7 Days)")
            critical_display = results['critical_stores'].copy()
            critical_display['Days_to_Depletion'] = critical_display['Days_to_Depletion'].apply(lambda x: f"{x:.1f}")
            critical_display['Inventory_Level'] = critical_display['Inventory_Level'].apply(lambda x: f"{x:,.0f}")
            critical_display['Daily_Consumption'] = critical_display['Daily_Consumption'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                critical_display,
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("#### 📋 Action Items")
            st.markdown("- 🚚 Prioritize replenishment")
            st.markdown("- 📞 Contact store managers")
            st.markdown("- 📊 Review consumption patterns")
            st.markdown("- 🔄 Adjust reorder points")
            st.markdown("- 📈 Monitor daily")
            
            # Days to depletion distribution
            if 'Days_to_Depletion' in results['critical_stores'].columns:
                st.markdown("#### ⏱️ Urgency Distribution")
                fig = px.histogram(
                    results['critical_stores'],
                    x='Days_to_Depletion',
                    nbins=7,
                    color_discrete_sequence=['#ef4444'],
                    template='plotly_white',
                    labels={'Days_to_Depletion': 'Days Remaining', 'count': 'Stores'}
                )
                fig.update_layout(
                    height=250,
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ **All stores have adequate inventory levels!**")
        st.caption("No stores are critically low on inventory")
    
    # Low Stock Alerts Over Time
    if not results['inventory_trend'].empty and 'Low_Stock_Alerts' in results['inventory_trend'].columns:
        st.markdown("---")
        st.markdown("### 📊 Low Stock Alerts Over Time")
        
        fig = px.bar(
            results['inventory_trend'],
            x='Date',
            y='Low_Stock_Alerts',
            color_discrete_sequence=['#ef4444'],
            template='plotly_white',
            labels={'Low_Stock_Alerts': 'Number of Alerts', 'Date': ''}
        )
        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Store Performance Heatmap
    if 'Store_ID' in filtered_df.columns and 'timestamp' in filtered_df.columns:
        st.markdown("---")
        st.markdown("### 🗓️ Store Inventory Heatmap")
        
        heatmap_df = filtered_df.copy()
        heatmap_df['Date'] = pd.to_datetime(heatmap_df['timestamp']).dt.date
        heatmap_pivot = heatmap_df.groupby(['Date', 'Store_ID'])['Inventory_Level'].mean().reset_index()
        heatmap_pivot = heatmap_pivot.pivot(index='Store_ID', columns='Date', values='Inventory_Level').fillna(0)
        
        fig = px.imshow(
            heatmap_pivot,
            color_continuous_scale='Greens',
            aspect='auto',
            labels=dict(x="Date", y="Store ID", color="Inventory"),
            template='plotly_white'
        )
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Data View
    st.markdown("---")
    st.markdown("### 📋 Detailed Inventory Records")
    
    with st.expander("View Raw Data", expanded=False):
        # Display columns selection
        display_cols = st.multiselect(
            "Select columns to display",
            options=filtered_df.columns.tolist(),
            default=['timestamp', 'Store_ID', 'Inventory_Level', 'Low_Stock_Alerts', 'Daily_Consumption', 'Days_to_Depletion'] if all(col in filtered_df.columns for col in ['timestamp', 'Store_ID', 'Inventory_Level', 'Low_Stock_Alerts', 'Daily_Consumption', 'Days_to_Depletion']) else filtered_df.columns.tolist()[:6],
            key="inventory_display_cols"
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
            label="📥 Download Inventory Data (CSV)",
            data=csv,
            file_name=f"inventory_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("📦 **Inventory Management Dashboard**")
        st.markdown("""
        ### Get Started
        
        1. **Select a date range** in the sidebar
        2. **Click 'Load Inventory Data'** to fetch stock data
        3. **Apply filters** to analyze specific stores
        
        #### Available Metrics:
        - **Stock Levels:** Track inventory across stores
        - **Low Stock Alerts:** Identify stores needing replenishment
        - **Consumption Trends:** Monitor usage patterns
        - **Days to Depletion:** Predict when stock will run out
        
        #### Data Source:
        This page is connected to the **Field** MongoDB collection with real-time inventory and store data.
        """)

# Footer
st.markdown("---")
st.caption("Inventory Management | Connected to MongoDB 'Field' Collection")