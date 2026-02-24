FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV MONGO_URI="mongodb://database:27017/"

EXPOSE 5000

CMD ["python", "web_app/app.py"]
