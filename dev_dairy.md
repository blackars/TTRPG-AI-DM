# DEV DAIRY — TTRPG-AI-DM (diario para futuros agentes)

> Proyecto: Dungeon Master con IA + mesa aumentada (dashboard + proyector + sonido + cámara).
> Repo: https://github.com/blackars/TTRPG-AI-DM (rama main). Licencia decidida: AGPL-3.0 (YOLO abierto).
> Última actualización: 2026-10-01. Estado: V1 nano entrenado (mAP synth 0.971, falla en real) → lote 2 en curso.

## 1. Origen y contexto previo

- Usuario trabaja con 3 fuentes: `Downloads/principales sistemas de rol de mesa.pdf` (d20, d100/BRP, PbtA,
  FATE, GURPS), `Downloads/requerimientos actuales.pdf` (RPG-AI: spawn dX+Y, Mythic GM, guion secreto,
  one-shot/campaña/wargame, TTS ES/EN, doble pantalla) y `MINIBASE/MiniBase-Web`
  (Next.js 14 + FastAPI + Supabase pgvector + Cloudinary; contratos `/api/minis`, `/api/agent/search`,
  `/api/table/state`). MiniBase es la fuente de verdad del inventario vía API.
- Enfoque visión elegido: **segmentación agnóstica** (YOLO-seg, clases `pieza_juego` + `escenografia`),
  pacto inicial + ByteTrack, grid triple (lógico/proyectado/detectado). Grid dual cuadrado (A1) + hexagonal.
- JEV = TypeSafe Jev (System One, 15-sep-2026, cerrado en waitlist). Alternativa adoptada: **TinyJev 0.6B**
  (MIT, `pip install tinyjev`, verificado `TinyJev instalado: True`). JEV interno determinista
  (`01_RULES_JEV.md`) sigue válido en Python puro. **Caído-por-visión DEPRECADO**: lo decide la narrativa/DM.

## 2. Hardware real (medido, no supuesto)

- PC: RTX 3050 Laptop 4GB (no 3060), Python 3.10, torch cu121 + CUDA OK, ultralytics local OK.
- Cámara principal: **teléfono vía IP Webcam `http://192.168.1.14:8080/video`** (1920x1080, nitidez ~1400-3500).
  Webcam vieja 640x480 (nitidez 7-30) descartada salvo respaldo. Trípode + aro de luz, posiciones A1 cenital
  90° / A2 alto 60° (juego) / A3 45° / A4 lateral 25°.
- **Trampa OpenCV**: `albumentations`/`rembg` reinstalan `opencv-python-headless` y rompen `imshow`.
  Fix: `pip uninstall -y opencv-python-headless` tras cada pip install. Todos los scripts con GUI tienen
  fallback `--no-ver` y try/except en imshow (grid_cam, grabar_video).

## 3. Scripts (todos en `vision/scripts/`, compilan OK)

| Script | Uso |
|---|---|
| `grids.py` | math square+hex + genera SVG patrones (4x4 tests, 9x9 tablero grande) |
| `grid_cam.py` | grid en vivo sobre cámara/móvil; latch 4s, sens +/- , R reinicia fondo, --minis N, --url, --no-ver |
| `foto_webcam.py` | captura fotos (ESPACIO/Q), acepta --url |
| `grabar_video.py` | graba mp4 (--url, --no-ver, reintenta frames WiFi) |
| `probar_foto.py` | foto quieta por contraste + grid (--minis, --todas). SOLO sirve en fondos lisos; en tableros texturizados da falsos/0 (probado: 6-minis perfecta → 0) |
| `calibrate.py` | ArUco 10-13 → H.npy (pendiente de usar en mesa final) |
| `track_test.py` | movimiento en video (previo, superado por YOLO después) |
| `cutout.py` / rembg | fondo → PNG con alfa (modelo u2net descargado en `C:\Users\OSCAR\.u2net`) |
| `synth.py` | pega PNGs sobre fondos → dataset seg (args --smin/--smax; AUG suave tras lote1 oscuro) |
| `tenir.py` | variantes azul/rojo/verde/cálido/penumbra/frío (válidas como variedad, tono aproximado) |
| `recortar_marco.py` | quita marcos Samsung/cursor de fotos a pantalla (--borde 0.07) |
| `extraer_frames.py` | videos → dataset/frames_* |
| `gen_manifest.py` | regenera tests/sesion1/manifest.csv (incluye dioramas + biomas_crop; reglas: luz=PRIMER token, estudio nunca REPETIR, métrica miente en fondos lisos) |
| `probar_url.py` | prueba /video /videofeed /shot.jpg de la IP del teléfono |
| `detect_live.py` | YOLO-seg → celdas grid (foto o vivo). Requiere ultralytics + weights, falla limpio sin ellos |
| `dm/decide_tinyjev.py`, `dm/decide_ejemplo.py` | decidor rápido (tinyjev con fallback a reglas) |

## 4. Dataset (inventario real medido)

- `tests/sesion1/manifest.csv`: 171 filas (estudio 20, tablero 49 SI + 13 PARCIAL azul, diorama 58, bioma 31).
- Studio celu: 15 + 5 frontales colores (roja/Azul/amarilla/morada/naranja) + `frontal3.png` master verde.
- `data/pngs_lote2/`: 5 PNG + `dataset/images/criatura_frontal_master.png` (morado verificado limpio).
- Tablero Kill Team HD: 12 vacías + 12 con mini + `photo*.jpg` batalla (nitidez 1500-5200).
- Videos→frames: `dataset/frames_phone/` 165 (lateral) + 21 alto + 39 cenital_batalla (6 minis, dorada) + 41 morado.
- Dioramas 89: `diorama_bosque_00-34`, `diorama_agua_00-35..22`, pantalla 31 → `fondos_biomas/` + 31 recortadas en `fondos_biomas_crop/`.
- Métrica nitidez (Laplacian var): webcam 7-30, teléfono 1400-5200. **Miente en fondos lisos/negros** (frontal3 8.4 nítida, roja 11.7 nítida, agua 11-49 usables). Veredicto siempre visual.
- Niveles acordados: N1 Kill Team (V1) → N2 dioramas físicos → N3 biomas digitales → N4 videos competencias/screenshots (solo validación).

## 5. Entreno V1 (Colab, saga completa)

- `data/synth_lote1/`: 200 sintéticas 640px (SOLO mini verde + fondos webcam 640px — error reconocido:
  se debió usar las 6 minis + teléfono desde el lote 1) + `data.yaml` (path repo) + `data_colab.yaml`
  (path /content). Zip `synth_lote1_colab.zip` 20MB rehecho con zipfile (Compress-Archive mete backslashes).
- Cuaderno `colab/ENTRENAR_MESA_NANO.ipynb` (7 celdas, con verificación ls/cat antes del train).
- **OJO: entrenó en CPU Xeon, no T4** (val dice `torch CPU`). Por eso ~6h. Exigir `Entorno > T4` + celda `!nvidia-smi`.
- Resultado val: **Box mAP50 0.994, Mask mAP50 0.971**, 200 imgs/815 inst, 0 corruptas.
- `best.pt` (5.7MB) en `vision/weights/` + pusheado. `last.pt` en Downloads como respaldo.
- **Prueba real local (RTX 3050): foto 6 minis → FALLA.** conf 0.35: 9 celdas; conf 0.6: 6 celdas pero
  equivocadas (D3 = dibujo impreso). Diagnóstico: salto sintético (1 escultura, fondos 640px, sin reales).
  Acción: lote 2 (en curso, ver §7).

## 6. Git (blackars/TTRPG-AI-DM, gh auth OK como blackars)

- Commits: v0.1 docs+scripts, backup A (studio ~50MB), backup B (~65MB), C1a frames_phone 1/4 (~35MB),
  `1c7bebc` weights best.pt. Remoto verificado igual que local tras cada push.
- `.gitignore` excluye medios por defecto; se usa `git add -f` por lotes. **Límite duro GitHub 100MB/archivo**:
  mover_morado 182MB, cenital_batalla 174MB, mover_alto 105MB NO entran (partir en trozos 60MB o Drive).
- Red inestable en pushes ~70MB (curl 55): partir en ≤35MB y reintentar. `http.postBuffer=524288000`.
- Pendiente: resto frames_phone (3/4), videos <100MB, trozos de los 3 gigantes, dioramas/biomas (~350MB+).

## 7. ESTADO INTERRUMPIDO — continuar aquí (prioridad)

1. **LOTE 2 CAOS (mitad hecho):** `synth.py` necesita modo caos: `--pngs` múltiples dirs (pngs_lote1+lote2),
   `--recolor` (hue-shift aleatorio por mini pegada), `--nmin/--nmax` (3-12), rotación 90° parcial
   (acostadas), `--smin 0.08 --smax 0.5`. Generar 1500 con TODOS los fondos HD
   (fondos_lote1+lote2+dioramas+biomas_crop) + zip + entrenar **en T4** (agregar celda `!nvidia-smi` al cuaderno).
2. Etiquetar 30 reales (cenital_batalla/morado frames) con SAM/pseudo-labels del best.pt para mezclar 70/30.
3. Probar best.pt v2 en foto 6-minis con `detect_live.py`; si >0.80 real → puente visión→TinyJev→table/state.
4. Calibración ArUco + hex grid en mesa final (docs 02/07) cuando el detector sea fiable.
5. NO reinstalar headless; NO entrenar en CPU; NO meter N4 (competencias) hasta V2 estable.
