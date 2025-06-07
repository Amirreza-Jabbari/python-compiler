# auth_service/Dockerfile
FROM python:3.9-slim

# Install system dependencies (including netcat for waiting on Postgres)
RUN apt-get update && apt-get install -y netcat

# Environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project code
COPY . .

# Copy and set entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port your Gunicorn server will use
EXPOSE 8001

ENTRYPOINT ["/entrypoint.sh"]
