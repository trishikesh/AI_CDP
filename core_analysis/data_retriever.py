import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np # Needed for safe numeric conversion

# The database name is explicitly set
DB_NAME = "Starbucks"

@st.cache_resource 
def get_mongo_client():
    """Initializes and caches the MongoDB client connection."""
    try:
        # Fetch the URI securely from Streamlit's secrets
        uri = st.secrets["MONGO_URI"]
        client = MongoClient(uri)
        # Test connection by running a simple command
        client.admin.command('ping') 
        return client
    except Exception as e:
        # Display a custom error message for the user
        st.error(f"FATAL ERROR: Could not connect to MongoDB. Check URI and IP Whitelisting. Details: {e}")
        return None

@st.cache_data(ttl=60) 
def fetch_all_data():
    """Fetches all data, cleans, and standardizes field names."""
    client = get_mongo_client()
    if client is None:
        return pd.DataFrame()

    db = client[DB_NAME]
    
    # Mapping to standardize the key fields upon retrieval and handle type conversion
    FIELD_MAPPING = {
        # Standardized column names are used for cross-domain analysis in the AI engine
        "Manufacturing": {"Quantity_Produced": "Quantity_Produced", "Defects": "Defects", "Machine_ID": "Line_ID", "timestamp": "timestamp", "Product": "SKU"},
        "Testing": {"Passed/Failed": "Pass_Fail_Status", "Batch_ID": "Batch_ID", "timestamp": "timestamp"},
        "Sales": {"Total_Amount": "Revenue", "Quantity": "Quantity", "SKU": "SKU", "timestamp": "timestamp"},
        "Field": {"Inventory_Level": "Inventory_Level", "Daily_Consumption": "Daily_Consumption", "Date": "timestamp", "Low_Stock_Alerts": "Alerts"}
    }
    
    all_records = []
    
    for coll_name, mapping in FIELD_MAPPING.items():
        try:
            cursor = db[coll_name].find({})
            df_collection = pd.DataFrame(list(cursor))
            
            if not df_collection.empty:
                # 1. Clean up (Drop Mongo _id and non-mapped columns)
                if '_id' in df_collection.columns:
                    df_collection = df_collection.drop(columns=['_id'])
                
                # 2. Rename and standardize fields based on the mapping
                df_collection = df_collection.rename(columns={k: v for k, v in mapping.items() if k in df_collection.columns})
                
                # 3. Add 'Domain' column
                df_collection['Domain'] = coll_name
                
                # 4. Convert timestamp
                if 'timestamp' in df_collection.columns:
                    df_collection['timestamp'] = pd.to_datetime(df_collection['timestamp'], errors='coerce')
                
                # 5. Type Conversion for critical numeric fields (using NumPy for efficiency)
                for col in ['Revenue', 'Quantity', 'Defects', 'Inventory_Level', 'Daily_Consumption']:
                    if col in df_collection.columns:
                        df_collection[col] = pd.to_numeric(df_collection[col], errors='coerce').fillna(0)
                
                all_records.append(df_collection)
                
        except Exception as e:
            st.warning(f"Error fetching data from collection '{coll_name}': {e}")
            
    if all_records:
        # Concatenate all data into the Single Source of Truth DataFrame
        combined_df = pd.concat(all_records, ignore_index=True)
        # Sort by timestamp for proper time-series analysis
        combined_df = combined_df.sort_values('timestamp', ascending=False).reset_index(drop=True)
        return combined_df
        
    return pd.DataFrame()

@st.cache_data
def get_unique_skus(df):
    """Retrieves a list of all unique SKUs."""
    if df.empty or 'SKU' not in df.columns:
        return []
    return sorted(df['SKU'].dropna().unique().tolist())