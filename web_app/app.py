import os
import pickle
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "super_secret_key"

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.weather_db
users_collection = db.users

# Load ML artifacts safely
MODEL_PATH = "../models/linear_reg_model.pkl"
SCALER_PATH = "../models/scaler.pkl"
ENCODER_PATH = "../models/label_encoder.pkl"

model, scaler, label_encoder = None, None, None

def load_artifacts():
    global model, scaler, label_encoder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base_dir, MODEL_PATH), "rb") as f:
            model = pickle.load(f)
        with open(os.path.join(base_dir, SCALER_PATH), "rb") as f:
            scaler = pickle.load(f)
        with open(os.path.join(base_dir, ENCODER_PATH), "rb") as f:
            label_encoder = pickle.load(f)
    except FileNotFoundError:
        print("Warning: Model artifacts not found. Please run DVC pipeline first.")

load_artifacts()

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("predict"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            session["user"] = username
            return redirect(url_for("predict"))
        else:
            flash("Invalid credentials")
            
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if users_collection.find_one({"username": username}):
            flash("Username already exists")
        else:
            users_collection.insert_one({"username": username, "password": password})
            flash("Signup successful, please login")
            return redirect(url_for("login"))
            
    return render_template("signup.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))
        
    if request.method == "POST":
        if not model or not scaler or not label_encoder:
            # Attempt lazy routing load
            load_artifacts()
            if not model:
                return "Models are not loaded on server. Please train."
        
        humidity = float(request.form["humidity"])
        wind_kph = float(request.form["wind_kph"])
        condition = request.form["condition"]
        hour = int(request.form["hour"])
        day = int(request.form["day"])
        month = int(request.form["month"])
        day_of_year = int(request.form["day_of_year"])
        
        # Handle unseen classes gracefully
        try:
            weather_condition = label_encoder.transform([condition])[0]
        except ValueError:
            weather_condition = label_encoder.transform([label_encoder.classes_[0]])[0]
            
        features = pd.DataFrame([{
            "humidity": humidity, "wind_kph": wind_kph, 
            "hour": hour, "day": day, "month": month, 
            "day_of_year": day_of_year, "weather_condition": weather_condition
        }])
        
        # Scale specific numerical columns
        num_features = ['humidity', 'wind_kph', 'hour', 'day', 'month', 'day_of_year', 'weather_condition']
        features[num_features] = scaler.transform(features[num_features])
        
        prediction = model.predict(features)[0]
        
        return render_template("prediction.html", prediction=round(prediction, 1))
        
    return render_template("weather_form.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
