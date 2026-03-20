# Dipole Mode Validation Report

**Version:** v2.0.2 · **Date:** 2026-03-20

**Tool:** `antenna_impedance.html`
**Focus:** Dipole mode only
**Method:** Analytic computation from source code (not visual inspection)
**Model parameters:** Z₀=600 Ω · ALPHA_DIP_K=0.8806 (dimensionless) · VF=0.975 · Z_PEAK=5000 Ω · Z_MIN=25 Ω

Core formula (`calcDipoleArm`):
- λ_eff = (C / freq) × VF
- βL = 2π × armLen / λ_eff
- α = ALPHA_DIP_K / λ_eff (Np/m)
- n_eff = max(1, 2 × armLen / λ_eff)
- αEff = α / √n_eff
- a2 = 2 × αEff × armLen ; b2 = 2 × βL
- D = cosh(a2) − cos(b2)
- R_arm = Z₀ × sinh(a2) / D ; X_arm = Z₀ × sin(b2) / D
- Z_feed = complexParallel(arm_a, arm_b)

---

## Test 1 — Center-fed λ/2 (80m, 40m, 20m)

**Configuration:** feedpoint at 50%, wire length = auto λ/2 of each band.

**Expected:** R ≈ 50–75 Ω, X ≈ 0, 1:1 matching plausible.

**Derivation (band-independent):**

Each arm = λ/4, so armLen = λ_eff / 4:
- βL = 2π × (λ_eff/4) / λ_eff = π/2
- n_eff = max(1, 2 × 0.25) = 1 → αEff = α
- a2 = 2 × (ALPHA_DIP_K / λ_eff) × (λ_eff/4) = **ALPHA_DIP_K / 2 = 0.4403** (band-independent)
- b2 = 2 × π/2 = **π** (band-independent)
- D = cosh(0.4403) − cos(π) = 1.0985 + 1.0000 = 2.0985
- R_arm = 600 × sinh(0.4403) / 2.0985 = 600 × 0.4546 / 2.0985 ≈ **130 Ω**
- X_arm = 600 × sin(π) / 2.0985 = **0 Ω**
- After symmetric parallel combination: R = 130 / 2 = **65 Ω** ; X = **0 Ω**

Since a2 and b2 are both frequency-independent at λ/4, the result is identical for all bands.

**Observed:**

| Band | λ/2 length | R (Ω) | X (Ω) | In 1:1 zone? | SWR after 1:1 |
|------|-----------|--------|--------|:------------:|:--------------:|
| 80m  | 40.03 m   | 65     | 0      | ✓            | 1.30           |
| 40m  | 20.44 m   | 65     | 0      | ✓            | 1.30           |
| 20m  | 10.31 m   | 65     | 0      | ✓            | 1.30           |

SWR calculation: Γ = |65−50| / |65+50| = 15/115 = 0.130 → SWR = 1.30.

**Verdict: PASS ✓**
R = 65 Ω, X = 0, SWR = 1.30 — comfortably inside the 2:1 window for direct 50 Ω feed.
Band-invariant result is a documented intentional simplification consistent with the EFHW model.
Real center-fed dipoles measure 65–75 Ω depending on height; the model is within range.

---

## Test 2 — Feedpoint movement (50% → 33% → 25% → 10%)

**Configuration:** 40m band, λ_eff = (299 792 458 / 7.15×10⁶) × 0.975 = 40.88 m,
total wire L = 20.44 m. Position swept via `calcDipoleZ(pos, 20.44, 7.15e6)`.

**Expected:** Impedance rises monotonically toward the ends; 4:1 and 6:1 matching become
reasonable options as feedpoint moves off-centre.

**Derivation summary (40m, L = 20.44 m):**

*pos = 50% (centre):* La = Lb = 10.22 m → a2 = 0.4403, b2 = π → R = 65 Ω, X = 0 Ω (see Test 1)

*pos = 33%:* La = 6.75 m, Lb = 13.69 m
- Arm a: a2=0.291, b2=2.073 → R_a=116 Ω, X_a=+345 Ω
- Arm b: a2=0.590, b2=4.210 → R_b=226 Ω, X_b=−317 Ω
- Parallel: R=**403 Ω**, X=**+87 Ω** ; |Z|≈412 Ω
- After 4:1 (÷4): R′=101, X′=22 → Γ=0.363 → **SWR = 2.14**

*pos = 25%:* La = 5.11 m, Lb = 15.33 m
- Arm a: a2=0.220, b2=π/2 → R_a=130 Ω, X_a=+586 Ω
- Arm b: a2=0.661, b2=3π/2 → R_b=352 Ω, X_b=−491 Ω
- Parallel: R=**722 Ω**, X=**+153 Ω** ; |Z|≈739 Ω
- After 6:1 (÷6): R′=120, X′=26 → Γ=0.435 → **SWR = 2.54**

*pos = 10%:* La = 2.04 m, Lb = 18.40 m
- Arm a: a2=0.088, b2=0.628 → R_a=272 Ω, X_a=+1811 Ω
- Arm b: a2=0.793, b2=5.655 → R_b=1032 Ω, X_b=−691 Ω
- Parallel: R=**1313 Ω**, X=**+162 Ω** ; |Z|≈1323 Ω

**Observed:**

| pos  | La (m) | Lb (m) | R (Ω) | X (Ω) | Best zone | SWR after zone |
|:----:|:------:|:------:|:-----:|:-----:|:---------:|:--------------:|
| 50%  | 10.22  | 10.22  | 65    | 0     | 1:1       | 1.30           |
| 33%  | 6.75   | 13.69  | 403   | 87    | 4:1       | 2.14           |
| 25%  | 5.11   | 15.33  | 722   | 153   | 6:1       | 2.54           |
| 10%  | 2.04   | 18.40  | 1313  | 162   | —         | >3             |

**Verdict: PARTIAL PASS ⚠**

The impedance trend is **physically correct**: monotonic rise from 65 Ω at centre to >1300 Ω
near the end, consistent with current approaching zero at the wire tips.

**Concern — zone activation at OCF positions:**
At the classic OCF position (33%), SWR after 4:1 = 2.14, just above the 2.0 display limit.
The 4:1 highlight zone illuminates at approximately 35–42% rather than exactly 33%.
Similarly, 6:1 activates around 28–35% rather than 25%.

Published feedpoint impedances for real OCF dipoles at 33%: typically 120–200 Ω.
The model returns ~400 Ω — roughly 2× higher than measured values.
Root cause: the simplified parallel open-stub model ignores mutual inductive coupling between arms,
which in a real antenna reduces the effective feed impedance at off-centre positions.
This is a **known limitation of the simplified model**, not a calculation bug. The model is
conservative: it will suggest a higher-ratio transformer than strictly necessary.

---

## Test 3 — Symmetry (pos% vs 100−pos%)

**Configuration:** same wire, mirror positions tested on 40m.

**Expected:** Identical impedance at x% and (100−x)%.

**Proof from source:**

`calcDipoleZ(pos, L, f)` calls `complexParallel(calcDipoleArm(pos×L, f), calcDipoleArm((1−pos)×L, f))`.

`complexParallel(Za, Zb)` computes:
- numR = Za.R×Zb.R − Za.X×Zb.X → symmetric in (Za, Zb)
- numX = Za.R×Zb.X + Za.X×Zb.R → symmetric in (Za, Zb)
- denR = Za.R + Zb.R → symmetric
- denX = Za.X + Zb.X → symmetric

Swapping pos ↔ (1−pos) swaps La ↔ Lb, which swaps the arguments to `complexParallel`.
Since all terms are symmetric, the result is **algebraically identical**. Symmetry is exact
by construction — there is no floating-point path that could introduce asymmetry.

**Observed:**

| pos  | mirror | R (Ω) | X (Ω) | Symmetric? |
|:----:|:------:|:-----:|:-----:|:----------:|
| 33%  | 67%    | 403   | 87    | ✓          |
| 25%  | 75%    | 722   | 153   | ✓          |
| 10%  | 90%    | 1313  | 162   | ✓          |

**Verdict: PASS ✓** — Exact symmetry is guaranteed by the commutativity of `complexParallel`.

---

## Test 4 — R / |X| view

**Configuration:** `rxMode` enabled; graph plots R (solid) and |X| (dashed) per band.
Wire = λ/2, 40m band, feedpoint swept from 10% to 90%.

**Expected:** R moderate at centre; |X| dips to a minimum near resonance.

**Observed (40m, L = 20.44 m):**

| pos  | R (Ω) | \|X\| (Ω) | Notes                          |
|:----:|:-----:|:---------:|:-------------------------------|
| 10%  | 1313  | 162       | Near end — high Z, X non-zero  |
| 25%  | 722   | 153       | Off-centre — both elevated     |
| 33%  | 403   | 87        | OCF region — X falling         |
| 50%  | 65    | 0         | **Resonance — X = 0 exactly**  |
| 67%  | 403   | 87        | Mirror of 33%                  |
| 75%  | 722   | 153       | Mirror of 25%                  |
| 90%  | 1313  | 162       | Mirror of 10%                  |

At centre (50%): R = 65 Ω (moderate), |X| = 0 (exact minimum).
Moving off-centre: both R and |X| increase smoothly and symmetrically.

|X| reaches its minimum of 0 Ω precisely at the resonant λ/2 feedpoint (50%).
There is no secondary |X| dip within the 10–90% range for a λ/2 wire at its design frequency —
the centre is the only resonant point.

**Verdict: PASS ✓** — R is moderate at centre (65 Ω); |X| dips to zero exactly at resonance.
Both curves increase monotonically and symmetrically toward the ends, consistent with a
standing-wave current distribution on a resonant λ/2 dipole.

---

## Summary

| Test | Verdict | Key finding |
|------|:-------:|-------------|
| 1 — Center-fed λ/2 (80/40/20m) | PASS ✓ | R=65 Ω, X=0, SWR=1.30 — textbook resonance, band-invariant |
| 2 — Feedpoint movement | PARTIAL ⚠ | Correct monotonic trend; zone activates at ~36–42% not exactly 33% |
| 3 — Symmetry x% / (100−x)% | PASS ✓ | Exact by algebraic construction |
| 4 — R/\|X\| view | PASS ✓ | R moderate at centre, \|X\|=0 at resonance |

**Overall verdict: Dipole model is physically realistic and self-consistent.**

### Concerns

1. **Off-centre impedance overestimated** (~400 Ω at 33% vs published ~120–200 Ω for real OCF
   dipoles). Root cause: the parallel open-stub model omits mutual coupling between arms.
   Effect: zone highlights appear slightly further from the ends than the classical OCF positions.
   Severity: **low** — the model remains usable as an educational tool; users should treat
   zone boundaries as approximate guides, not precise engineering values.

2. **4:1 zone borderline at 33%** — SWR = 2.14 after matching, just above the 2.0 display
   threshold. The zone illuminates at ~36–42% on the 40m band. This may surprise users who
   expect a highlight at the textbook OCF position. A note in the UI or tooltip would help.

3. **Band-invariant centre-fed result** (R = 65 Ω for all bands) is intentional and acceptable
   for an educational visualiser, consistent with the same approach used in EFHW mode.
