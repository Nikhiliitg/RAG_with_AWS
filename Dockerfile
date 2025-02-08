# Use official Python image (Slim version for smaller size)
FROM python:3.11-slim-buster

# Set working directory
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies (Use --no-cache-dir to save space)
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining project files
COPY . .

# Use correct CMD syntax (JSON array format to avoid shell issues)
CMD ["python3", "app/main.py"]
