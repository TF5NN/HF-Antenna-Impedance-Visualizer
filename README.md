# HF Antenna Impedance Visualizer

An interactive, browser-based educational tool for amateur radio operators that visualises how feedpoint impedance varies across HF wire antennas — both end-fed and dipole configurations.

No installation, no build step — open `antenna_impedance.html` directly in any modern browser.

---

## Features

### Both modes
- **11 HF bands** — 160 m through 6 m, individually toggleable
- **Wire velocity factor** — slider adjusts for insulated vs. bare wire (0.90 – 1.00)
- **Antenna Tuner** — analytic L-network solver with three presets (internal 3:1, external 10:1, wide-range 20:1) plus custom; Q-based feasibility gate prevents unrealistic matches; tooltip shows rejection hint when no match is found
- **Log-scale Y-axis** — 10 – 5 000 Ω, HiDPI-aware canvas
- **Hover tooltip** — real-time impedance and SWR for every active band under the cursor
- **Mode switcher** — toggle between End-Fed and Dipole modes at the top of the control panel

### End-Fed mode
- **Three matching zones** — 49:1 Unun, 9:1 Unun + Tuner, 1:1 Balun; colour-shaded on the graph
- **★ Sweet Spots overlay** — highlights wire lengths where multiple bands simultaneously fall inside matching zones; adjustable minimum-band threshold. By default every counted band must match through one and the same transformer; **Mix transformers** lets each band use any selected transformer
- **Sweet Spots results table** — lists every sweet-spot cluster with its centre length, usable range, and per-band zone/SWR
- **Inspect pin** — draggable vertical line (or type a length) that shows the impedance and SWR for every active band at that exact wire length
- **Counterpoise modelling** — wire and counterpoise are treated as the two arms of one antenna; ghost curves show the wire alone for comparison
- **ITU Region 1 allocation width** — toggle that scales each band's curve thickness proportionally to its ITU R1 bandwidth

### Dipole mode
- **X-axis = feedpoint position** — 0% (one end) to 100% (other end), with 50% = centre-fed
- **Four matching zones** — 1:1 (50 Ω), 4:1 (200 Ω), 6:1 (300 Ω), Custom ratio; colour-shaded overlays
- **Wire length control** — auto (λ/2 of lowest active band × VF) or manual override; "Reset to λ/2" clears override
- **Feedpoint position controls** — slider + numeric input + preset buttons (50% centre, 33% OCF, 25% extreme OCF)
- **Half-view toggle** — collapse X-axis to 0–50% (one arm) to zoom in on one side
- **Height above ground** — optional: shows how a horizontal dipole's feedpoint resistance changes with height over average soil
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

Since v3.0.0 the wire model has no fitted peak values: its loss term is set equal to the wire's radiation resistance. Against NEC-2 (1 mm bare wire, 40/20/15/10 m) the typical (RMS) error in |Z| is about **4 %** for an end-fed wire against ideal ground, **12 %** for off-centre-fed wires, **11 %** for an end-fed wire with a counterpoise and **13 %** for a dipole 5–20 m above average ground. See [validation/nec_comparison_v3.md](validation/nec_comparison_v3.md).

---

### 1 — Wire Model (End-Fed)

Each conductor is an **open-ended transmission line whose loss is the radiation**. For a wire of length *L* at frequency *f*:

```
θ   = 2πL / (λ · VF) + end·π        electrical length (rad)
end = 0.0464 − 0.0030 · ln(λ / a)   open-end effect in half-waves (≈ 0.012 on 40 m)
Z₀  = 60 · ln(0.22 · λ / a) · VF    average characteristic impedance, a = wire radius (0.5 mm)
a   = atanh(R_rad(θ) / Z₀)          line loss chosen so the line dissipates what the wire radiates

Z   = Z₀ · coth(a + jθ)
R   =  Z₀ · sinh(2a) / D            D = cosh(2a) − cos(2θ)
X   = −Z₀ · sin(2θ)  / D
```

- **VF** is the slowing caused by the insulation only (bare wire = 1.00).
- **end·π** is the open-end effect: a fixed extra electrical length per open end, not a percentage of the wire. It grows as the wire gets thicker compared with the wavelength (0.8 % of a half-wave on 160 m, 1.7 % on 10 m for 1 mm wire). Harmonic resonances are therefore *not* exact multiples of the fundamental length: the n-th half-wave point is at `(n − end) · VF · λ/2`.
- **R_rad(θ)** is the induced-EMF radiation resistance of a sinusoidal standing-wave current, referred to the current maximum. For a wire against an ideal ground it has a closed form in sine and cosine integrals (half the classic dipole result).

What falls out, with no calibration constants:

| Length | Model | Why |
|--------|-------|-----|
| λ/4 | ≈ 36 Ω | R ≈ R_rad |
| 3λ/4, 5λ/4 | ≈ 53 Ω, 60 Ω | R_rad grows slowly with length |
| λ/2 (40 m) | ≈ 3.4 kΩ | R ≈ Z₀² / R_rad |
| λ, 3λ/2 … | falls slowly | R_rad of the longer wire is larger |

R is clamped to 5 000 Ω and the plotted |Z| to 25 Ω.

---

### 2 — Dipole and Off-Centre Feed

A wire of total length *L* fed at position *p* (0.0 = one end, 1.0 = other end) has two arms, `La = p × L` and `Lb = (1 − p) × L`. The generator sits between them, so the arms are **in series**:

```
Z_feed = Z₀·coth(a_A + jθ_A) + Z₀·coth(a_B + jθ_B)
```

The loss terms come from the radiation resistance of the actual two-arm current, including the coupling between the arms:

```
R_feed ≈ R_AA / sin²θ_A + R_BB / sin²θ_B + 2·R_AB / (sinθ_A · sinθ_B)

tanh(a_A) = (R_AA + T·R_AB) / Z₀      T = 2·sinθ_A·sinθ_B / (sin²θ_A + sin²θ_B)
tanh(a_B) = (R_BB + T·R_AB) / Z₀
```

R_AA, R_BB and R_AB are evaluated numerically from the far-field power integral of the two sinusoidal arm currents (cached, so redraws are instant). The weight *T* reproduces the R_feed expression above for low loss and stays finite where one arm is a multiple of λ/2.

Results:

- Centre-fed λ/2 → **≈ 73 Ω**, X ≈ 0 (free space).
- A resonant wire stays resonant wherever it is fed; on the fundamental `R(p) ≈ R_centre / sin²(π·p)` — about 100 Ω at 33 %, 140 Ω at 25 %.
- Centre-fed full-wave → several kΩ.

**Auto wire length** is the resonant half-wave: two λ/4 arms, each with its end effect.

**Height above ground** (optional, off by default). The ground acts as a partial mirror: an image of the wire at depth *h* carries `−ρ` times its current, which multiplies the radiated-power integrand by

```
1 − ρ · J₀(2·k·h·sinψ)          ρ = −Re[(1 − n)/(1 + n)],  n² = εr − j·σ/(ω·ε₀)
```

with average soil assumed (εr = 13, σ = 5 mS/m; ρ ≈ 0.63 on 40 m). A half-wave dipole then reads about 45 Ω at 0.12 λ, about 80 Ω near λ/4 and tends to 73 Ω when high. Only the resistance is corrected; the small ground-induced shift in resonant length is not modelled, and the wire is assumed straight and horizontal.

> Versions before v3.0.0 combined the two arms in parallel, which overstated off-centre impedance by a factor of 2–3 (≈ 400 Ω at 33 % instead of ≈ 100 Ω).

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

When the Antenna Tuner is on, an analytic L-network solver attempts to match the transformer output to 50 Ω. Two topologies are tried (series→shunt and shunt→series).

Tuner efficiency is computed on the solved circuit: every inductor gets a series loss resistance and capacitors are treated as lossless.

```
ESR_L   = X_L / Q                       Q = 120
η_tuner = P_load / P_in                 evaluated on the actual network
```

**Total delivered-power efficiency:**

```
tuner finds a match:   η_total = η_transformer × η_tuner        (radio sees 50 Ω — no mismatch loss)
otherwise:             η_total = η_mismatch × η_transformer
```

All displays (SWR strips, sweet spots, tooltip, inspect panel) read from the same calculation.

**Q-based feasibility gate (`canTune`):**

Before invoking the L-network solver, a feasibility check rejects degenerate or
unrealistic inputs:

```
ratio       = max(R, 50) / min(R, 50)
Q_transform = √(ratio − 1)
Q_reactive  = |X| / R
Q_total     = Q_transform + Q_reactive

Hard rejects: R ≤ 1 Ω, R ≥ 10 000 Ω, |X| > 10·R, ratio > 100
Soft reject:  Q_total > Qmax  (preset-dependent: 4 / 9 / 17)
```

In practice the primary gate is the SWR check (`rawSwr > maxSWR`); the Qmax
formula is a conservative secondary safety net. When no match is found the
tooltip shows *"Match unlikely — required tuner Q too high"* as a subtle hint.

---

### 6 — Counterpoise Model (End-Fed mode)

When **Show effect** is enabled, the wire and the counterpoise are the two arms of one antenna — the same series model as the dipole mode fed off-centre, including the coupling between the arms:

```
Z_feedpoint = Z_wire(L) + Z_counterpoise(L_cp)
```

Without a counterpoise the wire is modelled against an ideal ground. The counterpoise is assumed straight, in line with the wire and in free space; one lying on the ground, or a coax shield acting as counterpoise, will be detuned and lossier. The ghost curves (wire alone) are shown for comparison.

At half-wave (49:1) lengths a short counterpoise of about 0.05 λ is enough. At low-impedance lengths the counterpoise is half of the antenna and its length moves the match a lot.

---

## License

Copyright © 2026 Gunnar B. Guðlaugsson, TF5NN

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence.
You are free to share, adapt, and build upon this work — including commercially — as long as you credit **Gunnar B. Guðlaugsson (TF5NN)** as the original creator.

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

See [LICENSE](LICENSE) for the full terms.

---

*Created by Gunnar B. Guðlaugsson (TF5NN) · v3.1.0*
