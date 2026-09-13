// 4x4-Makropad, Pro Micro.
//
// Zwei Ebenen. Unten rechts liegt die Umschalttaste: gedrueckt halten
// schaltet auf die zweite Ebene, loslassen zurueck. Kein Rasten, damit
// man nie in der falschen Ebene haengenbleibt.

#include QMK_KEYBOARD_H

enum ebenen { ZIFFERN, FUNKTION };

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

    // Zifferblock. Die P-Tasten sind die des Nummernblocks, nicht die der
    // oberen Zahlenreihe - Programme koennen die beiden unterscheiden.
    [ZIFFERN] = LAYOUT_ortho_4x4(
        KC_P7,   KC_P8,   KC_P9,   KC_PSLS,
        KC_P4,   KC_P5,   KC_P6,   KC_PAST,
        KC_P1,   KC_P2,   KC_P3,   KC_PMNS,
        KC_P0,   KC_PDOT, KC_PENT, MO(FUNKTION)
    ),

    // F13 bis F24 gibt es auf keiner gewoehnlichen Tastatur. Genau deshalb
    // sind sie nuetzlich: Kein Programm belegt sie bereits, und Hammerspoon
    // oder die Kurzbefehle-App koennen sie frei binden.
    [FUNKTION] = LAYOUT_ortho_4x4(
        KC_F13,  KC_F14,  KC_F15,  KC_F16,
        KC_F17,  KC_F18,  KC_F19,  KC_F20,
        KC_F21,  KC_F22,  KC_F23,  KC_F24,
        KC_MUTE, KC_VOLD, KC_VOLU, KC_TRNS
    )
};
