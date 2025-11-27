"""
Testing & Quality Assurance Dashboard
Connected to 'Testing' MongoDB collection
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
    page_title="Testing & QA",
    page_icon="🧪",
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
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
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
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .status-excellent {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-good {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-critical {
        background-color: #fee2e2;
        color: #991b1b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_retriever' not in st.session_state:
    st.session_state.data_retriever = None
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'testing_data_loaded' not in st.session_state:
    st.session_state.testing_data_loaded = False
if 'testing_data' not in st.session_state:
    st.session_state.testing_data = None

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
st.title("🧪 Testing & Quality Assurance")
st.markdown("##### Test results, pass rates, and quality validation")

# Sidebar - Filters
with st.sidebar:
    st.markdown("## 📅 Date Range")
    date_range = st.date_input(
        "Select Period",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now(),
        key="testing_date_range"
    )
    
    st.markdown("## 🔍 Filters")
    
    # Batch ID Filter
    batch_filter = st.multiselect(
        "Filter by Batch ID",
        options=st.session_state.get('available_batches', []),
        default=[],
        key="testing_batch_filter"
    )
    
    # Status Filter
    status_filter = st.selectbox(
        "Filter by Test Status",
        options=["All", "Passed", "Failed"],
        index=0,
        key="testing_status_filter"
    )
    
    if st.button("🔄 Load Testing Data", use_container_width=True, type="primary"):
        with st.spinner("Loading testing data from MongoDB..."):
            if initialize_connections():
                try:
                    if len(date_range) == 2:
                        start_date = datetime.combine(date_range[0], datetime.min.time())
                        end_date = datetime.combine(date_range[1], datetime.max.time())
                    else:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=30)
                    
                    # Fetch Testing data from 'Testing' collection
                    testing_df = st.session_state.data_retriever.get_testing_data(start_date, end_date)
                    
                    if not testing_df.empty:
                        # Analyze testing data
                        results = st.session_state.ai_engine.analyze_testing(testing_df)
                        
                        st.session_state.testing_data = {
                            'df': testing_df,
                            'results': results,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                        st.session_state.testing_data_loaded = True
                        
                        # Populate filter options
                        if 'Batch_ID' in testing_df.columns:
                            st.session_state.available_batches = sorted(testing_df['Batch_ID'].unique().tolist())
                        
                        st.success(f"✅ Loaded {len(testing_df):,} test records!")
                        st.rerun()
                    else:
                        st.warning("No testing data found for the selected period")
                        
                except Exception as e:
                    st.error(f"Error loading testing data: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📊 Connected Collection")
    st.info("**MongoDB Collection:** Testing")
    st.caption("Real-time QA test data")

# Main Dashboard
if st.session_state.testing_data_loaded and st.session_state.testing_data:
    testing_df = st.session_state.testing_data['df']
    results = st.session_state.testing_data['results']
    
    # Apply filters
    filtered_df = testing_df.copy()
    if batch_filter:
        filtered_df = filtered_df[filtered_df['Batch_ID'].isin(batch_filter)]
    
    if status_filter != "All" and 'Pass_Fail_Status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Pass_Fail_Status'].str.lower() == status_filter.lower()]
    
    # Recalculate results for filtered data
    if batch_filter or status_filter != "All":
        results = st.session_state.ai_engine.analyze_testing(filtered_df)
    
    # KPI Row
    st.markdown("### 📈 Key Testing Metrics")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        pass_rate = results['pass_rate']
        st.metric("Pass Rate", f"{pass_rate:.2f}%")
    
    with kpi_cols[1]:
        st.metric("Total Tests", f"{results['total_tests']:,}")
    
    with kpi_cols[2]:
        st.metric("Tests Passed", f"{results['total_tests'] - results['failed_tests']:,}")
    
    with kpi_cols[3]:
        st.metric("Tests Failed", f"{results['failed_tests']:,}")
    
    # Quality Status Badge
    st.markdown("---")
    if pass_rate >= 98:
        st.markdown('<div class="status-badge status-excellent">✨ EXCELLENT: Pass rate exceeds 98%</div>', unsafe_allow_html=True)
    elif pass_rate >= 95:
        st.markdown('<div class="status-badge status-good">✅ GOOD: Pass rate above 95%</div>', unsafe_allow_html=True)
    elif pass_rate >= 90:
        st.markdown('<div class="status-badge status-warning">⚡ WARNING: Pass rate below 95%</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-critical">⚠️ CRITICAL: Pass rate below 90%</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pass/Fail Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Test Results Distribution")
        passed = results['total_tests'] - results['failed_tests']
        failed = results['failed_tests']
        
        fig = px.pie(
            names=['Passed', 'Failed'],
            values=[passed, failed],
            hole=0.5,
            color_discrete_sequence=['#10b981', '#ef4444'],
            template='plotly_white'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Pass Rate Gauge")
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pass_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Pass Rate %", 'font': {'size': 24}},
            delta={'reference': 95, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#06b6d4"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 90], 'color': '#fee2e2'},
                    {'range': [90, 95], 'color': '#fef3c7'},
                    {'range': [95, 100], 'color': '#d1fae5'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#1e293b", 'family': "Arial"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Daily Pass Rate Trend
    if 'timestamp' in filtered_df.columns and 'Pass_Fail_Status' in filtered_df.columns:
        st.markdown("---")
        st.markdown("### 📊 Daily Pass Rate Trend")
        
        trend_df = filtered_df.copy()
        trend_df['Date'] = pd.to_datetime(trend_df['timestamp']).dt.date
        
        daily_stats = trend_df.groupby('Date').agg({
            'Pass_Fail_Status': lambda x: (x.str.lower() == 'passed').sum() / len(x) * 100
        }).reset_index()
        daily_stats.columns = ['Date', 'Pass_Rate']
        daily_stats = daily_stats.sort_values('Date')
        
        fig = px.line(
            daily_stats,
            x='Date',
            y='Pass_Rate',
            color_discrete_sequence=['#06b6d4'],
            template='plotly_white',
            labels={'Pass_Rate': 'Pass Rate (%)', 'Date': ''}
        )
        fig.add_hline(y=95, line_dash="dash", line_color="green", opacity=0.5, 
                     annotation_text="Target (95%)", annotation_position="right")
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    # Batch Performance Analysis
    if 'Batch_ID' in filtered_df.columns and 'Pass_Fail_Status' in filtered_df.columns:
        st.markdown("---")
        st.markdown("### 🏭 Batch Performance Analysis")
        
        batch_stats = filtered_df.groupby('Batch_ID').agg({
            'Pass_Fail_Status': [
                'count',
                lambda x: (x.str.lower() == 'passed').sum(),
                lambda x: (x.str.lower() == 'passed').sum() / len(x) * 100
            ]
        }).reset_index()
        batch_stats.columns = ['Batch_ID', 'Total_Tests', 'Passed', 'Pass_Rate']
        batch_stats = batch_stats.sort_values('Pass_Rate', ascending=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Batch Pass Rates")
            fig = px.bar(
                batch_stats.head(15),
                x='Pass_Rate',
                y='Batch_ID',
                orientation='h',
                color='Pass_Rate',
                color_continuous_scale=['#ef4444', '#fbbf24', '#10b981'],
                template='plotly_white',
                labels={'Pass_Rate': 'Pass Rate (%)', 'Batch_ID': 'Batch ID'}
            )
            fig.add_vline(x=95, line_dash="dash", line_color="gray", opacity=0.5)
            fig.update_layout(
                height=500,
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📋 Batch Summary Table")
            display_batch = batch_stats.copy()
            display_batch['Pass_Rate'] = display_batch['Pass_Rate'].apply(lambda x: f"{x:.2f}%")
            display_batch['Total_Tests'] = display_batch['Total_Tests'].apply(lambda x: f"{x:,.0f}")
            display_batch['Passed'] = display_batch['Passed'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                display_batch.head(15),
                use_container_width=True,
                hide_index=True,
                height=500
            )
    
    # Failed Tests Analysis
    st.markdown("---")
    st.markdown("### ⚠️ Failed Tests Analysis")
    
    if results['failed_tests'] > 0:
        failed_df = filtered_df[filtered_df['Pass_Fail_Status'].str.lower() == 'failed']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.warning(f"**{results['failed_tests']} tests failed** in the selected period")
            
            # Show recent failures
            st.markdown("#### Recent Test Failures")
            display_cols = ['timestamp', 'Test_ID', 'Batch_ID', 'Pass_Fail_Status']
            display_cols = [col for col in display_cols if col in failed_df.columns]
            
            if display_cols:
                st.dataframe(
                    failed_df[display_cols].sort_values('timestamp', ascending=False).head(10),
                    use_container_width=True,
                    hide_index=True
                )
        
        with col2:
            st.markdown("#### Recommended Actions")
            st.markdown("- 🔍 Investigate failed batches")
            st.markdown("- 📋 Review test procedures")
            st.markdown("- 🔧 Check equipment calibration")
            st.markdown("- 👥 Verify operator compliance")
            st.markdown("- 📊 Analyze failure patterns")
    else:
        st.success("✅ **No failed tests in the selected period!**")
        st.caption("All tests passed successfully")
    
    # Detailed Data View
    st.markdown("---")
    st.markdown("### 📋 Detailed Testing Records")
    
    with st.expander("View Raw Data", expanded=False):
        # Display columns selection
        display_cols = st.multiselect(
            "Select columns to display",
            options=filtered_df.columns.tolist(),
            default=['timestamp', 'Test_ID', 'Batch_ID', 'Pass_Fail_Status'] if all(col in filtered_df.columns for col in ['timestamp', 'Test_ID', 'Batch_ID', 'Pass_Fail_Status']) else filtered_df.columns.tolist()[:4],
            key="testing_display_cols"
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
            label="📥 Download Testing Data (CSV)",
            data=csv,
            file_name=f"testing_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("🧪 **Testing & Quality Assurance Dashboard**")
        st.markdown("""
        ### Get Started
        
        1. **Select a date range** in the sidebar
        2. **Click 'Load Testing Data'** to fetch QA test results
        3. **Apply filters** to analyze specific batches or test statuses
        
        #### Available Metrics:
        - **Pass Rates:** Overall and daily test success rates
        - **Test Results:** Pass/fail distribution analysis
        - **Batch Performance:** Quality metrics by production batch
        - **Failed Tests:** Detailed failure analysis and trends
        
        #### Data Source:
        This page is connected to the **Testing** MongoDB collection with real-time quality assurance test data.
        """)

# Footer
st.markdown("---")
st.caption("Testing & QA | Connected to MongoDB 'Testing' Collection")