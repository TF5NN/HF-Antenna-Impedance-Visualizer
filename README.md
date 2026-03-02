# HF End-Fed Antenna Impedance — Visual Tool

An interactive, browser-based educational tool for amateur radio operators that visualises how the feedpoint impedance of an HF end-fed wire antenna varies with wire length across the major amateur bands.

No installation, no build step — open `antenna_impedance.html` directly in any modern browser.

---

## Features

- **11 HF bands** — 160 m through 6 m, individually toggleable
- **Three matching zones** — 49:1 Unun, 9:1 Unun + Tuner, 1:1 Unun; colour-shaded on the graph
- **★ Sweet Spots overlay** — highlights wire lengths where multiple bands simultaneously fall inside matching zones; adjustable minimum-band threshold
- **Sweet Spots results table** — lists every sweet-spot cluster with its centre length, usable range, and per-band zone/SWR
- **Inspect pin** — draggable vertical line (or type a length) that shows the impedance and SWR for every active band at that exact wire length
- **Counterpoise modelling** — shows the effect of an added counterpoise wire on effective feedpoint impedance
- **Wire velocity factor** — slider adjusts for insulated vs. bare wire (0.90 – 1.00)
- **ITU Region 1 allocation width** — toggle that scales each band's curve thickness proportionally to its ITU R1 bandwidth (logarithmic, 1 – 4 px); wider line = more operating room
- **Hover tooltip** — real-time impedance, SWR, and matching efficiency for every active band under the cursor

---

## How to Use

1. Download or clone this repository.
2. Open `antenna_impedance.html` in a web browser (Chrome, Firefox, Safari, Edge — all work).
3. Toggle the bands and matching zones you care about.
4. Hover over the graph to read off impedance and SWR at any wire length.
5. Enable **★ Sweet Spots** to find multi-band lengths.
6. Drag the **inspect pin** or type a length to lock a measurement in place.

The tool can also be hosted as a static page on any web server or GitHub Pages — no server-side code is required.

---

## Model Notes

The impedance model is an open-circuit transmission-line approximation:

```
|Z| = Z₀ · |cot(βL)|     Z₀ ≈ 550 Ω (typical end-fed characteristic impedance)
```

With counterpoise enabled, a simplified series-stub model is applied. The model is intentionally educational rather than a full EM simulation — real antenna impedance is also affected by height above ground, nearby objects, soil conductivity, and wire geometry. Anti-resonance dips are clamped to a realistic minimum (~25 Ω) rather than the theoretical zero.

---

## License

Copyright © 2026 TF5NN

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence.
You are free to share, adapt, and build upon this work — including commercially — as long as you credit **TF5NN** as the original creator.

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

See [LICENSE](LICENSE) for the full terms.

---

*Created by TF5NN · v1.01*
