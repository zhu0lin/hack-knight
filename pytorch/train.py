# train.py
import numpy as np
import torch, torch.nn as nn, torch.optim as optim
from torchvision import models
from sklearn.metrics import f1_score
from pathlib import Path
from datasets import build_loaders

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH = 32; EPOCHS = 5; LR = 3e-4; LAMBDA_BCE = 0.7

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

def tune_thresholds(y_true, y_prob, y_true_floor=0.5):
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    # binarize soft labels for F1 calculation only
    y_true_bin = (y_true >= y_true_floor).astype(int)

    best = [0.5]*5
    for k in range(5):
        ts = np.linspace(0.1, 0.9, 17)
        scores = [
            (t, f1_score(y_true_bin[:, k],
                         (y_prob[:, k] >= t).astype(int),
                         zero_division=0))
            for t in ts
        ]
        best[k] = max(scores, key=lambda x: x[1])[0]
    return best


def main():
    train_ld, val_ld, classes = build_loaders(
        fruit_root= "", #"datasets/fruits-360_100x100",   # expects Training/ and Test/
        food11_root="datasets/food-11",
        batch_size=BATCH, max_train=1000, max_val=200, num_workers = 0
    )
    model = ResNet50TwoHead(num_classes=len(classes)).to(DEVICE)
    ce, bce = nn.CrossEntropyLoss(), nn.BCEWithLogitsLoss()
    opt = optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)

    for ep in range(1, EPOCHS+1):
        model.train(); total=0; steps=0
        for xb, y_cls, y_pyr in train_ld:
            xb, y_cls, y_pyr = xb.to(DEVICE), y_cls.to(DEVICE), y_pyr.to(DEVICE)
            lc, lp = model(xb)
            loss = ce(lc, y_cls) + LAMBDA_BCE * bce(lp, y_pyr)
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item(); steps += 1
        print(f"epoch {ep}: train loss {total/max(1,steps):.4f}")

    # quick val pass for thresholds
    model.eval(); Yt=[]; Yp=[]; Ycls=[]; Ycls_hat=[]
    with torch.no_grad():
        for xb, y_cls, y_pyr in val_ld:
            xb = xb.to(DEVICE)
            lc, lp = model(xb)
            Ycls_hat += lc.argmax(1).cpu().tolist()
            Ycls     += y_cls.tolist()
            Yp.append(torch.sigmoid(lp).cpu().numpy())
            Yt.append(y_pyr.numpy())
    Yp = np.concatenate(Yp,0); Yt = np.concatenate(Yt,0)
    acc = (np.array(Ycls_hat)==np.array(Ycls)).mean()
    th = tune_thresholds(Yt, Yp)
    print(f"val class acc: {acc:.3f} | thresholds: {th}")

    out_dir = Path("artifacts"); out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir/"resnet50_food11.pt"
    torch.save({"state_dict": model.state_dict(),
                "classes": classes,
                "thresholds": th}, str(out_path))
    print(f"Saved -> {out_path}")

if __name__ == "__main__":
    main()

