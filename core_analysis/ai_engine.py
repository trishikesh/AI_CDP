"""
AI Analysis Engine for AI-CDP
Contains corrected analysis logic using properly mapped MongoDB schema
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class AIEngine:
    """
    Analytics engine with corrected schema-aware analysis functions
    """

    def __init__(self):
        pass

    def analyze_sales(self, sales_df):
        """
        Sales Analysis with corrected Revenue/Profit calculations

        Uses mapped 'Revenue' field (from Total_Amount)
        Calculates Profit at 40% margin

        Args:
            sales_df: DataFrame with sales data (must have 'Revenue' and 'timestamp')

        Returns:
            Dictionary containing sales metrics and visualization data
        """
        if sales_df.empty:
            return {
                'total_revenue': 0,
                'total_profit': 0,
                'profit_margin': 0,
                'revenue_trend': pd.DataFrame(),
                'top_products': pd.DataFrame()
            }

        # Ensure Revenue column exists
        if 'Revenue' not in sales_df.columns:
            return {
                'total_revenue': 0,
                'total_profit': 0,
                'profit_margin': 0,
                'revenue_trend': pd.DataFrame(),
                'top_products': pd.DataFrame()
            }

        # Calculate Profit (40% margin)
        sales_df['Profit'] = sales_df['Revenue'] * 0.40

        # Aggregate metrics
        total_revenue = sales_df['Revenue'].sum()
        total_profit = sales_df['Profit'].sum()
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Revenue trend over time
        revenue_trend = pd.DataFrame()
        if 'timestamp' in sales_df.columns:
            sales_df['Date'] = pd.to_datetime(sales_df['timestamp']).dt.date
            revenue_trend = sales_df.groupby('Date').agg({
                'Revenue': 'sum',
                'Profit': 'sum'
            }).reset_index()
            revenue_trend = revenue_trend.sort_values('Date')

        # Top products by revenue
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

        Uses mapped 'Line_ID' (from Machine_ID) and 'Quantity_Produced', 'Defects'
        Flags anomalies where defect rate > 5%

        Args:
            manufacturing_df: DataFrame with manufacturing data

        Returns:
            Dictionary containing quality metrics and visualization data
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

        # Calculate defect rate per batch
        manufacturing_df['Defect_Rate'] = 0
        if 'Quantity_Produced' in manufacturing_df.columns and 'Defects' in manufacturing_df.columns:
            mask = manufacturing_df['Quantity_Produced'] > 0
            manufacturing_df.loc[mask, 'Defect_Rate'] = (
                manufacturing_df.loc[mask, 'Defects'] / 
                manufacturing_df.loc[mask, 'Quantity_Produced'] * 100
            )

        # Aggregate metrics
        total_produced = manufacturing_df['Quantity_Produced'].sum()
        total_defects = manufacturing_df['Defects'].sum()
        avg_defect_rate = (total_defects / total_produced * 100) if total_produced > 0 else 0

        # Defect trend over time
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

        # Line/Machine performance
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

            # Flag anomalies (defect rate > 5%)
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

        Uses 'Inventory_Level' and 'Daily_Consumption' to predict stock depletion
        This is the key predictive metric for inventory management

        Args:
            field_df: DataFrame with field/inventory data

        Returns:
            Dictionary containing inventory metrics and predictions
        """
        if field_df.empty:
            return {
                'total_inventory': 0,
                'low_stock_alerts': 0,
                'avg_days_to_depletion': 0,
                'critical_stores': pd.DataFrame(),
                'inventory_trend': pd.DataFrame()
            }

        # Calculate Days-to-Depletion (key predictive metric)
        field_df['Days_to_Depletion'] = 0
        if 'Inventory_Level' in field_df.columns and 'Daily_Consumption' in field_df.columns:
            mask = field_df['Daily_Consumption'] > 0
            field_df.loc[mask, 'Days_to_Depletion'] = (
                field_df.loc[mask, 'Inventory_Level'] / 
                field_df.loc[mask, 'Daily_Consumption']
            )

        # Replace infinite values with 999 (effectively unlimited)
        field_df['Days_to_Depletion'] = field_df['Days_to_Depletion'].replace([np.inf, -np.inf], 999)

        # Aggregate metrics
        total_inventory = field_df['Inventory_Level'].sum()
        low_stock_alerts = field_df['Low_Stock_Alerts'].sum()
        avg_days_to_depletion = field_df[field_df['Days_to_Depletion'] < 999]['Days_to_Depletion'].mean()

        # Critical stores (Days to Depletion < 7 days)
        critical_stores = pd.DataFrame()
        if 'Store_ID' in field_df.columns:
            critical_mask = field_df['Days_to_Depletion'] < 7
            critical_stores = field_df[critical_mask][
                ['Store_ID', 'Inventory_Level', 'Daily_Consumption', 'Days_to_Depletion']
            ].sort_values('Days_to_Depletion')

        # Inventory trend over time
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

        Uses mapped 'Pass_Fail_Status' field

        Args:
            testing_df: DataFrame with testing data

        Returns:
            Dictionary containing testing metrics
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

        Args:
            data_dict: Dictionary with keys 'sales', 'manufacturing', 'field', 'testing'

        Returns:
            Dictionary containing all analysis results
        """
        return {
            'sales': self.analyze_sales(data_dict.get('sales', pd.DataFrame())),
            'quality': self.analyze_quality(data_dict.get('manufacturing', pd.DataFrame())),
            'inventory': self.analyze_inventory(data_dict.get('field', pd.DataFrame())),
            'testing': self.analyze_testing(data_dict.get('testing', pd.DataFrame()))
        }