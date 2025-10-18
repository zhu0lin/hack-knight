# datasets.py
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from torch.utils.data import Dataset, ConcatDataset, DataLoader, Subset
from torchvision import transforms
from torchvision.datasets import ImageFolder

# === We output 5 flags in this order: [fats, protein, dairy, fruits_veg, carbs]
Pyramid = List[float]

# -------- Fruit-360 mapping (rule-based) ----------
STARCHY_VEG = {"Potato", "Potato___Early_blight", "Potato___Late_blight",
               "Sweetcorn", "Corn", "Cassava", "Sweet_Potato", "Yam"}
def fruit360_to_pyr(class_name: str) -> Pyramid:
    # fruits/veg default
    pyr = [0.0, 0.0, 0.0, 1.0, 0.0]
    if class_name in STARCHY_VEG:
        pyr[-1] = 1.0  # carbs
    return pyr

# -------- Food-11 mapping (soft labels help noise) ----------
FOOD11_IDX2NAME = [
    "Bread","Dairy product","Dessert","Egg","Fried food",
    "Meat","Noodles-Pasta","Rice","Seafood","Soup","Vegetable-Fruit"
]
FOOD11_TO_PYR: Dict[str, Pyramid] = {
    "Bread":            [0.0, 0.0, 0.0, 0.0, 1.0],
    "Dairy product":    [0.6, 0.3, 1.0, 0.0, 0.2],
    "Dessert":          [0.9, 0.0, 0.2, 0.1, 0.9],
    "Egg":              [0.7, 1.0, 0.0, 0.0, 0.0],
    "Fried food":       [1.0, 0.6, 0.0, 0.1, 0.8],
    "Meat":             [0.7, 1.0, 0.0, 0.0, 0.0],
    "Noodles-Pasta":    [0.1, 0.0, 0.0, 0.0, 1.0],
    "Rice":             [0.0, 0.0, 0.0, 0.0, 1.0],
    "Seafood":          [0.2, 1.0, 0.0, 0.0, 0.0],
    "Soup":             [0.1, 0.3, 0.0, 0.7, 0.3],
    "Vegetable-Fruit":  [0.0, 0.0, 0.0, 1.0, 0.0],
}

# -------- transforms ----------
def build_transforms():
    tfm_train = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.1,0.1,0.1,0.05),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
    ])
    tfm_val = transforms.Compose([
        transforms.Resize(256), transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
    ])
    return tfm_train, tfm_val

# -------- wrappers ----------
class WrappedFolder(Dataset):
    def __init__(self, folder: ImageFolder, local2global: Dict[int,int], src: str):
        self.folder, self.l2g, self.src = folder, local2global, src
    def __len__(self): return len(self.folder)
    def __getitem__(self, i):
        x, y_local = self.folder[i]
        y_global = self.l2g[y_local]
        cls_name = self.folder.classes[y_local]
        if self.src == "fruit360":
            y_pyr = torch.tensor(fruit360_to_pyr(cls_name), dtype=torch.float32)
        elif self.src == "food11":
            # Food-11 class dirs are "0..10"; map via index
            name = FOOD11_IDX2NAME[int(cls_name)]
            y_pyr = torch.tensor(FOOD11_TO_PYR[name], dtype=torch.float32)
        else:
            raise ValueError("unknown src")
        return x, y_global, y_pyr

def register_classes(ds: ImageFolder, prefix: str, start: int) -> Tuple[Dict[int,int], List[str]]:
    mapping = {i: start+i for i in range(len(ds.classes))}
    names = [f"{prefix}:{c}" for c in ds.classes]
    return mapping, names

def _maybe_subset(ds: Dataset, k: Optional[int], seed=42):
    if k is None: return ds
    n = min(k, len(ds))
    idx = list(range(len(ds)))
    random.Random(seed).shuffle(idx)
    return Subset(ds, idx[:n])

# -------- public builders ----------
def build_datasets(
    fruit_root="datasets/fruits-360_100x100",   # your folder name (has Test/ Training/)
    food11_root="datasets/food-11",             # has training/ validation/
    max_train: Optional[int]=500,
    max_val: Optional[int]=200,
    seed: int = 42,
):
    tfm_train, tfm_val = build_transforms()

    def _resolve_base_dir(user_root: str, candidates: List[str]) -> Optional[Path]:
        ur = Path(user_root)
        if ur.exists():
            return ur
        for cand in [user_root, *candidates]:
            p = Path(cand)
            if p.exists():
                return p
        return None

    # Fruit-360
    fruit_base = _resolve_base_dir(
        fruit_root,
        [
            "datasets/fruits-360",
            "datasets/Fruits-360",
            "data/fruits-360",
            "fruits-360",
        ],
    )
    fruit_train = fruit_val = None
    fruit_err = None
    if fruit_base is not None:
        train_dir = fruit_base / "Training"
        test_dir = fruit_base / "Test"
        try:
            if not train_dir.exists() or not test_dir.exists():
                raise FileNotFoundError(f"Expected 'Training' and 'Test' under {fruit_base}")
            fruit_train = ImageFolder(str(train_dir), transform=tfm_train)
            fruit_val = ImageFolder(str(test_dir), transform=tfm_val)
        except Exception as e:
            fruit_err = str(e)
            fruit_train = fruit_val = None
    else:
        fruit_err = f"Base dir not found for Fruit-360 (tried variants of '{fruit_root}')"

    # Food-11 (class folders are "0","1",..."10")
    food_base = _resolve_base_dir(
        food11_root,
        [
            "datasets/food-11",
            "datasets/Food-11",
            "data/food-11",
            "Food-11",
        ],
    )
    food11_train = food11_val = None
    food_err = None
    if food_base is not None:
        tr_dir = food_base / "training"
        va_dir = food_base / "validation"
        try:
            if not tr_dir.exists() or not va_dir.exists():
                raise FileNotFoundError(f"Expected 'training' and 'validation' under {food_base}")
            if not any(child.is_dir() for child in tr_dir.iterdir()):
                raise FileNotFoundError(f"Couldn't find any class folder in {tr_dir}")
            if not any(child.is_dir() for child in va_dir.iterdir()):
                raise FileNotFoundError(f"Couldn't find any class folder in {va_dir}")
            food11_train = ImageFolder(str(tr_dir), transform=tfm_train)
            food11_val = ImageFolder(str(va_dir), transform=tfm_val)
        except Exception as e:
            food_err = str(e)
            food11_train = food11_val = None
    else:
        food_err = f"Base dir not found for Food-11 (tried variants of '{food11_root}')"

    if fruit_train is None and food11_train is None:
        hints = [
            "Place Fruit-360 at one of: datasets/fruits-360_100x100, datasets/fruits-360",
            "Place Food-11 at one of: datasets/food-11, datasets/Food-11",
            "For Food-11, ensure 'training' and 'validation' each contain class folders 0..10",
        ]
        problems = [msg for msg in [fruit_err, food_err] if msg]
        raise FileNotFoundError("No datasets found.\n" + "\n".join(problems + hints))

    # register global classes
    start = 0
    global_classes: List[str] = []
    m_fruit = m_food11 = None  # type: ignore
    if fruit_train is not None:
        m_fruit, names_fruit = register_classes(fruit_train, "fruit360", start)
        start += len(names_fruit)
        global_classes += names_fruit
    if food11_train is not None:
        m_food11, names_food11 = register_classes(food11_train, "food11", start)
        start += len(names_food11)
        global_classes += names_food11

    # wrap
    train_parts = []
    val_parts = []
    if fruit_train is not None and m_fruit is not None:
        train_parts.append(WrappedFolder(fruit_train, m_fruit, "fruit360"))
        if fruit_val is not None:
            val_parts.append(WrappedFolder(fruit_val, m_fruit, "fruit360"))
    if food11_train is not None and m_food11 is not None:
        train_parts.append(WrappedFolder(food11_train, m_food11, "food11"))
        if food11_val is not None:
            val_parts.append(WrappedFolder(food11_val, m_food11, "food11"))

    train_ds = ConcatDataset(train_parts)
    val_ds = ConcatDataset(val_parts)

    # tiny caps for hackathon speed
    train_ds = _maybe_subset(train_ds, max_train, seed)
    val_ds   = _maybe_subset(val_ds,   max_val,   seed)
    return train_ds, val_ds, global_classes

def build_loaders(
    fruit_root="datasets/fruits-360_100x100",
    food11_root="datasets/food-11",
    batch_size=32, max_train=500, max_val=200, num_workers=4, seed=42
):
    train_ds, val_ds, cls = build_datasets(fruit_root, food11_root, max_train, max_val, seed)
    train_ld = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  num_workers=num_workers, pin_memory=True)
    val_ld   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
    return train_ld, val_ld, cls

if __name__ == "__main__":
    print("Building loaders...")
    train_ld, val_ld, classes = build_loaders(
        fruit_root="datasets/fruits-360_100x100",
        food11_root="datasets/food-11",
        batch_size=8,
        max_train=20,
        max_val=10,
        num_workers=0
    )

    x, gid, pyr = next(iter(train_ld))
    print("Dataset loaded successfully!")
    print("Image batch:", x.shape)
    print("Global IDs:", gid[:5])
    print("Pyramid labels:", pyr[:5])
    print("Total classes:", len(classes))

