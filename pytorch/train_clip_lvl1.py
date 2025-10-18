# train_clip_lvl1_fixed.py
from datasets import load_dataset, Image
import torch, open_clip
from torch import nn, optim
from torch.utils.data import DataLoader
import json

# 1) Load a small subset and cast the image column
ds = load_dataset("Codatta/MM-Food-100K", split="train[:1000]")
ds = ds.cast_column("image_url", Image())   # <-- this makes PIL images accessible at ds[i]["image_url"]


# 2) Frozen CLIP
model, preprocess, _ = open_clip.create_model_and_transforms("ViT-B-32", pretrained="openai")
model.eval().requires_grad_(False)

# 3) Tiny head: predict protein, carbs, fat (regression)
head = nn.Sequential(
    nn.Linear(512, 256), nn.ReLU(),
    nn.Linear(256, 3)
)
crit = nn.MSELoss()
opt = optim.Adam(head.parameters(), lr=1e-3)

def collate(batch):
    # Convert image URLs to tensors
    imgs = [b["image_url"].convert("RGB") for b in batch]
    x = torch.stack([preprocess(im) for im in imgs])  # [B,3,224,224]

    targets = []
    for b in batch:
        prof = b["nutritional_profile"]

        # if it's a string like '{"protein_g": 25, ...}', parse it
        if isinstance(prof, str):
            try:
                prof = json.loads(prof)
            except Exception:
                prof = {}

        protein = float(prof.get("protein_g", 0.0))
        carbs = float(prof.get("carbohydrate_g", 0.0))
        fat = float(prof.get("fat_g", 0.0))
        targets.append([protein, carbs, fat])

    y = torch.tensor(targets, dtype=torch.float)
    return x, y

loader = DataLoader(ds, batch_size=8, shuffle=True, collate_fn=collate)

# 5) Train a few epochs just to see loss go down
for epoch in range(3):
    total = 0.0
    for imgs, labels in loader:
        with torch.no_grad():
            feats = model.encode_image(imgs).float()
            feats = feats / feats.norm(dim=-1, keepdim=True)      # [B,512]

        preds = head(feats)
        loss = crit(preds, labels)

        opt.zero_grad()
        loss.backward()
        opt.step()
        total += loss.item()

    print(f"Epoch {epoch+1}: avg loss = {total/len(loader):.4f}")

print("✅ level 1 training complete")
