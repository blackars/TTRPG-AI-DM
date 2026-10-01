"""synth.py: pega PNGs sobre fondos tablero -> dataset YOLO-seg sintetico.
Requiere: pip install albumentations opencv-python pillow numpy
Exporta imagen + label YOLO-seg (poligono = bbox del alpha, simplificado).
Suficiente para MVP agnostico 2 clases.
"""
import argparse
import random
from pathlib import Path

try:
    import albumentations as A
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    raise SystemExit("pip install albumentations opencv-python pillow numpy")


def load_pngs(d):
    return list(Path(d).glob("*.png"))


def load_bgs(d):
    exts = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    return [f for e in exts for f in Path(d).glob(e)]


AUG = A.Compose([
    A.RandomBrightnessContrast(0.1, 0.1, p=0.5),
    A.HueSaturationValue(8, 12, 10, p=0.4),
    A.Blur(3, p=0.1),
], bbox_params=A.BboxParams(format="albumentations"))


def multi(dirs, exts):
    out = []
    for d in dirs.split(","):
        p = Path(d.strip())
        for e in exts:
            out += list(p.glob(e))
    return out


def recolor_png(fg, max_shift=60):
    """Cambia el matiz de la mini (simula otros colores de plástico/luz RGB)."""
    arr = np.array(fg)
    rgb = arr[:, :, :3]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.int32)
    hsv[:, :, 0] = (hsv[:, :, 0] + random.randint(-max_shift, max_shift)) % 180
    arr[:, :, :3] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return Image.fromarray(arr)


CACHE_PNG = {}  # path -> PIL RGBA con lado mayor <= 512 (los masters 4K son lentos)


def precargar(pngs, lado=512):
    for p in pngs:
        img = Image.open(p).convert("RGBA")
        img.thumbnail((lado, lado), Image.LANCZOS)
        CACHE_PNG[str(p)] = img
    print(f"PNGs en caché: {len(CACHE_PNG)} (lado<={lado}px)")


def paste(bg, fg_path, scale, angle, recolor_p=0.0, acostar_p=0.0, flip_p=0.5):
    fg = CACHE_PNG.get(str(fg_path))
    if fg is None:
        fg = Image.open(fg_path).convert("RGBA")
    else:
        fg = fg.copy()
    w = max(8, int(fg.width * scale))
    h = max(8, int(fg.height * scale))
    fg = fg.resize((w, h))
    if random.random() < flip_p:
        fg = fg.transpose(Image.FLIP_LEFT_RIGHT)
    if random.random() < recolor_p:
        fg = recolor_png(fg)
    ang = angle
    if random.random() < acostar_p:
        ang += 90  # acostada de lado
    fg = fg.rotate(ang, expand=True, resample=Image.BICUBIC)
    # Si rotada queda más grande que el fondo (master 1080px en fondo 640), encogerla.
    bh, bw = bg.shape[:2]
    if fg.width > bw or fg.height > bh:
        k = min(bw / fg.width, bh / fg.height) * 0.9
        fg = fg.resize((max(8, int(fg.width * k)), max(8, int(fg.height * k))))
    x = random.randint(0, max(0, bg.shape[1] - fg.width))
    y = random.randint(0, max(0, bg.shape[0] - fg.height))
    alpha = np.array(fg)[:, :, 3] / 255.0
    for c in range(3):
        roi = bg[y:y + fg.height, x:x + fg.width, c].astype(float)
        fgc = np.array(fg)[:, :, c].astype(float)
        bg[y:y + fg.height, x:x + fg.width, c] = (roi * (1 - alpha) + fgc * alpha).astype(np.uint8)
    # poligono simple: bbox del alpha
    ys, xs = np.where(alpha > 0.3)
    if len(xs) == 0:
        return None
    x0, x1, y0, y1 = xs.min() + x, xs.max() + x, ys.min() + y, ys.max() + y
    W, H = bg.shape[1], bg.shape[0]
    # rectangulo como poly 4 pts normalizado (suficiente para nano MVP)
    return [(x0 / W, y0 / H), (x1 / W, y0 / H), (x1 / W, y1 / H), (x0 / W, y1 / H)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pngs", required=True)
    ap.add_argument("--fondos", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out", required=True)
    ap.add_argument("--smin", type=float, default=0.08, help="escala mínima (0.08 = muy lejos/chica)")
    ap.add_argument("--smax", type=float, default=0.5, help="escala máxima (0.5 = muy cerca/grande)")
    ap.add_argument("--nmin", type=int, default=3, help="mínimo de minis por imagen (caos)")
    ap.add_argument("--nmax", type=int, default=10, help="máximo de minis por imagen (caos)")
    ap.add_argument("--recolor", type=float, default=0.4, help="prob. de cambiar color a cada mini")
    ap.add_argument("--acostar", type=float, default=0.25, help="prob. de acostar cada mini")
    a = ap.parse_args()
    pngs = multi(a.pngs, ("*.png",))
    bgs = multi(a.fondos, ("*.jpg", "*.jpeg", "*.png", "*.webp"))
    assert pngs, f"Sin PNGs en {a.pngs}. Corre cutout.py primero."
    assert bgs, f"Sin fondos en {a.fondos}. Saca fotos del tablero."
    print(f"PNGs: {len(pngs)} | fondos: {len(bgs)} | caos {a.nmin}-{a.nmax}/img")
    precargar(pngs)
    out = Path(a.out)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "labels").mkdir(parents=True, exist_ok=True)
    for i in range(a.n):
        bg = cv2.imread(str(random.choice(bgs)))
        bg = cv2.resize(bg, (640, 640))
        labels = []
        for _ in range(random.randint(a.nmin, a.nmax)):
            poly = paste(bg, random.choice(pngs), random.uniform(a.smin, a.smax),
                         random.uniform(-45, 45), a.recolor, a.acostar)
            if poly:
                pts = " ".join(f"{x:.4f} {y:.4f}" for x, y in poly)
                labels.append(f"0 {pts}")  # clase 0 pieza_juego
        bg = AUG(image=bg)["image"]
        cv2.imwrite(str(out / "images" / f"syn_{i:04d}.jpg"), bg)
        (out / "labels" / f"syn_{i:04d}.txt").write_text("\n".join(labels), encoding="utf-8")
        if (i + 1) % 250 == 0:
            print(f"  {i + 1}/{a.n}")
    print(f"OK {a.n} sinteticas en {out}/images + labels (clase 0).")


if __name__ == "__main__":
    main()
