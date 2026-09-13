#!/usr/bin/env python3
"""
Erzeugt eine KiCad-Platine fuer ein 4x4-Makropad mit Cherry-MX-Schaltern
und acht Loetpunkten fuer den Anschluss eines beliebigen Controllers.

Geschrieben wird das Dateiformat von KiCad 7. KiCad 8 und 9 lesen das und
wandeln es beim ersten Speichern selbst um - andersherum ginge es nicht,
deshalb bewusst die aeltere Fassung.

Die Fussabdruecke stehen vollstaendig in der Platinendatei. Sie braucht
also keine Bibliothek und laesst sich auf jedem Rechner oeffnen, egal
welche Footprints dort installiert sind.

Matrix: Spalte -> Schalter -> Diode -> Zeile. Die Diode verhindert, dass
beim gleichzeitigen Druecken mehrerer Tasten Phantomtasten erscheinen.

Die Loetpunkte sitzen so, dass jede der acht Bahnen geradeaus laeuft:
die Spaltenpunkte genau ueber ihrer Spalte, die Zeilenpunkte genau neben
ihrer Zeile. Dadurch kreuzt sich nichts, es braucht keine Durchkontaktierung,
und die Platine ist vollstaendig verdrahtet.
"""

import math
import uuid
from pathlib import Path

# ── Masse ────────────────────────────────────────────────────────────────
PITCH   = 19.05          # Rastermass einer Taste
COLS    = 4
ROWS    = 4
M_LEFT  = 14.0           # Platz links, dort laufen die Zeilen herunter
M_TOP   = 10.0           # Platz oben fuer Anschlussreihe und Spuren
M_REST  = 6.0            # Rand rechts und unten, Platz fuer Schrauben
PAD_D   = 2.2            # Loetpunkt: Durchmesser
PAD_H   = 1.0            # Loetpunkt: Bohrung
CONN_P  = 2.54           # Raster der Anschlussreihe, passend fuer Stiftleiste

TRACE   = 0.25           # Leiterbahnbreite

# Platinenecke oben links
BX, BY  = 20.0, 20.0

KEY_X0  = BX + M_LEFT + PITCH / 2
KEY_Y0  = BY + M_TOP  + PITCH / 2

BW      = M_LEFT + COLS * PITCH + M_REST
BH      = M_TOP  + ROWS * PITCH + M_REST

# Alle acht Anschluesse in einer Reihe am oberen Rand, von links:
# R3 R2 R1 R0 C0 C1 C2 C3
#
# Die Reihenfolge ist nicht beliebig. Zeilen wie Spalten faechern sich auf,
# und dabei darf sich nichts kreuzen:
#   - Zeilen laufen links im Rand herunter. Die oberste Zeile (R0) biegt als
#     erste nach rechts ab, muss also am weitesten rechts stehen - sonst
#     schnitte ihr Weg die Spuren der tieferen Zeilen.
#   - Spalten fahren in vier Spuren zwischen Anschlussreihe und Tastenfeld
#     nach rechts. Die am weitesten rechts endende Spalte nimmt die oberste
#     Spur, sonst kreuzt sie die kuerzeren.
CONN_Y  = BY + 5.0                      # Hoehe der Anschlussreihe
CONN_X0 = BX + 6.0                      # erster Anschluss
def conn_x(i): return CONN_X0 + i * CONN_P
def row_pad_x(r): return conn_x(3 - r)          # R3 R2 R1 R0
def col_pad_x(c): return conn_x(4 + c)          # C0 C1 C2 C3
def col_spur_y(c): return 29.2 - c * 1.0        # Spur je Spalte

def kx(c): return KEY_X0 + c * PITCH
def ky(r): return KEY_Y0 + r * PITCH

# ── Netze ────────────────────────────────────────────────────────────────
nets = [""]
def net(name):
    if name not in nets:
        nets.append(name)
    return nets.index(name)

for c in range(COLS): net(f"COL{c}")
for r in range(ROWS): net(f"ROW{r}")
for r in range(ROWS):
    for c in range(COLS):
        net(f"SW{r*COLS+c+1}_D")

def uid(): return str(uuid.uuid4())

out = []
def w(s): out.append(s)

# ── Kopf ─────────────────────────────────────────────────────────────────
LAYERS = [
    (0,"F.Cu","signal",None),(31,"B.Cu","signal",None),
    (32,"B.Adhes","user","B.Adhesive"),(33,"F.Adhes","user","F.Adhesive"),
    (34,"B.Paste","user",None),(35,"F.Paste","user",None),
    (36,"B.SilkS","user","B.Silkscreen"),(37,"F.SilkS","user","F.Silkscreen"),
    (38,"B.Mask","user",None),(39,"F.Mask","user",None),
    (40,"Dwgs.User","user","User.Drawings"),(41,"Cmts.User","user","User.Comments"),
    (42,"Eco1.User","user","User.Eco1"),(43,"Eco2.User","user","User.Eco2"),
    (44,"Edge.Cuts","user",None),(45,"Margin","user",None),
    (46,"B.CrtYd","user","B.Courtyard"),(47,"F.CrtYd","user","F.Courtyard"),
    (48,"B.Fab","user",None),(49,"F.Fab","user",None),
]

w('(kicad_pcb (version 20221018) (generator "generate_pcb.py")')
w('  (general (thickness 1.6))')
w('  (paper "A4")')
w('  (layers')
for n, nm, ty, ui in LAYERS:
    w(f'    ({n} "{nm}" {ty}' + (f' "{ui}")' if ui else ')'))
w('  )')
w('  (setup (pad_to_mask_clearance 0))')

# ── Fussabdruecke ────────────────────────────────────────────────────────
def mx_switch(ref, x, y, net_col, net_d):
    """Cherry MX, PCB-montiert: zwei Kontaktstifte, Mittelloch, zwei Zapfen."""
    p = [f'  (footprint "Keypad:MX_1u" (layer "F.Cu") (tstamp {uid()})',
         f'    (at {x:.4f} {y:.4f})',
         f'    (attr through_hole)',
         f'    (fp_text reference "{ref}" (at 0 -10.5) (layer "F.SilkS") (tstamp {uid()})',
         f'      (effects (font (size 1 1) (thickness 0.15))))',
         f'    (fp_text value "MX" (at 0 10.5) (layer "F.Fab") hide (tstamp {uid()})',
         f'      (effects (font (size 1 1) (thickness 0.15))))',
         f'    (pad "1" thru_hole circle (at -3.81 -2.54) (size 2.5 2.5) (drill 1.5)'
         f' (layers "*.Cu" "*.Mask") (net {net_col} "{nets[net_col]}") (tstamp {uid()}))',
         f'    (pad "2" thru_hole circle (at 2.54 -5.08) (size 2.5 2.5) (drill 1.5)'
         f' (layers "*.Cu" "*.Mask") (net {net_d} "{nets[net_d]}") (tstamp {uid()}))',
         f'    (pad "" np_thru_hole circle (at 0 0) (size 4 4) (drill 4)'
         f' (layers "*.Cu" "*.Mask") (tstamp {uid()}))']
    for px in (-5.08, 5.08):
        p.append(f'    (pad "" np_thru_hole circle (at {px} 0) (size 1.75 1.75) (drill 1.75)'
                 f' (layers "*.Cu" "*.Mask") (tstamp {uid()}))')
    for (x1,y1,x2,y2) in ((-9.525,-9.525,9.525,-9.525),(9.525,-9.525,9.525,9.525),
                          (9.525,9.525,-9.525,9.525),(-9.525,9.525,-9.525,-9.525)):
        p.append(f'    (fp_line (start {x1} {y1}) (end {x2} {y2})'
                 f' (stroke (width 0.1) (type default)) (layer "F.Fab") (tstamp {uid()}))')
    p.append('  )')
    return p

def diode(ref, x, y, net_a, net_k):
    """SOD-123 auf der Rueckseite, senkrecht: Anode oben, Kathode unten."""
    return [
        f'  (footprint "Keypad:D_SOD-123" (layer "B.Cu") (tstamp {uid()})',
        f'    (at {x:.4f} {y:.4f} 90)',
        f'    (attr smd)',
        f'    (fp_text reference "{ref}" (at 0 -3 90) (layer "B.SilkS") (tstamp {uid()})',
        f'      (effects (font (size 0.8 0.8) (thickness 0.12)) (justify mirror)))',
        f'    (fp_text value "1N4148W" (at 0 3 90) (layer "B.Fab") hide (tstamp {uid()})',
        f'      (effects (font (size 0.8 0.8) (thickness 0.12)) (justify mirror)))',
        f'    (pad "1" smd roundrect (at -1.65 0 90) (size 1.2 1.4)'
        f' (layers "B.Cu" "B.Paste" "B.Mask") (roundrect_rratio 0.2)'
        f' (net {net_k} "{nets[net_k]}") (tstamp {uid()}))',
        f'    (pad "2" smd roundrect (at 1.65 0 90) (size 1.2 1.4)'
        f' (layers "B.Cu" "B.Paste" "B.Mask") (roundrect_rratio 0.2)'
        f' (net {net_a} "{nets[net_a]}") (tstamp {uid()}))',
        f'    (fp_line (start -2.7 -0.9) (end -2.7 0.9)'
        f' (stroke (width 0.2) (type default)) (layer "B.SilkS") (tstamp {uid()}))',
        '  )']

def loetpunkt(ref, x, y, n, label, unten=True):
    """Durchkontaktierter Anschlusspunkt fuer einen angeloeteten Draht.
    Groesser gebohrt als ein Stiftleistenloch, damit auch Litze hineinpasst."""
    ly = 3.0 if unten else -3.0
    return [
        f'  (footprint "Keypad:Pad" (layer "F.Cu") (tstamp {uid()})',
        f'    (at {x:.4f} {y:.4f})',
        f'    (attr through_hole)',
        f'    (fp_text reference "{ref}" (at 0 -6) (layer "F.Fab") hide (tstamp {uid()})',
        f'      (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'    (fp_text user "{label}" (at 0 {ly}) (layer "F.SilkS") (tstamp {uid()})',
        f'      (effects (font (size 1.1 1.1) (thickness 0.18))))',
        f'    (pad "1" thru_hole circle (at 0 0) (size {PAD_D} {PAD_D}) (drill {PAD_H})'
        f' (layers "*.Cu" "*.Mask") (net {n} "{nets[n]}") (tstamp {uid()}))',
        '  )']

def mount_hole(x, y):
    return [f'  (footprint "Keypad:M2" (layer "F.Cu") (tstamp {uid()})',
            f'    (at {x:.4f} {y:.4f})',
            f'    (attr through_hole)',
            f'    (pad "" np_thru_hole circle (at 0 0) (size 2.2 2.2) (drill 2.2)'
            f' (layers "*.Cu" "*.Mask") (tstamp {uid()}))',
            '  )']

for r in range(ROWS):
    for c in range(COLS):
        i  = r * COLS + c + 1
        nd = net(f"SW{i}_D")
        out += mx_switch(f"SW{i}", kx(c), ky(r), net(f"COL{c}"), nd)
        out += diode(f"D{i}", kx(c) + 2.54, ky(r) + 6.0, nd, net(f"ROW{r}"))

for r in range(ROWS):
    out += loetpunkt(f"J{4-r}", row_pad_x(r), CONN_Y, net(f"ROW{r}"), f"R{r}", unten=False)
for c in range(COLS):
    out += loetpunkt(f"J{5+c}", col_pad_x(c), CONN_Y, net(f"COL{c}"), f"C{c}", unten=False)

for mx_, my_ in ((BX+3, BY+3), (BX+BW-3, BY+3),
                 (BX+3, BY+BH-3), (BX+BW-3, BY+BH-3)):
    out += mount_hole(mx_, my_)

# ── Leiterbahnen der Matrix ──────────────────────────────────────────────
def seg(x1, y1, x2, y2, layer, n):
    w(f'  (segment (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f})'
      f' (width {TRACE}) (layer "{layer}") (net {n}) (tstamp {uid()}))')

# Spalten senkrecht auf der Vorderseite, ueber Stift 1 aller Schalter
for c in range(COLS):
    x = kx(c) - 3.81
    for r in range(ROWS - 1):
        seg(x, ky(r) - 2.54, x, ky(r+1) - 2.54, "F.Cu", net(f"COL{c}"))

# Stift 2 des Schalters zur Anode der Diode, senkrecht auf der Rueckseite
for r in range(ROWS):
    for c in range(COLS):
        i = r * COLS + c + 1
        x = kx(c) + 2.54
        seg(x, ky(r) - 5.08, x, ky(r) + 6.0 - 1.65, "B.Cu", net(f"SW{i}_D"))

# Zeilen waagerecht auf der Rueckseite, ueber die Kathoden
for r in range(ROWS):
    y = ky(r) + 6.0 + 1.65
    for c in range(COLS - 1):
        seg(kx(c) + 2.54, y, kx(c+1) + 2.54, y, "B.Cu", net(f"ROW{r}"))

# ── Anschluesse zu den Loetpunkten ───────────────────────────────────────
# Beide Richtungen laufen geradeaus: die Spalten senkrecht auf der
# Vorderseite, die Zeilen waagerecht auf der Rueckseite. Weil jede Bahn auf
# der Achse ihres Punktes liegt, kreuzt sich nichts - kein Durchkontakt.
# Zeilen: senkrecht im linken Rand herunter, dann nach rechts auf ihre Bahn
for r in range(ROWS):
    x, y, n = row_pad_x(r), ky(r) + 7.65, net(f"ROW{r}")
    seg(x, CONN_Y, x, y, "B.Cu", n)
    seg(x, y, kx(0) + 2.54, y, "B.Cu", n)

# Spalten: auf die eigene Spur, nach rechts, dann herunter auf die Spaltenbahn
for c in range(COLS):
    xp, xs, ys, n = col_pad_x(c), kx(c) - 3.81, col_spur_y(c), net(f"COL{c}")
    seg(xp, CONN_Y, xp, ys, "F.Cu", n)
    seg(xp, ys, xs, ys, "F.Cu", n)
    seg(xs, ys, xs, ky(0) - 2.54, "F.Cu", n)

# ── Platinenumriss mit abgerundeten Ecken ────────────────────────────────
R = 3.0
x0, y0, x1_, y1_ = BX, BY, BX + BW, BY + BH
for (ax, ay, bx_, by_) in ((x0+R,y0,x1_-R,y0), (x1_,y0+R,x1_,y1_-R),
                           (x1_-R,y1_,x0+R,y1_), (x0,y1_-R,x0,y0+R)):
    w(f'  (gr_line (start {ax:.4f} {ay:.4f}) (end {bx_:.4f} {by_:.4f})'
      f' (stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (tstamp {uid()}))')
for (cx, cy, sa, ea) in ((x0+R,y0+R,180,270), (x1_-R,y0+R,270,360),
                         (x1_-R,y1_-R,0,90), (x0+R,y1_-R,90,180)):
    sx, sy = cx + R*math.cos(math.radians(sa)), cy + R*math.sin(math.radians(sa))
    mx_, my_ = cx + R*math.cos(math.radians((sa+ea)/2)), cy + R*math.sin(math.radians((sa+ea)/2))
    ex, ey = cx + R*math.cos(math.radians(ea)), cy + R*math.sin(math.radians(ea))
    w(f'  (gr_arc (start {sx:.4f} {sy:.4f}) (mid {mx_:.4f} {my_:.4f}) (end {ex:.4f} {ey:.4f})'
      f' (stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (tstamp {uid()}))')

# ── Massstab zum Pruefen von Ausdrucken ──────────────────────────────────
# Liegt auf Dwgs.User und kommt damit weder in die Gerber noch auf die
# fertige Platine. Nur die Druckvorlage zeigt ihn: Misst der Balken auf dem
# Papier keine 100 mm, hat der Drucker skaliert und der Ausdruck taugt nicht
# zum Anhalten von Schaltern.
MY = BY + BH + 10.0
def ul(x1, y1, x2, y2, breite=0.25):
    w(f'  (gr_line (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f})'
      f' (stroke (width {breite}) (type solid)) (layer "Dwgs.User")'
      f' (tstamp {uid()}))')

ul(BX, MY, BX + 100, MY, 0.4)
for i in range(11):                       # Teilstriche alle 10 mm
    h = 3.0 if i % 5 == 0 else 1.8
    ul(BX + i * 10, MY - h, BX + i * 10, MY + h, 0.4 if i % 5 == 0 else 0.25)
w(f'  (gr_text "100 mm  – misst der Balken das nicht, hat der Drucker skaliert"'
  f' (at {BX + 50:.4f} {MY + 7:.4f}) (layer "Dwgs.User") (tstamp {uid()})'
  f' (effects (font (size 2.5 2.5) (thickness 0.35))))')

# ── Netzliste hinter den Kopf einfuegen ──────────────────────────────────
netblock = [f'  (net {i} "{n}")' for i, n in enumerate(nets)]
head_end = next(i for i, l in enumerate(out) if l.startswith('  (setup')) + 1
out = out[:head_end] + netblock + out[head_end:]
out.append(')')

import re
libdir = Path(__file__).with_name("keypad.pretty")
libdir.mkdir(exist_ok=True)

def als_modul(zeilen, name):
    """Macht aus den Zeilen eines platzierten Bauteils eine .kicad_mod-Datei.

    Position und Netzzuordnung gehoeren zur Platine, nicht in die Bibliothek.
    Der Drehwinkel ebenso: In der Platinendatei tragen Lotaugen und Texte den
    Winkel des Bauteils mit sich (absolut, nicht relativ). Bleibt er stehen,
    waehrend das Bauteil selbst ungedreht abgelegt wird, meldet der Regel-
    pruefer zu Recht eine Abweichung zur Bibliothek."""
    k, rot = [], 0.0
    for i, ln in enumerate(zeilen):
        if i == 0:
            k.append(f'(footprint "{name}" (version 20221018)'
                     f' (generator "generate_pcb.py")')
            k.append(f'  (layer "{"B.Cu" if "B.Cu" in ln else "F.Cu"}")')
            continue
        m = re.match(r"\s*\(at [-\d.]+ [-\d.]+(?: ([-\d.]+))?\)$", ln)
        if m:                              # Platzierung auf der Platine
            rot = float(m.group(1) or 0)
            continue
        ln = re.sub(r' \(net \d+ "[^"]*"\)', "", ln)
        if rot:                            # Winkel herausrechnen
            def ohne(mm):
                a = (float(mm.group(3)) - rot) % 360
                return f"(at {mm.group(1)} {mm.group(2)}" + (f" {a:g})" if a else ")")
            ln = re.sub(r"\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)", ohne, ln)
        k.append(ln[2:] if ln.startswith("  ") else ln)
    return "\n".join(k) + "\n"

for name, zeilen in (("MX_1u",     mx_switch("REF**", 0, 0, 0, 0)),
                     ("D_SOD-123", diode("REF**", 0, 0, 0, 0)),
                     ("Pad",       loetpunkt("REF**", 0, 0, 0, "")),
                     ("M2",        mount_hole(0, 0))):
    (libdir / f"{name}.kicad_mod").write_text(als_modul(zeilen, name), encoding="utf-8")

Path(__file__).with_name("fp-lib-table").write_text(
    '(fp_lib_table\n  (version 7)\n'
    '  (lib (name "Keypad")(type "KiCad")(uri "${KIPRJMOD}/keypad.pretty")'
    '(options "")(descr "Fussabdruecke dieses Makropads"))\n)\n', encoding="utf-8")

dest = Path(__file__).with_name("keypad4x4.kicad_pcb")
dest.write_text("\n".join(out) + "\n", encoding="utf-8")

print(f"geschrieben : {dest}")
print(f"Platine     : {BW:.1f} x {BH:.1f} mm")
print(f"Tasten      : {ROWS} x {COLS} im Raster {PITCH} mm")
print(f"Netze       : {len(nets)-1}")
print(f"Leiterbahnen: {sum(1 for l in out if l.lstrip().startswith('(segment'))}")
