# ml_service/predict.py
import torch, torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import os
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class ResNet50TwoHead(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        # Use ImageNet weights as in the earlier working version
        m = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        self.backbone = nn.Sequential(*list(m.children())[:-1])
        self.class_head = nn.Linear(2048, num_classes)
        self.pyr_head   = nn.Linear(2048, 5)
    def forward(self, x):
        f = self.backbone(x).flatten(1)
        return self.class_head(f), self.pyr_head(f)

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])

NAMES_PYR = ["fats", "protein", "dairy", "fruits_veg", "carbs"]

def load_model(ckpt_path: str):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    classes = ckpt["classes"]
    model = ResNet50TwoHead(num_classes=len(classes)).to(DEVICE)
    model.load_state_dict(ckpt["state_dict"], strict=True)
    model.eval()
    return model, classes

def load_all_models(artifacts_dir: str = "artifacts", explicit_paths: Optional[List[str]] = None):
    paths: List[Path] = []
    if explicit_paths:
        paths = [Path(p) for p in explicit_paths]
    else:
        ad = Path(artifacts_dir)
        if ad.exists():
            paths = sorted(ad.glob("*.pt"))
    loaded = []
    for p in paths:
        try:
            m, cls = load_model(str(p))
            loaded.append({"model": m, "classes": cls, "name": p.name})
        except Exception as e:
            # skip incompatible checkpoints
            continue
    return loaded

def _predict_single(model, classes, image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    x = transform(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        cls_logits, pyr_logits = model(x)
        cls_probs = torch.softmax(cls_logits, dim=1).squeeze(0).cpu().numpy()
        pyr_probs = torch.sigmoid(pyr_logits).squeeze(0).cpu().numpy()

    topk = np.argsort(-cls_probs)[:3]
    answers = ["Yes" if p >= 0.5 else "No" for p in pyr_probs]
    # confidence score: blend of top1 prob and margin
    top1 = float(cls_probs[topk[0]])
    top2 = float(cls_probs[topk[1]]) if len(cls_probs) > 1 else 0.0
    margin = max(0.0, top1 - top2)
    score = 0.7 * top1 + 0.3 * margin

    return {
        "top_classes": [
            {"label": classes[i], "prob": float(cls_probs[i])} for i in topk
        ],
        "pyramid": [
            {"name": n, "prob": float(p), "yes_no": a}
            for n, a, p in zip(NAMES_PYR, answers, pyr_probs)
        ],
        "score": float(score),
    }

def predict_best(models: List[dict], image_bytes: bytes):
    if not models:
        raise RuntimeError("No models loaded for prediction")
    best = None
    for item in models:
        res = _predict_single(item["model"], item["classes"], image_bytes)
        res["model_name"] = item.get("name", "unknown")
        if best is None or res.get("score", 0.0) > best.get("score", 0.0):
            best = res
    return best

# Backward-compatible alias
def predict(model, classes, image_bytes: bytes):
    return _predict_single(model, classes, image_bytes)
