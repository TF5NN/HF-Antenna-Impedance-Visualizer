# Tuner & Matching Validation Report

**Tool:** `antenna_impedance.html`
**Focus:** Matching zones + ATU (antenna tuner) logic — both EF and Dipole modes
**Method:** Analytic computation from source code (no browser execution)

## Model parameters

| Item | Value | Source |
|------|-------|--------|
| EFHW Z₀ | 450 Ω | `Z0_EF` |
| Dipole Z₀ | 600 Ω | `Z0_DIP = 600` |
| TUNER_L_Q | 120 | assumed inductor Q (small toroid) |
| `swr50(Z)` | `(1+Γ)/(1−Γ)`, Γ = \|Z−50\|/\|Z+50\| | complex form |

### Tuner presets (lines 1238–1242)

| Preset | Lmax (µH) | Cmax (pF) | maxSWR |
|--------|-----------|-----------|--------|
| internal | 4 | 500 | 3 |
| external | 24 | 1200 | 10 |
| widerange | 60 | 3500 | 20 |

### EFHW zones

| Zone | ratio | zRef (Ω) | rawSwrLimit | swrLimit | xfrmrEff |
|------|-------|----------|-------------|----------|----------|
| 49:1 | 49 | 2450 | 2.0 (no tuner) | 3.0 (tuner on) | 0.90 |
| 9:1 | 9 | 450 | — | 2.0 | 0.90 |
| 1:1 | 1 | 50 | — | 2.0 | 1.00 |

### Dipole zones

| Zone | ratio | zRef (Ω) | swrLimit | xfrmrEff |
|------|-------|----------|----------|----------|
| 1:1 | 1 | 50 | 2.0 | 1.00 |
| 4:1 | 4 | 200 | 2.0 | 0.94 |
| 6:1 | 6 | 300 | 2.0 | 0.92 |

---

## Test 1 — Tuner OFF vs ON

### Test case A: Dipole, 40m, 33% OCF, 4:1 zone

Feed impedance from dipole model: R=403 Ω, X=+87 Ω (derived in dipole validation).

After 4:1 transformer: Za = {R: 403/4 = 100.75, X: 87/4 = 21.75}

```
Γ = √((100.75−50)² + 21.75²) / √((100.75+50)² + 21.75²)
  = √(2575.6 + 473.1) / √(22725.6 + 473.1)
  = 55.22 / 152.32 = 0.3625
SWR = (1+0.3625)/(1−0.3625) = 2.14
```

**Tuner OFF:** SWR = 2.14 > swrLimit=2.0 → zone **INACTIVE**

**Tuner ON (external, maxSWR=10):** 2.14 ≤ 10 → `solveL` invoked.

`solveL` Topology B (shunt→series), Za.R=100.75 ≥ 50:
```
R²+X² = 100.75² + 21.75² = 10623.7
Gs = 100.75/10623.7 = 0.009485   (≤ 1/50 = 0.020 ✓)
Bs = −21.75/10623.7 = −0.002048
disc = Gs/50 − Gs² = 0.0000997,  sq = 0.009985

BpBs = +0.009985:
  Bp = 0.009985 − (−0.002048) = 0.012033  [shunt cap: 268 pF ≤ 1200 pF ✓]
  Xs = 0.009985 / 0.0001897  = 52.63 Ω   [series L: 1.17 µH ≤ 24 µH ✓]
```

Both elements feasible → **matched** → SWR = 1.0 → zone **ACTIVE**

**Expected:** tuner OFF = poor SWR, tuner ON = improved.
**Observed:** SWR 2.14 → 1.0. Zone off → on. ✓
**Verdict: PASS ✓**

---

### Test case B: EFHW, 40m, 22 m wire (off-resonance), 49:1 zone

Wire 22 m is not a harmonic of λ_eff = 40.88 m. Using EFHW model:
```
α(40m) = 0.00375 × (7.15/3.65) = 0.007346 Np/m
n_eff  = max(1, 2×22/40.88) = 1.077
αEff   = 0.007346/√1.077 = 0.007079 Np/m
a2     = 2×0.007079×22   = 0.31148
b2     = 2×2π×22/40.88   = 6.7598 rad  (= 2π+0.4766)
D      = cosh(0.31148) − cos(0.4766) = 1.04852 − 0.88858 = 0.15994
R      = 450 × sinh(0.31148)/0.15994 = 450×1.9768 = 890 Ω
X      = 450 × sin(0.4766)/0.15994  = 450×2.866  = 1290 Ω
```

After 49:1: Za = {R: 890/49 = 18.16, X: 1290/49 = 26.33}
```
SWR = 3.60   (Γ = 41.32/73.07 = 0.5655)
```

**Tuner OFF (49:1 rawSwrLimit=2.0):** SWR=3.60 > 2.0 → zone INACTIVE

**Tuner ON (internal, maxSWR=3):** 3.60 > 3 → `swrAtRadio` exits early → zone **INACTIVE**

**Tuner ON (external, maxSWR=10):** 3.60 ≤ 10 → `solveL` invoked.

`solveL` Topology A (series→shunt), Za.R=18.16 < 50:
```
disc = 50×18.16 − 18.16² = 908 − 329.8 = 578.2,  sq = 24.05
Xs_total = −24.05:  Xs = −24.05 − 26.33 = −50.38 Ω [series C: 442 pF ≤ 1200 pF ✓]
                    Bp = +24.05/(50×18.16) = +0.02650 [shunt C: 590 pF ≤ 1200 pF ✓]
```

Both feasible → **matched** → SWR = 1.0 → zone **ACTIVE** (with 49:1 swrLimit=3.0, 1.0 < 3.0 ✓)

**Expected:** OFF=poor SWR, ON=improved within tuner range.
**Observed:** SWR 3.60 → 1.0 (external). Internal blocked by maxSWR gate. ✓
**Verdict: PASS ✓**

---

## Test 2 — Tuner presets: internal vs external vs widerange

### Test case: EFHW, 40m, λ/4 wire (10.22 m), 9:1 zone

From EFHW validation: λ/4 on 40m → R=34 Ω, X=0.
After 9:1: Za = {R: 34/9 = 3.78, X: 0}
```
SWR = (50−3.78)/(50+3.78) → Γ = 46.22/53.78 = 0.8595 → SWR = 13.24
```

| Preset | maxSWR | Gate (13.24 ≤ maxSWR?) | solveL | Zone active? |
|--------|--------|------------------------|--------|:------------:|
| internal | 3 | **FAIL** (13.24 > 3) | not tried | ✗ |
| external | 10 | **FAIL** (13.24 > 10) | not tried | ✗ |
| widerange | 20 | PASS (13.24 ≤ 20) | → attempted | ? |

`solveL` for widerange (Lmax=60µH, Cmax=3500pF), Za={R=3.78, X=0}:
```
omega = 44.924e6 rad/s
XLmax = 44.924e6×60e-6  = 2695.5 Ω   XCmin = 1/(44.924e6×3500e-12) = 6.36 Ω
BLmin = 1/2695.5 = 3.71e-4            BCmax = 44.924e6×3500e-12    = 0.1572

Topology A, disc = 50×3.78 − 3.78² = 174.71, sq = 13.22
Xs_total = +13.22:  Xs = 13.22 Ω  [series L: 0.294 µH ≤ 60 µH ✓]
                    Bp = −13.22/(50×3.78) = −0.06993 [shunt L: 0.318 µH ≤ 60 µH ✓]
```
→ **matched** → SWR = 1.0 → widerange zone **ACTIVE**

---

### Test case: EFHW, 40m, 3λ/4 wire (30.66 m), 9:1 zone

From EFHW validation: 3λ/4 → R=82 Ω, X=0.
After 9:1: Za = {R: 82/9 = 9.11, X: 0} → SWR = 5.49

| Preset | Gate (5.49 ≤ maxSWR?) | solveL feasible? | Zone active? |
|--------|-----------------------|-----------------|:------------:|
| internal | FAIL (5.49 > 3) | not tried | ✗ |
| external | PASS (5.49 ≤ 10) | series L (19.3 Ω, 0.43 µH) + shunt L (Bp=−0.04235) → ✓ | ✓ |
| widerange | PASS | same → ✓ | ✓ |

**Expected:** internal fails more often, widerange matches most cases.
**Observed:**
- SWR=13.24: internal ✗ / external ✗ / widerange ✓ — widerange uniquely handles extreme mismatch
- SWR=5.49: internal ✗ / external ✓ / widerange ✓ — internal excluded by maxSWR gate
- Note: for SWR=5.49, internal component limits (Lmax=4µH) would actually allow a match if the gate were bypassed — the `maxSWR` parameter is the primary differentiator between presets for this frequency/case

**Verdict: PASS ✓** — Progression internal→external→widerange correctly expands matching coverage.

---

## Test 3 — Efficiency behavior

### Easy match: EFHW λ/2 on 40m, 49:1 zone (no tuner needed)

Feed impedance: R=3028 Ω, X=0.
After 49:1: Za = {R: 3028/49 = 61.8, X: 0}
```
Γ = (61.8−50)/(61.8+50) = 11.8/111.8 = 0.1056
η_mismatch = 1 − 0.1056² = 1 − 0.01115 = 98.9 %
```
No tuner needed (SWR=1.24 < 2.0 rawSwrLimit).
```
η_total = xfrmrEff × η_mismatch = 0.90 × 0.989 = 89.0 %
```

### Hard match: EFHW 22 m off-resonance, 40m, 49:1 zone (external tuner)

After 49:1: Za={R=18.16, X=26.33}, SWR=3.60.

**Without tuner:**
```
η_mismatch = 1 − 0.5655² = 1 − 0.3198 = 68.0 %
η_total = 0.90 × 0.680 = 61.2 %
```

**With external tuner (series C + shunt C, no inductors):**
```
estimateTunerEff(freq, L_uH=0, Rload) → 0.98  [caps only, minimal loss]
η_total = xfrmrEff × η_mm × η_tuner = 0.90 × 1.0 × 0.98 = 88.2 %
```

### Comparison table

| Case | Config | η_mismatch | η_tuner | η_total |
|------|--------|-----------|---------|---------|
| Easy (λ/2 resonance) | 49:1, no tuner | 98.9 % | — | **89.0 %** |
| Hard (off-resonance) | 49:1, no tuner | 68.0 % | — | **61.2 %** |
| Hard (off-resonance) | 49:1 + external tuner | 100 % | 98 % | **88.2 %** |
| Dipole OCF 33%, borderline | 4:1 + external tuner | 100 % | 99.1 % | **93.1 %** |

**Expected:** easy = high efficiency; hard = lower efficiency (without tuner); tuner recovers most loss.
**Observed:**
- Easy resonant case: 89 % — high ✓
- Hard off-resonance without tuner: 61 % — significantly lower ✓
- Hard off-resonance with tuner: 88 % — nearly recovers to resonant efficiency ✓
- The tuner efficiency model (Q=120 toroid, stress-aware kI₂ factor) gives 98–99% for small inductances at 7 MHz; larger inductances at lower frequencies would show more loss

**Verdict: PASS ✓** — Efficiency ordering is physically correct and the tuner recovery effect is realistic.

---

## Test 4 — Transformer ratios

### Impedance scaling correctness

`swrAtRadio`: Za = {R: Zc.R / ratio, X: Zc.X / ratio} — linear scaling of both components.
`mismatchEffComplex(Zc, zRef)`: k = zRef/50 = ratio → Za = {R: Zc.R/ratio, X: Zc.X/ratio} — **identical scaling** ✓

**Ideal target impedance → SWR = 1.0 (algebraic verification):**

For Zc = {R: zRef, X: 0}: Za = {R: zRef/ratio, X: 0} = {R: 50, X: 0} → SWR = 1.0 ✓

| Zone | ratio | zRef | Test Zc | Za after ratio | SWR |
|------|-------|------|---------|----------------|-----|
| 49:1 (EFHW) | 49 | 2450 | {R:2450, X:0} | {R:50, X:0} | **1.00** ✓ |
| 9:1 (EFHW) | 9 | 450 | {R:450, X:0} | {R:50, X:0} | **1.00** ✓ |
| 1:1 (EFHW) | 1 | 50 | {R:50, X:0} | {R:50, X:0} | **1.00** ✓ |
| 1:1 (Dipole) | 1 | 50 | {R:50, X:0} | {R:50, X:0} | **1.00** ✓ |
| 4:1 (Dipole) | 4 | 200 | {R:200, X:0} | {R:50, X:0} | **1.00** ✓ |
| 6:1 (Dipole) | 6 | 300 | {R:300, X:0} | {R:50, X:0} | **1.00** ✓ |

### Cross-checks with realistic antenna impedances

**49:1 applied to EFHW λ/2 on 40m (R=3028, X=0):**
Za = {R:61.8, X:0} → SWR = **1.24** — inside rawSwrLimit=2.0 ✓ (zone active without tuner)

**9:1 applied to EFHW λ/2 on 40m (R=3028, X=0):**
Za = {R:336.4, X:0} → Γ=0.741 → SWR = **6.73** — correctly outside 9:1 zone ✓
(9:1 is wrong ratio for EFHW resonance; 49:1 is the appropriate match)

**1:1 applied to EFHW λ/2 on 40m (R=3028, X=0):**
Za = {R:3028, X:0} → Γ=0.968 → SWR ≈ **60.5** — correctly excluded ✓

**1:1 applied to center-fed dipole (R=65, X=0):**
Za = {R:65, X:0} → SWR = **1.30** — inside swrLimit=2.0 ✓

**4:1 applied to dipole at 33% OCF (R=403, X=87):**
Za = {R:100.75, X:21.75} → SWR = **2.14** — marginally above 2.0 limit ⚠ (see dipole validation concern)

**6:1 applied to dipole at 25% (R=722, X=153):**
Za = {R:120.3, X:25.5} → SWR = **2.54** — outside 2.0 limit ⚠

**49:1 applied to EFHW 3λ/4 anti-resonance on 40m (R=82, X=0):**
Za = {R:1.67, X:0} → Γ=0.935 → SWR ≈ **30** — correctly excluded even with widerange tuner (30 > maxSWR=20) ✓

**Expected:** impedance scales by 1/ratio for both R and X; SWR follows logically.
**Observed:** Linear 1/ratio scaling confirmed algebraically. SWR values follow correctly. Each zone activates at the expected impedance range. Zones correctly exclude mismatched cases.
**Verdict: PASS ✓**

---

## Summary

| Test | Verdict | Key finding |
|------|:-------:|-------------|
| 1 — Tuner OFF vs ON | PASS ✓ | SWR 2.14→1.0 (dipole OCF); SWR 3.60→1.0 (EFHW off-resonance) |
| 2 — Presets: internal/external/widerange | PASS ✓ | maxSWR gate is primary differentiator; component limits secondary |
| 3 — Efficiency: easy vs hard | PASS ✓ | 89% (resonant) vs 61% (off-resonance, no tuner) vs 88% (with tuner) |
| 4 — Transformer ratios (all six) | PASS ✓ | Linear 1/ratio scaling; SWR follows correctly; zones logically exclusive |

**Overall verdict: Matching and tuner logic is physically realistic and internally consistent.**

### Concerns

1. **maxSWR gate is a hard cutoff.** A tuner rated for maxSWR=10 returns rawSwr unchanged for any input exceeding 10:1, even if the L-network could theoretically still match (the `solveL` check is never invoked). Real tuners have soft rolloff, not hard cutoffs. Appropriate conservatism for an educational tool, but users should understand the boundary is sharp.

2. **Dipole mode zone limit with tuner ON.** In dipole mode, enabling the tuner changes the zone acceptance limit from `swrLimit=2.0` to `maxSWR` (e.g., 10 for external). This means any post-transformer SWR ≤ 10 shows as "in zone" — even without a confirmed L-network match. This is more permissive than the EFHW mode which only widens to `swrLimit=3.0`. The dipole visual could highlight more positions than are realistically matchable if the L-network solver happens to fail.

3. **Tuner efficiency model uses fixed Q=120.** For a real small toroid at 1.9 MHz with 40+ µH, Q can drop below 80. The widerange tuner handling 160m with large inductances will underestimate insertion loss. Efficiency values shown for widerange at low bands should be treated as optimistic.

4. **kI₂ stress factor** (`max(Rl,50)/min(Rl,50)`) penalises both high and low load impedances equally, which is correct physics. However, it only applies to the inductor's loss — capacitor losses are fixed at 2% (`return 0.98`). Real high-C ATU capacitors at high voltage stress can have significant loss; this is not modelled.
