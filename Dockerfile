# 1. Use a lightweight Python image
FROM python:3.11-slim

# 2. Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Copy application code and env file
COPY . .

# 7. Expose port
EXPOSE 8000

# 8. Run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
