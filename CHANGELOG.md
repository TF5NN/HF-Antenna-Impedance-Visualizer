# Changelog

All notable changes to **HF End-Fed Antenna Impedance — Visual Tool**.
Creator and rights holder: **TF5NN**.

---

## [v4.02] — 2026-03-02

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
  and build upon this work freely; credit TF5NN as the original creator.
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
- **Version label and TF5NN © credit** in the page header.

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
