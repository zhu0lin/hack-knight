# reorganize_food11.py
from pathlib import Path
import shutil

ROOT = Path("datasets/food-11")
for split in ["training", "validation"]:
    base = ROOT / split
    # create class dirs 0..10
    for k in range(11):
        (base / str(k)).mkdir(parents=True, exist_ok=True)

    # move flat files like "0_123.jpg" into "<class>/0_123.jpg"
    for p in base.glob("*.jpg"):
        cls = p.stem.split("_", 1)[0]   # "0_123" -> "0"
        dest = base / cls / p.name
        if not dest.exists():
            shutil.move(str(p), str(dest))

print("✅ reorganized into class folders.")
