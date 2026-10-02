// Belegung fuer Vial. Alle 16 Tasten sind Programmtasten, keine ist fuer
// einen Ebenenwechsel reserviert. Die beiden oberen Ebenen bleiben leer:
// In Vial belegst du sie zur Laufzeit, ohne neu zu uebersetzen. Sie muessen
// hier aber angelegt sein, sonst hat Vial keinen Platz zum Schreiben.
//
// Reihen 1-3: F13 bis F24 (gibt es auf keiner gewoehnlichen Tastatur).
// Reihe 4: F13 bis F16 mit Strg+Umschalt+Alt (MEH), denn mehr als zwoelf
// freie F-Tasten kennt der USB-Standard nicht.

#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

    [0] = LAYOUT_ortho_4x4(
        KC_F13,       KC_F14,       KC_F15,       KC_F16,
        KC_F17,       KC_F18,       KC_F19,       KC_F20,
        KC_F21,       KC_F22,       KC_F23,       KC_F24,
        MEH(KC_F13),  MEH(KC_F14),  MEH(KC_F15),  MEH(KC_F16)
    ),

    [1] = LAYOUT_ortho_4x4(
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS
    ),

    [2] = LAYOUT_ortho_4x4(
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS
    )
};
