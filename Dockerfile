FROM python:3.12-slim

# Set working directory
WORKDIR /project

# Copy requirements first
COPY requirements.txt .

# Install build tools and Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get purge -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the app code
COPY . .

# Expose the FastAPI port
EXPOSE 5000

# Run using Gunicorn with Uvicorn workers (production-grade)
CMD ["gunicorn", "app:app", \
     "--workers=18", \
     "--worker-class=uvicorn.workers.UvicornWorker", \
     "--bind=0.0.0.0:5000", \
     "--timeout=60"]
