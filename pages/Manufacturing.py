"""
Manufacturing & Quality Dashboard
Connected to 'Manufacturing' MongoDB collection
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
    page_title="Manufacturing & Quality",
    page_icon="🔧",
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
        background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
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
    
    /* Alert badge */
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
if 'manufacturing_data_loaded' not in st.session_state:
    st.session_state.manufacturing_data_loaded = False
if 'manufacturing_data' not in st.session_state:
    st.session_state.manufacturing_data = None

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
st.title("🔧 Manufacturing & Quality Control")
st.markdown("##### Production monitoring, defect rates, and quality metrics")

# Sidebar - Filters
with st.sidebar:
    st.markdown("## 📅 Date Range")
    date_range = st.date_input(
        "Select Period",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now(),
        key="manufacturing_date_range"
    )
    
    st.markdown("## 🔍 Filters")
    
    # Line ID Filter
    line_filter = st.multiselect(
        "Filter by Production Line",
        options=st.session_state.get('available_lines', []),
        default=[],
        key="manufacturing_line_filter"
    )
    
    # SKU Filter
    sku_filter = st.multiselect(
        "Filter by Product SKU",
        options=st.session_state.get('available_mfg_skus', []),
        default=[],
        key="manufacturing_sku_filter"
    )
    
    if st.button("🔄 Load Manufacturing Data", use_container_width=True, type="primary"):
        with st.spinner("Loading manufacturing data from MongoDB..."):
            if initialize_connections():
                try:
                    if len(date_range) == 2:
                        start_date = datetime.combine(date_range[0], datetime.min.time())
                        end_date = datetime.combine(date_range[1], datetime.max.time())
                    else:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=30)
                    
                    # Fetch Manufacturing data from 'Manufacturing' collection
                    manufacturing_df = st.session_state.data_retriever.get_manufacturing_data(start_date, end_date)
                    
                    if not manufacturing_df.empty:
                        # Analyze manufacturing data
                        results = st.session_state.ai_engine.analyze_quality(manufacturing_df)
                        
                        st.session_state.manufacturing_data = {
                            'df': manufacturing_df,
                            'results': results,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                        st.session_state.manufacturing_data_loaded = True
                        
                        # Populate filter options
                        if 'Line_ID' in manufacturing_df.columns:
                            st.session_state.available_lines = sorted(manufacturing_df['Line_ID'].unique().tolist())
                        if 'SKU' in manufacturing_df.columns:
                            st.session_state.available_mfg_skus = sorted(manufacturing_df['SKU'].unique().tolist())
                        
                        st.success(f"✅ Loaded {len(manufacturing_df):,} production records!")
                        st.rerun()
                    else:
                        st.warning("No manufacturing data found for the selected period")
                        
                except Exception as e:
                    st.error(f"Error loading manufacturing data: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📊 Connected Collection")
    st.info("**MongoDB Collection:** Manufacturing")
    st.caption("Real-time production data")

# Main Dashboard
if st.session_state.manufacturing_data_loaded and st.session_state.manufacturing_data:
    manufacturing_df = st.session_state.manufacturing_data['df']
    results = st.session_state.manufacturing_data['results']
    
    # Apply filters
    filtered_df = manufacturing_df.copy()
    if line_filter:
        filtered_df = filtered_df[filtered_df['Line_ID'].isin(line_filter)]
    if sku_filter:
        filtered_df = filtered_df[filtered_df['SKU'].isin(sku_filter)]
    
    # Recalculate results for filtered data
    if line_filter or sku_filter:
        results = st.session_state.ai_engine.analyze_quality(filtered_df)
    
    # KPI Row
    st.markdown("### 📈 Key Quality Metrics")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        defect_rate = results['avg_defect_rate']
        delta_color = "inverse" if defect_rate > 5 else "normal"
        st.metric("Avg Defect Rate", f"{defect_rate:.2f}%", 
                 delta=f"Target: 5.0%" if defect_rate > 5 else "Within target")
    
    with kpi_cols[1]:
        st.metric("Total Produced", f"{results['total_produced']:,.0f}")
    
    with kpi_cols[2]:
        st.metric("Total Defects", f"{results['total_defects']:,.0f}")
    
    with kpi_cols[3]:
        quality_rate = 100 - defect_rate
        st.metric("Quality Rate", f"{quality_rate:.2f}%")
    
    # Quality Status Alert
    st.markdown("---")
    if defect_rate > 10:
        st.markdown('<div class="alert-badge alert-critical">⚠️ CRITICAL: Defect rate exceeds 10%</div>', unsafe_allow_html=True)
    elif defect_rate > 5:
        st.markdown('<div class="alert-badge alert-warning">⚡ WARNING: Defect rate above target (5%)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-badge alert-good">✅ GOOD: Quality metrics within acceptable range</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Defect Rate Trend
    st.markdown("### 📊 Defect Rate Trend Over Time")
    if not results['defect_trend'].empty:
        fig = px.line(
            results['defect_trend'],
            x='Date',
            y='Defect_Rate',
            color_discrete_sequence=['#f59e0b'],
            template='plotly_white',
            labels={'Defect_Rate': 'Defect Rate (%)', 'Date': ''}
        )
        fig.add_hline(y=5, line_dash="dash", line_color="red", opacity=0.5, 
                     annotation_text="Target Threshold (5%)", annotation_position="right")
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
    
    # Production Line Performance
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏭 Production Line Performance")
        if not results['line_performance'].empty:
            # Color code by defect rate
            line_perf = results['line_performance'].copy()
            line_perf['Status'] = line_perf['Defect_Rate'].apply(
                lambda x: 'Critical' if x > 10 else ('Warning' if x > 5 else 'Good')
            )
            
            fig = px.bar(
                line_perf,
                x='Line_ID',
                y='Defect_Rate',
                color='Status',
                color_discrete_map={'Good': '#10b981', 'Warning': '#f59e0b', 'Critical': '#ef4444'},
                template='plotly_white',
                labels={'Defect_Rate': 'Defect Rate (%)', 'Line_ID': 'Production Line'}
            )
            fig.add_hline(y=5, line_dash="dash", line_color="gray", opacity=0.5)
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(title="Status")
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No line performance data available")
    
    with col2:
        st.markdown("### 📊 Production Volume by Line")
        if not results['line_performance'].empty:
            fig = px.pie(
                results['line_performance'],
                values='Quantity_Produced',
                names='Line_ID',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r,
                template='plotly_white'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No production volume data available")
    
    # Anomalies and Issues
    st.markdown("---")
    st.markdown("### ⚠️ Quality Alerts & Anomalies")
    
    if results['anomalies']:
        st.warning(f"**{len(results['anomalies'])} production lines** have defect rates above 5% threshold")
        
        # Show anomalous lines
        anomaly_df = results['line_performance'][results['line_performance']['Line_ID'].isin(results['anomalies'])].copy()
        anomaly_df = anomaly_df.sort_values('Defect_Rate', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(
                anomaly_df[['Line_ID', 'Defect_Rate', 'Quantity_Produced', 'Defects']],
                use_container_width=True,
                hide_index=True
            )
        with col2:
            st.markdown("#### Recommended Actions:")
            for line in results['anomalies'][:3]:
                st.markdown(f"- 🔧 Inspect Line **{line}**")
            st.markdown("- 📋 Review QA protocols")
            st.markdown("- 👥 Check operator training")
    else:
        st.success("✅ **All production lines operating within quality standards!**")
        st.caption("No lines have defect rates exceeding 5%")
    
    # Production Stats Table
    st.markdown("---")
    st.markdown("### 📋 Line Performance Summary")
    
    if not results['line_performance'].empty:
        display_df = results['line_performance'].copy()
        display_df['Defect_Rate'] = display_df['Defect_Rate'].apply(lambda x: f"{x:.2f}%")
        display_df['Quantity_Produced'] = display_df['Quantity_Produced'].apply(lambda x: f"{x:,.0f}")
        display_df['Defects'] = display_df['Defects'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Daily Production Heatmap
    if 'timestamp' in filtered_df.columns and 'Line_ID' in filtered_df.columns:
        st.markdown("---")
        st.markdown("### 🗓️ Daily Production Heatmap")
        
        heatmap_df = filtered_df.copy()
        heatmap_df['Date'] = pd.to_datetime(heatmap_df['timestamp']).dt.date
        heatmap_pivot = heatmap_df.groupby(['Date', 'Line_ID'])['Quantity_Produced'].sum().reset_index()
        heatmap_pivot = heatmap_pivot.pivot(index='Line_ID', columns='Date', values='Quantity_Produced').fillna(0)
        
        fig = px.imshow(
            heatmap_pivot,
            color_continuous_scale='YlOrRd',
            aspect='auto',
            labels=dict(x="Date", y="Production Line", color="Quantity"),
            template='plotly_white'
        )
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Data View
    st.markdown("---")
    st.markdown("### 📋 Detailed Manufacturing Records")
    
    with st.expander("View Raw Data", expanded=False):
        # Display columns selection
        display_cols = st.multiselect(
            "Select columns to display",
            options=filtered_df.columns.tolist(),
            default=['timestamp', 'Line_ID', 'SKU', 'Quantity_Produced', 'Defects', 'Defect_Rate'] if all(col in filtered_df.columns for col in ['timestamp', 'Line_ID', 'SKU', 'Quantity_Produced', 'Defects', 'Defect_Rate']) else filtered_df.columns.tolist()[:6],
            key="manufacturing_display_cols"
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
            label="📥 Download Manufacturing Data (CSV)",
            data=csv,
            file_name=f"manufacturing_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("🔧 **Manufacturing & Quality Dashboard**")
        st.markdown("""
        ### Get Started
        
        1. **Select a date range** in the sidebar
        2. **Click 'Load Manufacturing Data'** to fetch production data
        3. **Apply filters** to analyze specific lines or products
        
        #### Available Metrics:
        - **Defect Rates:** Track quality across production lines
        - **Production Volume:** Monitor output by line
        - **Quality Trends:** Identify patterns over time
        - **Anomaly Detection:** Spot lines exceeding thresholds
        
        #### Data Source:
        This page is connected to the **Manufacturing** MongoDB collection with real-time production and quality control data.
        """)

# Footer
st.markdown("---")
st.caption("Manufacturing & Quality Control | Connected to MongoDB 'Manufacturing' Collection")