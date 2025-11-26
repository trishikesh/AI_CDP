
"""
AI Analysis Engine for AI-CDP
Contains corrected analysis logic using properly mapped MongoDB schema
+ Gemini-powered conversational query processing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


class AIEngine:
    """
    Analytics engine with corrected schema-aware analysis functions
    + Conversational capabilities via Google Gemini API
    """

    def __init__(self):
        # Initialize api_key as None first
        self.api_key = None
        
        # Load Gemini API key from secrets
        try:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                self.api_key = st.secrets['GEMINI_API_KEY']
        except Exception:
            pass

        # Define the data schema for Gemini
        self.data_schema = """
        MongoDB Data Schema:
        
        1. Sales Collection:
           - Bill_ID: Transaction identifier
           - Revenue (mapped from Total_Amount): Transaction revenue in dollars
           - Profit: Calculated as Revenue * 0.40
           - Quantity: Number of items sold
           - SKU: Product identifier/code
           - timestamp: Date and time of transaction
           
        2. Manufacturing Collection:
           - Batch_ID: Production batch identifier
           - Quantity_Produced: Number of units produced
           - Defects: Number of defective units
           - Defect_Rate: Percentage calculated as (Defects/Quantity_Produced)*100
           - Line_ID (mapped from Machine_ID): Production line identifier
           - SKU (mapped from Product): Product identifier
           - timestamp: Production date and time
           
        3. Testing Collection:
           - Test_ID: Test identifier
           - Batch_ID: Associated batch identifier
           - Pass_Fail_Status (mapped from Passed/Failed): "Passed" or "Failed"
           - timestamp: Test date and time
           
        4. Field Collection:
           - Store_ID: Store/location identifier
           - Inventory_Level: Current inventory quantity
           - Low_Stock_Alerts: Number of low stock alerts
           - Daily_Consumption: Average daily consumption rate
           - Days_to_Depletion: Calculated as Inventory_Level/Daily_Consumption
           - timestamp (mapped from Date): Date of record
        """

    def analyze_sales(self, sales_df):
        """
        Sales Analysis with corrected Revenue/Profit calculations
        """
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

    def analyze_quality(self, manufacturing_df):
        """
        Quality Analysis with corrected defect rate calculations
        """
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

    def analyze_inventory(self, field_df):
        """
        Inventory/Field Analysis with Days-to-Depletion prediction
        """
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

        field_df['Days_to_Depletion'] = field_df['Days_to_Depletion'].replace([np.inf, -np.inf], 999)

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

    def analyze_testing(self, testing_df):
        """
        Testing/Quality Control Analysis
        """
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

    def run_all_analyses(self, data_dict):
        """
        Run all analysis modules on the provided data
        """
        return {
            'sales': self.analyze_sales(data_dict.get('sales', pd.DataFrame())),
            'quality': self.analyze_quality(data_dict.get('manufacturing', pd.DataFrame())),
            'inventory': self.analyze_inventory(data_dict.get('field', pd.DataFrame())),
            'testing': self.analyze_testing(data_dict.get('testing', pd.DataFrame()))
        }

    # ==================== GEMINI AI CHATBOT METHODS ====================

    def _call_gemini_api(self, prompt):
        """
        Call Google Gemini API to parse user intent
        """
        if not self.api_key:
            return None

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 2048,
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                text_response = text_response.replace('```json', '').replace('```', '').strip()
                parsed_json = json.loads(text_response)
                return parsed_json
            
            return None
            
        except Exception as e:
            st.error(f"Gemini API Error: {str(e)}")
            return None

    def _apply_filters(self, df, filters):
        """
        Apply filters to the DataFrame based on parsed intent
        """
        filtered_df = df.copy()

        if filters is None or df.empty:
            return filtered_df

        if 'time_range' in filters and 'timestamp' in filtered_df.columns:
            time_filter = filters['time_range'].lower()
            now = datetime.now()
            
            if 'last month' in time_filter or 'past month' in time_filter:
                start_date = now - timedelta(days=30)
                filtered_df = filtered_df[filtered_df['timestamp'] >= start_date]
            elif 'last week' in time_filter or 'past week' in time_filter:
                start_date = now - timedelta(days=7)
                filtered_df = filtered_df[filtered_df['timestamp'] >= start_date]
            elif 'last year' in time_filter or 'past year' in time_filter:
                start_date = now - timedelta(days=365)
                filtered_df = filtered_df[filtered_df['timestamp'] >= start_date]
            elif 'today' in time_filter:
                filtered_df = filtered_df[filtered_df['timestamp'].dt.date == now.date()]

        if 'domain' in filters and 'domain' in filtered_df.columns:
            domain_map = {
                'sales': 'Sales',
                'manufacturing': 'Manufacturing',
                'testing': 'Testing',
                'field': 'Field',
                'inventory': 'Field'
            }
            domain_value = domain_map.get(filters['domain'].lower(), filters['domain'])
            filtered_df = filtered_df[filtered_df['domain'] == domain_value]

        if 'sku' in filters and 'SKU' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['SKU'] == filters['sku']]

        if 'line_id' in filters and 'Line_ID' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Line_ID'] == filters['line_id']]

        if 'store_id' in filters and 'Store_ID' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Store_ID'] == filters['store_id']]

        return filtered_df

    def _execute_analysis(self, df, analysis_type, visualization_type):
        """
        Execute the specific analysis and create visualization
        """
        if df.empty:
            return "No data available for the specified filters.", None

        insight = ""
        fig = None

        if 'sales' in analysis_type.lower() or 'revenue' in analysis_type.lower():
            if 'Revenue' not in df.columns:
                return "Sales data not available in filtered results.", None

            total_revenue = df['Revenue'].sum()
            total_profit = df['Profit'].sum() if 'Profit' in df.columns else total_revenue * 0.40
            
            insight = f"💰 **Sales Analysis:**\n\n"
            insight += f"- Total Revenue: **${total_revenue:,.2f}**\n"
            insight += f"- Total Profit: **${total_profit:,.2f}**\n"
            insight += f"- Profit Margin: **{(total_profit/total_revenue*100):.2f}%**\n"
            
            if 'SKU' in df.columns:
                top_product = df.groupby('SKU')['Revenue'].sum().idxmax()
                top_revenue = df.groupby('SKU')['Revenue'].sum().max()
                insight += f"- Top Product: **{top_product}** (${top_revenue:,.2f})\n"

            if 'timestamp' in df.columns:
                df['Date'] = pd.to_datetime(df['timestamp']).dt.date
                daily_revenue = df.groupby('Date')['Revenue'].sum().reset_index()
                
                if 'line' in visualization_type.lower():
                    fig = px.line(daily_revenue, x='Date', y='Revenue',
                                 title='Revenue Trend',
                                 color_discrete_sequence=['#667eea'])
                elif 'area' in visualization_type.lower():
                    fig = px.area(daily_revenue, x='Date', y='Revenue',
                                 title='Revenue Trend',
                                 color_discrete_sequence=['#667eea'])
                else:
                    fig = px.bar(daily_revenue, x='Date', y='Revenue',
                                title='Daily Revenue',
                                color_discrete_sequence=['#667eea'])
                
                fig.update_layout(template='plotly_white', height=300, margin=dict(l=0, r=0, t=30, b=0))

        elif 'manufacturing' in analysis_type.lower() or 'quality' in analysis_type.lower() or 'defect' in analysis_type.lower():
            if 'Defect_Rate' not in df.columns:
                return "Manufacturing data not available in filtered results.", None

            avg_defect_rate = df['Defect_Rate'].mean()
            total_produced = df['Quantity_Produced'].sum() if 'Quantity_Produced' in df.columns else 0
            total_defects = df['Defects'].sum() if 'Defects' in df.columns else 0
            
            insight = f"🔧 **Manufacturing Analysis:**\n\n"
            insight += f"- Average Defect Rate: **{avg_defect_rate:.2f}%**\n"
            insight += f"- Total Produced: **{total_produced:,.0f} units**\n"
            insight += f"- Total Defects: **{total_defects:,.0f} units**\n"
            
            if 'Line_ID' in df.columns:
                line_defects = df.groupby('Line_ID')['Defect_Rate'].mean()
                worst_line = line_defects.idxmax()
                worst_rate = line_defects.max()
                insight += f"- Highest Defect Rate: **Line {worst_line}** ({worst_rate:.2f}%)\n"

            if 'Line_ID' in df.columns:
                line_stats = df.groupby('Line_ID')['Defect_Rate'].mean().reset_index()
                
                if 'bar' in visualization_type.lower():
                    fig = px.bar(line_stats, x='Line_ID', y='Defect_Rate',
                                title='Defect Rate by Production Line',
                                color='Defect_Rate',
                                color_continuous_scale='RdYlGn_r')
                else:
                    fig = px.line(line_stats, x='Line_ID', y='Defect_Rate',
                                 title='Defect Rate by Production Line',
                                 color_discrete_sequence=['#f59e0b'])
                
                fig.add_hline(y=5, line_dash="dash", line_color="red", 
                             annotation_text="5% Threshold")
                fig.update_layout(template='plotly_white', height=300, margin=dict(l=0, r=0, t=30, b=0))

        elif 'testing' in analysis_type.lower() or 'test' in analysis_type.lower():
            if 'Pass_Fail_Status' not in df.columns:
                return "Testing data not available in filtered results.", None

            total_tests = len(df)
            passed = (df['Pass_Fail_Status'].str.lower() == 'passed').sum()
            failed = total_tests - passed
            pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
            
            insight = f"🧪 **Testing Analysis:**\n\n"
            insight += f"- Total Tests: **{total_tests}**\n"
            insight += f"- Passed: **{passed}** ({pass_rate:.2f}%)\n"
            insight += f"- Failed: **{failed}** ({100-pass_rate:.2f}%)\n"

            if 'pie' in visualization_type.lower() or 'donut' in visualization_type.lower():
                fig = go.Figure(data=[go.Pie(
                    labels=['Passed', 'Failed'],
                    values=[passed, failed],
                    marker=dict(colors=['#10b981', '#ef4444']),
                    hole=0.4
                )])
                fig.update_layout(title='Test Results Distribution', height=300, margin=dict(l=0, r=0, t=30, b=0))
            else:
                results_df = pd.DataFrame({'Status': ['Passed', 'Failed'], 'Count': [passed, failed]})
                fig = px.bar(results_df, x='Status', y='Count',
                            title='Test Results',
                            color='Status',
                            color_discrete_map={'Passed': '#10b981', 'Failed': '#ef4444'})
                fig.update_layout(template='plotly_white', height=300, margin=dict(l=0, r=0, t=30, b=0))

        elif 'field' in analysis_type.lower() or 'inventory' in analysis_type.lower():
            if 'Inventory_Level' not in df.columns:
                return "Field/Inventory data not available in filtered results.", None

            total_inventory = df['Inventory_Level'].sum()
            low_stock_alerts = df['Low_Stock_Alerts'].sum() if 'Low_Stock_Alerts' in df.columns else 0
            
            if 'Daily_Consumption' in df.columns:
                mask = df['Daily_Consumption'] > 0
                df.loc[mask, 'Days_to_Depletion'] = df.loc[mask, 'Inventory_Level'] / df.loc[mask, 'Daily_Consumption']
                avg_days = df.loc[mask, 'Days_to_Depletion'].mean()
            else:
                avg_days = 0
            
            insight = f"📦 **Field/Inventory Analysis:**\n\n"
            insight += f"- Total Inventory: **{total_inventory:,.0f} units**\n"
            insight += f"- Low Stock Alerts: **{low_stock_alerts:,.0f}**\n"
            insight += f"- Avg Days to Depletion: **{avg_days:.1f} days**\n"
            
            if 'Store_ID' in df.columns:
                critical_stores = df[df.get('Days_to_Depletion', float('inf')) < 7]
                if not critical_stores.empty:
                    insight += f"- ⚠️ Critical Stores: **{len(critical_stores)}** stores with <7 days inventory\n"

            if 'timestamp' in df.columns:
                df['Date'] = pd.to_datetime(df['timestamp']).dt.date
                daily_inventory = df.groupby('Date')['Inventory_Level'].sum().reset_index()
                
                if 'line' in visualization_type.lower():
                    fig = px.line(daily_inventory, x='Date', y='Inventory_Level',
                                 title='Inventory Level Trend',
                                 color_discrete_sequence=['#10b981'])
                else:
                    fig = px.area(daily_inventory, x='Date', y='Inventory_Level',
                                 title='Inventory Level Trend',
                                 color_discrete_sequence=['#10b981'])
                
                fig.update_layout(template='plotly_white', height=300, margin=dict(l=0, r=0, t=30, b=0))

        else:
            insight = "Analysis type not recognized. Please try rephrasing your query."

        return insight, fig

    def process_chat_query(self, user_message, full_df, chat_history=None):
        """
        Process chatbot conversation with context awareness
        """
        # Check if api_key exists and is valid
        if self.api_key is None or not self.api_key:
            return "❌ Gemini API key not configured. Please add GEMINI_API_KEY to secrets.toml", None

        context = ""
        if chat_history:
            context = "\n\nPrevious Conversation:\n"
            for msg in chat_history[-3:]:
                context += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n"

        data_summary = ""
        if full_df is not None and not full_df.empty:
            domains = full_df['domain'].unique().tolist() if 'domain' in full_df.columns else []
            date_range = ""
            if 'timestamp' in full_df.columns:
                min_date = full_df['timestamp'].min()
                max_date = full_df['timestamp'].max()
                date_range = f"from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            
            data_summary = f"""
Available Data:
- Total Records: {len(full_df)}
- Domains: {', '.join(domains)}
- Date Range: {date_range}
"""

        chat_prompt = f"""
{self.data_schema}

{data_summary}

{context}

You are an AI assistant for a business intelligence dashboard. You have access to real-time data from MongoDB covering Sales, Manufacturing, Testing, and Field/Inventory operations.

User's Question: "{user_message}"

Your task is to:
1. Understand the user's question
2. Determine if visualization is needed
3. If visualization is needed, return JSON with analysis details
4. If it's a conversational question, provide a helpful text response

If the question requires data analysis and visualization, respond with JSON:
{{
    "requires_visualization": true,
    "analysis_type": "sales_revenue | manufacturing_quality | testing | field_inventory",
    "filters": {{
        "time_range": "last week | last month | all",
        "domain": "Sales | Manufacturing | Testing | Field",
        "sku": "product_code or null",
        "line_id": "line_identifier or null",
        "store_id": "store_identifier or null"
    }},
    "visualization_type": "line_chart | bar_chart | area_chart | pie_chart",
    "explanation": "Brief explanation of what you'll show"
}}

If it's a general question or greeting, respond with:
{{
    "requires_visualization": false,
    "response": "Your conversational response here"
}}

Respond with JSON only:
"""

        parsed_response = self._call_gemini_api(chat_prompt)

        if not parsed_response:
            return "❌ Failed to process your question. Please try again.", None

        requires_viz = parsed_response.get('requires_visualization', False)

        if not requires_viz:
            response_text = parsed_response.get('response', 'I understand your question. How can I help you with data analysis?')
            return response_text, None

        explanation = parsed_response.get('explanation', 'Analyzing your data...')
        filters = parsed_response.get('filters', {})
        analysis_type = parsed_response.get('analysis_type', '')
        visualization_type = parsed_response.get('visualization_type', 'bar_chart')

        filtered_df = self._apply_filters(full_df, filters)
        insight, fig = self._execute_analysis(filtered_df, analysis_type, visualization_type)

        full_response = f"💡 {explanation}\n\n{insight}"

        return full_response, fig