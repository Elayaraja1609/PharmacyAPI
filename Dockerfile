# Dockerfile for AWS App Runner or ECS deployment
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

