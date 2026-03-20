# HF Antenna Impedance Visualizer

An interactive, browser-based educational tool for amateur radio operators that visualises how feedpoint impedance varies across HF wire antennas — both end-fed and dipole configurations.

No installation, no build step — open `antenna_impedance.html` directly in any modern browser.

---

## Features

### Both modes
- **11 HF bands** — 160 m through 6 m, individually toggleable
- **Wire velocity factor** — slider adjusts for insulated vs. bare wire (0.90 – 1.00)
- **Antenna Tuner** — analytic L-network solver with three presets (internal 3:1, external 10:1, wide-range 20:1) plus custom
- **Log-scale Y-axis** — 10 – 5 000 Ω, HiDPI-aware canvas
- **Hover tooltip** — real-time impedance and SWR for every active band under the cursor
- **Mode switcher** — toggle between End-Fed and Dipole modes at the top of the control panel

### End-Fed mode
- **Three matching zones** — 49:1 Unun, 9:1 Unun + Tuner, 1:1 Balun; colour-shaded on the graph
- **★ Sweet Spots overlay** — highlights wire lengths where multiple bands simultaneously fall inside matching zones; adjustable minimum-band threshold
- **Sweet Spots results table** — lists every sweet-spot cluster with its centre length, usable range, and per-band zone/SWR
- **Inspect pin** — draggable vertical line (or type a length) that shows the impedance and SWR for every active band at that exact wire length
- **Counterpoise modelling** — shows the effect of an added counterpoise wire on effective feedpoint impedance
- **ITU Region 1 allocation width** — toggle that scales each band's curve thickness proportionally to its ITU R1 bandwidth

### Dipole mode
- **X-axis = feedpoint position** — 0% (one end) to 100% (other end), with 50% = centre-fed
- **Four matching zones** — 1:1 (50 Ω), 4:1 (200 Ω), 6:1 (300 Ω), Custom ratio; colour-shaded overlays
- **Wire length control** — auto (λ/2 of lowest active band × VF) or manual override; "Reset to λ/2" clears override
- **Feedpoint position controls** — slider + numeric input + preset buttons (50% centre, 33% OCF, 25% extreme OCF)
- **Half-view toggle** — collapse X-axis to 0–50% (one arm) to zoom in on one side
- **Common-mode risk strip** — colour bar at the bottom of the graph: green (near centre) → orange → red (extreme OCF)
- **SWR strips** below the X-axis — one row per active dipole zone showing where each band is matched
- **Click-to-set feedpoint** — click or drag on the canvas to move the feedpoint indicator
- **Inspect panel** — per-band R+jX, SWR after transformer, and delivered efficiency at the selected feedpoint position

---

## How to Use

1. Download or clone this repository.
2. Open `antenna_impedance.html` in a web browser (Chrome, Firefox, Safari, Edge — all work).
3. Select **End Fed** or **Dipole** mode with the buttons at the top of the control panel.
4. Toggle the bands and matching zones you care about.
5. Hover over the graph to read off impedance and SWR at any wire length / feedpoint position.

**End-Fed mode:** Enable **★ Sweet Spots** to find multi-band wire lengths. Drag the inspect pin or type a length to lock a measurement.

**Dipole mode:** Use the feedpoint slider or preset buttons (50%/33%/25%) to explore centre-fed and off-centre-fed configurations. Click directly on the graph to set the feedpoint position. The common-mode risk strip indicates how much asymmetry the chosen feedpoint introduces.

The tool can also be hosted as a static page on any web server or GitHub Pages — no server-side code is required.

---

## ⚠️ Why Loading Coils Are Not Included

This tool models antennas as **lossy open-circuit transmission lines**. That model is accurate for:

- End-Fed Half-Wave (EFHW) antennas
- End-Fed Random Wire (EFRW) antennas
- Centre-fed and off-centre-fed dipoles
- Other electrically long wires where standing-wave behaviour dominates

It is **not valid** for:

- Electrically short antennas (much shorter than λ/2)
- Loaded verticals or whip antennas with series inductors

### Why the model breaks down

Long antennas behave as **distributed systems**: their impedance is governed by standing waves, characterised by `βL` (electrical length) and described by transmission-line equations. This tool implements those equations directly.

Short antennas with loading coils behave as **lumped-element systems**: the antenna is a capacitive load and the coil is a series inductor — described by a simple RLC circuit, not by TL equations.

Adding a "loading coil" inside this model does **not** represent a real loaded antenna. It adds inductive reactance to a transmission-line feedpoint impedance, producing results that look plausible but are physically meaningless for short, loaded antennas.

> For accurate modelling of short loaded antennas, a separate tool using a lumped-element model is required.

The loading coil code remains in the source for future reference and may form the basis of a dedicated loaded-antenna tool in a later release.

---

## Model Notes

The tool is intentionally educational rather than a full EM simulator. Real antenna impedance is also shaped by height above ground, nearby objects, soil conductivity, and wire geometry.

---

### 1 — End-Fed Antenna Feedpoint Impedance

The wire is modelled as a **lossy open-circuit transmission line**. For a wire of length *L* at frequency *f*:

```
β  = 2πf / (c · VF)          phase constant (rad/m)
α  = α₀ · (f / f₀)           attenuation constant (Np/m), scales with frequency

D  = cosh(2αL) − cos(2βL)    common denominator

R  = Z₀ · sinh(2αL) / D      resistive part  (Ω)
X  = Z₀ · sin(2βL)  / D      reactive part   (Ω)

Z₀ = 450 Ω  (effective characteristic impedance of a typical HF wire)
```

**Harmonic-order correction** — attenuation is reduced at higher harmonics:

```
α_eff  = α / √n_eff        n_eff = max(1,  2L / λ_eff)
```

Anti-resonance dips are clamped to Z_MIN = 25 Ω and peaks to Z_MAX = 5 000 Ω.

---

### 2 — Dipole Feedpoint Impedance

A dipole of total length *L* with feedpoint at position *p* (0.0 = one end, 1.0 = other end) is modelled as two open-circuit stubs in parallel:

- Left arm: `La = p × L`
- Right arm: `Lb = (1 − p) × L`
- Feedpoint impedance: `Z_feed = Za ∥ Zb` (complex parallel combination)

Each arm uses the same coth formula with dipole-calibrated constants:

```
Z0_DIP  = 600 Ω
α       = K / λ_eff   (Np/m)     K = 0.8806 (dimensionless)
α_eff   = α / √n_eff             n_eff = max(1, 2·L_arm / λ_eff)
```

**Why `α = K / λ_eff`?** For a resonant quarter-wave arm, `L_arm = λ_eff / 4`, so:

```
α · L_arm  =  (K / λ_eff) · (λ_eff / 4)  =  K / 4   — constant, independent of frequency or VF
```

This means the centre-fed λ/2 model gives the same impedance at every HF band and at any velocity factor setting. K is chosen so that the centre result lands at **R ≈ 65 Ω** (within the 1:1 direct-feed window):

```
K  =  4 · arctanh(2 · Z_target / Z0_DIP)
   =  4 · arctanh(130 / 600)  ≈  0.8806
```

> **This is a simplified standing-wave / feedpoint-position model, not a full EM solver.** It is normalised to give a realistic centre-fed λ/2 baseline. OCF results are approximate and installation-dependent (height above ground, nearby conductors, and feed-line common-mode all affect real antenna impedance).

**Calibration:** centre-fed λ/2 dipole → R ≈ 65 Ω, X ≈ 0 at every HF band.

Edge case: feedpoint at 0% or 100% (end-fed) — one arm has zero length, feedpoint impedance equals the other arm alone (EFHW-like high impedance).

**Common-mode risk** (indicated by the colour strip at the bottom of the graph):

| Feedpoint range | Risk level |
|----------------|------------|
| 40%–60% | Low — near-symmetric currents |
| 25%–40% or 60%–75% | Moderate — OCF |
| 0%–25% or 75%–100% | High — extreme OCF, strong common-mode |

---

### 3 — SWR and Reflection-Coefficient Math

```
Γ = (Za − 50) / (Za + 50)        Za = antenna impedance after transformer division

|Γ| = |Za − 50| / |Za + 50|      magnitude, full complex arithmetic

SWR        = (1 + |Γ|) / (1 − |Γ|)
η_mismatch = 1 − |Γ|²
```

---

### 4 — Transformer Matching

End-Fed zones:

| Zone | Transformer | ratio | Z_ref |
|------|-------------|-------|-------|
| 49:1 Unun | Wound 1:49 | 49 | 2 450 Ω |
| 9:1 Unun  | Wound 1:9  |  9 |   450 Ω |
| 1:1 Balun | Choke      |  1 |    50 Ω |

Dipole zones:

| Zone | Transformer | ratio | Z_ref |
|------|-------------|-------|-------|
| 1:1 | Direct feed / choke | 1 |  50 Ω |
| 4:1 Balun | Wound 4:1 |  4 | 200 Ω |
| 6:1 Balun | Wound 6:1 |  6 | 300 Ω |
| Custom | User-defined ratio | n | 50 × n Ω |

---

### 5 — ATU L-network Matching and Efficiency

When the Antenna Tuner is on, an analytic L-network solver attempts to match the transformer output to 50 Ω. Two topologies are tried (series→shunt and shunt→series). Inductor-Q loss model:

```
Rs = 2π · f · L / Q          Q = 120
kI² = max(R_load, 50) / min(R_load, 50)
Rs_eff = Rs × kI²
η_tuner = R_load / (R_load + Rs_eff)    clamped [0.30, 0.98]
```

**Total delivered-power efficiency:**

```
η_total = η_mismatch × η_transformer × η_tuner
```

---

### 6 — Counterpoise Model (End-Fed mode)

When **Show effect** is enabled, a counterpoise is modelled as a series stub:

```
Z_feedpoint = Z_wire(L, f) + Z_counterpoise(L_cp, f)
```

This approximation is least accurate near λ/4 counterpoise lengths where ground-plane physics dominate. The ghost curves shown are illustrative rather than definitive.

---

## License

Copyright © 2026 Gunnar B. Guðlaugsson, TF5NN

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence.
You are free to share, adapt, and build upon this work — including commercially — as long as you credit **Gunnar B. Guðlaugsson (TF5NN)** as the original creator.

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

See [LICENSE](LICENSE) for the full terms.

---

*Created by Gunnar B. Guðlaugsson (TF5NN) · v2.0*
