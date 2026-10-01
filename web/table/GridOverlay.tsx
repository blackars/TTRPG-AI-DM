// GridOverlay.tsx — renderer dual square/hex para proyector (monitor 2).
// Props: grid {tipo, cols, rows, cell_px, orientacion}, tokens, spawns, overlays.
// Sin dependencias, solo SVG + CSS. 60fps con <200 nodos.
"use client";
import React from "react";

type Cell = { id: string; points: string; cx: number; cy: number; label: string };
type Overlay =
  | { tipo: "circulo"; celda: string; color: string }
  | { tipo: "flecha"; de: string; a: string; color: string }
  | { tipo: "spawn"; celda: string; clase: string; color: string }
  | { tipo: "niebla"; celda: string };

const CLASE_COLOR: Record<string, string> = {
  jugador: "#44ff88",
  enemigo: "#ff4444",
  npc: "#44aaff",
  criatura: "#cc66ff",
};

function buildSquare(cols: number, rows: number, cell: number): Cell[] {
  const out: Cell[] = [];
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++) {
      const x = c * cell, y = r * cell;
      const id = `${String.fromCharCode(65 + c)}${r + 1}`;
      out.push({
        id,
        label: id,
        cx: x + cell / 2,
        cy: y + cell / 2,
        points: `${x},${y} ${x + cell},${y} ${x + cell},${y + cell} ${x},${y + cell}`,
      });
    }
  return out;
}

function hexCorners(cx: number, cy: number, s: number, pointy: boolean) {
  const start = pointy ? 30 : 0;
  const pts: string[] = [];
  for (let i = 0; i < 6; i++) {
    const a = ((start + i * 60) * Math.PI) / 180;
    pts.push(`${(cx + s * Math.cos(a)).toFixed(1)},${(cy + s * Math.sin(a)).toFixed(1)}`);
  }
  return pts.join(" ");
}

function buildHex(cols: number, rows: number, size: number, pointy = true): Cell[] {
  const out: Cell[] = [];
  const ox = 80, oy = 80;
  for (let r = 0; r < rows; r++)
    for (let q = 0; q < cols; q++) {
      const aq = q - ((r - (r & 1)) >> 1);
      const cx = pointy
        ? size * Math.sqrt(3) * (aq + r / 2) + ox
        : size * 1.5 * aq + ox;
      const cy = pointy
        ? size * 1.5 * r + oy
        : size * Math.sqrt(3) * (r + aq / 2) + oy;
      const id = `${String(aq).padStart(2, "0")}.${String(r).padStart(2, "0")}`;
      out.push({ id, label: id, cx, cy, points: hexCorners(cx, cy, size, pointy) });
    }
  return out;
}

export default function GridOverlay({ grid, spawns = [], overlays = [], showLabels = true }: any) {
  const cells: Cell[] =
    grid.tipo === "hex"
      ? buildHex(grid.cols, grid.rows, (grid.cell_px ?? 68) / 2, (grid.orientacion ?? "pointy") === "pointy")
      : buildSquare(grid.cols, grid.rows, grid.cell_px ?? 60);
  const byId = new Map(cells.map((c) => [c.id, c]));
  return (
    <svg viewBox="0 0 1200 900" width="100%" height="100%" style={{ background: "black" }}>
      <style>{`.pulse{animation:pu 1.2s infinite}@keyframes pu{50%{opacity:.3}}.dash{stroke-dasharray:8 6;animation:da 1s linear infinite}@keyframes da{to{stroke-dashoffset:-14}}`}</style>
      <g id="grid" fill="none" stroke="#ffffff44" strokeWidth={1.2}>
        {cells.map((c) => (
          <polygon key={c.id} points={c.points} />
        ))}
      </g>
      {showLabels && (
        <g fill="#ffffff66" fontSize={11} fontFamily="monospace">
          {cells.map((c) => (
            <text key={c.id} x={c.cx - 14} y={c.cy + 4}>{c.label}</text>
          ))}
        </g>
      )}
      <g id="spawns">
        {spawns.map((s: any, i: number) => {
          const c = byId.get(s.celda);
          if (!c) return null;
          const col = s.color ?? CLASE_COLOR[s.clase] ?? "#ffcc00";
          return <circle key={i} cx={c.cx} cy={c.cy} r={22} fill={`${col}33`} stroke={col} strokeWidth={3} className="pulse" />;
        })}
      </g>
      <g id="overlays">
        {overlays.map((o: Overlay, i: number) => {
          if (o.tipo === "circulo") {
            const c = byId.get(o.celda);
            return c ? <circle key={i} cx={c.cx} cy={c.cy} r={26} fill="none" stroke={o.color} strokeWidth={4} className="pulse" /> : null;
          }
          if (o.tipo === "niebla") {
            const c = byId.get(o.celda);
            return c ? <polygon key={i} points={c.points} fill="#000000cc" stroke="none" /> : null;
          }
          if (o.tipo === "flecha") {
            const a = byId.get(o.de), b = byId.get(o.a);
            return a && b ? <line key={i} x1={a.cx} y1={a.cy} x2={b.cx} y2={b.cy} stroke={o.color} strokeWidth={4} className="dash" markerEnd="url(#arr)" /> : null;
          }
          return null;
        })}
      </g>
      <defs>
        <marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
          <path d="M0,0 L8,3 L0,6" fill="none" stroke="#fff" strokeWidth="1.5" />
        </marker>
      </defs>
    </svg>
  );
}
