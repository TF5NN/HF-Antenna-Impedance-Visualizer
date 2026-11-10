// Checks the page's own model code against the NEC-2 reference data and
// rebuilds every tuner solution from ideal parts.
//
// Requires:  npm i playwright   (and a Chromium for it)
// Run:       node validation/check_v3.mjs
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const ref  = JSON.parse(fs.readFileSync(path.join(here, 'data', 'nec_reference.json')));

const browser = await chromium.launch();
const page = await browser.newPage();
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
await page.goto('file://' + path.join(here, '..', 'antenna_impedance.html'));

const out = await page.evaluate(ref => {
  const F = ref.bands_hz, o = {};
  VF = 1.0;                                    // the NEC reference is bare wire
  const swr = (z, r) => swr50({ R: z.R / r, X: z.X / r });
  // RMS error of |Z| (as a percentage) and how well the SWR<2 windows coincide
  function compare(pairs, ratios) {
    let se = 0, n = 0, both = 0, either = 0;
    for (const [m, ref] of pairs) {
      se += Math.log10(Math.hypot(m.R, m.X) / Math.hypot(ref.R, ref.X)) ** 2; n++;
      for (const r of ratios) {
        const a = swr(ref, r) < 2, b = swr(m, r) < 2;
        if (a && b) both++;
        if (a || b) either++;
      }
    }
    return { points: n, rmsErrorPct: +(100 * (10 ** Math.sqrt(se / n) - 1)).toFixed(1),
             zoneAgreementPct: Math.round(100 * both / either) };
  }
  let P = [];
  for (const b in ref.mono) for (const [L, r, x] of ref.mono[b]) P.push([calcZwireComplex(L, F[b]), { R: r, X: x }]);
  o.endFedIdealGround = compare(P, [49, 1]);
  P = [];
  for (const k in ref.ocf) { const [b, Lw] = k.split('@'); for (const [p, r, x] of ref.ocf[k]) P.push([calcDipoleZ(p, +Lw, F[b]), { R: r, X: x }]); }
  o.offCentreFed = compare(P, [1, 4, 6]);
  cpEnabled = true; P = [];
  for (const k in ref.cp) { const [b, cp] = k.split('@'); cpLengthM = +cp; for (const [L, r, x] of ref.cp[k]) P.push([calcZcomplex(L, F[b]), { R: r, X: x }]); }
  o.endFedWithCounterpoise = compare(P, [49, 9, 1]);
  cpEnabled = false;

  // Tuner: rebuild each returned L-network from ideal parts and see what the radio gets
  function rebuilt(Z, sol) {
    const inv = p => { const d = p.r * p.r + p.i * p.i; return { r: p.r / d, i: -p.i / d }; };
    const xs = sol.seriesEl.type === 'none' ? 0 : sol.seriesEl.X;
    const bp = sol.shuntEl.type  === 'none' ? 0 : sol.shuntEl.B;
    let z = { r: Z.R, i: Z.X };
    if (sol.topology === 'series→shunt') { z.i += xs; z = inv(z); z.i += bp; z = inv(z); }
    else                                  { z = inv(z); z.i += bp; z = inv(z); z.i += xs; }
    return { R: z.r, X: z.i };
  }
  const t = { solutions: 0, wrong: 0, limitViolations: 0, noSolution: 0, worstSwr: 1 };
  for (const f of [1.9e6, 3.65e6, 7.15e6, 14.175e6, 28.85e6, 51e6])
    for (const R of [3, 5, 12.5, 25, 40, 49, 50, 51, 75, 100, 200, 450, 1000, 3000])
      for (const X of [-2000, -500, -100, -25, 0, 25, 100, 500, 2000])
        for (const [Lmax, Cmax] of [[4, 500], [24, 1200], [60, 3500], [1e6, 1e9]]) {
          const s = solveL({ R, X }, f, Lmax, Cmax);
          if (!s.matched) { t.noSolution++; continue; }
          t.solutions++;
          const w = swr50(rebuilt({ R, X }, s));
          t.worstSwr = Math.max(t.worstSwr, w);
          if (w > 1.02) t.wrong++;
          for (const el of [s.seriesEl, s.shuntEl]) {
            if (el.type === 'L' && el.val > Lmax * 1.001) t.limitViolations++;
            if (el.type === 'C' && el.val > Cmax * 1.001) t.limitViolations++;
          }
        }
  t.worstSwr = +t.worstSwr.toFixed(4);
  o.tuner = t;
  return o;
}, ref);

console.log(JSON.stringify(out, null, 2));
console.log('page errors:', errors.length ? errors : 'none');
await browser.close();
process.exit(errors.length || out.tuner.wrong || out.tuner.limitViolations ? 1 : 0);
