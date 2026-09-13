#!/usr/bin/env python3
"""
Zeichnet keypad4x4.kicad_pcb als SVG - zur Ansicht ohne KiCad.

Gelesen wird die erzeugte Platinendatei, nicht die Geometrie aus dem
Generator. Ein Fehler beim Schreiben faellt dadurch hier auf, statt
unbemerkt zu bleiben.
"""

import re, math
from pathlib import Path

src = Path(__file__).with_name("keypad4x4.kicad_pcb").read_text(encoding="utf-8")

# ── Umriss ───────────────────────────────────────────────────────────────
# Zeilenweise statt ueber einen Ausdruck, der die verschachtelten Klammern
# von (stroke (width ..) (type ..)) mitnehmen muesste - das ist zu leicht
# falsch geschrieben, und ein Tippfehler faellt dann als leeres Bild auf.
lines, arcs = [], []
for ln in src.splitlines():
    if '"Edge.Cuts"' not in ln:
        continue
    z = [float(v) for v in re.findall(r'-?\d+\.?\d*', ln.split("(stroke")[0])]
    if ln.lstrip().startswith("(gr_line") and len(z) >= 4:
        lines.append(tuple(z[:4]))
    elif ln.lstrip().startswith("(gr_arc") and len(z) >= 6:
        arcs.append(tuple(z[:6]))

# ── Fussabdruecke ────────────────────────────────────────────────────────
blocks = src.split("\n  (footprint ")[1:]
fps = []
for b in blocks:
    lib = b.split('"')[1]
    m = re.search(r'\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', b)
    ref = re.search(r'reference "([^"]+)"', b)
    fps.append((lib, float(m.group(1)), float(m.group(2)),
                float(m.group(3) or 0), ref.group(1) if ref else ""))

# ── Leiterbahnen ─────────────────────────────────────────────────────────
segs = [(float(a), float(b), float(c), float(d), l) for a, b, c, d, l in re.findall(
    r'\(segment \(start ([\d.-]+) ([\d.-]+)\) \(end ([\d.-]+) ([\d.-]+)\)'
    r' \(width [\d.]+\) \(layer "([^"]+)"\)', src)]

xs = [v for l in lines for v in (l[0], l[2])]
ys = [v for l in lines for v in (l[1], l[3])]
x0, x1, y0, y1 = min(xs)-6, max(xs)+6, min(ys)-6, max(ys)+6

o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} '
     f'{x1-x0:.1f} {y1-y0:.1f}" width="{(x1-x0)*4:.0f}" height="{(y1-y0)*4:.0f}">',
     '<style>'
     'text{font:2.2px system-ui,sans-serif;fill:#8b949e;text-anchor:middle}'
     '.ref{font:1.9px system-ui,sans-serif;fill:#6e7681}'
     '.edge{fill:#16853d14;stroke:#3fb950;stroke-width:.35}'
     '.key{fill:none;stroke:#58a6ff;stroke-width:.25}'
     '.pad{fill:#d29922}'
     '.hole{fill:#ffffff;stroke:#8b949e;stroke-width:.15}'
     '.dio{fill:#f8514933;stroke:#f85149;stroke-width:.2}'
     '.lot{fill:#d29922;stroke:#8b6914;stroke-width:.2}'
     '.ftrace{stroke:#f0883e;stroke-width:.25;fill:none}'
     '.btrace{stroke:#388bfd;stroke-width:.25;fill:none}'
     '</style>']

# Umriss
d = ""
for a, b, c, e in lines:
    d += f"M{a:.3f} {b:.3f} L{c:.3f} {e:.3f} "
for sx, sy, mx, my, ex, ey in arcs:
    d += f"M{sx:.3f} {sy:.3f} A3 3 0 0 1 {ex:.3f} {ey:.3f} "
o.append(f'<path class="edge" d="{d}"/>')

# Bahnen zuerst, damit Bauteile darueber liegen
for a, b, c, e, lay in segs:
    cls = "ftrace" if lay == "F.Cu" else "btrace"
    o.append(f'<line class="{cls}" x1="{a:.3f}" y1="{b:.3f}" x2="{c:.3f}" y2="{e:.3f}"/>')

for lib, x, y, rot, ref in fps:
    if lib.endswith("MX_1u"):
        o.append(f'<rect class="key" x="{x-9.525:.3f}" y="{y-9.525:.3f}" '
                 f'width="19.05" height="19.05" rx="1"/>')
        o.append(f'<circle class="hole" cx="{x:.3f}" cy="{y:.3f}" r="2"/>')
        for px in (-5.08, 5.08):
            o.append(f'<circle class="hole" cx="{x+px:.3f}" cy="{y:.3f}" r="0.875"/>')
        o.append(f'<circle class="pad" cx="{x-3.81:.3f}" cy="{y-2.54:.3f}" r="1.25"/>')
        o.append(f'<circle class="pad" cx="{x+2.54:.3f}" cy="{y-5.08:.3f}" r="1.25"/>')
        o.append(f'<text class="ref" x="{x:.3f}" y="{y+8.6:.3f}">{ref}</text>')
    elif lib.endswith("D_SOD-123"):
        o.append(f'<rect class="dio" x="{x-0.7:.3f}" y="{y-2.3:.3f}" '
                 f'width="1.4" height="4.6" rx="0.3"/>')
    elif lib.endswith("Pad"):
        o.append(f'<circle class="lot" cx="{x:.3f}" cy="{y:.3f}" r="1.3"/>')
        o.append(f'<circle class="hole" cx="{x:.3f}" cy="{y:.3f}" r="0.65"/>')
        o.append(f'<text class="ref" x="{x:.3f}" y="{y-2.4:.3f}">{ref}</text>')
    elif lib.endswith("M2"):
        o.append(f'<circle class="hole" cx="{x:.3f}" cy="{y:.3f}" r="1.1"/>')

o.append('</svg>')
dest = Path(__file__).with_name("vorschau.svg")
dest.write_text("\n".join(o), encoding="utf-8")
print(f"geschrieben: {dest}")
print(f"  Umriss {len(lines)} Linien + {len(arcs)} Boegen")
print(f"  {len(fps)} Bauteile, {len(segs)} Leiterbahnen")
