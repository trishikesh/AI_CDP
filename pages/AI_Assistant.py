"""
AI Analysis Assistant Dashboard
Conversational AI interface with real-time data visualization
Connected to all MongoDB collections
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
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced chat interface
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
    
    div[data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
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
    
    /* Chat Interface Styling */
    .chat-container {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    
    .chat-message {
        padding: 16px 20px;
        border-radius: 16px;
        margin: 12px 0;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message-user {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
        margin-left: 20%;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    
    .chat-message-assistant {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        color: #1e293b;
        margin-right: 20%;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .chat-timestamp {
        font-size: 11px;
        color: rgba(0,0,0,0.5);
        margin-top: 8px;
        font-weight: 500;
    }
    
    .chat-message-user .chat-timestamp {
        color: rgba(255,255,255,0.8);
    }
    
    .ai-badge {
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    
    .suggestion-chip {
        display: inline-block;
        background: white;
        border: 2px solid #e2e8f0;
        color: #64748b;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .suggestion-chip:hover {
        background: #f1f5f9;
        border-color: #8b5cf6;
        color: #8b5cf6;
        transform: translateY(-2px);
    }
    
    .connection-status {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    .status-connected {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-disconnected {
        background: #fee2e2;
        color: #991b1b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_retriever' not in st.session_state:
    st.session_state.data_retriever = None
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_full_df' not in st.session_state:
    st.session_state.chat_full_df = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

def initialize_connections():
    """Initialize database connections"""
    try:
        if st.session_state.data_retriever is None:
            st.session_state.data_retriever = DataRetriever()
        return True
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return False

def render_chat_message(message, is_user=True):
    """Render a single chat message with timestamp"""
    timestamp = message.get('timestamp', datetime.now()).strftime('%I:%M %p')
    
    if is_user:
        st.markdown(f"""
        <div class="chat-message chat-message-user">
            {message['text']}
            <div class="chat-timestamp">{timestamp}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message chat-message-assistant">
            {message['text']}
            <div class="chat-timestamp">🤖 AI Assistant • {timestamp}</div>
        </div>
        """, unsafe_allow_html=True)

# Main content
st.title("🤖 AI Analysis Assistant")
st.markdown('<div class="ai-badge">✨ Powered by Google Gemini AI</div>', unsafe_allow_html=True)
st.markdown("##### Ask questions about your data and get instant insights with visualizations")

# Sidebar - Data Loading
with st.sidebar:
    st.markdown("## 📅 Date Range")
    date_range = st.date_input(
        "Select Period for Analysis",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now(),
        key="ai_date_range"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Load Data", use_container_width=True, type="primary"):
            with st.spinner("Loading data from all MongoDB collections..."):
                if initialize_connections():
                    try:
                        if len(date_range) == 2:
                            start_date = datetime.combine(date_range[0], datetime.min.time())
                            end_date = datetime.combine(date_range[1], datetime.max.time())
                        else:
                            end_date = datetime.now()
                            start_date = end_date - timedelta(days=30)
                        
                        # Fetch all data from all collections
                        st.session_state.chat_full_df = st.session_state.data_retriever.fetch_all_data(
                            start_date, end_date
                        )
                        
                        if st.session_state.chat_full_df is not None and not st.session_state.chat_full_df.empty:
                            st.session_state.data_loaded = True
                            
                            # Add welcome message
                            st.session_state.chat_history = [{
                                'type': 'assistant',
                                'text': f"""👋 **Welcome!** I'm your AI Analysis Assistant.

📊 **Data Loaded Successfully**
- **Records:** {len(st.session_state.chat_full_df):,}
- **Date Range:** {date_range[0]} to {date_range[1]}
- **Collections:** Sales, Manufacturing, Testing, Field

💡 **Ask me anything about:**
- 📈 Sales trends and revenue analysis
- 🔧 Quality metrics and defect rates
- 🧪 Testing pass rates and failures
- 📦 Inventory levels and stock alerts

**Example questions:**
- "Show me sales revenue trends"
- "What are the defect rates by production line?"
- "Which stores have low inventory?"
- "Show testing pass rates over time"
""",
                                'timestamp': datetime.now(),
                                'chart': None
                            }]
                            
                            st.success(f"✅ Loaded {len(st.session_state.chat_full_df):,} records!")
                            st.rerun()
                        else:
                            st.error("❌ No data available for the selected date range")
                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.chat_full_df = None
            st.session_state.data_loaded = False
            st.rerun()
    
    st.markdown("---")
    
    # Connection Status
    st.markdown("### 📊 Data Status")
    if st.session_state.data_loaded and st.session_state.chat_full_df is not None:
        records = len(st.session_state.chat_full_df)
        st.markdown(f'<div class="connection-status status-connected">🟢 Connected | {records:,} records</div>', unsafe_allow_html=True)
        
        # Show data breakdown by domain
        if 'domain' in st.session_state.chat_full_df.columns:
            domain_counts = st.session_state.chat_full_df['domain'].value_counts()
            st.markdown("#### Records by Domain:")
            for domain, count in domain_counts.items():
                st.caption(f"• {domain}: {count:,}")
    else:
        st.markdown('<div class="connection-status status-disconnected">🔴 No data loaded</div>', unsafe_allow_html=True)
        st.caption("Click 'Load Data' to begin")
    
    st.markdown("---")
    st.markdown("### 💡 Quick Suggestions")
    st.caption("Click to copy example questions:")
    st.code("Show me sales revenue trends", language=None)
    st.code("What are defect rates by line?", language=None)
    st.code("Which stores have low inventory?", language=None)
    st.code("Show test pass rates", language=None)

# Main Chat Interface
st.markdown("---")

# Chat History Display
if st.session_state.chat_history:
    for idx, msg in enumerate(st.session_state.chat_history):
        render_chat_message(msg, is_user=(msg['type'] == 'user'))
        
        # Display chart if available
        if msg.get('chart') is not None:
            st.plotly_chart(msg['chart'], use_container_width=True, key=f"chat_chart_{idx}")
else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h2 style="color: #8b5cf6; margin-bottom: 20px;">👋 How can I help you today?</h2>
        <p style="color: #64748b; font-size: 18px; margin-bottom: 40px;">
            I can help you analyze your business data across multiple domains
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion chips
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📈 Sales & Revenue**
        - "Show me total revenue for last month"
        - "Which products have the highest sales?"
        - "Compare revenue across time periods"
        
        **🔧 Manufacturing & Quality**
        - "What are the defect rates by production line?"
        - "Show manufacturing trends"
        - "Which lines have quality issues?"
        """)
    
    with col2:
        st.markdown("""
        **📦 Inventory & Field**
        - "Which stores are running low on inventory?"
        - "Show inventory levels over time"
        - "Which stores need replenishment?"
        
        **🧪 Testing & Quality Assurance**
        - "What's the test pass rate?"
        - "Show failed tests by batch"
        - "Compare testing metrics"
        """)
    
    st.info("💡 **Get started:** Load data using the sidebar, then ask me any question about your business!")

# Chat Input Section
st.markdown("---")

with st.form(key='chat_input_form', clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Your Question",
            placeholder="Ask me anything about your data...",
            label_visibility="collapsed",
            key="chat_input"
        )
    
    with col2:
        submit_button = st.form_submit_button("Send 📤", use_container_width=True, type="primary")

# Process chat input
if submit_button and user_input:
    if st.session_state.chat_full_df is None or st.session_state.chat_full_df.empty:
        st.error("⚠️ Please load data first by clicking the 'Load Data' button in the sidebar!")
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
            try:
                # Prepare chat context
                chat_context = []
                for i in range(0, len(st.session_state.chat_history) - 1, 2):
                    if i + 1 < len(st.session_state.chat_history):
                        chat_context.append({
                            'user': st.session_state.chat_history[i]['text'],
                            'assistant': st.session_state.chat_history[i + 1].get('text', '')
                        })
                
                # Call AI engine
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
                
            except Exception as e:
                # Add error message
                st.session_state.chat_history.append({
                    'type': 'assistant',
                    'text': f"❌ **Error processing your query:** {str(e)}\n\nPlease try rephrasing your question or check if the data is loaded correctly.",
                    'timestamp': datetime.now(),
                    'chart': None
                })
        
        st.rerun()

# Footer
st.markdown("---")
st.caption("AI Assistant | Powered by Google Gemini AI | Connected to all MongoDB Collections")