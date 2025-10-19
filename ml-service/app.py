from fastapi import FastAPI, File, UploadFile, HTTPException
from predict import load_model, load_all_models, predict_best
import os

app = FastAPI(title="Food ML API")

# Load one or more models. If ML_CKPTS is set (comma-separated), use those.
# Otherwise, load all .pt files under artifacts/.
ckpts_env = os.environ.get("ML_CKPTS")
models = []
if ckpts_env:
    paths = [p.strip() for p in ckpts_env.split(",") if p.strip()]
    models = load_all_models(explicit_paths=paths)
else:
    models = load_all_models(artifacts_dir="artifacts")
if not models:
    # Fallback to the legacy single path if nothing was found
    m, cls = load_model("artifacts/foodmix_resnet50.pt")
    models = [{"model": m, "classes": cls, "name": "foodmix_resnet50.pt"}]

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        result = predict_best(models, image_bytes)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
