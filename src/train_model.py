import os
import pandas as pd
import pickle
import json
import mlflow
import mlflow.sklearn
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

PROCESSED_DATA_PATH = "data/processed/processed_weather_data.csv"
MODEL_PATH = "models/linear_reg_model.pkl"
METRICS_PATH = "report/metrics.json"

def evaluate_metrics(actual, pred):
    rmse = mean_squared_error(actual, pred) ** 0.5
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

def train_model():
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"Processed data not found at {PROCESSED_DATA_PATH}")
        return

    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    X = df.drop(columns=["temp_c"])
    y = df["temp_c"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # MLflow Setup
    # Assumes mlflow ui is running locally on port 9000
    mlflow.set_tracking_uri(uri="http://127.0.0.1:9000")
    mlflow.set_experiment("Weather Prediction")

    with mlflow.start_run():
        lr = LinearRegression()
        lr.fit(X_train, y_train)

        predicted_qualities = lr.predict(X_test)

        (rmse, mae, r2) = evaluate_metrics(y_test, predicted_qualities)

        print(f"Linear Regression model (rmse={rmse:f}, mae={mae:f}, r2={r2:f})")

        # Log metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        # Save metrics for DVC locally
        os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
        with open(METRICS_PATH, "w") as f:
            json.dump({"rmse": rmse, "mae": mae, "r2": r2}, f, indent=4)

        # Infer signature and register
        signature = infer_signature(X_train, predicted_qualities)
        mlflow.sklearn.log_model(
            sk_model=lr,
            artifact_path="weather_model",
            signature=signature,
            input_example=X_train,
            registered_model_name="tracking-weather-prediction-model",
        )

        # Save model locally for Flask App
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(lr, f)
        
        print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
