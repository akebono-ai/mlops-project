import os
import json
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_KEY")
CITY = "Jakarta"
URL = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}&aqi=no"

RAW_DATA_PATH = "data/raw/raw_weather_data.csv"
JSON_DATA_PATH = "data/raw/raw_weather_data.json"

def fetch_weather_data():
    print(f"Fetching data from {URL}")
    response = requests.get(URL)
    
    if response.status_code == 200:
        data = response.json()
        
        # Save raw JSON for reference
        os.makedirs(os.path.dirname(JSON_DATA_PATH), exist_ok=True)
        with open(JSON_DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
        
        # Extract features
        location = data["location"]
        current = data["current"]
        
        extracted_data = {
            "date_time": location["localtime"],
            "city": location["name"],
            "temp_c": current["temp_c"],
            "humidity": current["humidity"],
            "wind_kph": current["wind_kph"],
            "condition": current["condition"]["text"],
            "cloud": current["cloud"],
            "pressure_mb": current["pressure_mb"],
            "precip_mm": current["precip_mm"],
            "vis_km": current["vis_km"]
        }
        
        df = pd.DataFrame([extracted_data])
        
        # Append to CSV
        os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
        if os.path.exists(RAW_DATA_PATH):
            df.to_csv(RAW_DATA_PATH, mode='a', header=False, index=False)
        else:
            df.to_csv(RAW_DATA_PATH, mode='w', header=True, index=False)
            
        print(f"Data successfully saved to {RAW_DATA_PATH}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        response.raise_for_status()

if __name__ == "__main__":
    fetch_weather_data()
