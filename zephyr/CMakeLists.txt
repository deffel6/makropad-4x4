# Der C-Teil des Moduls.
#
# Die ZMK-Kopfdateien (zmk/event_manager.h und Co.) liegen in zmk/app/include.
# Modulen gibt ZMK nur app/module/include mit, deshalb muss der Pfad hier
# ausdruecklich dazu. CMAKE_SOURCE_DIR ist bei einem ZMK-Bau immer zmk/app.
if(CONFIG_TASTENDRUCK_LED)
  zephyr_library()
  zephyr_library_include_directories(${CMAKE_SOURCE_DIR}/include)
  zephyr_library_sources(${ZEPHYR_CURRENT_MODULE_DIR}/src/tastendruck_led.c)
endif()
