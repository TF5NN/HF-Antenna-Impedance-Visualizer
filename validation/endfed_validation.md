# End Fed Mode Validation Report

**Version:** v2.1.0 · **Date:** 2026-03-20

**Tool:** `antenna_impedance.html`
**Focus:** End Fed mode only
**Method:** Analytic computation from source code (not visual inspection)
**Model parameters:** Z₀=450 Ω · ALPHA=0.00375 Np/m at 3.65 MHz · VF=0.975 · Z_PEAK=5000 Ω · Z_MIN=25 Ω

---

## Test 1 — λ/2 Resonance (80m, 40m, 20m)

**Expected:** High impedance in the kΩ range, X ≈ 0 at resonance, consistent across bands.

The model scales α linearly with frequency so that α×L_res is constant, forcing
R_peak = Z₀/(αL) ≈ 3000 Ω at every band's fundamental λ/2 by design.

At exact λ/2 resonant lengths (VF=0.975):

| Band | λ/2 length | R (Ω) | X (Ω) | In 49:1 zone? |
|------|------------|--------|--------|---------------|
| 80m  | 40.04 m    | 3028   | 0      | ✓             |
| 40m  | 20.44 m    | 3028   | 0      | ✓             |
| 20m  | 10.31 m    | 3026   | 0      | ✓             |

At resonance: b2 = 2βL = 2π → sin(2π)=0, cos(2π)=1 → X=0 exactly; D=cosh(a2)−1 is small → R peaks.

**Verdict: Believable.**
R ≈ 3 kΩ, X = 0 exactly at resonance for all three bands. Consistent with published
EFHW measurements (typical 2–4 kΩ). The forced band-invariance of R_peak is a known,
documented simplification — not a defect.

---

## Test 2 — λ/4 Anti-resonance Region

**Expected:** Much lower impedance, tens of ohms, clear dip vs λ/2.

At λ/4 lengths: b2 = π → cos(π)=−1 → D = cosh(a2)+1 ≈ 2 (large) → R is small.

| Band | λ/4 length | R (Ω) | X (Ω) | Contrast vs λ/2 |
|------|------------|--------|--------|-----------------|
| 80m  | 20.02 m    | 33.6   | 0      | ~90:1           |
| 40m  | 10.22 m    | 33.7   | 0      | ~90:1           |

The 25 Ω floor clamp is not triggered (33.7 > 25), so the raw model value is shown.

**Verdict: Believable.**
Clear deep dip — 90:1 contrast ratio vs the λ/2 peak. Consistent with real EFHW wires
(20–60 Ω at λ/4 is well-documented). X=0 exactly at the anti-resonance point.

---

## Test 3 — Harmonic Families on 40m

**Expected:** Half-wave family = high-Z peaks; quarter-wave family = low-Z dips;
higher harmonics not identical.

Wire scanned at 7.150 MHz (λ_eff = 40.88 m).

### Half-wave (resonance) family — b2 = 2nπ → cos=1 → D small → high R

| Length  | Type | n_eff | R (Ω) | X (Ω) | In 49:1 zone? |
|---------|------|--------|--------|--------|---------------|
| 20.44 m | λ/2  | 1.00   | 3028   | 0      | ✓             |
| 40.88 m | λ    | 2.00   | 2143   | 0      | ✓             |
| 61.32 m | 3λ/2 | 3.00   | 1762   | 0      | ✓             |
| 81.76 m | 2λ   | 4.00   | 1578   | 0      | ✓             |

Without the harmonic-order correction (`alphaEff = alpha/√n_eff`), the 2λ peak would
fall to ~822 Ω — outside the 49:1 zone. The correction lifts it to ~1578 Ω.

### Quarter-wave (anti-resonance) family — b2 = (2n−1)π → cos=−1 → D large → low R

| Length  | Type  | n_eff | R (Ω) | X (Ω) |
|---------|-------|--------|--------|--------|
| 10.22 m | λ/4   | 1.00   | 34     | 0      |
| 30.66 m | 3λ/4  | 1.50   | 82     | 0      |
| 51.10 m | 5λ/4  | 2.50   | 105    | 0      |
| 71.54 m | 7λ/4  | 3.50   | 123    | 0      |

Anti-resonance values increase modestly with harmonic order (34 → 123 Ω). This is a
side-effect of the harmonic correction reducing alphaEff — R_anti ≈ Z₀×alphaEff×L,
and L grows faster than alphaEff shrinks. All values remain well within the "low-Z"
regime (<200 Ω).

**Verdict: Believable.**
Two clearly distinct impedance families, neither flat nor artificially symmetric.
Both families have X=0 exactly at every harmonic point (physically correct for an
open-ended TL). Higher anti-resonances increasing from 34 → 123 Ω is plausible.

---

## Test 4 — 49:1 Realism on 40m EFHW (L = 20.44 m)

**Expected:** 40/20/15/10 inside the 49:1 zone (SWR < 2:1 after transformer);
other bands clearly outside.

49:1 zone: zRef=2450 Ω, rawSwrLimit=2.0. Za = Zc/49. Complex SWR via `swr50(Za)`.

| Band | R at 20.44m | X at 20.44m | SWR after 49:1 | In zone? | Note |
|------|-------------|-------------|----------------|---------|------|
| 40m  | 3028 Ω      | 0 Ω         | **1.24:1**     | ✓       | Fundamental λ/2 |
| 20m  | 2012 Ω      | −510 Ω      | **1.35:1**     | ✓       | Near 2nd harmonic |
| 15m  | 1535 Ω      | −578 Ω      | **1.74:1**     | ✓       | Near 3rd harmonic |
| 10m  | 1374 Ω      | +480 Ω      | **1.88:1**     | ✓       | Near 4th harmonic (borderline) |
| 30m  | 80 Ω        | +61 Ω       | **30.7:1**     | ✗       | Near 3λ/4 anti-resonance |
| 17m  | 107 Ω       | −45 Ω       | **26.3:1**     | ✗       | Near 5λ/4 anti-resonance |

20/15/10 show residual reactance because the 40m wire is not exactly at an integer
harmonic for those frequencies (40m/20m/15m/10m ratio ≈ 1:1.982:2.968:4.035, not
perfectly 1:2:3:4).

10m is borderline at SWR 1.88:1. Real-world 10m on a 40m EFHW can be fussier
depending on installation — this result is slightly optimistic but within educational
tolerance.

**Verdict: Believable.**
The 40-10m harmonic family all land inside the 49:1 zone; 30m and 17m are correctly
excluded by wide margins. The pattern matches published behavior of real 40m EFHWs.

---

## Summary

| Test | Result | Verdict |
|------|--------|---------|
| T1 — λ/2 resonance (80/40/20m) | R ≈ 3028 Ω, X = 0 at resonance | **Believable** |
| T2 — λ/4 anti-resonance | R ≈ 34 Ω, X = 0, 90:1 contrast | **Believable** |
| T3 — Harmonic families on 40m | Distinct high-Z/low-Z families, not identical | **Believable** |
| T4 — 49:1 on 40m EFHW (40/20/15/10) | All four inside zone; 30m/17m excluded | **Believable** |

**Overall:** The End Fed model is internally consistent and physically credible for
an educational tool. The lossy open-circuit TL formula, frequency-scaled α, and
harmonic-order correction work together coherently.

### Known simplifications (by design, not defects)
- All bands show identical λ/2 peak R (≈3028 Ω) — real wires vary somewhat band to band.
- Anti-resonance floor is calibrated to ~34 Ω; real wires range 20–60 Ω depending on height and ground.
- Harmonic correction lifts higher resonance peaks; without it 10m on a 40m wire would fall outside the 49:1 zone.
- 10m result (SWR 1.88:1) is optimistic at the edge — real installations often need a tuner nudge on 10m.
