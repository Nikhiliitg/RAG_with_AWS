# Use stable Python image with prebuilt wheels support
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install build tools and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Run the Flask app
CMD ["python", "main.py"]
