#!/usr/bin/env python3
"""
Zeichnet die ausgelieferten Gerber- und Bohrdateien als SVG.

Bewusst unabhaengig von KiCad: Gelesen wird, was im Archiv liegt und beim
Hersteller ankommt - nicht die Platinendatei. Ein Fehler beim Ausgeben der
Fertigungsdaten wuerde hier auffallen, in einer Ansicht der Platine nicht.

Unterstuetzt den Umfang, den diese Dateien nutzen: Kreis-, Rechteck- und
Langlochblenden, Striche (D01), Spruenge (D02), Blitze (D03) und Flaechen
(G36/G37). Trifft der Leser auf etwas anderes, sagt er es, statt es
stillschweigend wegzulassen.
"""

import re, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent / "fertigung"

LAGEN = [  # Datei-Endung, Farbe, Deckkraft, Beschriftung
    ("gm1", "#e6edf3", 1.00, "Umriss"),
    ("gtl", "#f0883e", 0.85, "Kupfer vorn"),
    ("gbl", "#388bfd", 0.65, "Kupfer hinten"),
    ("gto", "#ffffff", 0.55, "Aufdruck vorn"),
]

def lies_gerber(pfad):
    """Liefert (striche, blitze, flaechen) in Millimetern."""
    txt = pfad.read_text(errors="replace")
    fs = re.search(r"%FSLAX(\d)(\d)Y\d\d\*%", txt)
    if not fs:
        raise ValueError(f"{pfad.name}: kein Koordinatenformat gefunden")
    nk = int(fs.group(2))                       # Nachkommastellen
    if "%MOMM*%" not in txt:
        raise ValueError(f"{pfad.name}: nicht in Millimetern")

    blenden = {}
    for m in re.finditer(r"%ADD(\d+)([CROP]),([\d.X-]+)\*%", txt):
        p = [float(v) for v in m.group(3).split("X")]
        blenden[int(m.group(1))] = (m.group(2), p)
    # Blendenmakro "RoundRect": Radius, dann die vier Eckpunkte, dann Drehung.
    # Aus den Ecken ergeben sich Breite und Hoehe, der Radius kommt beidseitig
    # dazu - sonst fehlten die Loetflaechen der Dioden im Bild.
    for m in re.finditer(r"%ADD(\d+)RoundRect,([\d.X-]+)\*%", txt):
        v = [float(x) for x in m.group(2).split("X")]
        r, ecken = v[0], v[1:9]
        xs_, ys_ = ecken[0::2], ecken[1::2]
        blenden[int(m.group(1))] = ("RR", [max(xs_)-min(xs_)+2*r,
                                           max(ys_)-min(ys_)+2*r, r])

    striche, blitze, flaechen, boegen = [], [], [], []
    x = y = px = py = 0.0
    akt = None
    modus = "G01"                      # Interpolation: gerade oder Bogen
    in_flaeche = False
    poly = []

    im_makro = False
    for roh in txt.splitlines():
        ln = roh.strip()
        # Der Rumpf einer Makro-Definition steht zwischen %AM.. und dem
        # abschliessenden %. Er wird oben ueber %ADD..RoundRect ausgewertet,
        # hier waeren seine Zeilen nur Rauschen.
        if ln.startswith("%AM"):
            im_makro = True; continue
        if im_makro:
            if ln.endswith("%"): im_makro = False
            continue
        if not ln or ln.startswith("G04") or ln.startswith("%"):
            continue
        if ln.startswith("G36"):
            in_flaeche, poly = True, []
            continue
        if ln.startswith("G37"):
            if len(poly) > 2: flaechen.append(poly)
            in_flaeche = False
            continue
        m = re.match(r"^D(\d+)\*$", ln)
        if m:
            akt = int(m.group(1)); continue
        m = re.match(r"^G0([123])\*$", ln)
        if m:
            modus = "G0" + m.group(1); continue
        if re.match(r"^(G7[45]|M02)\*$", ln):
            continue                   # Bogenbetriebsart, Dateiende
        m = re.match(r"^(?:G0[123])?(?:X(-?\d+))?(?:Y(-?\d+))?"
                     r"(?:I(-?\d+))?(?:J(-?\d+))?D(0[123])\*$", ln)
        if not m:
            print(f"   übergangen: {ln[:40]}", file=sys.stderr); continue
        if m.group(1) is not None: x =  int(m.group(1)) / 10**nk
        if m.group(2) is not None: y = -int(m.group(2)) / 10**nk   # Gerber zaehlt Y nach oben
        i = int(m.group(3) or 0) / 10**nk
        j = -int(m.group(4) or 0) / 10**nk
        op = m.group(5)
        if in_flaeche:
            poly.append((x, y))
        elif op == "01" and akt in blenden:
            if modus == "G01":
                striche.append((px, py, x, y, blenden[akt]))
            else:
                boegen.append((px, py, x, y, px + i, py + j,
                               modus == "G02", blenden[akt]))
        if op in ("01", "02"):
            px, py = x, y
        elif op == "03" and akt in blenden:
            blitze.append((x, y, blenden[akt]))
            px, py = x, y
    return striche, blitze, flaechen, boegen

def lies_bohr(pfad):
    werkz, akt, loecher = {}, None, []
    for ln in pfad.read_text(errors="replace").splitlines():
        m = re.match(r"T(\d+)C([\d.]+)", ln)
        if m: werkz[m.group(1)] = float(m.group(2)); continue
        m = re.match(r"^T(\d+)\s*$", ln)
        if m: akt = m.group(1); continue
        m = re.match(r"^X(-?[\d.]+)Y(-?[\d.]+)", ln)
        if m and akt:
            loecher.append((float(m.group(1)), -float(m.group(2)), werkz[akt]))
    return loecher

# ── einlesen ─────────────────────────────────────────────────────────────
daten, punkte = [], []
for endung, farbe, deck, name in LAGEN:
    treffer = list(HIER.glob(f"*.{endung}"))
    if not treffer:
        print(f"  fehlt: *.{endung} ({name})"); continue
    s, b, f, bg = lies_gerber(treffer[0])
    daten.append((farbe, deck, name, s, b, f, bg))
    punkte += [(a, c) for a, c, *_ in s] + [(a, b_) for a, b_, _ in b] \
            + [(a, c) for a, c, *_ in bg]
    print(f"  {name:<14} {len(s):>4} Striche  {len(b):>4} Blitze  {len(bg)} Bögen  {len(f)} Flächen")

bohr = []
for f in HIER.glob("*.drl"):
    l = lies_bohr(f)
    bohr += l
    print(f"  {f.name:<24} {len(l):>4} Bohrungen")

xs = [p[0] for p in punkte] + [h[0] for h in bohr]
ys = [p[1] for p in punkte] + [h[1] for h in bohr]
x0, x1 = min(xs) - 4, max(xs) + 4
y0, y1 = min(ys) - 4, max(ys) + 4

o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} '
     f'{x1-x0:.2f} {y1-y0:.2f}" width="{(x1-x0)*7:.0f}" height="{(y1-y0)*7:.0f}">',
     f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1-x0:.2f}" height="{y1-y0:.2f}" fill="#0d1117"/>']

def zeichne(farbe, deck, striche, blitze, flaechen, boegen):
    for px, py, x, y, (form, p) in striche:
        o.append(f'<line x1="{px:.4f}" y1="{py:.4f}" x2="{x:.4f}" y2="{y:.4f}" '
                 f'stroke="{farbe}" stroke-opacity="{deck}" stroke-width="{p[0]:.4f}" '
                 f'stroke-linecap="round"/>')
    for x, y, (form, p) in blitze:
        if form == "RR":
            o.append(f'<rect x="{x-p[0]/2:.4f}" y="{y-p[1]/2:.4f}" width="{p[0]:.4f}" '
                     f'height="{p[1]:.4f}" rx="{p[2]:.4f}" fill="{farbe}" '
                     f'fill-opacity="{deck}"/>')
        elif form == "C":
            o.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{p[0]/2:.4f}" '
                     f'fill="{farbe}" fill-opacity="{deck}"/>')
        else:
            wdt, hgt = p[0], p[1] if len(p) > 1 else p[0]
            rx = min(wdt, hgt)/2 if form == "O" else 0
            o.append(f'<rect x="{x-wdt/2:.4f}" y="{y-hgt/2:.4f}" width="{wdt:.4f}" '
                     f'height="{hgt:.4f}" rx="{rx:.4f}" fill="{farbe}" '
                     f'fill-opacity="{deck}"/>')
    for x1_, y1_, x2_, y2_, cx, cy, cw, (form, p) in boegen:
        r = ((x1_-cx)**2 + (y1_-cy)**2) ** 0.5
        o.append(f'<path d="M{x1_:.4f} {y1_:.4f} A{r:.4f} {r:.4f} 0 0 '
                 f'{1 if cw else 0} {x2_:.4f} {y2_:.4f}" fill="none" '
                 f'stroke="{farbe}" stroke-opacity="{deck}" '
                 f'stroke-width="{p[0]:.4f}" stroke-linecap="round"/>')
    for poly in flaechen:
        d = " ".join(f"{'M' if i==0 else 'L'}{px:.4f} {py:.4f}"
                     for i, (px, py) in enumerate(poly))
        o.append(f'<path d="{d} Z" fill="{farbe}" fill-opacity="{deck}"/>')

for farbe, deck, name, s, b, f, bg in daten:
    zeichne(farbe, deck, s, b, f, bg)

# Bohrungen zuletzt, als ausgestanzte Loecher
for x, y, d in bohr:
    o.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{d/2:.4f}" fill="#0d1117"/>')
    o.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{d/2:.4f}" fill="none" '
             f'stroke="#8b949e" stroke-width="0.06"/>')

o.append("</svg>")
ziel = Path(__file__).with_name("gerber-ansicht.svg")
ziel.write_text("\n".join(o), encoding="utf-8")
print(f"\ngeschrieben: {ziel.name}  ({len(bohr)} Bohrungen ausgestanzt)")
