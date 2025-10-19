from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import base64
import os

# Reuse prediction utilities from predict.py
from predict import load_all_models, predict_best


app = FastAPI(title="ML Service", version="1.0.0")


class AnalyzeRequest(BaseModel):
    image: str  # base64 string


class AnalyzeResponse(BaseModel):
    food_name: str
    category: str  # one of: fruit, vegetable, protein, dairy, grain, other
    healthiness_score: int  # 0-100
    calories: int
    confidence: float


MODELS: List[Dict] = []


def _load_models_on_startup() -> List[Dict]:
    dirs = os.environ.get("MODEL_DIRS", "artifacts,pytorch").split(",")
    models: List[Dict] = []
    seen_names = set()
    for d in [p.strip() for p in dirs if p.strip()]:
        try:
            loaded = load_all_models(artifacts_dir=d)
            for m in loaded:
                name = m.get("name")
                if name in seen_names:
                    continue
                seen_names.add(name)
                models.append(m)
        except Exception:
            # Ignore invalid dirs
            continue
    return models


def _map_to_backend_schema(pred: Dict) -> Dict:
    # pred: { top_classes: [{label, prob}], pyramid: [{name, prob, yes_no}], score }
    top_classes = pred.get("top_classes", [])
    food_name = top_classes[0]["label"] if top_classes else "Unknown Food"
    confidence = float(top_classes[0]["prob"]) if top_classes else 0.0

    # Derive category from pyramid flags if available
    pyramid = {p.get("name"): p for p in pred.get("pyramid", [])}
    category = "other"
    if pyramid.get("protein", {}).get("yes_no") == "Yes":
        category = "protein"
    elif pyramid.get("dairy", {}).get("yes_no") == "Yes":
        category = "dairy"
    elif pyramid.get("carbs", {}).get("yes_no") == "Yes":
        category = "grain"
    elif pyramid.get("fruits_veg", {}).get("yes_no") == "Yes":
        # cannot distinguish fruit vs vegetable without dataset mapping
        category = "fruit"

    # Healthiness: scale the internal score [0..1] to 0-100
    internal_score = float(pred.get("score", confidence))
    healthiness = max(0, min(100, int(round(internal_score * 100))))

    # Simple calories stub; replace with regressor if available
    calories = 100

    return {
        "food_name": food_name,
        "category": category,
        "healthiness_score": healthiness,
        "calories": calories,
        "confidence": float(confidence),
    }


@app.on_event("startup")
def startup_event():
    global MODELS
    MODELS = _load_models_on_startup()
    if not MODELS:
        print("[ml-service] Warning: no models loaded. Service will return mock-like defaults.")


@app.get("/")
def root():
    return {
        "message": "ML service ready",
        "models_loaded": len(MODELS),
        "model_names": [m.get("name") for m in MODELS],
    }


@app.get("/health")
def health():
    return {"status": "ok", "models": len(MODELS)}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    try:
        image_bytes = base64.b64decode(req.image)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image")

    try:
        if MODELS:
            pred = predict_best(MODELS, image_bytes)
            return _map_to_backend_schema(pred)
        else:
            # Fallback response when no models are available
            return {
                "food_name": "Apple",
                "category": "fruit",
                "healthiness_score": 85,
                "calories": 95,
                "confidence": 0.9,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


# Optional convenience endpoint for multipart uploads (manual testing)
@app.post("/predict")
async def predict_file(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        if MODELS:
            pred = predict_best(MODELS, image_bytes)
            return {"prediction": pred}
        else:
            return {"prediction": {
                "top_classes": [{"label": "Apple", "prob": 0.9}],
                "pyramid": [
                    {"name": "fats", "yes_no": "No", "prob": 0.1},
                    {"name": "protein", "yes_no": "No", "prob": 0.1},
                    {"name": "dairy", "yes_no": "No", "prob": 0.1},
                    {"name": "fruits_veg", "yes_no": "Yes", "prob": 0.9},
                    {"name": "carbs", "yes_no": "No", "prob": 0.2},
                ],
                "score": 0.9,
            }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
