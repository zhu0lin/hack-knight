import os, torch, open_clip
from torch import nn
from PIL import Image

# ----------------------------
# paths (just edit these)
# ----------------------------
image_path = "download (1).jpg"       # your food image
head_path  = "clip_head_v1.pt"     # your model file
device = "cuda" if torch.cuda.is_available() else "cpu"

# sanity check
if not os.path.exists(image_path): raise FileNotFoundError(os.path.abspath(image_path))
if not os.path.exists(head_path):  raise FileNotFoundError(os.path.abspath(head_path))

# ----------------------------
# small helpers
# ----------------------------
def infer_out_features(sd: dict) -> int:
    """detects if model outputs 3 (macros) or 4 (macros+calories)"""
    for k, W in sd.items():
        if k.endswith("weight") and getattr(W, "ndim", 0) == 2:
            out_f, in_f = W.shape
            if in_f == 256:  # last linear
                return out_f
    outs = [W.shape[0] for k, W in sd.items() if k.endswith("weight") and getattr(W, "ndim", 0) == 2]
    return max(outs) if outs else 3

class Head(nn.Module):
    def __init__(self, out_features: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(512, 256), nn.ReLU(),
            nn.Linear(256, out_features)
        )
    def forward(self, x): return self.net(x)

# ----------------------------
# load weights + CLIP
# ----------------------------
bundle = torch.load(head_path, map_location="cpu", weights_only=False)
state = bundle["state_dict"] if isinstance(bundle, dict) and "state_dict" in bundle else bundle
# fix key style if needed
if any(k.startswith("0.") for k in state.keys()):
    state = {f"net.{k}": v for k, v in state.items()}

out_features = infer_out_features(state)
head = Head(out_features).to(device)
head.load_state_dict(state)
head.eval()

clip_model, preprocess, _ = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai")
clip_model.eval().requires_grad_(False).to(device)

# ----------------------------
# inference
# ----------------------------
img = Image.open(image_path).convert("RGB")
with torch.no_grad():
    x = preprocess(img).unsqueeze(0).to(device)
    feats = clip_model.encode_image(x).float()
    feats = feats / feats.norm(dim=-1, keepdim=True)
    pred = head(feats)[0].detach().cpu().tolist()

# ----------------------------
# print numeric output
# ----------------------------
if out_features == 3:
    result = {
        "protein_g": round(float(pred[0]), 2),
        "carbohydrate_g": round(float(pred[1]), 2),
        "fat_g": round(float(pred[2]), 2),
    }
elif out_features == 4:
    result = {
        "protein_g": round(float(pred[0]), 2),
        "carbohydrate_g": round(float(pred[1]), 2),
        "fat_g": round(float(pred[2]), 2),
        "calories_kcal": round(float(pred[3]), 1),
    }
else:
    result = {f"y{i}": round(float(v), 3) for i, v in enumerate(pred)}

print("✅ Prediction for:", os.path.abspath(image_path))
print(result)

'''
import os, torch, open_clip
from torch import nn
from PIL import Image

# -------- set your paths here --------
image_path = "IMG_5271.jpeg"         # change to your image
head_path  = "download (1).jpg"       # your .pt from RunPod in same folder
device = "cuda" if torch.cuda.is_available() else "cpu"
# -------------------------------------

# sanity checks
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image not found: {os.path.abspath(image_path)}")
if not os.path.exists(head_path):
    raise FileNotFoundError(f"Model not found: {os.path.abspath(head_path)}")

def infer_out_features(sd: dict) -> int:
    """Infer last Linear out_features from weights."""
    # prefer the last linear with in_features 256
    candidate = None
    for k, W in sd.items():
        if k.endswith("weight") and W.ndim == 2:
            out_f, in_f = W.shape
            if in_f in (256, 512, 384):
                if candidate is None or in_f == 256:
                    candidate = (k, out_f, in_f)
    if candidate is None:
        # fallback: largest out_features among linear weights
        outs = [W.shape[0] for k, W in sd.items() if k.endswith("weight") and W.ndim == 2]
        if not outs:
            raise ValueError("Could not infer output size from state_dict.")
        return max(outs)
    return candidate[1]

class Head(nn.Module):
    def __init__(self, out_features: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(512, 256), nn.ReLU(),
            nn.Linear(256, out_features)
        )
    def forward(self, x): return self.net(x)

# 1) Load saved weights (CPU is fine)
bundle = torch.load(head_path, map_location="cpu")
state = bundle["state_dict"] if isinstance(bundle, dict) and "state_dict" in bundle else bundle

# 2) If keys are flat like '0.weight', prefix them to 'net.0.weight'
if any(k.startswith("0.") for k in state.keys()):
    state = {f"net.{k}": v for k, v in state.items()}

# 3) Figure out how many outputs (3 or 4)
out_features = infer_out_features(state)

# 4) Build head and load weights
head = Head(out_features).to(device)
head.load_state_dict(state, strict=True)
head.eval()

# 5) Load frozen CLIP
clip_model, preprocess, _ = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai")
clip_model.eval().requires_grad_(False).to(device)

# 6) Run inference on your image
img = Image.open(image_path).convert("RGB")
with torch.no_grad():
    x = preprocess(img).unsqueeze(0).to(device)
    feats = clip_model.encode_image(x).float()
    feats = feats / feats.norm(dim=-1, keepdim=True)
    pred = head(feats)[0].detach().cpu().tolist()

# 7) Pretty output
if out_features == 3:
    result = {
        "protein_g": round(float(pred[0]), 2),
        "carbohydrate_g": round(float(pred[1]), 2),
        "fat_g": round(float(pred[2]), 2),
    }
elif out_features == 4:
    result = {
        "protein_g": round(float(pred[0]), 2),
        "carbohydrate_g": round(float(pred[1]), 2),
        "fat_g": round(float(pred[2]), 2),
        "calories_kcal": round(float(pred[3]), 1),
    }
else:
    result = {f"y{i}": round(float(v), 3) for i, v in enumerate(pred)}

print("✅ Prediction for:", os.path.abspath(image_path))
print(result)

'''