# Fertige Firmware

Übersetzt und einsatzbereit — zum Flashen brauchst du weder QMK noch ein
Terminal, die [QMK Toolbox](https://github.com/qmk/qmk_toolbox/releases)
genügt.

| Datei | Größe | Belegung |
|---|---|---|
| `keypad4x4_default.hex` | 15.826 Bytes (55 %) | fest eingebaut |
| `keypad4x4_vial.hex` | 28.212 Bytes (98 %) | über Vial änderbar |

## Welche nehmen

**vial** für den Normalfall. Du änderst die Belegung dann in der Vial-App,
ohne je wieder zu flashen.

**default**, wenn du Vial nicht brauchst. Sie lässt 12 KB frei, in denen
später Erweiterungen Platz hätten — die Vial-Fassung ist mit 98 Prozent
randvoll.

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
eb3720195db8c39df6e22be1567f94a749dc5a6ef7856b84c1cad37751bfc8b5  keypad4x4_default.hex
594e2dab03956e62563ce7720427572946b67d1bedd4205df90dad1dd0f3d2b0  keypad4x4_vial.hex
```

Beide Dateien sind gegengelesen: keine Prüfsummenfehler im Intel-HEX-Format,
und die Vial-Fassung endet bei Adresse `0x6E34` — knapp unter `0x7000`, wo
der Bootloader beginnt.
