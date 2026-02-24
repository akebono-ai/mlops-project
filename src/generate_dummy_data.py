import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dummy_data(output_path, num_records=1000):
    start_date = datetime.now() - timedelta(days=num_records//4)
    data = []
    
    conditions = ["Sunny", "Partly cloudy", "Cloudy", "Overcast", "Mist", "Patchy rain possible", "Light rain", "Moderate rain", "Heavy rain", "Thunderstorm"]
    
    for i in range(num_records):
        current = start_date + timedelta(hours=i*6)
        
        # Synthetic generation rules to create some correlation
        hour = current.hour
        month = current.month
        
        # Temp has diurnal and seasonal cycle
        base_temp = 28 + (4 if 10 <= hour <= 16 else 0) - (2 if hour <= 5 else 0)
        
        humidity = np.random.uniform(55, 95)
        wind_kph = np.random.uniform(2, 25)
        
        condition = np.random.choice(conditions)
        if "rain" in condition.lower() or "thunder" in condition.lower():
            humidity += 10
            base_temp -= 2
            
        temp = base_temp - (humidity - 70) * 0.05 + wind_kph * 0.02 + np.random.normal(0, 1)
        
        data.append({
            "date_time": current.strftime("%Y-%m-%d %H:%M"),
            "city": "Jakarta",
            "temp_c": round(temp, 1),
            "humidity": round(min(100, humidity), 1),
            "wind_kph": round(wind_kph, 1),
            "condition": condition,
            "cloud": np.random.randint(0, 100),
            "pressure_mb": round(np.random.uniform(1005, 1015), 1),
            "precip_mm": round(np.random.uniform(0, 10) if "rain" in condition.lower() else 0, 1),
            "vis_km": round(np.random.uniform(2, 10), 1)
        })

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} dummy records at {output_path}")

if __name__ == "__main__":
    generate_dummy_data("data/raw/raw_weather_data.csv", 1000)
