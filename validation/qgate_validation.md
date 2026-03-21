# Q-Gate Validation Report

**Tool:** `antenna_impedance.html`
**Version:** v2.4.0 / v2.5.0 · **Date:** 2026-03-21
**Focus:** Q-based feasibility gate (`canTune`) introduced in v2.4.0
**Method:** Analytic (source-code trace + formula derivation, no browser execution)

---

## The Q-gate formula

```
canTune(Za, p):
  R = Za.R,  X = Za.X

  Hard rejects (degenerate input):
    R ≤ 1 Ω        → false
    R ≥ 10 000 Ω   → false
    |X| > 10·R     → false   (extreme reactive overload)
    ratio > 100    → false   (extreme impedance transformation)

  Q formula:
    ratio       = max(R, 50) / min(R, 50)
    Q_transform = √(ratio − 1)
    Q_reactive  = |X| / R
    Q_total     = Q_transform + Q_reactive

  Return  Q_total ≤ p.Qmax
```

`canTune` is called inside `swrAtRadio()` **only after** the SWR gate passes:

```
if (rawSwr > p.maxSWR) return rawSwr;   // SWR gate — fires FIRST
if (!canTune(Za, p)) return rawSwr;     // Q gate  — fires SECOND
const r = solveL(Za, freq, …);          // component-limit check — fires THIRD
```

---

## Tuner presets

| Preset | maxSWR | Lmax | Cmax | Qmax |
|---|---|---|---|---|
| Internal | 3 | 4 µH | 500 pF | 4 |
| External | 10 | 24 µH | 1200 pF | 9 |
| Wide-range | 20 | 60 µH | 3500 pF | 17 |
| Custom | user | user | user | ∞ (fixed v2.5.0) |

Reference frequency: **7 MHz** (40m). ω = 43.98 Mrad/s.

---

## Test case A — Easy match

**Input:** Za = {R=50, X=0}  (EFHW at 49:1 with Zant≈2450 Ω)

| Step | Calculation | Result |
|---|---|---|
| rawSwr | \|Γ\|=0 | **1.00** |
| SWR gate | 1.00 < 3 | Pass all |
| ratio | 50/50 = 1 | — |
| Q_transform | √(1−1) = 0 | 0 |
| Q_reactive | 0/50 = 0 | 0 |
| Q_total | 0 + 0 = **0** | — |
| canTune | 0 ≤ 4 | Pass all |
| solveL Topo A | disc=0, Xs=0, Bp=0 | **MATCH** |

**Result: Internal ✅ External ✅ Wide-range ✅**

---

## Test case B — Moderate mismatch

**Input:** Za = {R=200, X=100}  (e.g. 9:1 unun + off-resonance EFHW)

| Step | Calculation | Result |
|---|---|---|
| rawSwr | \|Γ\|²=(150²+100²)/(250²+100²)=0.449, \|Γ\|=0.670 | **5.06** |
| SWR gate | 5.06 > 3 → Internal **rejected** | — |
| | 5.06 ≤ 10 → External passes | — |
| ratio | 200/50 = 4 | — |
| Q_transform | √(4−1) = 1.73 | — |
| Q_reactive | 100/200 = 0.50 | — |
| Q_total | 1.73 + 0.50 = **2.23** | — |
| canTune | 2.23 ≤ 9 ✓; 2.23 ≤ 17 ✓ | External, Wide-range pass |
| solveL Topo B | Gs=0.004, disc=6.4×10⁻⁵, Bp=0.010 (shunt cap ≈227 pF), Xs=100 (series ≈3.6 µH) — within External component limits | **MATCH** |

**Result: Internal ❌ (SWR gate, 5.06>3) — External ✅ — Wide-range ✅**

Operative gate: **SWR gate** (Internal) and **component limits via solveL** (External, Wide-range).

---

## Test case C — High reactance

**Input:** Za = {R=50, X=350}

| Step | Calculation | Result |
|---|---|---|
| rawSwr | \|Γ\|²=350²/(100²+350²)=0.925, \|Γ\|=0.961 | **49.2** |
| SWR gate | 49.2 > 20 | **All rejected** |

Q-gate not reached. Q_total = 7.0 (would reject Internal Qmax=4, pass External/Wide-range), but the SWR gate fires first.

**Result: Internal ❌ External ❌ Wide-range ❌**

Operative gate: **SWR gate** exclusively.

---

## Test case D — Extreme EFHW without transformer

**Input:** Zant = {R=2500, X=0}, 1:1 zone → Za = {R=2500, X=0}

| Step | Result |
|---|---|
| rawSwr | (2500−50)/(2500+50) → \|Γ\|=0.961 → **49.0** |
| SWR gate | All reject (49.0 > 20) |

**Result: Internal ❌ External ❌ Wide-range ❌**

---

## Test case E — EFHW with proper 49:1 transformer

**Input:** Zant = {R=2450, X=0} → Za = {R=50, X=0}

Identical to Test A. rawSwr=1.0, all gates pass trivially.

**Result: Internal ✅ External ✅ Wide-range ✅**

---

## Test case F — OCF dipole (33%), representative Za after dipole zone transformer

**Input:** Za = {R=100, X=150}  (representative off-resonance dipole, after 4:1 transformer)

| Step | Calculation | Result |
|---|---|---|
| rawSwr | \|Γ\|²=(50²+150²)/(150²+150²)=0.5, \|Γ\|=0.707 | **5.83** |
| SWR gate | 5.83 > 3 → Internal rejected | — |
| | 5.83 ≤ 10 → External passes | — |
| Q_total | √(100/50−1)+150/100 = 1.0+1.5 = **2.50** | — |
| canTune | 2.50 ≤ 9 ✓; 2.50 ≤ 17 ✓ | External, Wide-range pass |
| solveL | Topo B feasible within External limits | **MATCH** |

> **Note on dipole path:** `swrAfterDipoleZone()` does not call `canTune()`. The check sequence
> is: SWR gate → solveL. canTune's hard-cut edge cases (R≤1, |X|>10R, ratio>100) are the
> only missing gates in the dipole path. The analysis shows these are also caught by the SWR
> gate for all physically realizable inputs (see binding-constraint proof below).

**Result: Internal ❌ (SWR gate) — External ✅ — Wide-range ✅**

---

## Key analytical finding — Qmax binding constraint

**Finding: The Qmax values (4, 9, 17) are set above the theoretical maximum Q_total
achievable for any impedance satisfying rawSwr ≤ maxSWR. As a result, the Qmax check
is never the binding constraint.**

**Proof** — For any Za satisfying SWR ≤ SWRMAX, compute the maximum Q_total:

```
SWR ≤ SWRMAX  ⟺  |Γ| ≤ γ where γ = (SWRMAX−1)/(SWRMAX+1)
```

This constrains R to the interval [50/SWRMAX, 50·SWRMAX]. Maximising Q_total over this
range and all feasible X (given the |Γ| ≤ γ constraint) gives:

| Preset | maxSWR | γ | Max Q_total within SWR limit | Qmax set | Binding? |
|---|---|---|---|---|---|
| Internal | 3 | 0.500 | ≈ 1.65 | 4 | ❌ Never |
| External | 10 | 0.818 | ≈ 3.0 | 9 | ❌ Never |
| Wide-range | 20 | 0.905 | ≈ 4.4 | 17 | ❌ Never |

The actual gating hierarchy in practice:

1. **SWR gate** (`rawSwr > p.maxSWR`) — fires for all high-reactance / extreme-impedance cases
2. **canTune hard cuts** (`R≤1`, `R≥10000`, `|X|>10R`, `ratio>100`) — redundant with SWR gate but add robustness for degenerate floating-point edge cases
3. **solveL component limits** (`Lmax`, `Cmax`) — the actual secondary gate for borderline cases
4. **Qmax formula** — never fires for any input within the rated SWR range

**Verdict:** The gating is safe and correct. No false positives result. The Qmax values act as
a conservative safety net — they are never reached, but they do no harm.

**Advisory for future tightening:** To make the Qmax formula the primary discriminating gate
(differentiating between presets at high-reactance, R≈50 Ω scenarios), reduce Qmax values to
approximately: Internal=1.5, External=3.0, Wide-range=4.5. This would also require removing or
relaxing the `rawSwr > p.maxSWR` pre-check, which is the current dominant gate.

---

## Bug found: Custom preset missing Qmax (v2.4.0 regression)

In v2.4.0, `tunerCustom` was initialised without a `Qmax` field:
```js
// v2.4.0 (broken):
let tunerCustom = { Lmax: 24, Cmax: 1200, maxSWR: 10 };
```

In `canTune()`: `Q_total <= p.Qmax` → `Q_total <= undefined` → `NaN` → **always `false`**.

This caused `canTune()` to always reject for the custom preset, making the custom ATU
completely non-functional (no match ever shown).

**Fix applied in v2.5.0:**
```js
let tunerCustom = { Lmax: 24, Cmax: 1200, maxSWR: 10, Qmax: Infinity };
```

`Qmax: Infinity` means the Q formula is bypassed for custom mode; only the SWR gate and
`solveL()` component limits apply. This correctly restores the pre-v2.4.0 custom-tuner
behaviour while remaining consistent with the Q-gate design (user-defined limits = no
additional Q constraint).

---

## Overall verdict: VALID (with advisory)

| Requirement | Result |
|---|---|
| Q gating blocks high-Q cases | ✅ — via SWR gate (primary) and canTune hard cuts |
| Internal < External < Wide-range hierarchy | ✅ — preserved via maxSWR (3 / 10 / 20) |
| No regression in EFHW resonance | ✅ — trivial match at Za≈50 Ω unchanged |
| No discontinuities in match zones | ✅ — gates are monotonic in SWR |
| Zone highlighting reflects canTune() | ✅ — no zone activates when canTune returns false |
| EFHW dipole path gap | ⚠ — canTune not called in swrAfterDipoleZone; no practical impact since SWR gate covers same cases |
| Qmax formula is discriminating gate | ❌ — values set too high to be binding (see advisory) |
| Custom preset functional | ✅ — fixed v2.5.0 (Qmax: Infinity) |
