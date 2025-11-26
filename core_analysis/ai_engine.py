"""
AI Analysis Engine for AI-CDP
Conversational query processing using Google Gemini API
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
    Conversational analytics engine powered by Google Gemini API
    """

    def __init__(self):
        # Load Gemini API key from secrets
        try:
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                self.api_key = st.secrets['GEMINI_API_KEY']
            else:
                self.api_key = None
                st.warning("Gemini API key not found in secrets. Conversational features will be limited.")
        except Exception as e:
            self.api_key = None
            st.warning(f"Could not load Gemini API key: {str(e)}")

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

    def _call_gemini_api(self, prompt):
        """
        Call Google Gemini API to parse user intent
        
        Args:
            prompt: The full prompt including schema and user query
            
        Returns:
            Parsed JSON response from Gemini
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
            
            # Extract the text response
            if 'candidates' in result and len(result['candidates']) > 0:
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                
                # Clean up the response to extract JSON
                # Remove markdown code blocks if present
                text_response = text_response.replace('```json', '').replace('```', '').strip()
                
                # Parse JSON
                parsed_json = json.loads(text_response)
                return parsed_json
            
            return None
            
        except requests.exceptions.RequestException as e:
            st.error(f"API Request Error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            st.error(f"JSON Parsing Error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected Error: {str(e)}")
            return None

    def _apply_filters(self, df, filters):
        """
        Apply filters to the DataFrame based on parsed intent
        
        Args:
            df: Input DataFrame
            filters: Dictionary of filters from Gemini response
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()

        if filters is None or df.empty:
            return filtered_df

        # Time filter
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

        # Domain filter
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

        # SKU filter
        if 'sku' in filters and 'SKU' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['SKU'] == filters['sku']]

        # Line ID filter
        if 'line_id' in filters and 'Line_ID' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Line_ID'] == filters['line_id']]

        # Store ID filter
        if 'store_id' in filters and 'Store_ID' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Store_ID'] == filters['store_id']]

        return filtered_df

    def _execute_analysis(self, df, analysis_type, visualization_type):
        """
        Execute the specific analysis and create visualization
        
        Args:
            df: Filtered DataFrame
            analysis_type: Type of analysis to perform
            visualization_type: Type of chart to create
            
        Returns:
            Tuple of (insight_message, plotly_figure)
        """
        if df.empty:
            return "No data available for the specified filters.", None

        insight = ""
        fig = None

        # Sales Analysis
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

            # Create visualization
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
                
                fig.update_layout(template='plotly_white', height=400)

        # Manufacturing/Quality Analysis
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

            # Create visualization
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
                fig.update_layout(template='plotly_white', height=400)

        # Testing Analysis
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

            # Create visualization
            if 'pie' in visualization_type.lower() or 'donut' in visualization_type.lower():
                fig = go.Figure(data=[go.Pie(
                    labels=['Passed', 'Failed'],
                    values=[passed, failed],
                    marker=dict(colors=['#10b981', '#ef4444']),
                    hole=0.4
                )])
                fig.update_layout(title='Test Results Distribution', height=400)
            else:
                results_df = pd.DataFrame({'Status': ['Passed', 'Failed'], 'Count': [passed, failed]})
                fig = px.bar(results_df, x='Status', y='Count',
                            title='Test Results',
                            color='Status',
                            color_discrete_map={'Passed': '#10b981', 'Failed': '#ef4444'})
                fig.update_layout(template='plotly_white', height=400)

        # Field/Inventory Analysis
        elif 'field' in analysis_type.lower() or 'inventory' in analysis_type.lower():
            if 'Inventory_Level' not in df.columns:
                return "Field/Inventory data not available in filtered results.", None

            total_inventory = df['Inventory_Level'].sum()
            low_stock_alerts = df['Low_Stock_Alerts'].sum() if 'Low_Stock_Alerts' in df.columns else 0
            
            # Calculate days to depletion
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

            # Create visualization
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
                
                fig.update_layout(template='plotly_white', height=400)

        else:
            insight = "Analysis type not recognized. Please try rephrasing your query."

        return insight, fig

    def process_conversational_query(self, query, full_df):
        """
        Main conversational query processing function
        
        Steps:
        1. Define schema and create prompt for Gemini
        2. Call Gemini API to parse user intent
        3. Apply filters based on parsed intent
        4. Execute analysis and create visualization
        5. Return insights and chart
        
        Args:
            query: User's natural language query
            full_df: Complete unified DataFrame from data_retriever
            
        Returns:
            Tuple of (insight_message, plotly_figure, parsed_intent)
        """
        if not self.api_key:
            return "Gemini API key not configured. Please add it to secrets.toml", None, None

        # Construct prompt for Gemini
        prompt = f"""
{self.data_schema}

Your task is to parse the user's query and return a structured JSON object that defines their intent.

Output JSON Schema:
{{
    "analysis_type": "sales_revenue | manufacturing_quality | testing | field_inventory",
    "filters": {{
        "time_range": "last week | last month | last year | today | all",
        "domain": "Sales | Manufacturing | Testing | Field",
        "sku": "product_code or null",
        "line_id": "line_identifier or null",
        "store_id": "store_identifier or null"
    }},
    "visualization_type": "line_chart | bar_chart | area_chart | pie_chart",
    "metrics": ["list of requested metrics"]
}}

User Query: "{query}"

Rules:
1. Return ONLY valid JSON, no additional text
2. If a filter is not mentioned, set it to null or "all"
3. Choose the most appropriate visualization type
4. Infer the domain from context (e.g., "revenue" -> Sales, "defects" -> Manufacturing)

Return JSON:
"""

        # Call Gemini API
        parsed_intent = self._call_gemini_api(prompt)

        if not parsed_intent:
            return "Failed to parse query. Please try again or rephrase your question.", None, None

        # Apply filters
        filters = parsed_intent.get('filters', {})
        filtered_df = self._apply_filters(full_df, filters)

        # Execute analysis
        analysis_type = parsed_intent.get('analysis_type', '')
        visualization_type = parsed_intent.get('visualization_type', 'bar_chart')
        
        insight, fig = self._execute_analysis(filtered_df, analysis_type, visualization_type)

        return insight, fig, parsed_intent
