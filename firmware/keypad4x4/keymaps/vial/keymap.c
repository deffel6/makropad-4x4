// Belegung fuer Vial. Die beiden oberen Ebenen bleiben leer: In Vial
// belegst du sie zur Laufzeit, ohne neu zu uebersetzen. Sie muessen hier
// aber angelegt sein, sonst hat Vial keinen Platz zum Schreiben.

#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

    [0] = LAYOUT_ortho_4x4(
        KC_P7,   KC_P8,   KC_P9,   KC_PSLS,
        KC_P4,   KC_P5,   KC_P6,   KC_PAST,
        KC_P1,   KC_P2,   KC_P3,   KC_PMNS,
        KC_P0,   KC_PDOT, KC_PENT, MO(1)
    ),

    [1] = LAYOUT_ortho_4x4(
        KC_F13,  KC_F14,  KC_F15,  KC_F16,
        KC_F17,  KC_F18,  KC_F19,  KC_F20,
        KC_F21,  KC_F22,  KC_F23,  KC_F24,
        KC_MUTE, KC_VOLD, KC_VOLU, KC_TRNS
    ),

    [2] = LAYOUT_ortho_4x4(
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS,
        KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS
    )
};
