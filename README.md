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

The tool is intentionally educational rather than a full EM simulator. Real antenna impedance is also shaped by height above ground, nearby objects, soil conductivity, and wire geometry. The sections below trace the signal path from raw wire impedance through to the efficiency figure shown in the tooltip.

---

### 1 — Antenna Feedpoint Impedance

The wire is modelled as a **lossy open-circuit transmission line**. For a wire of length *L* at frequency *f* the feedpoint presents a complex impedance Z = R + jX, where:

```
β  = 2πf / (c · VF)          phase constant (rad/m); VF = velocity factor
α  = α₀ · (f / f₀)           attenuation constant (Np/m), scales with frequency
                               so that R_peak ≈ 3 000 Ω at every band's λ/2

D  = cosh(2αL) − cos(2βL)    common denominator

R  = Z₀ · sinh(2αL) / D      resistive part  (Ω)
X  = Z₀ · sin(2βL)  / D      reactive part   (Ω, positive = inductive)

Z₀ = 450 Ω  (effective characteristic impedance of a typical HF wire)
```

**Behaviour at key lengths:**

| Wire length | Condition | Effect |
|-------------|-----------|--------|
| L = n·λ/2 (resonance) | cos(2βL) → 1, D → small | R peaks (2 000 – 5 000 Ω) |
| L = n·λ/4 (anti-resonance) | cos(2βL) → −1, D large | R drops to floor (~25 Ω) |

**Harmonic-order correction** — a wire at its *n*th harmonic resonance radiates more efficiently than the flat-α model predicts. The attenuation is reduced by:

```
α_eff  = α / √n_eff        n_eff = max(1,  2L / λ_eff)
```

At the fundamental (n_eff = 1) α is unchanged. At the 2λ resonance (n_eff = 4, e.g. 10 m on a 40 m wire) α is halved, doubling R_peak from ~750 Ω to ~1 500 Ω — consistent with real EFHW measurements.

Anti-resonance dips are clamped to Z_MIN = 25 Ω and peaks to Z_MAX = 5 000 Ω to reflect practical wire behaviour.

---

### 2 — SWR and Reflection-Coefficient Math

The **complex reflection coefficient** at a reference impedance Z_ref = 50 Ω is:

```
Γ = (Za − 50) / (Za + 50)        Za = antenna impedance after transformer division

|Γ| = |Za − 50| / |Za + 50|      magnitude, computed with full complex arithmetic
```

From this:

```
SWR            = (1 + |Γ|) / (1 − |Γ|)
η_mismatch     = 1 − |Γ|²          (fraction of incident power transferred)
```

Both numerator and denominator use `Math.hypot(R ± 50, X)` so that reactance is always included — the SWR shown in the tooltip is the true complex SWR, not a resistive approximation.

---

### 3 — Transformer Matching: Math and Efficiency

Each matching zone uses an **impedance transformer** (Unun or Balun) to shift the antenna's high impedance down to the 50 Ω radio reference. The transformation is exact:

```
Za_radio = Zc / ratio        ratio = n²  (e.g. 49 for a 49:1 Unun)
```

Design impedances (= ratio × 50 Ω):

| Zone | Transformer | ratio | Z_ref |
|------|-------------|-------|-------|
| 49:1 Unun | Wound 1:49 | 49 | 2 450 Ω |
| 9:1 Unun  | Wound 1:9  |  9 |   450 Ω |
| 1:1 Balun | Choke      |  1 |    50 Ω |

**Insertion efficiency** is a fixed constant per zone, chosen to reflect measured ferrite-toroid losses at HF:

| Zone | η_transformer |
|------|---------------|
| 49:1 Unun | 90 % |
| 9:1 Unun  | 90 % |
| 1:1 Balun | 100 % (choke only, negligible loss) |

The **coloured overlay band** on the graph shows the impedance window the transformer covers. When an ATU is active the band expands to `[Z_ref / maxSWR … Z_ref × maxSWR]` to reflect the wider impedance range the combined system can handle.

---

### 4 — ATU L-network Matching and Efficiency

When the **Antenna Tuner** toggle is on, an analytic **L-network solver** (`solveL`) attempts to match the impedance presented at the transformer output to 50 Ω. Two topologies are tried in order:

1. **series → shunt** — series element (L or C) facing the antenna, shunt element to ground.
2. **shunt → series** — shunt element across the antenna terminals, series element to the radio.

Each solution is constrained by the ATU preset's **Lmax** (µH) and **Cmax** (pF). The tooltip shows the winning topology and exact component values, or "No match within tuner limits" if neither topology fits.

**Inductor-Q loss model (v1):**

A real inductor has a quality factor Q that introduces an equivalent series resistance:

```
Rs = 2π · f · L / Q          Q = 120 (typical small toroidal ATU coil)
```

An L-network circulates extra reactive current when the impedance mismatch ratio is large. The circulating-current stress factor scales the effective loss resistance:

```
kI² = max(R_load, 50) / min(R_load, 50)     (impedance mismatch ratio, ≥ 1)
Rs_eff = Rs × kI²
η_tuner = R_load / (R_load + Rs_eff)         clamped to [0.30, 0.98]
```

Easy matches (R_load near 50 Ω, kI² ≈ 1) see almost no change. Hard matches (high impedance ratio, kI² >> 1) show noticeably lower efficiency. The tooltip shows **"tuner eff xx% Q≈Y.Y"** — the Q figure is the L-match loaded Q, a measure of how hard the network is working. Capacitor ESR is not modelled. Matching logic (whether a zone lights up) is not affected.

**Total delivered-power efficiency** (the `~xx%` figure in the tooltip):

```
η_total = η_mismatch × η_transformer × η_tuner
```

This is *power delivered to the feedpoint*, not power radiated. Radiation efficiency (dependent on wire height, ground quality, nearby objects) is a separate quantity and is not modelled here.

---

### 5 — Counterpoise Model

When **Show effect** is enabled, a counterpoise of length L_cp is modelled as a second open-circuit wire added **in series** at the feedpoint:

```
Z_feedpoint = Z_wire(L, f) + Z_counterpoise(L_cp, f)
```

Both components use the same lossy transmission-line formula. Electrically, the counterpoise acts as a series stub that modifies the effective feedpoint impedance seen by the transformer.

**Limitations:** this series-stub approximation is a first-order model. It is least accurate near **λ/4 counterpoise lengths** (which is also the 1:1 Unun zone) where `cot(βL_cp) ≈ 0`, ground-plane physics and common-mode current paths dominate, and the actual impedance depends heavily on installation geometry. The ghost curves shown when counterpoise is active are therefore illustrative rather than definitive.

---

### 6 — Why the 9:1 Unun Struggles Without a Counterpoise

The 9:1 Unun is designed for random-wire antennas that present approximately **450 Ω resistive** at the feedpoint (9 × 50 Ω). However, the transmission-line model reveals a fundamental challenge:

Between wire resonances — where the wire is neither at λ/2 nor at λ/4 — the impedance always has a large **reactive component X** alongside a moderate R. Even when |Z| ≈ 450 Ω, the reactive part can be 3–10× larger than R, driving the complex SWR after the 9:1 to 7–15:1.

A **counterpoise of suitable length** adds its own impedance in series. When that series impedance partially cancels the wire's reactance, the net |X| drops and R stays in the 225–900 Ω window — bringing the system into the 9:1's natural match band without a tuner.

This is not a corner case: it is the normal operating condition for a 9:1 random-wire installation. A counterpoise of **3–7 m** is a functional part of the matching system, not an optional accessory. The tool demonstrates this visually — enabling the counterpoise with a length of 3–5 m typically unlocks multiple green matching windows on the 9:1 SWR strip that are absent without it.

---

## License

Copyright © 2026 TF5NN

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** licence.
You are free to share, adapt, and build upon this work — including commercially — as long as you credit **TF5NN** as the original creator.

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

See [LICENSE](LICENSE) for the full terms.

---

*Created by TF5NN · v1.14*
