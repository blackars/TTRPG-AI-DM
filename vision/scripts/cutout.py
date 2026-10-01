"""cutout.py: fondo negro -> PNG sin fondo con rembg."""
import argparse
from pathlib import Path

try:
    from rembg import remove
    from PIL import Image
except ImportError:
    raise SystemExit("pip install rembg onnxruntime pillow")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    a = ap.parse_args()
    src, dst = Path(a.inp), Path(a.out)
    dst.mkdir(parents=True, exist_ok=True)
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    files = [f for e in exts for f in src.glob(e)]
    if not files:
        print(f"Sin fotos en {src}. Pon 5-8 por mini, fondo negro.")
        return
    for f in files:
        img = Image.open(f).convert("RGB")
        out = remove(img)
        slug = f.stem.lower().replace(" ", "-")
        out.save(dst / f"{slug}.png")
        print(f"OK {slug}.png")


if __name__ == "__main__":
    main()
