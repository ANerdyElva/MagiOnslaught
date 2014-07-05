import libtcodpy as tcod

SCREEN_WIDTH = 140
SCREEN_HEIGHT = 80

def Init( title ):
    tcod.console_set_custom_font( b'data/fonts/terminal8x8_gs_ro.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW )
    tcod.console_init_root( SCREEN_WIDTH, SCREEN_HEIGHT, title.encode('ascii'), False )
