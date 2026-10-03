# Der C-Teil des Moduls. Die ZMK-Kopfdateien sind global eingebunden,
# deshalb genuegt hier die Quelldatei.
if(CONFIG_TASTENDRUCK_LED)
  zephyr_library()
  zephyr_library_sources(${ZEPHYR_CURRENT_MODULE_DIR}/src/tastendruck_led.c)
endif()
