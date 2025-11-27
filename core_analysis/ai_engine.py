"""
AI Analysis Engine for AI-CDP
Contains corrected analysis logic using properly mapped MongoDB schema
+ Gemini-powered conversational query processing (using official SDK)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import re
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os

# --- JSON SCHEMA DEFINITION FOR GEMINI OUTPUT ---
# This dictionary defines the strict structure the model MUST follow.
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "requires_visualization": {"type": "BOOLEAN", "description": "Set to true if the user asks for a chart, graph, or trend."},
        "analysis_type": {
            "type": "STRING",
            "description": "The primary data domain to analyze. Must be one of: sales, manufacturing, testing, inventory."
        },
        "visualization_type": {
            "type": "STRING",
            "description": "The chart type. Must be one of: bar_chart, line_chart, pie_chart."
        },
        "filters": {
            "type": "OBJECT",
            "description": "Extracted filter parameters from the user's message.",
            "properties": {
                "time_range": {"type": "STRING", "description": "e.g., 'last month', 'this week', 'last 7 days', or 'all time'"},
                "sku": {"type": "STRING", "description": "Specific SKU value, if mentioned."},
                "line_id": {"type": "STRING", "description": "Specific Line_ID value, if mentioned."},
                "domain": {"type": "STRING", "description": "Primary domain to analyze (Sales, Manufacturing, etc.)."}
            }
        },
        "response": {"type": "STRING", "description": "A brief, natural language summary response to the user's query before the chart is displayed."}
    },
    "required": ["requires_visualization", "analysis_type", "visualization_type", "filters", "response"]
}
# ----------------------------------------------------

# Try to import the official SDK (we assume the older one for structured output reliability)
HAS_SDK = False
try:
    # We rely on the older, more stable path for structured JSON output
    import google.generativeai as genai
    HAS_SDK = True
except Exception:
    HAS_SDK = False


class AIEngine:
    """
    Analytics engine with corrected schema-aware analysis functions
    + Conversational capabilities via Google Gemini Official SDK
    """

    def __init__(self):
        self.api_key = None
        self.genai_client = None
        
        # 1. Try Streamlit Secrets (most common for deployed apps)
        try:
            if hasattr(st, 'secrets'):
                # Check direct key
                if 'GEMINI_API_KEY' in st.secrets:
                    self.api_key = st.secrets['GEMINI_API_KEY']
                    print(f"✅ Found API key in st.secrets['GEMINI_API_KEY']")
                # Check nested key (if you have it nested in secrets.toml)
                elif hasattr(st.secrets, 'get') and st.secrets.get('gemini', {}).get('api_key'):
                    self.api_key = st.secrets['gemini']['api_key']
                    print(f"✅ Found API key in st.secrets['gemini']['api_key']")
        except Exception as e:
            print(f"⚠️ Error reading from Streamlit secrets: {e}")
        
        # 2. Try Environment Variable (Fallback)
        if not self.api_key:
            self.api_key = os.environ.get('GEMINI_API_KEY')
            if self.api_key:
                print(f"✅ Found API key in environment variable")
        
        # 3. Try .env file (additional fallback)
        if not self.api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                self.api_key = os.environ.get('GEMINI_API_KEY')
                if self.api_key:
                    print(f"✅ Found API key in .env file")
            except ImportError:
                pass
        
        # SDK Configuration
        if not HAS_SDK:
            print("❌ Google Generative AI SDK not installed")
            print("   Please run: pip install google-generativeai")
            self.genai_client = False
        elif not self.api_key:
            print("❌ GEMINI_API_KEY not found")
            print("   Please add it to .streamlit/secrets.toml or as environment variable")
            self.genai_client = False
        else:
            try:
                # Configure the Gemini API
                genai.configure(api_key=self.api_key)
                
                # Test the configuration with a simple call
                model = genai.GenerativeModel('gemini-1.5-flash')
                test_response = model.generate_content("Say 'OK' if you're working")
                
                if test_response and test_response.text:
                    print(f"✅ Gemini SDK configured successfully")
                    print(f"   API Key: {self.api_key[:10]}...{self.api_key[-4:]}")
                    self.genai_client = True
                else:
                    print("⚠️ Gemini configured but test call failed")
                    self.genai_client = False
                    
            except Exception as e:
                print(f"❌ Failed to configure Gemini SDK: {e}")
                print(f"   API Key starts with: {self.api_key[:10] if self.api_key else 'None'}...")
                self.genai_client = False
        
        # Define the data schema for Gemini
        self.data_schema = """
        MongoDB Data Schema (The system is analyzing a Pandas DataFrame merged from these four collections):
        1. Sales: Bill_ID, Revenue, Profit, Quantity, SKU, timestamp (Use 'sales' for analysis_type)
        2. Manufacturing: Batch_ID, Quantity_Produced, Defects, Defect_Rate, Line_ID, SKU, timestamp (Use 'manufacturing' for analysis_type)
        3. Testing: Test_ID, Batch_ID, Pass_Fail_Status, timestamp (Use 'testing' for analysis_type)
        4. Field/Inventory: Store_ID, Inventory_Level, Low_Stock_Alerts, Daily_Consumption, Days_to_Depletion, timestamp (Use 'inventory' or 'field' for analysis_type)
        
        Note: The 'timestamp' column is crucial for time_range filtering.
        """

    def analyze_sales(self, sales_df):
        if sales_df.empty: return {'total_revenue': 0, 'total_profit': 0, 'profit_margin': 0, 'revenue_trend': pd.DataFrame(), 'top_products': pd.DataFrame()}
        if 'Revenue' not in sales_df.columns: return {'total_revenue': 0, 'total_profit': 0, 'profit_margin': 0, 'revenue_trend': pd.DataFrame(), 'top_products': pd.DataFrame()}
        
        if 'Profit' not in sales_df.columns:
            sales_df['Profit'] = sales_df['Revenue'] * 0.40

        total_revenue = sales_df['Revenue'].sum()
        total_profit = sales_df['Profit'].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

        revenue_trend = pd.DataFrame()
        if 'timestamp' in sales_df.columns:
            sales_df['Date'] = pd.to_datetime(sales_df['timestamp']).dt.date
            revenue_trend = sales_df.groupby('Date').agg({'Revenue': 'sum', 'Profit': 'sum'}).reset_index().sort_values('Date')

        top_products = pd.DataFrame()
        if 'SKU' in sales_df.columns:
            top_products = sales_df.groupby('SKU').agg({'Revenue': 'sum', 'Quantity': 'sum', 'Profit': 'sum'}).reset_index()
            top_products = top_products.sort_values('Revenue', ascending=False).head(10)

        return {'total_revenue': total_revenue, 'total_profit': total_profit, 'profit_margin': profit_margin, 'revenue_trend': revenue_trend, 'top_products': top_products}

    def analyze_quality(self, manufacturing_df):
        if manufacturing_df.empty: return {'avg_defect_rate': 0, 'total_defects': 0, 'total_produced': 0, 'defect_trend': pd.DataFrame(), 'line_performance': pd.DataFrame(), 'anomalies': []}
        
        # Initialize as float (0.0)
        manufacturing_df['Defect_Rate'] = 0.0
        
        if 'Quantity_Produced' in manufacturing_df.columns and 'Defects' in manufacturing_df.columns:
            mask = manufacturing_df['Quantity_Produced'] > 0
            manufacturing_df.loc[mask, 'Defect_Rate'] = (manufacturing_df.loc[mask, 'Defects'] / manufacturing_df.loc[mask, 'Quantity_Produced'] * 100)

        total_produced = manufacturing_df['Quantity_Produced'].sum()
        total_defects = manufacturing_df['Defects'].sum()
        avg_defect_rate = (total_defects / total_produced * 100) if total_produced > 0 else 0

        defect_trend = pd.DataFrame()
        if 'timestamp' in manufacturing_df.columns:
            manufacturing_df['Date'] = pd.to_datetime(manufacturing_df['timestamp']).dt.date
            daily_stats = manufacturing_df.groupby('Date').agg({'Quantity_Produced': 'sum', 'Defects': 'sum'}).reset_index()
            daily_stats['Defect_Rate'] = (daily_stats['Defects'] / daily_stats['Quantity_Produced'] * 100).fillna(0)
            defect_trend = daily_stats.sort_values('Date')

        line_performance = pd.DataFrame()
        anomalies = []
        if 'Line_ID' in manufacturing_df.columns:
            line_stats = manufacturing_df.groupby('Line_ID').agg({'Quantity_Produced': 'sum', 'Defects': 'sum'}).reset_index()
            line_stats['Defect_Rate'] = (line_stats['Defects'] / line_stats['Quantity_Produced'] * 100).fillna(0)
            line_performance = line_stats.sort_values('Defect_Rate', ascending=False)
            anomalies = line_stats[line_stats['Defect_Rate'] > 5]['Line_ID'].tolist()

        return {'avg_defect_rate': avg_defect_rate, 'total_defects': total_defects, 'total_produced': total_produced, 'defect_trend': defect_trend, 'line_performance': line_performance, 'anomalies': anomalies}

    def analyze_inventory(self, field_df):
        if field_df.empty: return {'total_inventory': 0, 'low_stock_alerts': 0, 'avg_days_to_depletion': 0, 'critical_stores': pd.DataFrame(), 'inventory_trend': pd.DataFrame()}

        # Initialize as float (0.0)
        field_df['Days_to_Depletion'] = 0.0
        
        if 'Inventory_Level' in field_df.columns and 'Daily_Consumption' in field_df.columns:
            mask = field_df['Daily_Consumption'] > 0
            field_df.loc[mask, 'Days_to_Depletion'] = (field_df.loc[mask, 'Inventory_Level'] / field_df.loc[mask, 'Daily_Consumption'])
        
        field_df['Days_to_Depletion'] = field_df['Days_to_Depletion'].replace([np.inf, -np.inf], 999.0)
        
        total_inventory = field_df['Inventory_Level'].sum()
        low_stock_alerts = field_df['Low_Stock_Alerts'].sum()
        avg_days_to_depletion = field_df[field_df['Days_to_Depletion'] < 999]['Days_to_Depletion'].mean()

        critical_stores = pd.DataFrame()
        if 'Store_ID' in field_df.columns:
            critical_stores = field_df[field_df['Days_to_Depletion'] < 7][['Store_ID', 'Inventory_Level', 'Daily_Consumption', 'Days_to_Depletion']].sort_values('Days_to_Depletion')

        inventory_trend = pd.DataFrame()
        if 'timestamp' in field_df.columns:
            field_df['Date'] = pd.to_datetime(field_df['timestamp']).dt.date
            daily_inventory = field_df.groupby('Date').agg({'Inventory_Level': 'sum', 'Low_Stock_Alerts': 'sum'}).reset_index()
            inventory_trend = daily_inventory.sort_values('Date')

        return {'total_inventory': total_inventory, 'low_stock_alerts': low_stock_alerts, 'avg_days_to_depletion': avg_days_to_depletion if not pd.isna(avg_days_to_depletion) else 0, 'critical_stores': critical_stores, 'inventory_trend': inventory_trend}

    def analyze_testing(self, testing_df):
        if testing_df.empty: return {'total_tests': 0, 'pass_rate': 0, 'failed_tests': 0}
        total_tests = len(testing_df)
        failed_tests = (testing_df['Pass_Fail_Status'].str.lower() == 'failed').sum() if 'Pass_Fail_Status' in testing_df.columns else 0
        pass_rate = ((total_tests - failed_tests) / total_tests * 100) if total_tests > 0 else 0
        return {'total_tests': total_tests, 'pass_rate': pass_rate, 'failed_tests': failed_tests}

    def run_all_analyses(self, data_dict):
        return {
            'sales': self.analyze_sales(data_dict.get('sales', pd.DataFrame())),
            'quality': self.analyze_quality(data_dict.get('manufacturing', pd.DataFrame())),
            'inventory': self.analyze_inventory(data_dict.get('field', pd.DataFrame())),
            'testing': self.analyze_testing(data_dict.get('testing', pd.DataFrame()))
        }

    # ==================== GEMINI AI CHATBOT METHODS ====================

    def _call_gemini_api(self, prompt):
        """
        Uses the Google SDK to call Gemini, enforcing structured JSON output.
        """
        if not self.genai_client:
            error_msg = "AI Engine not configured. "
            if not HAS_SDK:
                error_msg += "Google Generative AI SDK is not installed. Run: pip install google-generativeai"
            elif not self.api_key:
                error_msg += "GEMINI_API_KEY not found. Add it to .streamlit/secrets.toml"
            else:
                error_msg += "Configuration failed. Check your API key."
            
            return {"error": error_msg}

        try:
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA
                )
            )
            response = model.generate_content(prompt)
            
            if response.text:
                parsed = json.loads(response.text)
                return parsed
            
            return {"error": "Empty response from AI"}

        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}")
            print(f"   Raw response: {response.text[:200] if response and response.text else 'None'}")
            return {"error": f"Invalid JSON response from AI: {str(e)}"}
        
        except Exception as e:
            error_str = str(e)
            print(f"❌ Gemini API Error: {error_str}")
            
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return {"error": "API quota exceeded. Please wait a moment and try again."}
            elif "403" in error_str or "PERMISSION_DENIED" in error_str:
                return {"error": "API key invalid or doesn't have permission. Check your GEMINI_API_KEY."}
            elif "400" in error_str or "INVALID_ARGUMENT" in error_str:
                return {"error": "Invalid request to AI. Please rephrase your question."}
            else:
                return {"error": f"AI API Error: {error_str}"}

    def _apply_filters(self, df, filters):
        """Apply filters to the dataframe based on Gemini's extracted parameters."""
        filtered_df = df.copy()
        
        # Apply domain filter if specified
        if filters.get('domain'):
            domain = filters['domain'].lower()
            if 'domain' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['domain'].str.lower() == domain]
        
        # Apply SKU filter if specified
        if filters.get('sku') and 'SKU' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['SKU'] == filters['sku']]
        
        # Apply Line_ID filter if specified
        if filters.get('line_id') and 'Line_ID' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Line_ID'] == filters['line_id']]
        
        # Apply time range filter if specified
        if filters.get('time_range') and 'timestamp' in filtered_df.columns:
            filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'])
            now = datetime.now()
            
            time_range = filters['time_range'].lower()
            if 'last 7 days' in time_range or 'last week' in time_range:
                start_date = now - timedelta(days=7)
            elif 'last month' in time_range:
                start_date = now - timedelta(days=30)
            elif 'this week' in time_range:
                start_date = now - timedelta(days=now.weekday())
            else:
                start_date = filtered_df['timestamp'].min()
            
            filtered_df = filtered_df[filtered_df['timestamp'] >= start_date]
        
        return filtered_df

    def _execute_analysis(self, df, analysis_type, visualization_type):
        """Analyzes the filtered data and generates the Plotly figure."""
        if df.empty:
            return "No data matches your criteria.", None
        
        insight, fig = "", None
        
        # --- SALES ---
        if 'sales' in analysis_type.lower() or 'revenue' in analysis_type.lower():
            if 'Revenue' in df.columns and 'timestamp' in df.columns:
                total_rev = df['Revenue'].sum()
                insight = f"💰 **Sales Summary:** Total Revenue is **${total_rev:,.2f}** for the filtered data."
                
                df['Date'] = pd.to_datetime(df['timestamp']).dt.date
                daily = df.groupby('Date')['Revenue'].sum().reset_index()
                
                if 'line' in visualization_type:
                    fig = px.line(daily, x='Date', y='Revenue', title='Revenue Trend Over Time', color_discrete_sequence=['#667eea'])
                else:
                    top_sku = df.groupby('SKU')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False).head(10)
                    fig = px.bar(top_sku, x='SKU', y='Revenue', title='Top 10 SKUs by Revenue', color_discrete_sequence=['#667eea'])

        # --- MANUFACTURING ---
        elif 'manufacturing' in analysis_type.lower() or 'quality' in analysis_type.lower():
            if 'Defect_Rate' in df.columns and 'Line_ID' in df.columns:
                line_stats = df.groupby('Line_ID')['Defect_Rate'].mean().reset_index()
                avg_rate = line_stats['Defect_Rate'].mean()
                insight = f"🔧 **Quality Summary:** Avg Defect Rate across lines: **{avg_rate:.2f}%**."
                
                if 'line' in visualization_type and 'timestamp' in df.columns:
                    df['Date'] = pd.to_datetime(df['timestamp']).dt.date
                    daily_rate = df.groupby('Date')['Defect_Rate'].mean().reset_index()
                    fig = px.line(daily_rate, x='Date', y='Defect_Rate', title='Daily Defect Rate Trend', color_discrete_sequence=['#ef4444'])
                else:
                    fig = px.bar(line_stats, x='Line_ID', y='Defect_Rate', title='Defect Rate by Production Line', color='Defect_Rate', color_continuous_scale='RdYlGn_r')

        # --- TESTING ---
        elif 'testing' in analysis_type.lower():
            if 'Pass_Fail_Status' in df.columns:
                passed = (df['Pass_Fail_Status'].str.lower() == 'passed').sum()
                failed = len(df) - passed
                insight = f"🧪 **Testing Summary:** Total Tests: {len(df)}. Pass Rate: **{(passed / len(df) * 100):.1f}%**."
                fig = px.pie(names=['Passed', 'Failed'], values=[passed, failed], title='Test Results Distribution', color_discrete_sequence=['#10b981', '#ef4444'], hole=0.4)

        # --- INVENTORY ---
        elif 'field' in analysis_type.lower() or 'inventory' in analysis_type.lower():
            if 'Inventory_Level' in df.columns and 'Store_ID' in df.columns:
                total_inv = df['Inventory_Level'].sum()
                insight = f"📦 **Inventory Summary:** Total Stock: **{total_inv:,.0f}** for filtered stores/SKUs."
                
                top_stores = df.groupby('Store_ID')['Inventory_Level'].mean().reset_index().sort_values('Inventory_Level', ascending=False).head(10)
                fig = px.bar(top_stores, x='Store_ID', y='Inventory_Level', title='Average Inventory Level by Store', color_discrete_sequence=['#10b981'])

        if fig:
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        
        return insight, fig

    def process_chat_query(self, user_message, full_df, chat_history=None):
        """
        Main function to process user text, get structured query from Gemini,
        and execute the analysis/visualization.
        """
        # 1. Data Validation
        if full_df is None or full_df.empty:
            return "❌ Cannot analyze: No data has been loaded from MongoDB yet.", None

        # 2. Prepare Data Context for Gemini
        data_summary = f"Total Rows: {len(full_df)}\nColumns: {', '.join(full_df.columns)}\n"
        
        # 3. Prompt Construction
        system_instruction = f"""
You are a specialized Data Analyst AI. Your sole task is to convert a user's natural language question into a structured JSON query that drives an analytical backend.

DATA CONTEXT:
{self.data_schema}

INSTRUCTIONS:
1. Parse the user's intent. If they ask for a 'trend', a 'chart', 'graph', 'performance', or 'comparison', set 'requires_visualization' to true.
2. Identify the primary data domain and set 'analysis_type' (must be one of the four defined domains).
3. Extract any specific filters (like 'last month', 'SKU-101', or 'Line-A').
4. The 'response' field should be a short, encouraging confirmation of the task.
5. You MUST return ONLY the JSON object, strictly following the defined schema.

User Question: "{user_message}"
"""

        # 4. Call API
        try:
            parsed_response = self._call_gemini_api(system_instruction)
        except Exception as e:
            return f"❌ Critical API Call Error: {str(e)}", None

        # 5. Handle Errors Explicitly
        if "error" in parsed_response:
            return f"❌ System Error from AI: {parsed_response['error']}", None

        # 6. Process Success and Execute Analysis
        response_text = parsed_response.get('response', 'Analysis requested.')
        requires_viz = parsed_response.get('requires_visualization', False)

        fig = None
        if requires_viz:
            filters = parsed_response.get('filters', {})
            analysis_type = parsed_response.get('analysis_type', 'sales')
            viz_type = parsed_response.get('visualization_type', 'bar_chart')
            
            # --- EXECUTION STEP ---
            # Simulate fetching/filtering the data based on Gemini's query
            filtered_df = self._apply_filters(full_df, filters)
            
            # Run the specific analysis and get the chart
            insight, fig = self._execute_analysis(filtered_df, analysis_type, viz_type)
            
            if insight and insight != "No data matches your criteria.":
                response_text += f"\n\n**Data Insight:** {insight}"

        return response_text, fig
