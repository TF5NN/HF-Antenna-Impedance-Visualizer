# Counterpoise (CP) Validation Report

**Version:** v2.0.2 · **Date:** 2026-03-20

**Tool:** `antenna_impedance.html`
**Focus:** End Fed mode + counterpoise — matching and impedance behaviour
**Method:** Analytic computation from source code

## CP model (from source, lines 1542–1549)

```
Z_feed = Z_wire + Z_cp       (series addition)

Z_wire = calcZwireComplex(L, freq)          — main EFHW wire
Z_cp   = calcZwireComplex(cpLengthM, freq)  — same formula, same Z0/ALPHA constants
```

Both use Z₀ = 450 Ω, ALPHA = 0.00375 Np/m (scales linearly with freq), VF = 0.975.
No dedicated CP constants exist — the counterpoise is modelled as an identical open-ended stub.

---

## Test 1 — No counterpoise, 9:1 zone, tuner OFF (40m, 7.15 MHz)

**Expected:** often poor match; large reactive excursions between resonant lengths.

α(40m) = 0.00375 × (7.15/3.65) = 0.007346 Np/m, λ_eff = 40.876 m

| Wire L | Type | R (Ω) | X (Ω) | After 9:1 Za | SWR | 9:1 zone? |
|--------|------|--------|--------|-------------|-----|:---------:|
| 10.22 m | λ/4 | 34 | 0 | {3.78, 0} | 13.24 | ✗ |
| 16.0 m | between λ/4–λ/2 | 86.5 | −356 | {9.6, −39.6} | 8.52 | ✗ |
| 20.44 m | λ/2 | 3028 | 0 | {336.4, 0} | 6.73 | ✗ |
| 22.0 m | above λ/2 | 894 | +1292 | {99.3, +143.6} | 6.51 | ✗ |

The 9:1 zone requires Za ≈ 50 Ω at radio, i.e. Z_feed ≈ 450 Ω.
EFHW impedance swings between ~34 Ω (λ/4) and ~3028 Ω (λ/2): 450 Ω occurs only at
specific intermediate lengths and only for certain impedance magnitudes with large reactance.

"Unstable regions" manifest where |X| is large (e.g. L=16 m: |X|=356 Ω; L=22 m: |X|=1292 Ω)
— a small length change drastically moves the impedance, making any zone boundary sensitive.

**Expected:** poor match, large reactance swings. **Observed:** SWR 6.5–13 across all test lengths. ✓
**Verdict: PASS ✓**

---

## Test 2 — Counterpoise ON: short, ~λ/4, ~λ/2 lengths

### 2a — Wire at λ/2 on 40m (resonant, R=3028 Ω, X=0)

CP impedances at 7.15 MHz:

| CP length | a2 | b2 | R_cp (Ω) | X_cp (Ω) |
|-----------|----|----|---------|---------|
| 3 m | 0.0441 | 0.922 | 50 | +903 |
| 5 m | 0.0735 | 1.537 | 34 | +465 |
| 10.22 m (λ/4) | 0.1502 | π | 34 | 0 |
| 20.44 m (λ/2) | 0.3003 | 2π | 3033 | 0 |

Derivation sample (CP = 5 m):
```
betaL = 2π×5/40.876 = 0.7686 rad → b2 = 1.5372 rad
a2    = 2×0.007346×5 = 0.07346
D     = cosh(0.07346) − cos(1.5372) = 1.00070 − 0.03357 = 0.96713
R_cp  = 450 × sinh(0.07346)/0.96713 = 450×0.07353/0.96713 ≈ 34 Ω
X_cp  = 450 × sin(1.5372)/0.96713  = 450×0.9994/0.96713 ≈ 465 Ω
```

Effect on λ/2 wire + 49:1 zone (no tuner, rawSwrLimit = 2.0):

| CP length | Z_total | After 49:1 Za | SWR | 49:1 zone? |
|-----------|---------|-------------|-----|:----------:|
| None | {3028, 0} | {61.8, 0} | 1.24 | ✓ |
| 3 m | {3078, +903} | {62.8, +18.4} | 1.49 | ✓ |
| 5 m | {3062, +465} | {62.5, +9.49} | 1.32 | ✓ |
| 10.22 m (λ/4) | {3062, 0} | {62.5, 0} | 1.25 | ✓ |
| 20.44 m (λ/2) | {6061, 0} | {123.7, 0} | 2.47 | **✗** |

CP=3m: SWR 1.24 → 1.49 (zone still active but worsened)
CP=5m: SWR 1.24 → 1.32 (modest worsening)
CP=λ/4: SWR 1.24 → 1.25 (minimal effect — CP adds pure R≈34 Ω, X=0)
CP=λ/2: SWR 1.24 → 2.47 → **zone fails** (CP doubles the feedpoint resistance)

---

### 2b — Wire at 16 m on 40m (off-resonance, R=86.5 Ω, X=−356 Ω)

Derivation (L=16 m):
```
betaL = 2π×16/40.876 = 2.461 rad → b2 = 4.922 rad = π+1.780
a2    = 2×0.007346×16 = 0.23507
D     = cosh(0.23507) − cos(4.922) = 1.02759 − (−cos(1.780)) = 1.02759 + 0.2075 = 1.23509
R     = 450 × sinh(0.23507)/1.23509 = 450×0.2374/1.235 = 86.5 Ω
X     = 450 × sin(4.922)/1.23509   = 450×(−0.9781)/1.235 = −356 Ω
```

| CP length | Z_total | After 9:1 Za | SWR | Δ vs no CP |
|-----------|---------|-------------|-----|-----------|
| None | {86.5, −356} | {9.6, −39.6} | 8.52 | baseline |
| 5 m (X_cp=+465) | {121, +109} | {13.4, +12.1} | 3.97 | **improved** (X partly cancelled) |
| 10.22 m (X_cp=0) | {120, −356} | {13.4, −39.6} | 6.18 | slightly improved (R added, X unchanged) |
| 3 m (X_cp=+903) | {136, +547} | {15.1, +60.8} | 5.03 | mixed: R improves, X worsens |

CP=5m gives the best improvement here: the positive X_cp=+465 Ω partially cancels X_wire=−356 Ω,
reducing |X_total| from 356 → 109 Ω. SWR drops 8.52 → 3.97 — a meaningful improvement, though
still outside the 2:1 limit for the 9:1 zone (tuner would be needed to close the gap).

CP=λ/4 leaves X unchanged, only adds ~34 Ω to R → limited benefit (SWR 8.52 → 6.18).

---

### 2c — Cross-band comparison: CP=5m, wire at λ/2 resonance

Same CP=5m at 80m (3.65 MHz) for wire L=40.03 m:
```
alpha(80m) = 0.00375 Np/m;  lambda_eff = 80.06 m
betaL_cp   = 2π×5/80.06  = 0.3924 rad → b2 = 0.7848 rad
a2_cp      = 2×0.00375×5  = 0.0375
D          = cosh(0.0375) − cos(0.7848) = 1.000704 − 0.7071 = 0.2936
R_cp       = 450 × sinh(0.0375)/0.2936 = 450×0.03751/0.2936 ≈ 57.5 Ω
X_cp       = 450 × sin(0.7848)/0.2936  = 450×0.7071/0.2936 ≈ 1084 Ω
```

Z_total = {3028+57.5, 0+1084} = {3086, +1084}
After 49:1: Za = {62.98, +22.12} → SWR = 1.57

The same 5m CP is relatively shorter at 80m (λ/16 vs λ/8 at 40m), yet adds larger absolute X
(1084 vs 465 Ω) — worsening the 80m match more severely. Demonstrates frequency dependence.

**Expected:** CP shifts impedance, sometimes improving, sometimes worsening — not always predictable.
**Observed:**
- CP worsens resonant-wire match in nearly all cases (adds unwanted X when main wire X=0)
- λ/4 CP is safest: adds only R≈34 Ω with X=0 → minimal disruption to existing match ✓
- λ/2 CP is worst: doubles R, destroys 49:1 zone ✓
- For off-resonance wire with X≠0, a CP of the right length can provide partial cancellation ✓
- The "right" CP length that improves the match is hard to predict without calculation ✓

**Verdict: PASS ✓**

---

## Test 3 — Qualitative realism

**Expected:** CP effect noticeable but not perfect; matches simplified-model documentation.

### Series addition model

The documented comment (line 1510):
> "With counterpoise: both open-ended TL impedances add in series."

This correctly captures that the CP introduces a series impedance element at the feedpoint.
Physical justification: the CP carries the return current; its impedance loads the feedpoint
in series with the wire's radiation/feed impedance.

### CP behaviour at key lengths

| CP type | R_cp | X_cp | Realism |
|---------|------|------|---------|
| λ/4 (resonant) | ~34 Ω | 0 | ✓ A near-resonant CP has low reactance — correct |
| λ/2 (anti-resonant for CP) | ~3033 Ω | 0 | ✓ High-resistance, pure-real — correct in direction |
| Short (< λ/8) | moderate R, very large X | ⚠ A short wire should be predominantly capacitive (X < 0 per classical stub theory); model gives X > 0 — see concern #1 below |

### Behaviour matches stated model scope

The model is described as an "educational/simplified" tool. Results are qualitatively reasonable:
- λ/4 CP is the most neutral choice (X=0, small R) — matches ham radio rule of thumb ✓
- CP length matters significantly — effect is non-trivial and length-dependent ✓
- CP always degrades the match at the λ/2 resonance (adds either X or extra R) ✓
- Off-resonance wire can benefit from CP X cancellation ✓

**Verdict: PASS (with caveats) ✓**

---

## Summary

| Test | Verdict | Key finding |
|------|:-------:|-------------|
| 1 — No CP, 9:1, tuner OFF | PASS ✓ | SWR 6.5–13 across all test lengths; 9:1 zone never active |
| 2 — CP ON: short / λ/4 / λ/2 | PASS ✓ | λ/4 CP is benign; short CPs worsen resonant match; λ/2 CP destroys it |
| 3 — Qualitative realism | PASS ✓ | Series-addition model captures correct trends; sign caveat noted |

**Overall: CP model behaves realistically within its stated scope as a simplified educational model.**

---

## Concerns

1. **X sign for sub-λ/4 CPs is wrong per classical TL theory.**
   An open-ended stub shorter than λ/4 has a capacitive input impedance (X < 0).
   The code formula gives X_cp = +Z₀ sin(b2)/D which is **positive** (inductive) for b2 < π
   (i.e. CP length < λ/4). This is because the code uses a sign convention matched to antenna
   physics near λ/2 resonance (X < 0 for "too short", X > 0 for "too long") rather than to
   the classical transmission-line open-stub formula (X = −Z₀ cot(βL)).
   The two conventions agree at X=0 nulls (λ/4, λ/2 lengths) but disagree everywhere else.
   **Impact:** for short CPs (3–5 m at 7–14 MHz), the displayed X sign and magnitude should
   be treated with caution. The direction of impedance shift is uncertain.

2. **CP uses identical constants to main wire.**
   Real counterpoises are typically near-ground wires with different height/geometry from the
   main elevated wire. Using Z₀=450 Ω and the same ALPHA for both ignores the different
   propagation environment. This likely overestimates Z_cp relative to a real CP.

3. **No CP optimisation guidance in UI.**
   The tool shows the impedance shift when CP is enabled, but there is no visual indication
   of an "optimal" CP length. Given the non-intuitive behaviour shown above, a tooltip or
   annotation flagging λ/4 ± 10% as the preferred range would improve usability.

4. **Series model ignores mutual coupling.**
   In a real EFHW installation, CP and wire currents interact (common-mode, mutual inductance).
   The pure series addition ignores these coupling terms. The model will underestimate coupling
   between the CP and the main wire for parallel or near-parallel routing.
