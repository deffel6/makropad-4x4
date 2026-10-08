# Fertige Firmware

Übersetzt und einsatzbereit — zum Flashen brauchst du weder QMK noch ein
Terminal, die [QMK Toolbox](https://github.com/qmk/qmk_toolbox/releases)
genügt.

Hier liegen drei Dateien: zwei für das Pro-Micro-Keypad (QMK/Vial) und
eine für das nice!nano-Keypad (ZMK). Welche zu welchem Gerät gehört, steht
in der Tabelle.

| Datei | Gerät | Belegung |
|---|---|---|
| `keypad4x4_default.hex` | Pro Micro (ATmega32U4) | fest eingebaut, 15.808 Bytes (55 %) |
| `keypad4x4_vial.hex` | Pro Micro (ATmega32U4) | über Vial änderbar, 28.246 Bytes (98 %) |
| `keypad4x4_zmk.uf2` | nice!nano (nRF52840) | über ZMK Studio änderbar |

Die `.uf2` entsteht sonst nur als Artefakt eines GitHub-Actions-Laufs, und
die verfallen nach einiger Zeit. Deshalb liegt hier eine Kopie des jeweils
aktuellen Standes.

## Welche nehmen

**vial** für den Normalfall. Du änderst die Belegung dann in der Vial-App,
ohne je wieder zu flashen.

**default**, wenn du Vial nicht brauchst. Sie lässt 12 KB frei, in denen
später Erweiterungen Platz hätten — die Vial-Fassung ist mit 98 Prozent
randvoll.

## Flashen des nice!nano

Viel einfacher als beim Pro Micro — kein Programm nötig:

1. **Akku abziehen**, nur das USB-Kabel angesteckt lassen
2. **RST und GND zweimal kurz hintereinander** verbinden, im Takt eines
   Doppelklicks
3. Es erscheint ein Laufwerk **NICENANO**
4. `keypad4x4_zmk.uf2` daraufziehen

Das Board schreibt die Datei selbst, startet neu, und das Laufwerk
verschwindet. Die Fehlermeldung, die macOS dabei zeigt, gehört dazu: Das
Board hängt sich mitten im Schreiben selbst aus.

> **Wichtig:** Wurde die Belegung je in ZMK Studio geändert, liegt sie im
> Speicher des Keypads und **überstimmt die Firmware** — auch nach dem
> Flashen. Dann in ZMK Studio einmal **"Restore Stock Settings"** auslösen.

Der Akku muss ab, weil der Doppeltipp sonst oft nicht als zwei getrennte
Resets ankommt.

## Flashen mit der QMK Toolbox

1. Toolbox öffnen, oben über **Open** die `.hex`-Datei laden
2. Bei *MCU* **atmega32u4** wählen
3. Häkchen bei **Auto-Flash** setzen
4. Den **Reset**-Anschluss des Pro Micro **zweimal kurz hintereinander** auf
   Masse legen

Im Fenster erscheint dann grün „Caterina device connected", und der Vorgang
läuft von allein. Er dauert wenige Sekunden.

Das Zeitfenster ist kurz: Der Pro Micro meldet sich nach dem doppelten Reset
nur etwa acht Sekunden lang als Programmiergerät, danach startet er die
vorhandene Firmware. Deshalb das Häkchen bei *Auto-Flash* — sonst musst du
den Knopf in dieser Zeitspanne selbst treffen.

## Wenn nichts passiert

**Kein „Caterina device connected"** — der doppelte Reset war zu langsam
oder zu schnell. Zwei zügige Berührungen, etwa im Takt eines Doppelklicks.

**Beim ersten Flashen eines frischen Pro Micro** genügt oft ein einfacher
Reset, weil das Modul noch leer ist und ohnehin im Bootloader steht.

**Falscher Anschluss** — gemeint ist `RST` gegen `GND`, beide liegen auf der
rechten Stiftleiste nebeneinander.

## Prüfsummen

```
995e3e11b5357333569727529e88326333cffb72e6cc32e93cd0ee714375d42d  keypad4x4_default.hex
bea514d3c68f86d1b647a75fa26ab12ef3849a9da4298091c78cee10ecf70edc  keypad4x4_vial.hex
9e20bb151ac78a56d79cec0044b7cbb6d23fc76bdfa691837d731a94cf97e753  keypad4x4_zmk.uf2
```

Die Prüfsummen gelten für den Stand vom 8. Oktober 2026. Nach jedem
Neubau ändern sie sich.
