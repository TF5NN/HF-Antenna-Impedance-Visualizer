# Changelog

All notable changes to **HF End-Fed Antenna Impedance — Visual Tool**.
Creator and rights holder: **Gunnar B. Guðlaugsson (TF5NN)**.

---

## [Unreleased]

### Changed
- **Disabled loading coil feature** (code preserved but commented out)
  - Reason: The current transmission-line-based model is not valid for electrically short, loaded antennas
  - Prevents misleading results when users attempt to model whip antennas with loading coils
  - Loading coil support may return in a future dedicated tool using a lumped-element model

---

## [v1.14] — 2026-03-07

### Added
- **Advanced / Experimental collapsible section** — the Feedpoint Loading Coil controls are
  now hidden inside a collapsible "Advanced / Experimental" ctrl-group, keeping the main
  control bar uncluttered. Click the button to reveal the coil controls; they retain full
  function as before.

- **Inspect panel** — a persistent data panel now appears above the graph whenever a pin
  (inspect length) is set. Shows per-band: impedance magnitude, complex R±jX, half-wave
  fraction (n×λ/2), matched zone(s) with full loss breakdown (mismatch / transformer /
  tuner / coil efficiencies and total % delivered). Updates automatically on every state
  change (tuner preset, coil, counterpoise, etc.). Panel hides when the pin is cleared.

- **R/X view mode** — new "R/X view" toggle button in the X-range control bar. When active,
  each band is drawn as two curves on the same log-Y axis: R (solid, band colour) and |X|
  (dashed, same colour). Y-axis label changes to "R or |X| (Ω)"; a small legend "— R  ╌╌ |X|"
  appears inside the plot. Pin dots track the R curve in this mode. Toggle again to restore
  the standard |Z| view.

### Changed
- **Wider numeric inputs** — `#cpLengthInput` widened 56 → 72 px; `#ssMinInput` 40 → 56 px;
  `#ssSWRInput` 44 → 60 px. Numbers no longer truncate in the fields at typical browser zoom.

---

## [v1.13] — 2026-03-06

### Added
- **Feedpoint Loading Coil** — new optional series inductor (0–50 µH, step 0.1) placed at
  the feedpoint before the transformer. Controlled via a new "Feedpoint Loading Coil"
  control group (zone-btn toggle + slider + synced numeric input).

  Physics: `XL = 2πfL` added to feedpoint reactance; `Rs = XL / Q` (Q = 150) added to
  resistance. The modified feedpoint impedance propagates through the full matching chain —
  impedance curves shift, resonances move to longer wire lengths, zone overlaps change.

  Loss model: `η_coil = R_ant / (R_ant + Rs)` where R_ant is the wire-plus-counterpoise
  resistance before the coil. Folds into total delivered-power efficiency alongside
  mismatch, transformer, and tuner efficiencies.

  Tooltip shows "Loading coil: X.X µH &nbsp; X_L=+jXXX Ω &nbsp; coil eff ≈ XX%" per band.
  Dashed ghost curve (when counterpoise is active) is unaffected — always shows wire-only.

- **New constant** `COIL_Q = 150` — standalone wound coil Q, slightly higher than
  the ATU toroid `TUNER_L_Q = 120`.

- **In-tool model notes** — new "Feedpoint loading coil" block in the `<details>` panel
  explaining XL, Rs, Q=150 rationale, η_coil formula, and ghost curve behaviour.

---

## [v1.12] — 2026-03-04

### Changed
- **Stress-aware tuner efficiency model** — `estimateTunerEff()` now accounts for
  L-network circulating current. An L-match matching `R_load` to 50 Ω has loaded Q:
  `Q_match = √(max(R_load, 50) / min(R_load, 50) − 1)`.
  Circulating current stress factor `kI² = 1 + Q²` (= impedance mismatch ratio) scales
  the effective inductor loss resistance: `Rs_eff = Rs₀ × kI²`.
  Result: easy matches (near 50 Ω) barely change; hard matches (high impedance ratio)
  now show noticeably lower tuner efficiency (often 50–75% instead of 90–95%).

### Added
- **Tooltip Q display** — the tuner note line now shows "Q≈X.Y" alongside "tuner eff xx%",
  giving users a quick sense of how hard the L-network is working.

### Documentation
- In-tool model notes: ATU efficiency paragraph updated to describe the stress-aware model.

---

## [v1.11] — 2026-03-04

### Changed
- **X-range Start (left) selector** — options changed from ¼ λ to **⅛ λ** of
  highest / lowest active band; default remains ⅛ λ of highest band. The shorter
  default start exposes the first matching windows on higher bands without
  wasting canvas on near-zero-length wires.

### Documentation
- **In-tool model notes** (`<details>` panel) fully rewritten to reflect the
  current implementation:
  - Block 1 ("Why graph starts at…") updated to explain the configurable X-range
    selectors and the new ⅛ λ default.
  - Z₀ heading corrected from **550 Ω** to **450 Ω** (the actual code constant).
  - Physics model block extended with the **harmonic-order attenuation correction**
    (`α_eff = α / √n_eff`) paragraph.
  - Efficiency block restructured: now documents the three-factor
    `η_total = η_mismatch × η_transformer × η_tuner` formula; stale flat-rate
    "~13% loss" figure for the 9:1 zone replaced with the inductor-Q model
    description.
  - New **ATU L-network solver** block summarising topology search, component
    display, and all three presets with their Lmax/Cmax/maxSWR values.
  - Zone range block updated: 9:1 Unun now described as **dynamic**
    (225–900 Ω without tuner, expands with ATU preset); 49:1 Unun band
    description updated to reflect dynamic maxSWR behaviour.

---

## [v1.10] — 2026-03-04

### Changed
- **X-range end selector** — simplified to a single preset: **1.25× λ/2 of
  lowest band** (replaces the previous 0.75× and 1× options). The default
  right edge now shows the resonance peak plus a comfortable tail past it
  (~26 m for a 40 m-lowest configuration). "Set distance…" option retained.

### Documentation
- **CHANGELOG.md** updated to cover all versions from v1.03 onwards.
- **README.md** — Model Notes section replaced with a full technical writeup:
  antenna impedance formula, SWR / reflection-coefficient math, transformer
  efficiency decisions, ATU L-network matching and inductor-Q loss model,
  counterpoise series-stub model, and a dedicated note explaining why the
  9:1 Unun struggles to find matches without a counterpoise.

---

## [v1.09] — 2026-03-04

### Changed
- **Internal ATU preset** corrected to **3:1** (maxSWR 4 → 3); label and
  info-bar text updated accordingly.

### Added
- **X-axis range selectors** below the graph canvas:
  - *Start (left):* ¼ λ highest band (default) · ¼ λ lowest band · Set distance
  - *End (right):* 1× λ/2 lowest band (default) · 0.75× λ/2 · Set distance
  - Selecting "Set distance…" reveals a live numeric metre input.
- **Inductor-Q ATU loss estimate** (v1 spec):
  - Constant `TUNER_L_Q = 120` (typical small toroidal ATU coil Q).
  - Helper `estimateTunerEff(freq, L_µH, R_load)`:
    `Rs = 2πf·L/Q`, `η = R_load / (R_load + Rs)`, clamped to [0.30, 0.98].
  - Tooltip topology line now appends **"tuner eff xx %"**.
  - The `~xx%` delivered-power figure multiplies transformer efficiency by
    tuner efficiency (tooltip display only — matching logic unchanged).

---

## [v1.08] — 2026-03-04

### Changed
- **Zone overlay bands are now dynamic** — they grow or shrink based on the
  current tuner state and selected preset rather than using fixed `zMin`/`zMax`
  values:
  - Tuner **off**: band = `[zRef / rawSwrLimit … zRef × rawSwrLimit]`
    (e.g. 9:1 Unun: 225 – 900 Ω, the natural transformer window).
  - Tuner **on**: band = `[zRef / maxSWR … zRef × maxSWR]` per preset
    (internal 3:1 → 150–1350 Ω; external 10:1 → 45–4500 Ω; wide-range
    20:1 → ~23–5000 Ω for the 9:1 zone).
  - Band range label to the right of the plot updates in real time.
- Static `zMin` / `zMax` properties removed from all zone definitions
  (values now computed on every draw).

---

## [v1.07] — 2026-03-03

### Changed
- **Internal ATU maxSWR gate** raised from 3 to 4, allowing the analytic
  L-network solver to attempt a match for impedances that fall in the
  3:1 – 4:1 SWR range at the transformer output (e.g. higher-order
  harmonics through the 49:1 zone). *(Later revised to 3:1 in v1.09.)*

---

## [v1.06] — 2026-03-03

### Changed
- **Harmonic-order attenuation correction** in `calcZwireComplex`:
  `α_eff = α / √n_eff` where `n_eff = max(1, 2L / λ_eff)`.
  - At the fundamental λ/2 resonance (`n_eff = 1`): α unchanged — the
    cross-band calibration (`R_peak ≈ 3 000 Ω`) is preserved.
  - At the 2λ resonance (`n_eff = 4`, e.g. 10 m on a 40 m wire): α halved
    → `R_peak` approximately doubles from ~750 Ω to ~1 500 Ω, matching
    real-world EFHW behaviour more closely.

---

## [v1.05] — 2026-03-03

### Added
- **Uniform SWR≤ threshold input** in the Sweet Spots panel — a small
  numeric field lets the user set the per-band SWR limit used to count zone
  hits (default 2.0). Previously the per-zone `swrLimit` was used directly.

### Changed
- **Sweet Spots min-bands** auto-default reverted to `n` (all active bands)
  from the earlier `ceil(n/2)` value; the input label updated to match.
- Sweet Spots hit test now runs the full `swrAtRadio()` pipeline (transformer
  ratio + optional ATU) so the star columns respond correctly to tuner toggle.

---

## [v1.04] — 2026-03-03

### Added
- **Antenna Tuner** control group with three presets:
  - *Internal (4:1)* — Lmax 4 µH, Cmax 500 pF.
  - *External (10:1)* — Lmax 24 µH, Cmax 1 200 pF.
  - *Wide-range (20:1)* — Lmax 60 µH, Cmax 3 500 pF.
  - *Custom* — user-editable Lmax, Cmax, and maxSWR fields.
- **Analytic L-network solver** (`solveL`) — attempts series→shunt and
  shunt→series topologies; returns exact L and C values or `matched: false`
  when no feasible solution exists within the preset component limits.
- **Tooltip tuner note** — when a match is found, the tooltip shows the
  L-network topology, inductance (µH), and capacitance (pF).
- **Per-zone SWR threshold split** — `rawSwrLimit` (no tuner) vs `swrLimit`
  (with tuner) so that enabling the ATU visibly widens the 49:1 strip from
  SWR < 2 to SWR < 3 at the radio.

---

## [v1.03] — 2026-03-02

### Fixed
- Rebuilt zone buttons HTML (`z0`, `z1`, `z2`) and the Antenna Tuner
  control-group HTML that had failed to persist in the previous session.
  `setupTuner()` was crashing on `null` DOM references at page load.

### Changed
- **9:1 Unun** zone split into a no-tuner-required configuration with a
  tighter SWR limit, retaining the wider band for tuner-assisted operation.
- Zone `ZONES` array updated: added `rawSwrLimit`, `swrLimit`, `zRef`,
  and `xfrmrEff` fields; removed dead `tunerLimit` field.

---

## [v1.02] — 2026-03-02

### Added
- **ITU Region 1 allocation width toggle** — "ITU R1 alloc. width" button in
  the HF Bands panel scales each band's impedance curve thickness
  proportionally to its ITU Region 1 amateur allocation bandwidth (logarithmic
  scale, 1 – 4 px). Narrow allocations (60 m = 15 kHz) draw thin lines; wide
  allocations (6 m = 2000 kHz, 10 m = 1700 kHz) draw thick lines. Gives a
  quick visual sense of operating flexibility at any wire length. Ghost curves
  (counterpoise mode) and resonance tick marks scale proportionally.
- **README.md** — project description, full feature list, usage instructions,
  impedance model notes, and licence section with CC BY 4.0 badge.
- **LICENSE** — Creative Commons Attribution 4.0 International. Share, adapt,
  and build upon this work freely; credit Gunnar B. Guðlaugsson (TF5NN) as the original creator.
- **Meta and Open Graph tags** in `<head>` — `<meta name="description">`,
  `<meta name="author">`, `og:title`, `og:description`, and `og:type` for
  proper social sharing link previews.

### Fixed
- Corrected stale code comment in `syncSweetSpotsMin`: previously said
  "at least half the active bands (min 2)"; now correctly states the 1:1
  ratio behaviour implemented in v1.01.

---

## [v1.01] — 2026-03-01

### Added
- **Sweet Spots results table** — when Sweet Spots is active, a panel below
  the graph lists every highlighted wire-length segment: centre length, full
  range, and which bands land in which matching zone (with efficiency %).
- **Draggable inspect pin** — click anywhere on the graph to place a
  persistent vertical marker at a specific wire length. Drag it to move it.
  The new *Inspect length* input in the controls syncs bidirectionally with the
  pin; the × button clears it. Cursor changes to `ew-resize` when hovering
  near the pin to signal draggability.
- **All / None band-select shortcuts** — two small links below the band
  toggles select or clear all bands in one click.
- **Version label and Gunnar B. Guðlaugsson (TF5NN) © credit** in the page header.

### Changed
- Sweet-spot *min bands* input now auto-defaults to the number of currently
  active bands (1:1 ratio) whenever the band selection changes. Minimum
  allowed value lowered to 1 (highlights matching zones for any single band).
- Sweet Spots notes: updated stale "default 2" description to reflect the
  dynamic auto-default behaviour.
- Counterpoise model notes: added explicit callout that the series-stub
  approximation is least accurate at **λ/4 lengths** (1:1 Unun zone) — where
  `cot(βL_wire) ≈ 0` and ground-plane physics dominate — and should not be
  relied on there.

### Fixed / Performance
- Sweet spot scan (800 × N `calcZ` calls) is now **cached** in
  `sweetSpotsCache` and recomputed only when state actually changes (band
  toggle, zone toggle, VF, counterpoise). Previously re-ran on every
  `mousemove` and `draw()` call.
- `anyZoneHit` check in the tooltip no longer performs a redundant second
  pass with fresh `calcZ` calls; reuses `zoneMatches` data from the existing
  band loop.
- Double `draw()` in `onMove()` early-exit path suppressed when the cursor
  was already outside the plot area.
- Removed duplicate `#versionLabel` CSS block introduced by linter.

### Code quality
- Extracted `formatLength(L)` helper (was copy-pasted in three places).
- Extracted `calcSWR(Z, Zref)` helper.
- Added `SWEET_SPOT_SCAN_POINTS = 800` named constant.
- Extracted `setupSweetSpots()` from `buildZoneButtons()`; mirrors
  `setupCounterpoise()` pattern.
- Consolidated duplicate `.cp-len-wrap` / `.ss-min-wrap` CSS into shared
  `.toggle-sub` class.

---

## [v1.0] — 2026-02-28

Initial public release.

- Impedance vs. wire length visualisation for all HF bands (160 m – 6 m).
- Three togglable matching zones: **49:1 Unun**, **9:1 + Tuner**, **1:1 Unun**.
- Hover tooltip with per-band impedance, SWR, and combined matching +
  transformer efficiency for each zone the antenna falls in.
- Resonant-length annotations on canvas (rotated text, VF-adjusted λ/2
  multiples per band).
- **Sweet Spots** overlay: highlights wire lengths where ≥ N active bands
  simultaneously fall inside enabled matching zones; configurable min-bands
  threshold.
- Counterpoise effect: toggleable series-stub model with ghost curves and
  dashed counterpoise marker; model limitations documented.
- Velocity factor slider (0.90 – 1.00).
- Log-scale Y axis (10 – 5 000 Ω), HiDPI-aware canvas (devicePixelRatio).
- Band and zone toggle buttons.
- Detailed model notes and derivations panel (collapsible `<details>`).
- Responsive layout, dark theme.
