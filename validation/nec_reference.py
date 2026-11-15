#!/usr/bin/env python3
"""NEC-2 reference impedances used to check the v3 model.

Requires:  pip install PyNEC numpy
Run:       python3 validation/nec_reference.py
Writes:    validation/data/nec_reference.json

Geometry: straight 1 mm diameter bare copper-like (lossless) wire.
  mono  wire of length L standing on a perfect ground, fed at the base
        (the idealised "end-fed wire with a perfect return path")
  ocf   free-space wire of total length Lw fed at fraction p from one end
  cp    free-space end-fed wire of length L with a counterpoise of length cp,
        fed at the junction
Each record is [x, R, X] with x = L (m) or p (fraction).

Extra one-off sets (reported by check_v3.mjs but not used as a pass/fail gate):
  wide    other bands (160 m, 80 m, 6 m)
  diam    wire diameters 0.5 mm and 1.4 mm (the tool always assumes 1 mm)
  ins     PVC-insulated wire, emulated with distributed series inductance
          (NEC-2 has no insulation card)
  height  horizontal 20.2 m wire over perfect ground, fed at fraction p
  height_real  the same over average ground (er 13, 5 mS/m)

Low-band sets (160 m and 80 m; reported by check_v3.mjs, informational):
  low_ocf     free-space wires of 40.9 m and 81.8 m fed at fraction p
  low_cp      free-space end-fed wire with a 2.1, 5, 10 or 20 m counterpoise
  low_height  horizontal wire (40.9 m on 80 m, 81.8 m on 160 m) over average
              ground at 5, 10 and 20 m, fed at fraction p. These heights are as
              low as 0.03 wavelengths, so this set uses the Sommerfeld ground
  height_sommerfeld  the 40-10 m `height_real` cases recomputed with the
              Sommerfeld ground
The end-fed wire on a perfect ground for these bands is in `wide`.

Run with --low-only to add just the low-band sets to an existing file, leaving
every other number in it untouched.
"""
import json, os, sys
import numpy as np
from PyNEC import nec_context

C = 299792458.0
RADIUS = 0.0005
BANDS = {'40m': 7.15e6, '20m': 14.175e6, '15m': 21.225e6, '10m': 28.85e6}


def monopole(L, f, radius=RADIUS, series_l=0.0):
    lam = C / f
    n = max(9, int(np.ceil(L / (lam / 40))))
    ctx = nec_context()
    ctx.get_geometry().wire(1, n, 0, 0, 0, 0, 0, L, radius, 1, 1)
    ctx.geometry_complete(1)
    if series_l:
        ctx.ld_card(2, 1, 0, 0, 0.0, series_l, 0.0)   # distributed series inductance (H/m)
    ctx.gn_card(1, 0, 0, 0, 0, 0, 0, 0)          # perfect ground
    ctx.fr_card(0, 1, f / 1e6, 0)
    ctx.ex_card(0, 1, 1, 0, 1.0, 0, 0, 0, 0, 0)
    ctx.xq_card(0)
    return ctx.get_input_parameters(0).get_impedance()[0]


def two_arm(La, Lb, f):
    """Free-space wire: arm La below the feed, arm Lb above it."""
    seg = (C / f) / 80
    na = max(3, int(np.ceil(La / seg)))
    nb = max(3, int(np.ceil(Lb / seg)))
    d = min(La / na, Lb / nb)                    # source segment straddles the feed
    ctx = nec_context()
    g = ctx.get_geometry()
    g.wire(1, na, 0, 0, -La, 0, 0, -d / 2, RADIUS, 1, 1)
    g.wire(2, 1, 0, 0, -d / 2, 0, 0, d / 2, RADIUS, 1, 1)
    g.wire(3, nb, 0, 0, d / 2, 0, 0, Lb, RADIUS, 1, 1)
    ctx.geometry_complete(0)
    ctx.fr_card(0, 1, f / 1e6, 0)
    ctx.ex_card(0, 2, 1, 0, 1.0, 0, 0, 0, 0, 0)
    ctx.xq_card(0)
    return ctx.get_input_parameters(0).get_impedance()[0]


def horizontal(La, Lb, f, h, real_ground=False, sommerfeld=False):
    """Horizontal wire at height h, arms La and Lb either side of the feed.

    sommerfeld=True uses NEC's Sommerfeld-Norton ground, which stays valid close to the
    ground; the faster reflection-coefficient method is only good above about 0.1-0.2 wavelengths.
    """
    seg = (C / f) / 80
    na = max(3, int(np.ceil(La / seg)))
    nb = max(3, int(np.ceil(Lb / seg)))
    d = min(La / na, Lb / nb)
    ctx = nec_context()
    g = ctx.get_geometry()
    g.wire(1, na, -La, 0, h, -d / 2, 0, h, RADIUS, 1, 1)
    g.wire(2, 1, -d / 2, 0, h, d / 2, 0, h, RADIUS, 1, 1)
    g.wire(3, nb, d / 2, 0, h, Lb, 0, h, RADIUS, 1, 1)
    ctx.geometry_complete(1)
    if sommerfeld:
        ctx.gn_card(2, 0, 13.0, 0.005, 0, 0, 0, 0)   # average ground, Sommerfeld-Norton method
    elif real_ground:
        ctx.gn_card(0, 0, 13.0, 0.005, 0, 0, 0, 0)   # average ground, reflection-coefficient method
    else:
        ctx.gn_card(1, 0, 0, 0, 0, 0, 0, 0)
    ctx.fr_card(0, 1, f / 1e6, 0)
    ctx.ex_card(0, 2, 1, 0, 1.0, 0, 0, 0, 0, 0)
    ctx.xq_card(0)
    return ctx.get_input_parameters(0).get_impedance()[0]


# PVC sheath emulation: er = 3, outer/inner radius = 2 (0.5 mm of insulation on 1 mm wire)
INS_ER, INS_RATIO = 3.0, 2.0
INS_SERIES_L = 2e-7 * (1 - 1 / INS_ER) * np.log(INS_RATIO)     # H/m


def extras(out):
    wide = {'160m': (1.9e6, 10, 100), '80m': (3.65e6, 5, 52), '6m': (51e6, 0.4, 8)}
    out['wide'] = {b: [[float(L), z.real, z.imag] for L in np.linspace(lo, hi, 180) for z in [monopole(L, f)]]
                   for b, (f, lo, hi) in wide.items()}
    out['wide_hz'] = {b: v[0] for b, v in wide.items()}
    out['diam'] = {}
    for r in (0.00025, 0.0007):
        for b in ('40m', '10m'):
            out['diam']['%s@%s' % (b, r)] = [[float(L), z.real, z.imag]
                                              for L in np.linspace(1.3, 26.2, 125)
                                              for z in [monopole(L, BANDS[b], radius=r)]]
    out['ins'] = {'series_l_h_per_m': INS_SERIES_L, 'er': INS_ER, 'radius_ratio': INS_RATIO}
    for b in ('40m', '10m'):
        out['ins'][b] = [[float(L), z.real, z.imag] for L in np.linspace(1.3, 26.2, 125)
                         for z in [monopole(L, BANDS[b], series_l=INS_SERIES_L)]]
    for key, real in (('height', False), ('height_real', True)):
        out[key] = {}
        for h in (5.0, 10.0, 20.0):
            for b, f in BANDS.items():
                out[key]['%s@%s' % (b, h)] = [[float(p), z.real, z.imag]
                                               for p in np.linspace(0.04, 0.5, 24)
                                               for z in [horizontal(p * 20.2, (1 - p) * 20.2, f, h, real)]]


LOW = {'160m': 1.9e6, '80m': 3.65e6}
LOW_SWEEP = {'160m': (10, 100), '80m': (5, 52)}     # end-fed wire lengths, as in `wide`
LOW_DIPOLE = {'160m': 81.8, '80m': 40.9}            # roughly a half-wave on each band


def low_bands(out):
    out['low_hz'] = LOW
    out['low_ocf'] = {}
    for b, f in LOW.items():
        for Lw in (40.9, 81.8):
            out['low_ocf']['%s@%s' % (b, Lw)] = [[float(p), z.real, z.imag]
                                                  for p in np.linspace(0.03, 0.5, 48)
                                                  for z in [two_arm(p * Lw, (1 - p) * Lw, f)]]
    out['low_cp'] = {}
    for b, f in LOW.items():
        lo, hi = LOW_SWEEP[b]
        for cp in (2.1, 5.0, 10.0, 20.0):
            out['low_cp']['%s@%s' % (b, cp)] = [[float(L), z.real, z.imag]
                                                 for L in np.linspace(lo, hi, 120)
                                                 for z in [two_arm(cp, L, f)]]
    # The 40-10 m height cases again with the Sommerfeld ground, to show how much of the
    # agreement in `height_real` comes from sharing the reflection-coefficient approximation.
    out['height_sommerfeld'] = {}
    for h in (5.0, 10.0, 20.0):
        for b, f in BANDS.items():
            out['height_sommerfeld']['%s@%s' % (b, h)] = [[float(p), z.real, z.imag]
                                                           for p in np.linspace(0.04, 0.5, 24)
                                                           for z in [horizontal(p * 20.2, (1 - p) * 20.2, f, h, True, sommerfeld=True)]]
    out['low_height'] = {}
    for b, f in LOW.items():
        Lw = LOW_DIPOLE[b]
        for h in (5.0, 10.0, 20.0):
            out['low_height']['%s@%s@%s' % (b, Lw, h)] = [[float(p), z.real, z.imag]
                                                           for p in np.linspace(0.04, 0.5, 24)
                                                           for z in [horizontal(p * Lw, (1 - p) * Lw, f, h, True, sommerfeld=True)]]


def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'nec_reference.json')
    if '--low-only' in sys.argv:
        with open(path) as fh:
            out = json.load(fh)
        low_bands(out)
        with open(path, 'w') as fh:
            json.dump(out, fh)
        print('added the low-band sets to', path)
        return
    out = {'radius_m': RADIUS, 'bands_hz': BANDS, 'mono': {}, 'ocf': {}, 'cp': {}}
    for b, f in BANDS.items():
        out['mono'][b] = [[float(L), z.real, z.imag]
                          for L in np.linspace(1.3, 26.2, 250) for z in [monopole(L, f)]]
    for Lw in (20.2, 40.9):
        for b, f in BANDS.items():
            out['ocf']['%s@%s' % (b, Lw)] = [[float(p), z.real, z.imag]
                                              for p in np.linspace(0.03, 0.5, 48)
                                              for z in [two_arm(p * Lw, (1 - p) * Lw, f)]]
    for cp in (2.1, 5.0):
        for b, f in BANDS.items():
            out['cp']['%s@%s' % (b, cp)] = [[float(L), z.real, z.imag]
                                             for L in np.linspace(2.0, 26.2, 122)
                                             for z in [two_arm(cp, L, f)]]
    extras(out)
    low_bands(out)
    with open(path, 'w') as fh:
        json.dump(out, fh)
    print('wrote', path)


if __name__ == '__main__':
    main()
