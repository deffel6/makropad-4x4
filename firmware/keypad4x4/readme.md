# keypad4x4

16 Tasten im 4×4-Raster, Cherry MX, Pro Micro über acht Lötpunkte
angeschlossen. Passend zur Platine aus `~/keypad-4x4`.

## Anschluss

| Lötpunkt auf der Platine | Pin am Pro Micro |
|---|---|
| `C0` `C1` `C2` `C3` | `F4` `F5` `F6` `F7` |
| `R0` `R1` `R2` `R3` | `D4` `C6` `D7` `E6` |

Dioden in Richtung Spalte → Zeile, in QMK also `COL2ROW`.

## Übersetzen und flashen

```
cd ~/vial-qmk
make keypad4x4:default          # feste Belegung
make keypad4x4:vial             # zur Laufzeit änderbar
```

Flashen mit angehängtem `:flash`, also `make keypad4x4:vial:flash`. Der Pro
Micro meldet sich nur ein paar Sekunden lang als Programmiergerät — dafür
den Reset-Anschluss **zweimal kurz hintereinander** auf Masse legen, sobald
in der Ausgabe „Detecting USB port" erscheint.

## Die beiden Belegungen

**default** — zwei Ebenen, fest eingebaut. Unten liegt ein Zifferblock,
gedrückt gehaltene Umschalttaste unten rechts bringt `F13` bis `F24` und
die Lautstärke. Größe: rund 55 % des Speichers.

**vial** — dieselbe Grundbelegung, aber über die Vial-App änderbar, ohne
neu zu übersetzen. Entsperrt wird mit den beiden oberen linken Tasten
gleichzeitig.

## Warum F13 bis F24

Diese Tasten gibt es auf keiner gewöhnlichen Tastatur, und genau deshalb
sind sie nützlich: Kein Programm hat sie schon belegt. In Hammerspoon oder
der Kurzbefehle-App lassen sie sich frei binden, ohne mit bestehenden
Tastenkombinationen zu kollidieren.

## Speicherplatz

Der Pro Micro hat 32 KB Flash, davon belegt der Caterina-Bootloader vier —
es bleiben **28.672 Bytes**.

Die Vial-Fassung füllt davon 98 %. Damit sie überhaupt hineinpasst, sind in
`keymaps/vial/rules.mk` alle entbehrlichen Funktionen abgeschaltet und die
Zahl der Ebenen auf drei begrenzt.

**Das heißt: Für Erweiterungen ist kein Platz mehr.** Wer Tap Dance, Combos
oder eine vierte Ebene will, braucht einen Controller mit mehr Flash — ein
RP2040-Modul in Pro-Micro-Bauform etwa passt auf dieselben Lötpunkte und
bringt das Sechzehnfache mit.

Die **default**-Fassung hat dagegen reichlich Luft.
