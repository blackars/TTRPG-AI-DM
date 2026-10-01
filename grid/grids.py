"""Grid dual square + hex: math + SVG para proyector + calibracion.
Uso:
  python grids.py --tipo square --cols 12 --rows 9 --cell-px 60 --out patron_square.svg
  python grids.py --tipo hex --orientacion pointy --cols 11 --rows 9 --cell-px 34 --out patron_hex.svg
Sin dependencias: solo stdlib. OpenCV solo para runtime, no para generar.
"""
import argparse
import math


def square_to_pixel(col, row, cell_px, origin=(0, 0)):
    return (origin[0] + col * cell_px, origin[1] + row * cell_px)


def square_to_A1(col, row):
    return f"{chr(65 + col)}{row + 1}"


def square_distance(a, b, diagonal="chebyshev"):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dx, dy) if diagonal == "chebyshev" else dx + dy


def hex_to_pixel(q, r, size, origin=(0, 0), orient="pointy"):
    if orient == "pointy":
        return (size * math.sqrt(3) * (q + r / 2) + origin[0], size * 1.5 * r + origin[1])
    return (size * 1.5 * q + origin[0], size * math.sqrt(3) * (r + q / 2) + origin[1])


def hex_distance(a, b):
    aq, ar = a
    bq, br = b
    return (abs(aq - bq) + abs(aq + ar - bq - br) + abs(ar - br)) // 2


def hex_neighbors(q, r):
    return [(q + 1, r), (q + 1, r - 1), (q, r - 1), (q - 1, r), (q - 1, r + 1), (q, r + 1)]


def hex_round(qf, rf):
    sf = -qf - rf
    qi, ri, si = round(qf), round(rf), round(sf)
    dq, dr, ds = abs(qi - qf), abs(ri - rf), abs(si - sf)
    if dq > dr and dq > ds:
        qi = -ri - si
    elif dr > ds:
        ri = -qi - si
    return (qi, ri)


def hex_corners(cx, cy, size, orient="pointy"):
    start = 30 if orient == "pointy" else 0
    pts = []
    for i in range(6):
        ang = math.radians(start + i * 60)
        pts.append((cx + size * math.cos(ang), cy + size * math.sin(ang)))
    return pts


def svg_square(cols, rows, cell_px):
    w, h = cols * cell_px, rows * cell_px
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    parts.append('<rect width="100%" height="100%" fill="black"/>')
    parts.append('<g id="grid" stroke="#ffffff44" stroke-width="1">')
    for c in range(cols + 1):
        parts.append(f'<line x1="{c * cell_px}" y1="0" x2="{c * cell_px}" y2="{h}"/>')
    for r in range(rows + 1):
        parts.append(f'<line x1="0" y1="{r * cell_px}" x2="{w}" y2="{r * cell_px}"/>')
    parts.append('</g><g id="labels" fill="#ffffff88" font-size="14" font-family="monospace">')
    for c in range(cols):
        for r in range(rows):
            x, y = c * cell_px + 4, r * cell_px + 16
            parts.append(f'<text x="{x}" y="{y}">{square_to_A1(c, r)}</text>')
    parts.append('</g></svg>')
    return "\n".join(parts)


def svg_hex(cols, rows, size, orient="pointy"):
    # layout rectangular odd-r para proyeccion simple
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900">']
    parts.append('<rect width="100%" height="100%" fill="black"/>')
    parts.append('<g id="grid" fill="none" stroke="#ffffff55" stroke-width="1.5">')
    origin = (80, 80)
    for r in range(rows):
        for q in range(cols):
            # offset odd-r -> axial aprox para dibujo rectangular
            aq = q - (r - (r & 1)) // 2
            ar = r
            cx, cy = hex_to_pixel(aq, ar, size, origin, orient)
            pts = hex_corners(cx, cy, size, orient)
            p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<polygon points="{p}" data-q="{aq}" data-r="{ar}"/>')
    parts.append('</g></svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", choices=["square", "hex"], required=True)
    ap.add_argument("--cols", type=int, default=12)
    ap.add_argument("--rows", type=int, default=9)
    ap.add_argument("--cell-px", type=int, default=60)
    ap.add_argument("--cell-mm", type=int, default=50)
    ap.add_argument("--orientacion", choices=["pointy", "flat"], default="pointy")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.tipo == "square":
        svg = svg_square(a.cols, a.rows, a.cell_px)
    else:
        svg = svg_hex(a.cols, a.rows, a.cell_px // 2, a.orientacion)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK {a.out} tipo={a.tipo} orient={a.orientacion}")
