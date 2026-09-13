# Vial setzt auf VIA auf, beides muss an sein.
VIA_ENABLE  = yes
VIAL_ENABLE = yes

# Der Pro Micro hat nach Abzug des Bootloaders nur 28 KB Platz, und Vial
# bringt viel mit. Deshalb alles abschalten, was ein Makropad nicht braucht.
LTO_ENABLE         = yes   # spart am meisten: der Binder wirft Ungenutztes raus
MOUSEKEY_ENABLE    = no    # Mauszeiger ueber Tasten
NKRO_ENABLE        = no    # beliebig viele Tasten gleichzeitig
CONSOLE_ENABLE     = no
COMMAND_ENABLE     = no
SPACE_CADET_ENABLE = no
GRAVE_ESC_ENABLE   = no
MAGIC_ENABLE       = no    # Tastenvertauschungen zur Laufzeit
MUSIC_ENABLE       = no
