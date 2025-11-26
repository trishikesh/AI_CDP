"""
AI-Powered Central Data Platform - Conversational Dashboard
Gemini AI-powered natural language query interface
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from core_analysis.data_retriever import DataRetriever
from core_analysis.ai_engine import AIEngine


# Page configuration
st.set_page_config(
    page_title="AI-CDP",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Color palette
PRIMARY_COLOR = "#667eea"
SECONDARY_COLOR = "#764ba2"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
DANGER_COLOR = "#ef4444"

# Enhanced minimal CSS with conversational interface styling
st.markdown(f"""
<style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0;
    }}
    
    /* Remove default padding */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 0rem;
        max-width: 95%;
    }}
    
    /* Sidebar - minimal for filters only */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
    }}
    
    /* Metric cards - ultra minimal */
    div[data-testid="metric-container"] {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: none;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 13px;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Headers */
    h1 {{
        color: #1f2937;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    h2 {{
        color: #374151;
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}
    
    h3 {{
        color: #6b7280;
        font-weight: 500;
        font-size: 1.1rem;
    }}
    
    /* Search bar container */
    .search-container {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
        border: 2px solid rgba(102, 126, 234, 0.2);
    }}
    
    /* Text input styling */
    .stTextInput input {{
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 16px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
    }}
    
    .stTextInput input:focus {{
        border-color: {PRIMARY_COLOR};
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }}
    
    /* Button styling */
    .stButton button {{
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
    }}
    
    /* Chart containers */
    .chart-container {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }}
    
    /* Plotly charts */
    .js-plotly-plot {{
        border-radius: 12px;
    }}
    
    /* Insight box */
    .insight-box {{
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid {PRIMARY_COLOR};
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        font-size: 15px;
        line-height: 1.8;
    }}
    
    /* Filter section */
    .filter-section {{
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }}
    
    /* Divider */
    hr {{
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
    }}
    
    /* Alert boxes */
    .stAlert {{
        border-radius: 12px;
        border: none;
        backdrop-filter: blur(10px);
    }}
    
    /* Info boxes */
    .stInfo {{
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
    }}
    
    /* Success boxes */
    .stSuccess {{
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid {SUCCESS_COLOR};
    }}
    
    /* Warning boxes */
    .stWarning {{
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid {WARNING_COLOR};
    }}
    
    /* Error boxes */
    .stError {{
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid {DANGER_COLOR};
    }}
    
    /* Loading spinner */
    .stSpinner > div {{
        border-top-color: {PRIMARY_COLOR} !important;
    }}
    
    /* Date input styling */
    .stDateInput input {{
        border-radius: 10px;
        border: 2px solid #e5e7eb;
    }}
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'data_retriever' not in st.session_state:
    st.session_state.data_retriever = None
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'full_df' not in st.session_state:
    st.session_state.full_df = None


def initialize_connections():
    """Initialize database connections"""
    try:
        if st.session_state.data_retriever is None:
            st.session_state.data_retriever = DataRetriever()
        return True
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return False


def load_data(start_date, end_date):
    """Load all data from MongoDB"""
    if st.session_state.data_retriever is None:
        return None
    
    full_df = st.session_state.data_retriever.fetch_all_data(start_date, end_date)
    return full_df


def create_kpi_card(label, value, format_type="number"):
    """Create a styled KPI metric card"""
    if format_type == "currency":
        st.metric(label, f"${value:,.2f}")
    elif format_type == "percent":
        st.metric(label, f"{value:.2f}%")
    else:
        st.metric(label, f"{value:,.0f}")


def display_overview_kpis(full_df):
    """Display overview KPI cards"""
    if full_df is None or full_df.empty:
        st.info("No data available")
        return

    kpi_cols = st.columns(4)
    
    # Sales KPI
    with kpi_cols[0]:
        sales_df = full_df[full_df['domain'] == 'Sales']
        total_revenue = sales_df['Revenue'].sum() if not sales_df.empty and 'Revenue' in sales_df.columns else 0
        create_kpi_card("Total Revenue", total_revenue, "currency")
    
    # Manufacturing KPI
    with kpi_cols[1]:
        mfg_df = full_df[full_df['domain'] == 'Manufacturing']
        avg_defect = mfg_df['Defect_Rate'].mean() if not mfg_df.empty and 'Defect_Rate' in mfg_df.columns else 0
        create_kpi_card("Avg Defect Rate", avg_defect, "percent")
    
    # Field KPI
    with kpi_cols[2]:
        field_df = full_df[full_df['domain'] == 'Field']
        total_inventory = field_df['Inventory_Level'].sum() if not field_df.empty and 'Inventory_Level' in field_df.columns else 0
        create_kpi_card("Total Inventory", total_inventory)
    
    # Testing KPI
    with kpi_cols[3]:
        test_df = full_df[full_df['domain'] == 'Testing']
        if not test_df.empty and 'Pass_Fail_Status' in test_df.columns:
            pass_rate = (test_df['Pass_Fail_Status'].str.lower() == 'passed').sum() / len(test_df) * 100
        else:
            pass_rate = 0
        create_kpi_card("Test Pass Rate", pass_rate, "percent")


async def process_query_async(query, full_df):
    """Async wrapper for query processing"""
    return st.session_state.ai_engine.process_conversational_query(query, full_df)


def main():
    """Main application"""
    
    # Header
    st.title("🤖 AI-CDP: Conversational Analytics")
    st.markdown("##### Ask questions about your data in natural language")
    
    # Initialize connections
    if not initialize_connections():
        st.stop()
    
    # Filter section (in main dashboard, not sidebar)
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("#### 📅 Data Filters")
    
    filter_cols = st.columns([2, 1])
    
    with filter_cols[0]:
        date_range = st.date_input(
            "Select Date Range",
            value=(
                datetime.now() - timedelta(days=30),
                datetime.now()
            ),
            max_value=datetime.now(),
            key="date_range"
        )
    
    with filter_cols[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        load_button = st.button("🔄 Load Data", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load data
    if load_button or st.session_state.full_df is None:
        with st.spinner("Loading data from MongoDB..."):
            start_date = datetime.combine(date_range[0], datetime.min.time()) if len(date_range) > 0 else None
            end_date = datetime.combine(date_range[1], datetime.max.time()) if len(date_range) > 1 else None
            
            st.session_state.full_df = load_data(start_date, end_date)
            
            if st.session_state.full_df is not None and not st.session_state.full_df.empty:
                st.success(f"✅ Loaded {len(st.session_state.full_df)} records from MongoDB")
            else:
                st.warning("⚠️ No data found for the selected date range")
    
    # Display overview KPIs
    if st.session_state.full_df is not None:
        st.markdown("---")
        display_overview_kpis(st.session_state.full_df)
        st.markdown("---")
    
    # Conversational Search Interface
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown("### 💬 Ask a Question")
    st.markdown("*Examples: 'Show me sales revenue for last month', 'What are the defect rates by production line?', 'Show inventory levels for critical stores'*")
    
    # Search input and button
    search_cols = st.columns([5, 1])
    
    with search_cols[0]:
        user_query = st.text_input(
            "Your Question",
            placeholder="Type your question here...",
            label_visibility="collapsed",
            key="query_input"
        )
    
    with search_cols[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Analyze", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process query
    if search_button and user_query:
        if st.session_state.full_df is None or st.session_state.full_df.empty:
            st.error("⚠️ Please load data first using the 'Load Data' button above")
        else:
            with st.spinner("🤖 AI is analyzing your query..."):
                # Process query
                insight, fig, parsed_intent = st.session_state.ai_engine.process_conversational_query(
                    user_query,
                    st.session_state.full_df
                )
                
                # Add to history
                st.session_state.query_history.append({
                    'query': user_query,
                    'timestamp': datetime.now(),
                    'insight': insight,
                    'parsed_intent': parsed_intent
                })
                
                # Display results
                st.markdown("### 📊 Analysis Results")
                
                # Show parsed intent (collapsible)
                if parsed_intent:
                    with st.expander("🔍 View Parsed Intent (Debug)"):
                        st.json(parsed_intent)
                
                # Display insight
                st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
                
                # Display chart
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{len(st.session_state.query_history)}")
                
                st.success("✅ Analysis complete!")
    
    # Query history
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### 📜 Query History")
        
        for idx, history_item in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
            with st.expander(f"🕐 {history_item['timestamp'].strftime('%H:%M:%S')} - {history_item['query'][:50]}..."):
                st.markdown(f"**Query:** {history_item['query']}")
                st.markdown(history_item['insight'])
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #6b7280; font-size: 12px;'>"
        f"AI-CDP Conversational Dashboard | Powered by Google Gemini | "
        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
