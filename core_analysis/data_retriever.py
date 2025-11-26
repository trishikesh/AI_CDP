"""
Data Retriever Module for AI-CDP
Handles MongoDB Atlas connections and data retrieval with proper schema mapping
"""

import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import streamlit as st


class DataRetriever:
    """
    Centralized data retrieval class with explicit schema mapping
    Maps disparate MongoDB collection schemas to unified analysis-ready format
    """

    def __init__(self):
        """Initialize MongoDB connection using Streamlit secrets or environment variables"""
        try:
            # Try Streamlit secrets first (for deployment)
            if hasattr(st, 'secrets') and 'mongodb' in st.secrets:
                mongo_uri = st.secrets['mongodb']['uri']
                db_name = st.secrets['mongodb']['database']
            else:
                # Fallback to environment variables
                mongo_uri = os.getenv('MONGODB_URI')
                db_name = os.getenv('MONGODB_DATABASE', 'ai_cdp')

            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]

            # Test connection
            self.client.admin.command('ping')

        except Exception as e:
            st.error(f"MongoDB Connection Error: {str(e)}")
            raise

    def _convert_to_datetime(self, df, date_column):
        """
        Safely convert date/timestamp columns to pandas datetime

        Args:
            df: DataFrame to process
            date_column: Name of the column to convert

        Returns:
            DataFrame with converted datetime column
        """
        if date_column in df.columns:
            try:
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            except Exception:
                pass
        return df

    def _safe_numeric_conversion(self, df, columns):
        """
        Safely convert columns to numeric, filling NaN with 0

        Args:
            df: DataFrame to process
            columns: List of column names to convert

        Returns:
            DataFrame with converted numeric columns
        """
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df

    def get_field_data(self, start_date=None, end_date=None):
        """
        Retrieve Field/Inventory data with proper schema mapping

        Schema Mapping:
        - Date -> timestamp (unified datetime field)
        - All numeric fields validated

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            DataFrame with mapped Field data
        """
        try:
            collection = self.db['Field']

            # Build query filter
            query = {}
            if start_date and end_date:
                query['Date'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }

            # Fetch data
            cursor = collection.find(query)
            df = pd.DataFrame(list(cursor))

            if df.empty:
                return pd.DataFrame()

            # Drop MongoDB _id field
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)

            # CRITICAL MAPPING: Date -> timestamp
            if 'Date' in df.columns:
                df['timestamp'] = df['Date']
                df = self._convert_to_datetime(df, 'timestamp')

            # Ensure numeric conversions
            numeric_columns = [
                'Inventory_Level',
                'Low_Stock_Alerts',
                'Daily_Consumption'
            ]
            df = self._safe_numeric_conversion(df, numeric_columns)

            return df

        except Exception as e:
            st.error(f"Error retrieving Field data: {str(e)}")
            return pd.DataFrame()

    def get_manufacturing_data(self, start_date=None, end_date=None):
        """
        Retrieve Manufacturing data with proper schema mapping

        Schema Mapping:
        - Machine_ID -> Line_ID (unified machine identifier)
        - Product -> SKU (unified product identifier)
        - timestamp remains timestamp

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            DataFrame with mapped Manufacturing data
        """
        try:
            collection = self.db['Manufacturing']

            # Build query filter
            query = {}
            if start_date and end_date:
                query['timestamp'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }

            # Fetch data
            cursor = collection.find(query)
            df = pd.DataFrame(list(cursor))

            if df.empty:
                return pd.DataFrame()

            # Drop MongoDB _id field
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)

            # CRITICAL MAPPINGS
            if 'Machine_ID' in df.columns:
                df['Line_ID'] = df['Machine_ID']

            if 'Product' in df.columns:
                df['SKU'] = df['Product']

            # Convert timestamp
            df = self._convert_to_datetime(df, 'timestamp')

            # Ensure numeric conversions
            numeric_columns = [
                'Quantity_Produced',
                'Defects'
            ]
            df = self._safe_numeric_conversion(df, numeric_columns)

            return df

        except Exception as e:
            st.error(f"Error retrieving Manufacturing data: {str(e)}")
            return pd.DataFrame()

    def get_sales_data(self, start_date=None, end_date=None):
        """
        Retrieve Sales data with proper schema mapping

        Schema Mapping:
        - Total_Amount -> Revenue (unified revenue field)
        - timestamp remains timestamp

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            DataFrame with mapped Sales data
        """
        try:
            collection = self.db['Sales']

            # Build query filter
            query = {}
            if start_date and end_date:
                query['timestamp'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }

            # Fetch data
            cursor = collection.find(query)
            df = pd.DataFrame(list(cursor))

            if df.empty:
                return pd.DataFrame()

            # Drop MongoDB _id field
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)

            # CRITICAL MAPPING: Total_Amount -> Revenue
            if 'Total_Amount' in df.columns:
                df['Revenue'] = df['Total_Amount']

            # Convert timestamp
            df = self._convert_to_datetime(df, 'timestamp')

            # Ensure numeric conversions
            numeric_columns = [
                'Revenue',
                'Total_Amount',
                'Quantity'
            ]
            df = self._safe_numeric_conversion(df, numeric_columns)

            return df

        except Exception as e:
            st.error(f"Error retrieving Sales data: {str(e)}")
            return pd.DataFrame()

    def get_testing_data(self, start_date=None, end_date=None):
        """
        Retrieve Testing/Quality data with proper schema mapping

        Schema Mapping:
        - Passed/Failed -> Pass_Fail_Status (unified status field)
        - timestamp remains timestamp

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            DataFrame with mapped Testing data
        """
        try:
            collection = self.db['Testing']

            # Build query filter
            query = {}
            if start_date and end_date:
                query['timestamp'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }

            # Fetch data
            cursor = collection.find(query)
            df = pd.DataFrame(list(cursor))

            if df.empty:
                return pd.DataFrame()

            # Drop MongoDB _id field
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)

            # CRITICAL MAPPING: Passed/Failed -> Pass_Fail_Status
            if 'Passed/Failed' in df.columns:
                df['Pass_Fail_Status'] = df['Passed/Failed']

            # Convert timestamp
            df = self._convert_to_datetime(df, 'timestamp')

            return df

        except Exception as e:
            st.error(f"Error retrieving Testing data: {str(e)}")
            return pd.DataFrame()

    def get_all_data(self, start_date=None, end_date=None):
        """
        Retrieve all domain data with unified schema mapping

        Args:
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)

        Returns:
            Dictionary containing all mapped DataFrames
        """
        return {
            'field': self.get_field_data(start_date, end_date),
            'manufacturing': self.get_manufacturing_data(start_date, end_date),
            'sales': self.get_sales_data(start_date, end_date),
            'testing': self.get_testing_data(start_date, end_date)
        }

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()