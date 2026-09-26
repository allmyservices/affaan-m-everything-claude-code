# Matrix Visualizer

A digital-rain visualizer in the style of *The Matrix*. Two independent implementations, same idea:

- **Web** (`index.html`, `style.css`, `script.js`) — plain HTML/CSS/JS and the Canvas API, no build step, no dependencies.
- **Pygame** (`matrix_pygame.py`) — a native desktop app.

## Web version

Open `index.html` in a browser, or serve the directory:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

### Controls

Click the ☰ button (top-left) to open the settings panel:

- **Character set** — Katakana, binary, Latin, hex, or a custom string
- **Theme** — green, amber, cyan, red, white, or rainbow
- **Speed**, **density**, **font size**, **trail length**
- **Glow** — toggles the neon glow on the leading character
- **Glitch flicker** — random character dropout for a glitchy look
- **React to cursor** — columns near the mouse speed up

Keyboard shortcuts: `Space` to pause/resume, `H` to hide/show the panel.

## Pygame version

```bash
pip install -r requirements.txt
python3 matrix_pygame.py
```

Katakana rendering needs a CJK-capable font installed on your system (e.g. Noto Sans CJK, IPAGothic, or unifont on Linux; most macOS/Windows installs already have one). If none is found, it falls back to pygame's built-in font, which only covers Latin/digits — switch to the `latin`, `binary`, or `hex` character set in that case.

### Controls

An in-app help overlay (toggle with `H`) shows live settings:

| Key | Action |
| --- | --- |
| `Space` | pause / resume |
| `H` | toggle help overlay |
| `C` | cycle character set |
| `T` | cycle theme |
| `Up` / `Down` | speed +/- |
| `Left` / `Right` | density +/- |
| `[` / `]` | font size -/+ |
| `G` | toggle glow |
| `F` | toggle glitch flicker |
| `M` | toggle mouse reactivity |
| `R` | reset drops |
| `Q` / `Esc` | quit |

### Tests

Headless regression tests run under SDL's dummy video driver (no display needed):

```bash
python3 -m unittest test_matrix_pygame.py -v
```
