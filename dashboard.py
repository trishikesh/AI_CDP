"""
AI-Powered Central Data Platform - Main Dashboard
Professional BI-style interface with AI Chatbot
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

# Custom CSS for professional BI aesthetic + Chat styling
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
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 2px solid #e0e0e0;
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
    
    /* Chat Container */
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 15px;
        border: 1px solid #dee2e6;
    }
    
    /* Chat Message - User */
    .chat-message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 20%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    
    /* Chat Message - Assistant */
    .chat-message-assistant {
        background-color: #ffffff;
        color: #212529;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 20%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        word-wrap: break-word;
    }
    
    /* Chat Input */
    .chat-input-container {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding: 10px 0;
        border-top: 1px solid #dee2e6;
    }
    
    /* Timestamp */
    .chat-timestamp {
        font-size: 11px;
        color: #6c757d;
        margin-top: 4px;
        text-align: right;
    }
    
    /* AI Badge */
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 10px;
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
            <div class="chat-timestamp">AI • {timestamp}</div>
        </div>
        """, unsafe_allow_html=True)


def render_ai_chatbot_sidebar():
    """Render AI Analysis chatbot in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🤖 AI Analysis")
    st.sidebar.markdown('<div class="ai-badge">✨ Powered by Gemini</div>', unsafe_allow_html=True)
    
    # Load data button for chat
    if not st.session_state.chat_data_loaded:
        if st.sidebar.button("📊 Connect to Live Data", use_container_width=True):
            with st.spinner("Loading real-time data from MongoDB..."):
                # Load last 30 days of data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                st.session_state.chat_full_df = st.session_state.data_retriever.fetch_all_data(
                    start_date, end_date
                )
                
                if st.session_state.chat_full_df is not None and not st.session_state.chat_full_df.empty:
                    st.session_state.chat_data_loaded = True
                    st.sidebar.success(f"✅ Loaded {len(st.session_state.chat_full_df)} records")
                    
                    # Add welcome message
                    st.session_state.chat_history.append({
                        'type': 'assistant',
                        'text': f"👋 Hi! I'm connected to your MongoDB database. I have access to {len(st.session_state.chat_full_df)} records from the last 30 days. Ask me anything about your Sales, Manufacturing, Testing, or Field data!",
                        'timestamp': datetime.now(),
                        'chart': None
                    })
                else:
                    st.sidebar.error("❌ No data available")
    else:
        st.sidebar.success("🟢 Connected to MongoDB")
        if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.chat_data_loaded = False
            st.rerun()
    
    # Chat history display
    st.sidebar.markdown("### 💬 Chat")
    
    # Chat container
    chat_container = st.sidebar.container()
    
    with chat_container:
        # Display chat history
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                render_chat_message(msg, is_user=(msg['type'] == 'user'))
                
                # Display chart if available
                if msg.get('chart') is not None:
                    st.plotly_chart(msg['chart'], use_container_width=True, key=f"chat_chart_{msg['timestamp']}")
        else:
            st.sidebar.info("💡 Start a conversation! Try asking:\n- 'Show sales trends'\n- 'What's the defect rate?'\n- 'Show inventory levels'")
    
    # Chat input
    st.sidebar.markdown("---")
    
    with st.sidebar.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input(
            "Ask me anything...",
            placeholder="e.g., Show me revenue trends",
            label_visibility="collapsed"
        )
        submit_button = st.form_submit_button("Send 📤", use_container_width=True)
    
    # Process chat input
    if submit_button and user_input:
        if not st.session_state.chat_data_loaded:
            st.sidebar.error("⚠️ Please connect to live data first!")
        else:
            # Add user message to history
            st.session_state.chat_history.append({
                'type': 'user',
                'text': user_input,
                'timestamp': datetime.now(),
                'chart': None
            })
            
            # Process with AI
            with st.spinner("🤖 AI is thinking..."):
                # Prepare chat history for context
                chat_context = [
                    {
                        'user': msg['text'],
                        'assistant': st.session_state.chat_history[i+1]['text'] 
                            if i+1 < len(st.session_state.chat_history) 
                            else ''
                    }
                    for i, msg in enumerate(st.session_state.chat_history)
                    if msg['type'] == 'user'
                ]
                
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
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
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
        # Calculate days to depletion for each store
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


# Add legacy analysis functions to ai_engine for compatibility
def analyze_sales(sales_df):
    """Legacy sales analysis function"""
    if sales_df.empty:
        return {
            'total_revenue': 0,
            'total_profit': 0,
            'profit_margin': 0,
            'revenue_trend': pd.DataFrame(),
            'top_products': pd.DataFrame()
        }

    if 'Revenue' not in sales_df.columns:
        return {
            'total_revenue': 0,
            'total_profit': 0,
            'profit_margin': 0,
            'revenue_trend': pd.DataFrame(),
            'top_products': pd.DataFrame()
        }

    sales_df['Profit'] = sales_df['Revenue'] * 0.40
    total_revenue = sales_df['Revenue'].sum()
    total_profit = sales_df['Profit'].sum()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    revenue_trend = pd.DataFrame()
    if 'timestamp' in sales_df.columns:
        sales_df['Date'] = pd.to_datetime(sales_df['timestamp']).dt.date
        revenue_trend = sales_df.groupby('Date').agg({
            'Revenue': 'sum',
            'Profit': 'sum'
        }).reset_index()
        revenue_trend = revenue_trend.sort_values('Date')

    top_products = pd.DataFrame()
    if 'SKU' in sales_df.columns:
        top_products = sales_df.groupby('SKU').agg({
            'Revenue': 'sum',
            'Quantity': 'sum',
            'Profit': 'sum'
        }).reset_index()
        top_products = top_products.sort_values('Revenue', ascending=False).head(10)

    return {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'revenue_trend': revenue_trend,
        'top_products': top_products
    }


def analyze_quality(manufacturing_df):
    """Legacy quality analysis function"""
    if manufacturing_df.empty:
        return {
            'avg_defect_rate': 0,
            'total_defects': 0,
            'total_produced': 0,
            'defect_trend': pd.DataFrame(),
            'line_performance': pd.DataFrame(),
            'anomalies': []
        }

    manufacturing_df['Defect_Rate'] = 0
    if 'Quantity_Produced' in manufacturing_df.columns and 'Defects' in manufacturing_df.columns:
        mask = manufacturing_df['Quantity_Produced'] > 0
        manufacturing_df.loc[mask, 'Defect_Rate'] = (
            manufacturing_df.loc[mask, 'Defects'] / 
            manufacturing_df.loc[mask, 'Quantity_Produced'] * 100
        )

    total_produced = manufacturing_df['Quantity_Produced'].sum()
    total_defects = manufacturing_df['Defects'].sum()
    avg_defect_rate = (total_defects / total_produced * 100) if total_produced > 0 else 0

    defect_trend = pd.DataFrame()
    if 'timestamp' in manufacturing_df.columns:
        manufacturing_df['Date'] = pd.to_datetime(manufacturing_df['timestamp']).dt.date
        daily_stats = manufacturing_df.groupby('Date').agg({
            'Quantity_Produced': 'sum',
            'Defects': 'sum'
        }).reset_index()
        daily_stats['Defect_Rate'] = (
            daily_stats['Defects'] / daily_stats['Quantity_Produced'] * 100
        ).fillna(0)
        defect_trend = daily_stats.sort_values('Date')

    line_performance = pd.DataFrame()
    anomalies = []
    if 'Line_ID' in manufacturing_df.columns:
        line_stats = manufacturing_df.groupby('Line_ID').agg({
            'Quantity_Produced': 'sum',
            'Defects': 'sum'
        }).reset_index()
        line_stats['Defect_Rate'] = (
            line_stats['Defects'] / line_stats['Quantity_Produced'] * 100
        ).fillna(0)
        line_performance = line_stats.sort_values('Defect_Rate', ascending=False)
        anomalies = line_stats[line_stats['Defect_Rate'] > 5]['Line_ID'].tolist()

    return {
        'avg_defect_rate': avg_defect_rate,
        'total_defects': total_defects,
        'total_produced': total_produced,
        'defect_trend': defect_trend,
        'line_performance': line_performance,
        'anomalies': anomalies
    }


def analyze_inventory(field_df):
    """Legacy inventory analysis function"""
    if field_df.empty:
        return {
            'total_inventory': 0,
            'low_stock_alerts': 0,
            'avg_days_to_depletion': 0,
            'critical_stores': pd.DataFrame(),
            'inventory_trend': pd.DataFrame()
        }

    field_df['Days_to_Depletion'] = 0
    if 'Inventory_Level' in field_df.columns and 'Daily_Consumption' in field_df.columns:
        mask = field_df['Daily_Consumption'] > 0
        field_df.loc[mask, 'Days_to_Depletion'] = (
            field_df.loc[mask, 'Inventory_Level'] / 
            field_df.loc[mask, 'Daily_Consumption']
        )

    field_df['Days_to_Depletion'] = field_df['Days_to_Depletion'].replace([float('inf'), -float('inf')], 999)

    total_inventory = field_df['Inventory_Level'].sum()
    low_stock_alerts = field_df['Low_Stock_Alerts'].sum()
    avg_days_to_depletion = field_df[field_df['Days_to_Depletion'] < 999]['Days_to_Depletion'].mean()

    critical_stores = pd.DataFrame()
    if 'Store_ID' in field_df.columns:
        critical_mask = field_df['Days_to_Depletion'] < 7
        critical_stores = field_df[critical_mask][
            ['Store_ID', 'Inventory_Level', 'Daily_Consumption', 'Days_to_Depletion']
        ].sort_values('Days_to_Depletion')

    inventory_trend = pd.DataFrame()
    if 'timestamp' in field_df.columns:
        field_df['Date'] = pd.to_datetime(field_df['timestamp']).dt.date
        daily_inventory = field_df.groupby('Date').agg({
            'Inventory_Level': 'sum',
            'Low_Stock_Alerts': 'sum'
        }).reset_index()
        inventory_trend = daily_inventory.sort_values('Date')

    return {
        'total_inventory': total_inventory,
        'low_stock_alerts': low_stock_alerts,
        'avg_days_to_depletion': avg_days_to_depletion if not pd.isna(avg_days_to_depletion) else 0,
        'critical_stores': critical_stores,
        'inventory_trend': inventory_trend
    }


def analyze_testing(testing_df):
    """Legacy testing analysis function"""
    if testing_df.empty:
        return {
            'total_tests': 0,
            'pass_rate': 0,
            'failed_tests': 0
        }

    total_tests = len(testing_df)
    failed_tests = 0
    pass_rate = 0

    if 'Pass_Fail_Status' in testing_df.columns:
        failed_tests = (testing_df['Pass_Fail_Status'].str.lower() == 'failed').sum()
        pass_rate = ((total_tests - failed_tests) / total_tests * 100) if total_tests > 0 else 0

    return {
        'total_tests': total_tests,
        'pass_rate': pass_rate,
        'failed_tests': failed_tests
    }


# Add legacy methods to AIEngine class
AIEngine.analyze_sales = analyze_sales
AIEngine.analyze_quality = analyze_quality
AIEngine.analyze_inventory = analyze_inventory
AIEngine.analyze_testing = analyze_testing


def main():
    """Main application with sidebar navigation and AI chatbot"""
    
    # Initialize connections
    if not initialize_connections():
        st.stop()
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("# 📊 AI-CDP")
        st.markdown("### Navigation")
        
        # Navigation buttons
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'Home'
        
        if st.button("📈 Sales", use_container_width=True):
            st.session_state.current_page = 'Sales'
        
        if st.button("🔧 Manufacturing", use_container_width=True):
            st.session_state.current_page = 'Manufacturing'
        
        if st.button("📦 Inventory", use_container_width=True):
            st.session_state.current_page = 'Inventory'
        
        if st.button("🧪 Testing", use_container_width=True):
            st.session_state.current_page = 'Testing'
        
        st.markdown("---")
        
        # Global filters (for all pages)
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
        
        # AI CHATBOT SECTION
        render_ai_chatbot_sidebar()
    
    # Load data with date filters
    with st.spinner("Loading data..."):
        start_date = datetime.combine(date_range[0], datetime.min.time()) if len(date_range) > 0 else None
        end_date = datetime.combine(date_range[1], datetime.max.time()) if len(date_range) > 1 else None
        
        data_dict = st.session_state.data_retriever.get_all_data(start_date, end_date)
        results = {
            'sales': analyze_sales(data_dict['sales']),
            'quality': analyze_quality(data_dict['manufacturing']),
            'inventory': analyze_inventory(data_dict['field']),
            'testing': analyze_testing(data_dict['testing'])
        }
    
    # Render appropriate page
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
