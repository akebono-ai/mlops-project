import os
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import mlflow

def evaluate(input_dir: str, model_dir: str):
    test_path = os.path.join(input_dir, "test.csv")
    
    print(f"Loading test data from {test_path}")
    df = pd.read_csv(test_path)
    
    X_test = df.drop('Churn', axis=1)
    y_test = df['Churn']
    
    print("Loading model...")
    model_path = os.path.join(model_dir, "rf_model.pkl")
    model = joblib.load(model_path)
    
    print("Evaluating model...")
    predictions = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # MLflow tracking
    mlflow.set_experiment("Telco_Customer_Churn")
    with mlflow.start_run():
        mlflow.log_param("model_type", "RandomForestClassifier")
        
        # We can fetch the model parameters 
        params = model.get_params()
        mlflow.log_params(params)
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        
        # Log Model
        mlflow.sklearn.log_model(model, "random_forest_model")
        
        print("Model and metrics logged to MLflow successfully.")

if __name__ == "__main__":
    INPUT_DIR = "data/processed"
    MODEL_DIR = "models"
    evaluate(INPUT_DIR, MODEL_DIR)
