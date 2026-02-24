import os
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler, LabelEncoder

RAW_DATA_PATH = "data/raw/raw_weather_data.csv"
PROCESSED_DATA_PATH = "data/processed/processed_weather_data.csv"
SCALER_PATH = "models/scaler.pkl"
ENCODER_PATH = "models/label_encoder.pkl"

def preprocess_data():
    if not os.path.exists(RAW_DATA_PATH):
        print(f"File not found: {RAW_DATA_PATH}")
        return

    df = pd.DataFrame(pd.read_csv(RAW_DATA_PATH))
    
    # Feature Engineering
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['hour'] = df['date_time'].dt.hour
    df['day'] = df['date_time'].dt.day
    df['month'] = df['date_time'].dt.month
    df['day_of_year'] = df['date_time'].dt.dayofyear
    
    # Selecting the relevant features based on user's test case
    # humidity, wind_kph (changed from wind_speed), condition, hour, day, month, day_of_year
    # Target: temp_c
    
    features = ['humidity', 'wind_kph', 'condition', 'hour', 'day', 'month', 'day_of_year']
    target = 'temp_c'
    
    # Keep only relevant columns
    df = df[features + [target]]
    
    # Drop NAs
    df = df.dropna()
    
    os.makedirs("models", exist_ok=True)

    # Encode categorical feature
    le = LabelEncoder()
    # Handle unseen labels by adding a default or fitting on known
    df['weather_condition'] = le.fit_transform(df['condition'])
    
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(le, f)
        
    df = df.drop(columns=['condition'])
    
    # Scale numerical features
    num_features = ['humidity', 'wind_kph', 'hour', 'day', 'month', 'day_of_year', 'weather_condition']
    scaler = StandardScaler()
    df[num_features] = scaler.fit_transform(df[num_features])
    
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
        
    # Save processed data
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Data preprocessed and saved to {PROCESSED_DATA_PATH}")

if __name__ == "__main__":
    preprocess_data()
