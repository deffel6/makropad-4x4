#pragma once

// Muss je Tastatur einmalig sein - Vial erkennt das Geraet daran wieder.
// Wuerfelt man sie nicht neu, verwechselt Vial zwei eigene Bauten.
#define VIAL_KEYBOARD_UID {0xB7, 0x07, 0x80, 0xF3, 0x47, 0x36, 0x82, 0x28}

// Entsperrgriff: die beiden oberen linken Tasten gleichzeitig halten.
// Ohne ihn laesst Vial die Belegung nicht aendern - das schuetzt davor,
// dass ein Programm die Tastatur im Hintergrund umbelegt.
#define VIAL_UNLOCK_COMBO_ROWS {0, 0}
#define VIAL_UNLOCK_COMBO_COLS {0, 1}

// Jede Ebene belegt Platz im Flash. Drei reichen fuer ein Makropad.
#define DYNAMIC_KEYMAP_LAYER_COUNT 3
