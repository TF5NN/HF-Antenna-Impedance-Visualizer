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
"""
import json, os
import numpy as np
from PyNEC import nec_context

C = 299792458.0
RADIUS = 0.0005
BANDS = {'40m': 7.15e6, '20m': 14.175e6, '15m': 21.225e6, '10m': 28.85e6}


def monopole(L, f):
    lam = C / f
    n = max(9, int(np.ceil(L / (lam / 40))))
    ctx = nec_context()
    ctx.get_geometry().wire(1, n, 0, 0, 0, 0, 0, L, RADIUS, 1, 1)
    ctx.geometry_complete(1)
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


def main():
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
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'nec_reference.json')
    with open(path, 'w') as fh:
        json.dump(out, fh)
    print('wrote', path)


if __name__ == '__main__':
    main()
