from fastapi import FastAPI, File, UploadFile, HTTPException
from predict import load_model, predict

app = FastAPI(title="Food ML API")

model, classes = load_model("artifacts/foodmix_resnet50.pt")

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        result = predict(model, classes, image_bytes)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
