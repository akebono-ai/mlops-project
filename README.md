# End-to-End MLOps Weather Prediction Pipeline

This project demonstrates a complete Machine Learning Operations (MLOps) lifecycle for a weather prediction system. It integrates modern tools like **Apache Airflow**, **DVC**, **MLflow**, **Flask**, **Docker**, **Kubernetes (Minikube)**, and **GitHub Actions** to achieve automation, scalability, and reproducibility.

---

## 🏗️ Architecture Overview

The system architecture consists of several interconnected layers to manage the end-to-end ML lifecycle:

1.  **Data Ingestion & Orchestration (Airflow + DVC):** Automated data fetching from WeatherAPI, preprocessing, and model training. DVC handles data and model versioning.
2.  **Experiment Tracking & Registry (MLflow):** Tracks model performance metrics (RMSE, MAE, R2) and manages model artifacts and versions.
3.  **Application Layer (Flask + MongoDB):** A full-stack web application providing user authentication and real-time weather predictions using the trained model.
4.  **Containerization & Deployment (Docker + Kubernetes):** The application and database are containerized and deployed to a Minikube cluster for scalable serving.
5.  **CI/CD (GitHub Actions):** Automated testing, Docker image building, and Kubernetes deployment pipelines.

---

## 🚀 How to Run the Project Locally

Follow these steps to set up and run the entire pipeline on your local machine.

### Prerequisites
Ensure you have the following installed:
*   Python 3.9+
*   Git
*   Docker & Docker Compose
*   Minikube & kubectl
*   (Optional but recommended) A virtual environment manager like `venv` or `conda`

### Step 1: Environment Setup & Initialization

1.  **Clone the repository and navigate to the project directory:**
    ```bash
    git clone <your-repo-url>
    cd mlops-project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize Git and DVC (if not already initialized):**
    ```bash
    git init
    dvc init
    ```

### Step 2: Generate Initial Data
Before running the pipeline, we need some historical data to train the model. We provide a script to generate synthetic weather data for Jakarta.

```bash
python src/generate_dummy_data.py
```
*This will create `data/raw/raw_weather_data.csv` with 1000 records.*

### Step 3: Run the Machine Learning Pipeline (DVC & MLflow)

1.  **Start the MLflow Tracking Server (in a separate terminal):**
    ```bash
    # Activate your venv if needed
    mlflow server --host 127.0.0.1 --port 9000
    ```
    *You can access the MLflow UI at `http://127.0.0.1:9000` to view experiments and registered models.*

2.  **Run the DVC Pipeline:**
    This step will execute preprocessing and model training.
    ```bash
    dvc repro
    ```
    *DVC will run `src/data_preprocessing.py` followed by `src/train_model.py`. The trained model and transformers will be saved in the `models/` directory, and metrics will be logged to MLflow.*

3.  **Track the generated artifacts:**
    ```bash
    dvc add data/raw
    git add dvc.yaml dvc.lock data/raw.dvc .gitignore
    git commit -m "Run initial ML pipeline and track models"
    ```

### Step 4: Run the Web Application Locally (Docker Compose)

You can run the Flask app and MongoDB locally using Docker Compose to verify everything works before deploying to Kubernetes.

1.  **Start the services:**
    ```bash
    docker-compose up --build
    ```
    *This will build the Flask app image and start both the app and MongoDB.*

2.  **Access the application:**
    Open your browser and navigate to `http://localhost:5000`. You can Sign Up, Log In, and use the prediction form.

3.  **Stop the services:**
    ```bash
    docker-compose down
    ```

### Step 5: Orchestrate with Apache Airflow (Optional setup)

To automate the pipeline execution (data ingestion -> preprocessing -> training):

1.  Initialize Airflow (usually under `~/airflow`):
    ```bash
    airflow db init
    airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
    ```
2.  Copy the DAG file:
    ```bash
    cp dags/ml_pipeline_dag.py ~/airflow/dags/
    ```
3.  Start the Airflow webserver and scheduler (in separate terminals):
    ```bash
    airflow webserver --port 8080
    # In another terminal
    airflow scheduler
    ```
    *Access the Airflow UI at `http://localhost:8080` to trigger the `mlops_weather_prediction_dag`.*

### Step 6: Deploy to Kubernetes (Minikube)

Once you are satisfied with the local testing, you can deploy the application to a local Kubernetes cluster.

1.  **Start Minikube:**
    ```bash
    minikube start
    ```

2.  **Point your local Docker daemon to the Minikube docker daemon (Optional but recommended for local images):**
    ```bash
    # Windows PowerShell
    minikube docker-env | Invoke-Expression
    # Linux/Mac
    eval $(minikube docker-env)
    ```

3.  **Build the Docker image (if you configured the docker-env above, otherwise skip this and rely on Docker Hub if you pushed it):**
    ```bash
    docker build -t your-dockerhub-username/mlops-weather-app:latest .
    ```
    *(Note: Remember to update the `image` field in `k8s/app.yaml` with your actual image name).*

4.  **Deploy MongoDB and the Flask App:**
    ```bash
    kubectl apply -f k8s/database.yaml
    kubectl apply -f k8s/app.yaml
    ```

5.  **Verify the deployment:**
    ```bash
    kubectl get pods
    kubectl get services
    ```

6.  **Access the application via Minikube:**
    Minikube provides a direct command to access the NodePort service:
    ```bash
    minikube service flask-app-service --url
    ```
    *Copy the provided URL into your browser to access the deployed Web App!*

---

## 🛠️ Modifying the CI/CD Pipeline

The `.github/workflows/` directory contains two pipelines:
1.  **`ci-pipeline.yml`**: Triggers on push to `testing` or `main` branches. It runs `pytest` and builds/pushes the Docker image.
    *   **Requirement:** Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` as secrets in your GitHub repository settings.
2.  **`cd-pipeline.yml`**: Triggers on push to the `prod` branch. It sets up Minikube and applies the Kubernetes manifests.

To use the CD pipeline effectively, ensure the image referenced in `k8s/app.yaml` matches the one built and pushed by your CI pipeline.
