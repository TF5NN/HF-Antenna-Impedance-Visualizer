# v3.0.0 Model Check Against NEC-2

**Tool:** `antenna_impedance.html` · **Version:** v3.0.0 · **Date:** 2026-11-10

This report compares the tool's antenna model with NEC-2 and checks the tuner
solver by rebuilding its circuits. It supersedes the antenna-model parts of the
v2.6.0 reports in this folder (`endfed_validation.md`, `dipole_validation.md`,
`counterpoise_validation.md`), which describe the old model.

## How to reproduce

```
pip install PyNEC numpy
python3 validation/nec_reference.py     # writes validation/data/nec_reference.json
npm i playwright
node validation/check_v3.mjs            # runs the page's own code against that data
```

`check_v3.mjs` loads `antenna_impedance.html` in a browser and calls the same
functions the page uses (`calcZwireComplex`, `calcDipoleZ`, `calcZcomplex`,
`solveL`), so it tests the shipped code, not a copy of it.

## Reference cases

All NEC cases use straight, lossless, 1 mm diameter bare wire on 40, 20, 15 and
10 m (7.15, 14.175, 21.225, 28.85 MHz). The tool is run with velocity factor
1.00 to match bare wire.

| Case | NEC geometry | Sweep | Points |
|------|--------------|-------|--------|
| End-fed, ideal return | wire on a perfect ground, fed at the base | length 1.3–26.2 m | 1 000 |
| Off-centre-fed | free-space wire, 20.2 m and 40.9 m | feed position 3–50 % | 384 |
| End-fed with counterpoise | free-space wire + 2.1 m or 5.0 m counterpoise, fed at the junction | wire length 2.0–26.2 m | 976 |

Two measures are reported:

- **RMS error in |Z|** — the typical ratio between model and NEC, as a percentage.
- **Zone agreement** — of all the points where *either* the model or NEC says
  "SWR < 2 through this transformer", the share where *both* say so. It is a
  strict measure: a matching window that is the right width but shifted by half
  its width scores about 33 %.

## Results

| Case | v2.6.0 error | v2.6.0 zones | v3.0.0 error | v3.0.0 zones |
|------|-------------:|-------------:|-------------:|-------------:|
| End-fed, ideal return | 36 % | 45 % | **3.9 %** | **95 %** |
| Off-centre-fed | 144 % | 3 % | **12.4 %** | **85 %** |
| End-fed with counterpoise | 22 % | 76 % | **10.5 %** | 75 % |

v2.6.0 figures are with its default velocity factor of 0.975. Setting v2.6.0 to
1.00 gives 24 % / 53 %, 145 % / 3 % and 29 % / 39 %.

The counterpoise case halves its |Z| error but its zone agreement does not
improve. The remaining error there is mostly in where the half-wave peaks sit:
NEC puts them about 0.2 m shorter than the model when the counterpoise is short.

### End-fed wire on 10 m: peaks and dips

Half-wave (high-impedance) points, as length → resistance:

| n × λ/2 | NEC | v2.6.0 | v3.0.0 |
|--------:|-----|--------|--------|
| 1 | 5.1 m → 2 569 Ω | 5.1 m → 2 951 Ω | 5.1 m → 2 550 Ω |
| 2 | 10.3 m → 2 054 Ω | 10.1 m → 2 136 Ω | 10.3 m → 1 963 Ω |
| 3 | 15.5 m → 1 842 Ω | 15.2 m → 1 769 Ω | 15.5 m → 1 726 Ω |
| 4 | 20.7 m → 1 720 Ω | 20.3 m → 1 533 Ω | 20.7 m → 1 589 Ω |
| 5 | 25.9 m → 1 637 Ω | 25.3 m → 1 387 Ω | 25.9 m → 1 497 Ω |

Quarter-wave-type (low-impedance) points:

| odd × λ/4 | NEC | v2.6.0 | v3.0.0 |
|----------:|-----|--------|--------|
| 1 | 2.5 m → 35 Ω | 2.5 m → 33 Ω | 2.5 m → 36 Ω |
| 3 | 7.7 m → 53 Ω | 7.6 m → 82 Ω | 7.7 m → 52 Ω |
| 5 | 12.9 m → 61 Ω | 12.7 m → 105 Ω | 12.9 m → 60 Ω |
| 7 | 18.1 m → 67 Ω | 17.7 m → 123 Ω | 18.1 m → 65 Ω |
| 9 | 23.3 m → 71 Ω | 22.8 m → 139 Ω | 23.3 m → 69 Ω |

The length sweep has 0.1 m steps, so lengths are rounded to that.

### Off-centre feed on the fundamental (20.2 m wire, 7.15 MHz)

| Feed position | NEC | v2.6.0 | v3.0.0 |
|--------------:|-----|--------|--------|
| 50 % | 70 − j21 Ω | 64 − j5 Ω | 72 − j12 Ω |
| 40 % | 76 − j23 Ω | 189 − j28 Ω | 79 − j14 Ω |
| 34 % | 88 − j28 Ω | 369 − j56 Ω | 91 − j18 Ω |
| 25 % | 130 − j45 Ω | 728 − j92 Ω | 134 − j33 Ω |
| 15 % | 278 − j126 Ω | 1 136 − j79 Ω | 282 − j103 Ω |

## What changed in the model

1. **Arms in series.** A dipole, an off-centre-fed wire and a wire with a
   counterpoise are two conductors with the generator between them, so their
   impedances add. v2.6.0 combined the dipole arms in parallel.
2. **Loss equals radiation.** The line-loss term is set from the induced-EMF
   radiation resistance of the standing-wave current instead of a constant
   tuned to give 3 000 Ω, with a `1/√n` rule for harmonics. For two arms the
   coupling between them is included.
3. **End effect is a fixed length.** An open end adds about 1.5 % of a
   half-wave of electrical length. v2.6.0 folded this into the velocity factor,
   which stretched every harmonic by the same percentage and put the higher
   half-wave points too short (0.6 m at the fifth half-wave on 10 m).
4. **Z₀ follows the wire.** `Z₀ = 60·ln(0.22·λ/a)` replaces the fixed 450 Ω.

The two constants that were chosen by comparison with NEC are the `0.22` in Z₀
and the `0.015` end effect. Both were fitted on the end-fed case only; the
off-centre and counterpoise cases use them unchanged.

## Internal cross-check

The radiation resistance is computed two independent ways in the code: a closed
form using sine and cosine integrals (single wire against ground) and a
numerical far-field power integral (two arms). For a symmetric pair they must
agree, and they do to five significant figures at every length tried
(0.3 to 60 rad), for example 36.565 Ω at λ/4 and 99.544 Ω at λ/2.

## Tuner solver

Each solution returned by `solveL` was rebuilt from ideal parts and the
impedance seen by the radio calculated independently: 6 frequencies × 14
resistances × 9 reactances × 4 component-limit sets.

| | v2.6.0 | v3.0.0 |
|---|---:|---:|
| Solutions returned | — | 2 637 |
| Rebuilt circuit not 50 Ω (SWR > 1.02) | 137 of 171 series→shunt solutions on a smaller grid | **0** |
| Solutions exceeding the L or C limit | — | 0 |

v2.6.0 had the wrong sign on the shunt element of the series→shunt topology.
Example: a 25 Ω load at 7.15 MHz returned two inductors and claimed 1:1; the
rebuilt circuit presents 10 + j20 Ω, SWR 5.8:1. The shunt→series topology was
correct.

Delivered power after a successful match, 200 Ω load on a direct feed:
v2.6.0 reported 63 % (it kept the 64 % mismatch factor of the unmatched load);
v3.0.0 reports 98.6 %, which is the tuner's own loss with inductor Q = 120.

## What this does not cover

- Real ground, height above ground, sloping or bent wires, nearby objects.
- Insulated wire (the velocity-factor slider is not checked against NEC here).
- Wire diameters other than 1 mm.
- Bands other than 40, 20, 15 and 10 m.
- The transformer itself (stray capacitance, leakage, core loss).
- Measurements on a real antenna.

The comparison shows the model follows NEC for the idealised geometries above.
It is not a prediction for a particular installation.
