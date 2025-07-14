# 🛒 Mall Demand Forecasting API

A machine learning-powered API that predicts mall demand using Ridge Regression, optimized with GridSearchCV. The model is containerized using Docker and deployed with Gunicorn + Uvicorn for production readiness. Load testing was performed using Locust to benchmark performance under concurrent usage.inputs are loggged on postgresql for logging and checking 

---

## 🚀 Features

- 📈 **Demand Forecasting** using Ridge Regression (R² = 0.91, RMSE = 0.35)
- 🔍 **Hyperparameter Optimization** using GridSearchCV
- 🌐 **API Interface** using FastAPI, served with Gunicorn + Uvicorn workers
- 🐳 **Dockerized** for portability and consistent deployment
- ⚡ **Load Testing** with Locust (1000 users, ~319 RPS, latency measured at 99th percentile)
- 🗃️ **Logging** logged the predictions and input features for data persisitency and retraining

---

## 🧠 Tech Stack

- **Modeling**: Ridge Regression, Scikit-learn
- **API**: FastAPI
- **Deployment**: Docker, Gunicorn, Uvicorn , postgresSQL
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
