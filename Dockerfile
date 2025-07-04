FROM python:3.12-slim

# Set working directory
WORKDIR /project

# Copy requirements file
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 5000

# Run using Gunicorn with Uvicorn workers
CMD ["gunicorn", "app:app", \
     "--workers=16", \
     "--worker-class=uvicorn.workers.UvicornWorker", \
     "--bind=0.0.0.0:5000", \
     "--timeout=60"]
