# ml_service/predict.py
import torch, torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class ResNet50TwoHead(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
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

def predict(model, classes, image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    x = transform(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        cls_logits, pyr_logits = model(x)
        cls_probs = torch.softmax(cls_logits, dim=1).squeeze(0).cpu().numpy()
        pyr_probs = torch.sigmoid(pyr_logits).squeeze(0).cpu().numpy()

    topk = np.argsort(-cls_probs)[:3]
    answers = ["Yes" if p >= 0.5 else "No" for p in pyr_probs]

    return {
        "top_classes": [
            {"label": classes[i], "prob": float(cls_probs[i])} for i in topk
        ],
        "pyramid": [
            {"name": n, "prob": float(p), "yes_no": a}
            for n, a, p in zip(NAMES_PYR, answers, pyr_probs)
        ],
    }
