import os
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv() 

# --- CONFIGURATION ---
MONGO_URI = os.getenv("MONGO_URI") 
DB_NAME = "Starbucks"
DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")

# Mapping of your local file to your MongoDB collection name
DATA_MAPPING = {
    "manufacturing.csv": "Manufacturing",
    "testing.csv": "Testing",
    "field.csv": "Field",
    "sales.csv": "Sales",
}

def connect_to_mongo():
    """Establishes connection to MongoDB Atlas."""
    if not MONGO_URI:
        print("❌ Configuration Error: MONGO_URI is not set in the .env file.")
        return None
        
    try:
        # Crucial: Setting a short timeout to diagnose connection failure faster.
        # SSL is the default, essential for Atlas connections.
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) 
        db = client[DB_NAME]
        
        # Test connection by forcing a simple operation (this checks connectivity/auth)
        client.admin.command('ping') 
        
        print(f"✅ Connection successful to Database: {DB_NAME}")
        return db
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ Connection Error: Timeout accessing cluster.")
        print("HINT: This usually means your IP address is NOT whitelisted in MongoDB Atlas.")
        print(f"Error details: {e}")
        return None
    except Exception as e:
        print(f"❌ Connection Error (Authentication/Configuration): {e}")
        print("HINT: Check username/password in the MONGO_URI.")
        return None

def ingest_data():
    """Reads CSVs, processes them, and loads into MongoDB collections."""
    db = connect_to_mongo()
    
    # FIX: Check if db is explicitly None (Pymongo 4.0+ requirement)
    if db is None:
        print("🛑 Data ingestion aborted due to connection failure.")
        return

    for file_name, collection_name in DATA_MAPPING.items():
        file_path = os.path.join(DATA_DIR, file_name)
        
        if not os.path.exists(file_path):
            print(f"⚠️ Skipping {file_name}: File not found at {file_path}")
            continue

        print(f"\n--- Processing {file_name} into {collection_name} ---")
        try:
            # 1. EXTRACT: Read CSV into Pandas DataFrame
            df = pd.read_csv(file_path)

            # 2. TRANSFORM: Add mandatory fields and standardize
            df['type'] = collection_name[0] # Add 'M', 'T', 'F', or 'S'
            
            # Simplified date column detection: finds the first column containing 'date' or 'time'
            date_col = next((col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()), None)
            
            if date_col:
                 df['timestamp'] = pd.to_datetime(df[date_col], errors='coerce')
                 df = df.drop(columns=[date_col]) 
            else:
                 # Default to current time if no explicit date/time column is found
                 df['timestamp'] = datetime.now() 
            
            # Convert DataFrame to a list of dictionaries (MongoDB format)
            records = df.to_dict('records')
            
            # Get the target collection
            collection = db[collection_name]
            
            # 3. LOAD: Insert the records into MongoDB
            # We are using insert_many, which is efficient for bulk upload.
            result = collection.insert_many(records)
            print(f"✅ Successfully inserted {len(result.inserted_ids)} records.")

        except Exception as e:
            print(f"❌ Failed to ingest data from {file_name}. Error: {e}")

if __name__ == "__main__":
    ingest_data()