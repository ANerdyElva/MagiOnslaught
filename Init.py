import libtcodpy as tcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 60

def Init( title ):
    tcod.console_set_custom_font( b'data/fonts/arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD )
    tcod.console_init_root( SCREEN_WIDTH, SCREEN_HEIGHT, title.encode('ascii'), False )
