import os
import random
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent.parent / "data"
CLASSES = {
    "healthy": (60, 180, 75),
    "mild": (255, 195, 55),
    "moderate": (240, 130, 40),
    "severe": (200, 60, 50),
}
COUNTS = {"train": 32, "val": 12}
random.seed(42)

def ensure_dirs():
    for split in ["train", "val"]:
        for cls in CLASSES:
            (BASE / split / cls).mkdir(parents=True, exist_ok=True)

def make_image(color):
    img = Image.new("RGB", (224, 224), color)
    draw = ImageDraw.Draw(img)
    for _ in range(12):
        x1, y1 = random.randint(0, 112), random.randint(0, 112)
        x2, y2 = random.randint(112, 223), random.randint(112, 223)
        col = tuple(min(255, c + random.randint(-20, 20)) for c in color)
        draw.rectangle([x1, y1, x2, y2], outline=col, width=3)
    return img

def main():
    ensure_dirs()
    for split in ["train", "val"]:
        for cls, color in CLASSES.items():
            target = BASE / split / cls
            n = COUNTS[split]
            for i in range(n):
                img = make_image(color)
                img.save(target / f"{cls}_{i:03d}.png")
    print(f"Synthetic data written under {BASE}")

if __name__ == "__main__":
    main()
