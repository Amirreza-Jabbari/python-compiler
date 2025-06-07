# compiler_service/Dockerfile
FROM python:3.9-slim

# Install system dependencies (netcat for waiting on dependencies)
RUN apt-get update && apt-get install -y netcat

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project code
COPY . .

# Copy and set entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port for Daphne (Channels) server
EXPOSE 8002

ENTRYPOINT ["/entrypoint.sh"]
