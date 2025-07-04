from fastapi import FastAPI, Request, Form, status, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

# === App Setup === #
app = FastAPI()
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# === Database Setup === #
DATABASE_URL = "postgresql://postgres:Hussain30@host.docker.internal:5432/mall_demand"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    units_sold = Column(Float)
    inventory_level = Column(Float)
    weather_condition = Column(Integer)
    seasonality = Column(Integer)
    region = Column(Integer)
    discount = Column(Float)
    units_ordered = Column(Float)
    category = Column(Integer)
    predicted_demand = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Config === #
MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'
FEATURES = [
    'Units Sold', 'Inventory Level', 'Weather Condition', 'Seasonality',
    'Region', 'Discount', 'Units Ordered'
]
CATEGORY_MAPPING = {'Groceries': 3, 'Toys': 4, 'Electronics': 1}
REGION_MAPPING = {'North': 1, 'South': 2, 'West': 3, 'East': 0}
WEATHER_MAPPING = {'Rainy': 1, 'Sunny': 3, 'Cloudy': 0}
SEASONALITY_MAPPING = {'Autumn': 0, 'Summer': 2}

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
except Exception as e:
    raise RuntimeError(f"Error loading model or scaler: {e}")

# === Routes === #
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
    Category: str = Form(...),
    db: Session = Depends(get_db)
):
    data = {}
    error_message = None
    prediction_text = None

    try:
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

        data['Category'] = CATEGORY_MAPPING[Category]
        data['Region'] = REGION_MAPPING[Region]
        data['Weather Condition'] = WEATHER_MAPPING[Weather_Condition]
        data['Seasonality'] = SEASONALITY_MAPPING[Seasonality]

        features = np.array([
            float(Units_Sold), float(Inventory_Level), float(data['Weather Condition']),
            float(data['Seasonality']), float(data['Region']), float(Discount), float(Units_Ordered)
        ]).reshape(1, -1)

        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)
        prediction_value = float(prediction[0])
        prediction_text = f'Predicted Demand Forecast: {prediction_value:.2f}'

        db_record = Prediction(
            units_sold=float(Units_Sold),
            inventory_level=float(Inventory_Level),
            weather_condition=data['Weather Condition'],
            seasonality=data['Seasonality'],
            region=data['Region'],
            discount=float(Discount),
            units_ordered=float(Units_Ordered),
            category=data['Category'],
            predicted_demand=prediction_value
        )
        db.add(db_record)
        db.commit()

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
async def api_predict(payload: dict, db: Session = Depends(get_db)):
    try:
        data = payload.copy()
        data['Category'] = CATEGORY_MAPPING[data['Category']]
        data['Region'] = REGION_MAPPING[data['Region']]
        data['Weather Condition'] = WEATHER_MAPPING[data['Weather Condition']]
        data['Seasonality'] = SEASONALITY_MAPPING[data['Seasonality']]

        features = np.array([
            float(data['Units Sold']), float(data['Inventory Level']), float(data['Weather Condition']),
            float(data['Seasonality']), float(data['Region']), float(data['Discount']), float(data['Units Ordered'])
        ]).reshape(1, -1)

        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)
        prediction_value = float(prediction[0])

        db_record = Prediction(
            units_sold=data['Units Sold'],
            inventory_level=data['Inventory Level'],
            weather_condition=data['Weather Condition'],
            seasonality=data['Seasonality'],
            region=data['Region'],
            discount=data['Discount'],
            units_ordered=data['Units Ordered'],
            category=data['Category'],
            predicted_demand=prediction_value
        )
        db.add(db_record)
        db.commit()

        return {"prediction": prediction_value}

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(e)})
