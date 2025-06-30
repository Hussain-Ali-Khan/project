from locust import HttpUser, task, between

class MyTestUser(HttpUser):
    wait_time = between(1, 2)  # Simulates user think time

    @task
    def predict_endpoint(self):
        self.client.post("/api/predict", json={
            "Units Sold": 120,
            "Inventory Level": 45,
            "Weather Condition": "Sunny",
            "Seasonality": "Summer",
            "Region": "North",
            "Discount": 10.5,
            "Units Ordered": 200,
            "Category": "Groceries"
        })
