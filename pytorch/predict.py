# predict.py
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
from pathlib import Path

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# === same model as train.py ===
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

# === normalization ===
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])

# === hard-coded paths ===
#image_path = r"C:\Users\nihad\Desktop\hack-knight\datasets\fruits-360_100x100\Test\Apple Braeburn 1\0_100.jpg"
#ckpt_path  = r"C:\Users\nihad\Desktop\hack-knight\pytorch\artifacts\foodmix_resnet50.pt"
image_path = "download (2).jpg"           # or "./apple.jpg" if same folder
ckpt_path  = "artifacts/foodmix_resnet50.pt"
# === load checkpoint ===
ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)

classes = ckpt["classes"]

model = ResNet50TwoHead(num_classes=len(classes)).to(DEVICE)
model.load_state_dict(ckpt["state_dict"], strict=True)
model.eval()

# === load image ===
img = Image.open(image_path).convert("RGB")
x = transform(img).unsqueeze(0).to(DEVICE)

# === predict ===
with torch.no_grad():
    cls_logits, pyr_logits = model(x)
    cls_probs = torch.softmax(cls_logits, dim=1).squeeze(0).cpu().numpy()
    pyr_probs = torch.sigmoid(pyr_logits).squeeze(0).cpu().numpy()

# === interpret ===
NAMES_PYR = ["fats", "protein", "dairy", "fruits_veg", "carbs"]
topk = np.argsort(-cls_probs)[:3]
answers = ["Yes" if p >= 0.5 else "No" for p in pyr_probs]

print(f"\n🖼️ Image: {Path(image_path).name}")
print("\n🍽️ Top predicted food classes:")
for i in topk:
    print(f"  - {classes[i]:25s} prob={cls_probs[i]:.3f}")

print("\n🥗 Predicted Food Pyramid (Yes/No):")
for name, ans, p in zip(NAMES_PYR, answers, pyr_probs):
    print(f"  {name:10s}: {ans:3s}  (prob={p:.3f})")
