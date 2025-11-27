import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

# Configuration
NUM_ROWS = 1000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)

# Store profiles to maintain consistency between ID, Name, and City
STORES = [
    {"id": "STORE-101", "name": "Starbucks Andheri", "city": "Mumbai"},
    {"id": "STORE-102", "name": "Starbucks Indiranagar", "city": "Bengaluru"},
    {"id": "STORE-103", "name": "Starbucks Connaught Place", "city": "New Delhi"},
    {"id": "STORE-104", "name": "Starbucks Jubilee Hills", "city": "Hyderabad"},
    {"id": "STORE-105", "name": "Starbucks Koregaon Park", "city": "Pune"},
]

def random_date(start, end):
    """Generate a random datetime between `start` and `end`"""
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def generate_data():
    data = []
    
    for _ in range(NUM_ROWS):
        # Select a random store profile
        store = random.choice(STORES)
        
        # Generate random date/time within 2023-2025
        dt = random_date(START_DATE, END_DATE)
        date_str = dt.strftime("%Y-%m-%d")
        
        # Create a timestamp that matches the date but adds time info (ISO format)
        # This replaces the static 1970 epoch from the example with a real value
        timestamp_str = dt.isoformat() 
        
        # Random numerical values for metrics
        inventory = random.randint(50, 500)
        daily_consumption = random.randint(100, 300)
        footfall = random.randint(200, 1500)
        
        # Logic for Low Stock Alert (Simple rule based on inventory)
        low_stock = "YES" if inventory < 100 else "NO"
        
        # Anomalies generation (Weighted probabilities)
        # 90% None, 8% Mismatch, 2% Data Missing
        anomalies = random.choices(["None", "Mismatch", "Data Missing"], weights=[90, 8, 2], k=1)[0]
        
        # Weather data
        temp = round(random.uniform(15.0, 42.0), 2)
        humidity = random.randint(30, 90)

        # Construct the record matching the user's requested schema
        record = {
            "_id": str(uuid.uuid4()).replace("-", "")[:24], # 24-char hex string like MongoDB ObjectId
            "Store_ID": store["id"],
            "Store_Name": store["name"],
            "City": store["city"],
            "Inventory_Level": inventory,
            "Low_Stock_Alerts": low_stock,
            "Anomalies": anomalies,
            "Daily_Consumption": daily_consumption,
            "Temperature_Celsius": temp,
            "Humidity_Percent": humidity,
            "Customer_Footfall": footfall,
            "Date": date_str,
            "type": "F",
            "timestamp": timestamp_str
        }
        data.append(record)
        
    return data

if __name__ == "__main__":
    print(f"Generating {NUM_ROWS} rows of data...")
    dataset = generate_data()
    
    # Create DataFrame
    df = pd.DataFrame(dataset)
    
    # Save to CSV
    csv_filename = "store_data.csv"
    df.to_csv(csv_filename, index=False)
    
    print(f"✅ Success! Data saved to '{csv_filename}'")
    print("\nFirst 5 rows preview:")
    print(df.head())