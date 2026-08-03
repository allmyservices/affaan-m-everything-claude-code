# Matrix Visualizer

A digital-rain visualizer in the style of *The Matrix*, built with plain HTML/CSS/JS and the Canvas API — no build step, no dependencies.

## Usage

Open `index.html` in a browser, or serve the directory:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Controls

Click the ☰ button (top-left) to open the settings panel:

- **Character set** — Katakana, binary, Latin, hex, or a custom string
- **Theme** — green, amber, cyan, red, white, or rainbow
- **Speed**, **density**, **font size**, **trail length**
- **Glow** — toggles the neon glow on the leading character
- **Glitch flicker** — random character dropout for a glitchy look
- **React to cursor** — columns near the mouse speed up

Keyboard shortcuts: `Space` to pause/resume, `H` to hide/show the panel.
