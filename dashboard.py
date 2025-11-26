"""
AI-Powered Central Data Platform - Main Dashboard
Professional BI-style interface with dedicated AI Chatbot page
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

# Custom CSS - Light Blue Sidebar with Dark Blue Tabs
st.markdown("""
<style>
    /* Main background and fonts */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #1f77b4;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 500;
        color: #6c757d;
        text-transform: uppercase;
    }
    
    /* Headers */
    h1 {
        color: #212529;
        font-weight: 700;
        padding-bottom: 10px;
        border-bottom: 3px solid #1f77b4;
    }
    
    h2 {
        color: #495057;
        font-weight: 600;
        margin-top: 30px;
    }
    
    h3 {
        color: #6c757d;
        font-weight: 500;
    }
    
    /* LIGHT BLUE SIDEBAR with DARK BLUE TABS */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
        border-right: 2px solid #90caf9;
    }
    
    /* Sidebar headings - Dark Blue */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0d47a1 !important;
        font-weight: 700;
    }
    
    /* Sidebar text - Dark color for readability */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #1565c0 !important;
        font-weight: 500;
    }
    
    /* Navigation Tab Buttons - DARK BLUE */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        background-color: #1565c0;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #0d47a1;
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    /* Active page highlight */
    section[data-testid="stSidebar"] .stButton button:active {
        background-color: #0a3d91;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: #ffffff;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* AI Chatbot Page Styling */
    .chat-page-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .chat-history-container {
        height: 600px;
        overflow-y: auto;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 2px solid #dee2e6;
    }
    
    /* Chat Message - User */
    .chat-message-user {
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 10px 0;
        margin-left: 25%;
        box-shadow: 0 2px 8px rgba(21, 101, 192, 0.3);
        word-wrap: break-word;
        font-size: 15px;
    }
    
    /* Chat Message - Assistant */
    .chat-message-assistant {
        background-color: #ffffff;
        color: #212529;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 10px 0;
        margin-right: 25%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 2px solid #e3f2fd;
        word-wrap: break-word;
        font-size: 15px;
    }
    
    /* Timestamp */
    .chat-timestamp {
        font-size: 11px;
        color: #6c757d;
        margin-top: 4px;
        text-align: right;
    }
    
    /* Chat message timestamp for user messages */
    .chat-message-user .chat-timestamp {
        color: rgba(255,255,255,0.8);
    }
    
    /* AI Badge */
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    /* Chat input styling */
    .chat-input-section {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        border: 2px solid #e3f2fd;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background-color: #dee2e6;
    }
    
    /* Date input in sidebar */
    section[data-testid="stSidebar"] .stDateInput label {
        color: #0d47a1 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'data_retriever' not in st.session_state:
    st.session_state.data_retriever = None
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_data_loaded' not in st.session_state:
    st.session_state.chat_data_loaded = False
if 'chat_full_df' not in st.session_state:
    st.session_state.chat_full_df = None


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


def render_chat_message(message, is_user=True):
    """Render a single chat message"""
    timestamp = message.get('timestamp', datetime.now()).strftime('%H:%M')
    
    if is_user:
        st.markdown(f"""
        <div class="chat-message-user">
            {message['text']}
            <div class="chat-timestamp">{timestamp}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message-assistant">
            {message['text']}
            <div class="chat-timestamp">AI Assistant • {timestamp}</div>
        </div>
        """, unsafe_allow_html=True)


def render_ai_chatbot_page():
    """Render the dedicated AI Chatbot page"""
    st.title("🤖 AI Analysis Assistant")
    st.markdown('<div class="ai-badge">✨ Powered by Google Gemini AI</div>', unsafe_allow_html=True)
    st.markdown("##### Ask questions about your data and get instant insights with visualizations")
    
    # Data connection status
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.chat_data_loaded and st.session_state.chat_full_df is not None:
            st.success(f"🟢 Connected to MongoDB | {len(st.session_state.chat_full_df)} records loaded")
        else:
            st.warning("⚠️ Not connected to data source")
    
    with col2:
        if not st.session_state.chat_data_loaded:
            if st.button("📊 Load Data", use_container_width=True, type="primary"):
                with st.spinner("Loading real-time data from MongoDB..."):
                    try:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=30)
                        
                        st.session_state.chat_full_df = st.session_state.data_retriever.fetch_all_data(
                            start_date, end_date
                        )
                        
                        if st.session_state.chat_full_df is not None and not st.session_state.chat_full_df.empty:
                            st.session_state.chat_data_loaded = True
                            
                            # Add welcome message
                            st.session_state.chat_history.append({
                                'type': 'assistant',
                                'text': f"👋 **Welcome!** I'm your AI Analysis Assistant.\n\n📊 **Connected to MongoDB**\n- Records loaded: **{len(st.session_state.chat_full_df)}**\n- Date range: Last 30 days\n- Domains: Sales, Manufacturing, Testing, Field\n\n💡 **Try asking:**\n- 'Show me sales revenue trends'\n- 'What are the defect rates by production line?'\n- 'Which stores have low inventory?'\n- 'Show testing pass rates'",
                                'timestamp': datetime.now(),
                                'chart': None
                            })
                            st.rerun()
                        else:
                            st.error("❌ No data available for the selected period")
                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")
        else:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.session_state.chat_data_loaded = False
                st.session_state.chat_full_df = None
                st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("---")
    
    # Chat history display
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        for idx, msg in enumerate(st.session_state.chat_history):
            render_chat_message(msg, is_user=(msg['type'] == 'user'))
            
            # Display chart if available
            if msg.get('chart') is not None:
                st.plotly_chart(msg['chart'], use_container_width=True, key=f"chat_chart_{idx}")
    else:
        st.info("""
        ### 👋 How can I help you today?
        
        I can help you analyze your business data across multiple domains:
        
        **📈 Sales & Revenue**
        - "Show me total revenue for last month"
        - "Which products have the highest sales?"
        
        **🔧 Manufacturing & Quality**
        - "What are the defect rates by production line?"
        - "Show manufacturing trends"
        
        **📦 Inventory & Field**
        - "Which stores are running low on inventory?"
        - "Show inventory levels over time"
        
        **🧪 Testing & Quality Assurance**
        - "What's the test pass rate?"
        - "Show failed tests by batch"
        
        **Get started by loading data above!**
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input section
    st.markdown('<div class="chat-input-section">', unsafe_allow_html=True)
    
    with st.form(key='chat_input_form', clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Your Question",
                placeholder="Ask me anything about your data...",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Send 📤", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process chat input
    if submit_button and user_input:
        if not st.session_state.chat_data_loaded:
            st.error("⚠️ Please load data first by clicking the 'Load Data' button above!")
        else:
            # Add user message to history
            st.session_state.chat_history.append({
                'type': 'user',
                'text': user_input,
                'timestamp': datetime.now(),
                'chart': None
            })
            
            # Process with AI
            with st.spinner("🤖 AI is analyzing your query..."):
                # Prepare chat history for context
                chat_context = []
                for i in range(0, len(st.session_state.chat_history) - 1, 2):
                    if i + 1 < len(st.session_state.chat_history):
                        chat_context.append({
                            'user': st.session_state.chat_history[i]['text'],
                            'assistant': st.session_state.chat_history[i + 1].get('text', '')
                        })
                
                response_text, fig = st.session_state.ai_engine.process_chat_query(
                    user_input,
                    st.session_state.chat_full_df,
                    chat_context
                )
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    'type': 'assistant',
                    'text': response_text,
                    'timestamp': datetime.now(),
                    'chart': fig
                })
            
            st.rerun()


def render_home_overview(data_dict, results):
    """Render the home overview dashboard"""
    st.title("📊 Overview Dashboard")
    st.markdown("##### Real-time insights across all domains")
    
    # Top KPI Row - 4 key metrics
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
    
    # 4 Chart Grid - One per domain
    st.markdown("### Domain Snapshots")
    
    chart_row_1 = st.columns(2)
    chart_row_2 = st.columns(2)
    
    # Sales Chart
    with chart_row_1[0]:
        st.markdown("**📈 Sales Revenue Trend**")
        if not results['sales']['revenue_trend'].empty:
            fig = px.area(
                results['sales']['revenue_trend'],
                x='Date',
                y='Revenue',
                color_discrete_sequence=['#667eea'],
                template='plotly_white'
            )
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Revenue ($)"
            )
            st.plotly_chart(fig, use_container_width=True, key="home_sales")
        else:
            st.info("No sales data available")
    
    # Manufacturing/Quality Chart
    with chart_row_1[1]:
        st.markdown("**🔧 Defect Rate Trend**")
        if not results['quality']['defect_trend'].empty:
            fig = px.line(
                results['quality']['defect_trend'],
                x='Date',
                y='Defect_Rate',
                color_discrete_sequence=['#f59e0b'],
                template='plotly_white'
            )
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Defect Rate (%)"
            )
            fig.add_hline(y=5, line_dash="dash", line_color="red", opacity=0.5)
            st.plotly_chart(fig, use_container_width=True, key="home_quality")
        else:
            st.info("No quality data available")
    
    # Inventory Chart
    with chart_row_2[0]:
        st.markdown("**📦 Inventory Levels**")
        if not results['inventory']['inventory_trend'].empty:
            fig = px.bar(
                results['inventory']['inventory_trend'],
                x='Date',
                y='Inventory_Level',
                color_discrete_sequence=['#10b981'],
                template='plotly_white'
            )
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Inventory (Units)"
            )
            st.plotly_chart(fig, use_container_width=True, key="home_inventory")
        else:
            st.info("No inventory data available")
    
    # Testing Chart
    with chart_row_2[1]:
        st.markdown("**🧪 Test Results**")
        if results['testing']['total_tests'] > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Passed', 'Failed'],
                values=[
                    results['testing']['total_tests'] - results['testing']['failed_tests'],
                    results['testing']['failed_tests']
                ],
                marker=dict(colors=['#10b981', '#ef4444']),
                hole=0.5
            )])
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True, key="home_testing")
        else:
            st.info("No testing data available")


def render_sales_dashboard(data_dict, results):
    """Render dedicated Sales dashboard with filters"""
    st.title("📈 Sales & Revenue")
    
    # Filters in columns
    filter_cols = st.columns(3)
    with filter_cols[0]:
        sku_options = []
        if not data_dict['sales'].empty and 'SKU' in data_dict['sales'].columns:
            sku_options = ['All'] + sorted(data_dict['sales']['SKU'].unique().tolist())
        selected_sku = st.selectbox("Product SKU", sku_options, key="sales_sku_filter")
    
    with filter_cols[1]:
        aggregation = st.selectbox("Aggregate By", ["Daily", "Weekly", "Monthly"], key="sales_agg")
    
    with filter_cols[2]:
        top_n = st.slider("Top N Products", 5, 20, 10, key="sales_top_n")
    
    # Filter data
    filtered_sales = data_dict['sales'].copy()
    if selected_sku != 'All' and 'SKU' in filtered_sales.columns:
        filtered_sales = filtered_sales[filtered_sales['SKU'] == selected_sku]
    
    # Recalculate with filtered data
    sales_results = st.session_state.ai_engine.analyze_sales(filtered_sales)
    
    st.markdown("---")
    
    # KPIs
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        create_kpi_card("Total Revenue", sales_results['total_revenue'], "currency")
    with kpi_cols[1]:
        create_kpi_card("Total Profit", sales_results['total_profit'], "currency")
    with kpi_cols[2]:
        create_kpi_card("Profit Margin", sales_results['profit_margin'], "percent")
    with kpi_cols[3]:
        avg_order = sales_results['total_revenue'] / len(filtered_sales) if len(filtered_sales) > 0 else 0
        create_kpi_card("Avg Order Value", avg_order, "currency")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Revenue & Profit Trend")
        if not sales_results['revenue_trend'].empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sales_results['revenue_trend']['Date'],
                y=sales_results['revenue_trend']['Revenue'],
                name='Revenue',
                line=dict(color='#667eea', width=3),
                fill='tonexty',
                fillcolor='rgba(102, 126, 234, 0.1)'
            ))
            fig.add_trace(go.Scatter(
                x=sales_results['revenue_trend']['Date'],
                y=sales_results['revenue_trend']['Profit'],
                name='Profit',
                line=dict(color='#764ba2', width=3)
            ))
            fig.update_layout(
                template='plotly_white',
                hovermode='x unified',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True, key="sales_trend")
        else:
            st.info("No trend data available")
    
    with col2:
        st.markdown(f"### Top {top_n} Products by Revenue")
        if not sales_results['top_products'].empty:
            top_products_limited = sales_results['top_products'].head(top_n)
            fig = px.bar(
                top_products_limited,
                x='Revenue',
                y='SKU',
                orientation='h',
                color='Profit',
                color_continuous_scale='Purples',
                template='plotly_white'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis_title="Revenue ($)",
                yaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, key="sales_top_products")
        else:
            st.info("No product data available")
    
    # Detailed table
    st.markdown("### Detailed Sales Data")
    if not sales_results['top_products'].empty:
        st.dataframe(
            sales_results['top_products'],
            use_container_width=True,
            hide_index=True,
            height=300
        )


def render_manufacturing_dashboard(data_dict, results):
    """Render dedicated Manufacturing/Quality dashboard with filters"""
    st.title("🔧 Manufacturing & Quality")
    
    # Filters
    filter_cols = st.columns(3)
    with filter_cols[0]:
        line_options = []
        if not data_dict['manufacturing'].empty and 'Line_ID' in data_dict['manufacturing'].columns:
            line_options = ['All'] + sorted(data_dict['manufacturing']['Line_ID'].unique().tolist())
        selected_line = st.selectbox("Production Line", line_options, key="mfg_line_filter")
    
    with filter_cols[1]:
        defect_threshold = st.slider("Defect Threshold (%)", 1.0, 10.0, 5.0, 0.5, key="mfg_threshold")
    
    with filter_cols[2]:
        show_anomalies = st.checkbox("Show Only Anomalies", False, key="mfg_anomalies")
    
    # Filter data
    filtered_mfg = data_dict['manufacturing'].copy()
    if selected_line != 'All' and 'Line_ID' in filtered_mfg.columns:
        filtered_mfg = filtered_mfg[filtered_mfg['Line_ID'] == selected_line]
    
    # Recalculate
    quality_results = st.session_state.ai_engine.analyze_quality(filtered_mfg)
    
    st.markdown("---")
    
    # KPIs
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        create_kpi_card("Avg Defect Rate", quality_results['avg_defect_rate'], "percent")
    with kpi_cols[1]:
        create_kpi_card("Total Produced", quality_results['total_produced'])
    with kpi_cols[2]:
        create_kpi_card("Total Defects", quality_results['total_defects'])
    with kpi_cols[3]:
        anomaly_count = len(quality_results['anomalies'])
        create_kpi_card("Anomalies", anomaly_count)
    
    st.markdown("---")
    
    # Alert
    if quality_results['anomalies']:
        st.warning(f"⚠️ **{len(quality_results['anomalies'])} production line(s)** exceed {defect_threshold}% defect threshold: {', '.join(map(str, quality_results['anomalies']))}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Defect Rate Over Time")
        if not quality_results['defect_trend'].empty:
            fig = px.area(
                quality_results['defect_trend'],
                x='Date',
                y='Defect_Rate',
                color_discrete_sequence=['#f59e0b'],
                template='plotly_white'
            )
            fig.add_hline(y=defect_threshold, line_dash="dash", line_color="red", 
                         annotation_text=f"{defect_threshold}% Threshold")
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                yaxis_title="Defect Rate (%)",
                xaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True, key="mfg_trend")
        else:
            st.info("No defect trend data available")
    
    with col2:
        st.markdown("### Production Line Performance")
        if not quality_results['line_performance'].empty:
            line_perf = quality_results['line_performance']
            if show_anomalies:
                line_perf = line_perf[line_perf['Defect_Rate'] > defect_threshold]
            
            fig = px.bar(
                line_perf,
                x='Line_ID',
                y='Defect_Rate',
                color='Defect_Rate',
                color_continuous_scale='RdYlGn_r',
                template='plotly_white'
            )
            fig.add_hline(y=defect_threshold, line_dash="dash", line_color="red")
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                yaxis_title="Defect Rate (%)",
                xaxis_title="Production Line"
            )
            st.plotly_chart(fig, use_container_width=True, key="mfg_lines")
        else:
            st.info("No line performance data available")
    
    # Production output chart
    st.markdown("### Production Output & Defects")
    if not quality_results['line_performance'].empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=quality_results['line_performance']['Line_ID'],
            y=quality_results['line_performance']['Quantity_Produced'],
            name='Produced',
            marker_color='#10b981'
        ))
        fig.add_trace(go.Bar(
            x=quality_results['line_performance']['Line_ID'],
            y=quality_results['line_performance']['Defects'],
            name='Defects',
            marker_color='#ef4444'
        ))
        fig.update_layout(
            template='plotly_white',
            height=350,
            margin=dict(l=0, r=0, t=20, b=0),
            barmode='group',
            xaxis_title="Production Line",
            yaxis_title="Units"
        )
        st.plotly_chart(fig, use_container_width=True, key="mfg_output")


def render_inventory_dashboard(data_dict, results):
    """Render dedicated Inventory/Field dashboard with filters"""
    st.title("📦 Inventory & Field Management")
    
    # Filters
    filter_cols = st.columns(3)
    with filter_cols[0]:
        store_options = []
        if not data_dict['field'].empty and 'Store_ID' in data_dict['field'].columns:
            store_options = ['All'] + sorted(data_dict['field']['Store_ID'].unique().tolist())
        selected_store = st.selectbox("Store", store_options, key="inv_store_filter")
    
    with filter_cols[1]:
        critical_days = st.slider("Critical Days Threshold", 3, 14, 7, key="inv_critical_days")
    
    with filter_cols[2]:
        sort_by = st.selectbox("Sort By", ["Days to Depletion", "Inventory Level", "Store ID"], key="inv_sort")
    
    # Filter data
    filtered_field = data_dict['field'].copy()
    if selected_store != 'All' and 'Store_ID' in filtered_field.columns:
        filtered_field = filtered_field[filtered_field['Store_ID'] == selected_store]
    
    # Recalculate
    inventory_results = st.session_state.ai_engine.analyze_inventory(filtered_field)
    
    st.markdown("---")
    
    # KPIs
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        create_kpi_card("Total Inventory", inventory_results['total_inventory'])
    with kpi_cols[1]:
        create_kpi_card("Low Stock Alerts", inventory_results['low_stock_alerts'])
    with kpi_cols[2]:
        days_val = inventory_results['avg_days_to_depletion']
        st.metric("Avg Days to Depletion", f"{days_val:.1f}")
    with kpi_cols[3]:
        critical_count = len(inventory_results['critical_stores']) if not inventory_results['critical_stores'].empty else 0
        create_kpi_card("Critical Stores", critical_count)
    
    st.markdown("---")
    
    # Critical stores alert
    if not inventory_results['critical_stores'].empty:
        critical_df = inventory_results['critical_stores']
        critical_df = critical_df[critical_df['Days_to_Depletion'] < critical_days]
        if not critical_df.empty:
            st.error(f"🚨 **{len(critical_df)} store(s)** have less than {critical_days} days of inventory!")
            
            # Sort critical stores
            if sort_by == "Days to Depletion":
                critical_df = critical_df.sort_values('Days_to_Depletion')
            elif sort_by == "Inventory Level":
                critical_df = critical_df.sort_values('Inventory_Level')
            else:
                critical_df = critical_df.sort_values('Store_ID')
            
            st.dataframe(
                critical_df,
                use_container_width=True,
                hide_index=True,
                height=200
            )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Inventory Level Trend")
        if not inventory_results['inventory_trend'].empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=inventory_results['inventory_trend']['Date'],
                y=inventory_results['inventory_trend']['Inventory_Level'],
                name='Inventory',
                line=dict(color='#10b981', width=3),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)'
            ))
            fig.update_layout(
                template='plotly_white',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                yaxis_title="Inventory (Units)",
                xaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, key="inv_trend")
        else:
            st.info("No inventory trend available")
    
    with col2:
        st.markdown("### Low Stock Alerts")
        if not inventory_results['inventory_trend'].empty:
            fig = px.bar(
                inventory_results['inventory_trend'],
                x='Date',
                y='Low_Stock_Alerts',
                color_discrete_sequence=['#ef4444'],
                template='plotly_white'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                yaxis_title="Alert Count",
                xaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True, key="inv_alerts")
        else:
            st.info("No alert data available")
    
    # Days to depletion by store
    st.markdown("### Days to Depletion by Store")
    if not filtered_field.empty and 'Store_ID' in filtered_field.columns:
        store_summary = filtered_field.groupby('Store_ID').agg({
            'Inventory_Level': 'mean',
            'Daily_Consumption': 'mean'
        }).reset_index()
        store_summary['Days_to_Depletion'] = store_summary['Inventory_Level'] / store_summary['Daily_Consumption']
        store_summary = store_summary.sort_values('Days_to_Depletion')
        
        fig = px.bar(
            store_summary,
            x='Store_ID',
            y='Days_to_Depletion',
            color='Days_to_Depletion',
            color_continuous_scale='RdYlGn',
            template='plotly_white'
        )
        fig.add_hline(y=critical_days, line_dash="dash", line_color="red",
                     annotation_text=f"{critical_days} Days")
        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis_title="Store ID",
            yaxis_title="Days to Depletion"
        )
        st.plotly_chart(fig, use_container_width=True, key="inv_depletion")


def render_testing_dashboard(data_dict, results):
    """Render dedicated Testing dashboard with filters"""
    st.title("🧪 Testing & Quality Assurance")
    
    # Filters
    filter_cols = st.columns(3)
    with filter_cols[0]:
        batch_options = []
        if not data_dict['testing'].empty and 'Batch_ID' in data_dict['testing'].columns:
            batch_options = ['All'] + sorted(data_dict['testing']['Batch_ID'].unique().tolist())
        selected_batch = st.selectbox("Batch ID", batch_options, key="test_batch_filter")
    
    with filter_cols[1]:
        status_filter = st.selectbox("Status", ["All", "Passed", "Failed"], key="test_status")
    
    with filter_cols[2]:
        show_details = st.checkbox("Show Detailed Results", True, key="test_details")
    
    # Filter data
    filtered_testing = data_dict['testing'].copy()
    if selected_batch != 'All' and 'Batch_ID' in filtered_testing.columns:
        filtered_testing = filtered_testing[filtered_testing['Batch_ID'] == selected_batch]
    
    if status_filter != 'All' and 'Pass_Fail_Status' in filtered_testing.columns:
        filtered_testing = filtered_testing[
            filtered_testing['Pass_Fail_Status'].str.lower() == status_filter.lower()
        ]
    
    # Recalculate
    testing_results = st.session_state.ai_engine.analyze_testing(filtered_testing)
    
    st.markdown("---")
    
    # KPIs
    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        create_kpi_card("Total Tests", testing_results['total_tests'])
    with kpi_cols[1]:
        create_kpi_card("Pass Rate", testing_results['pass_rate'], "percent")
    with kpi_cols[2]:
        create_kpi_card("Failed Tests", testing_results['failed_tests'])
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Test Results Distribution")
        if testing_results['total_tests'] > 0:
            passed = testing_results['total_tests'] - testing_results['failed_tests']
            failed = testing_results['failed_tests']
            
            fig = go.Figure(data=[go.Pie(
                labels=['Passed', 'Failed'],
                values=[passed, failed],
                marker=dict(colors=['#10b981', '#ef4444']),
                hole=0.5,
                textinfo='label+percent+value',
                textfont_size=14
            )])
            fig.update_layout(
                template='plotly_white',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, key="test_pie")
        else:
            st.info("No test data available")
    
    with col2:
        st.markdown("### Pass Rate Gauge")
        if testing_results['total_tests'] > 0:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=testing_results['pass_rate'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Pass Rate (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, 50], 'color': "#fee2e2"},
                        {'range': [50, 80], 'color': "#fef3c7"},
                        {'range': [80, 100], 'color': "#d1fae5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True, key="test_gauge")
    
    # Test results over time
    if not filtered_testing.empty and 'timestamp' in filtered_testing.columns:
        st.markdown("### Test Results Over Time")
        filtered_testing['Date'] = pd.to_datetime(filtered_testing['timestamp']).dt.date
        daily_tests = filtered_testing.groupby('Date').size().reset_index(name='Total_Tests')
        
        if 'Pass_Fail_Status' in filtered_testing.columns:
            daily_passed = filtered_testing[filtered_testing['Pass_Fail_Status'].str.lower() == 'passed'].groupby('Date').size().reset_index(name='Passed')
            daily_tests = daily_tests.merge(daily_passed, on='Date', how='left').fillna(0)
            daily_tests['Failed'] = daily_tests['Total_Tests'] - daily_tests['Passed']
            daily_tests['Pass_Rate'] = (daily_tests['Passed'] / daily_tests['Total_Tests'] * 100).fillna(0)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=daily_tests['Date'],
                y=daily_tests['Passed'],
                name='Passed',
                marker_color='#10b981'
            ))
            fig.add_trace(go.Bar(
                x=daily_tests['Date'],
                y=daily_tests['Failed'],
                name='Failed',
                marker_color='#ef4444'
            ))
            fig.update_layout(
                template='plotly_white',
                height=350,
                margin=dict(l=0, r=0, t=20, b=0),
                barmode='stack',
                xaxis_title="",
                yaxis_title="Number of Tests"
            )
            st.plotly_chart(fig, use_container_width=True, key="test_timeline")
    
    # Detailed table
    if show_details and not filtered_testing.empty:
        st.markdown("### Detailed Test Results")
        display_cols = ['Test_ID', 'Batch_ID', 'Pass_Fail_Status', 'timestamp'] if all(
            col in filtered_testing.columns for col in ['Test_ID', 'Batch_ID', 'Pass_Fail_Status', 'timestamp']
        ) else filtered_testing.columns.tolist()
        st.dataframe(
            filtered_testing[display_cols],
            use_container_width=True,
            hide_index=True,
            height=300
        )


def main():
    """Main application with sidebar navigation"""
    
    # Initialize connections
    if not initialize_connections():
        st.stop()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("# 📊 AI-CDP")
        st.markdown("### Navigation")
        
        # Navigation buttons - DARK BLUE TABS
        if st.button("🏠 Home", use_container_width=True, key="nav_home"):
            st.session_state.current_page = 'Home'
            st.rerun()
        
        if st.button("📈 Sales", use_container_width=True, key="nav_sales"):
            st.session_state.current_page = 'Sales'
            st.rerun()
        
        if st.button("🔧 Manufacturing", use_container_width=True, key="nav_mfg"):
            st.session_state.current_page = 'Manufacturing'
            st.rerun()
        
        if st.button("📦 Inventory", use_container_width=True, key="nav_inv"):
            st.session_state.current_page = 'Inventory'
            st.rerun()
        
        if st.button("🧪 Testing", use_container_width=True, key="nav_test"):
            st.session_state.current_page = 'Testing'
            st.rerun()
        
        # AI CHATBOT TAB
        if st.button("🤖 AI Assistant", use_container_width=True, key="nav_ai"):
            st.session_state.current_page = 'AI_Chatbot'
            st.rerun()
        
        st.markdown("---")
        
        # Global filters (for dashboard pages only)
        if st.session_state.current_page != 'AI_Chatbot':
            st.markdown("### 🔍 Global Filters")
            
            date_range = st.date_input(
                "Date Range",
                value=(
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                ),
                max_value=datetime.now(),
                key="global_date_range"
            )
        else:
            st.markdown("### 🤖 AI Assistant")
            st.info("💡 **Tip:** Ask natural language questions about your data to get instant insights!")
    
    # Render appropriate page
    if st.session_state.current_page == 'AI_Chatbot':
        # AI Chatbot Page - No data loading needed
        render_ai_chatbot_page()
    else:
        # Dashboard pages - Load data
        with st.spinner("Loading data..."):
            date_range = st.session_state.get('global_date_range', (datetime.now() - timedelta(days=30), datetime.now()))
            start_date = datetime.combine(date_range[0], datetime.min.time()) if len(date_range) > 0 else None
            end_date = datetime.combine(date_range[1], datetime.max.time()) if len(date_range) > 1 else None
            
            data_dict = st.session_state.data_retriever.get_all_data(start_date, end_date)
            results = st.session_state.ai_engine.run_all_analyses(data_dict)
        
        # Render dashboard pages
        if st.session_state.current_page == 'Home':
            render_home_overview(data_dict, results)
        elif st.session_state.current_page == 'Sales':
            render_sales_dashboard(data_dict, results)
        elif st.session_state.current_page == 'Manufacturing':
            render_manufacturing_dashboard(data_dict, results)
        elif st.session_state.current_page == 'Inventory':
            render_inventory_dashboard(data_dict, results)
        elif st.session_state.current_page == 'Testing':
            render_testing_dashboard(data_dict, results)


if __name__ == "__main__":
    main()
