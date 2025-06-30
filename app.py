from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

app = FastAPI()

# Mount static directory
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Configuration
MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'

# Feature list
FEATURES = [
    'Units Sold',
    'Inventory Level',
    'Weather Condition',
    'Seasonality',
    'Region',
    'Discount',
    'Units Ordered'
]

# Mapping dictionaries
CATEGORY_MAPPING = {'Groceries': 3, 'Toys': 4, 'Electronics': 1}
REGION_MAPPING = {'North': 1, 'South': 2, 'West': 3, 'East': 0}
WEATHER_MAPPING = {'Rainy': 1, 'Sunny': 3, 'Cloudy': 0}
SEASONALITY_MAPPING = {'Autumn': 0, 'Summer': 2}

# Load model and scaler
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    if os.path.exists(SCALER_PATH):
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
    else:
        scaler = StandardScaler()
except Exception as e:
    raise RuntimeError(f"Error loading model or scaler: {e}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "features": FEATURES,
        "categories": list(CATEGORY_MAPPING.keys()),
        "regions": list(REGION_MAPPING.keys()),
        "weathers": list(WEATHER_MAPPING.keys()),
        "seasons": list(SEASONALITY_MAPPING.keys()),
        "form_data": None,
        "prediction_text": None,
        "error": None
    })

@app.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    Units_Sold: str = Form(...),
    Inventory_Level: str = Form(...),
    Weather_Condition: str = Form(...),
    Seasonality: str = Form(...),
    Region: str = Form(...),
    Discount: str = Form(...),
    Units_Ordered: str = Form(...),
    Category: str = Form(...)
):
    data = {}
    error_message = None
    prediction_text = None

    try:
        # Assemble data
        data = {
            "Units Sold": Units_Sold,
            "Inventory Level": Inventory_Level,
            "Weather Condition": Weather_Condition,
            "Seasonality": Seasonality,
            "Region": Region,
            "Discount": Discount,
            "Units Ordered": Units_Ordered,
            "Category": Category
        }

        # Validate and map categorical features
        data['Category'] = CATEGORY_MAPPING[Category]
        data['Region'] = REGION_MAPPING[Region]
        data['Weather Condition'] = WEATHER_MAPPING[Weather_Condition]
        data['Seasonality'] = SEASONALITY_MAPPING[Seasonality]

        # Convert to float
        features = np.array([
            float(Units_Sold),
            float(Inventory_Level),
            float(data['Weather Condition']),
            float(data['Seasonality']),
            float(data['Region']),
            float(Discount),
            float(Units_Ordered)
        ]).reshape(1, -1)

        # Scale & predict
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)
        prediction_text = f'Predicted Demand Forecast: {prediction[0]:.2f}'

    except KeyError as e:
        error_message = f"Invalid category input: {str(e)}"
    except ValueError as e:
        error_message = f"Invalid numerical input: {str(e)}"
    except Exception as e:
        error_message = f"Prediction failed: {str(e)}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "features": FEATURES,
        "categories": list(CATEGORY_MAPPING.keys()),
        "regions": list(REGION_MAPPING.keys()),
        "weathers": list(WEATHER_MAPPING.keys()),
        "seasons": list(SEASONALITY_MAPPING.keys()),
        "form_data": data,
        "prediction_text": prediction_text,
        "error": error_message
    })

@app.post("/api/predict")
async def api_predict(payload: dict):
    try:
        data = payload.copy()

        data['Category'] = CATEGORY_MAPPING[data['Category']]
        data['Region'] = REGION_MAPPING[data['Region']]
        data['Weather Condition'] = WEATHER_MAPPING[data['Weather Condition']]
        data['Seasonality'] = SEASONALITY_MAPPING[data['Seasonality']]

        features = np.array([
            float(data['Units Sold']),
            float(data['Inventory Level']),
            float(data['Weather Condition']),
            float(data['Seasonality']),
            float(data['Region']),
            float(data['Discount']),
            float(data['Units Ordered'])
        ]).reshape(1, -1)

        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)
        return {"prediction": float(prediction[0])}

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(e)})
