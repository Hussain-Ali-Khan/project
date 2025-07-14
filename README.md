# 🛒 Mall Demand Forecasting API

A machine learning-powered API that predicts mall demand using Ridge Regression, optimized with GridSearchCV. The model is containerized using Docker and deployed with Gunicorn + Uvicorn for production readiness. Load testing was performed using Locust to benchmark performance under concurrent usage.

---

## 🚀 Features

- 📈 **Demand Forecasting** using Ridge Regression (R² = 0.91, RMSE = 0.35)
- 🔍 **Hyperparameter Optimization** using GridSearchCV
- 🌐 **API Interface** using FastAPI, served with Gunicorn + Uvicorn workers
- 🐳 **Dockerized** for portability and consistent deployment
- ⚡ **Load Testing** with Locust (1000 users, ~319 RPS, latency measured at 99th percentile)

---

## 🧠 Tech Stack

- **Modeling**: Ridge Regression, Scikit-learn
- **API**: FastAPI
- **Deployment**: Docker, Gunicorn, Uvicorn
- **Testing**: Locust
- **Environment**: Python 3.12, Pip, Jupyter/Colab

---

## 📦 Installation

Clone the repo and build the Docker container:

```bash
git clone https://github.com/yourusername/project.git
cd project
docker build -t mall-demand-api .
docker run -p 5000:5000 mall-demand-api
![alt text](<Screenshot 2025-06-16 120527.png>)
![alt text](<Screenshot 2025-07-04 192131.png>)
![alt text](<Screenshot 2025-07-04 192145.png>)