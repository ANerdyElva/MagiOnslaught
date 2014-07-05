import libtcodpy as tcod

tileMap = {
        0x10: ' ',
        0x11: '\'',
        0x12: '\"',
        1: chr( 179 ), #Vertical wall
        2: chr( 179 ), #Vertical wall
        4: chr( 196 ), #Horizontal wall
        5: chr( 217 ), #Corner up and left
        6: chr( 192 ), #Corner up and right
        8: chr( 196 ), #Horizontal wall
        9: chr( 191 ), #Corner down and left
        10: chr( 218 ), #Corner down and right
        12: chr( 196 ), #Horizontal wall
        13: chr( 196 ), #Horizontal wall, end piece
        14: 'i',
        0x20: ' ', #Empty room tile
        }

print( tileMap )

def Render( map_, renderTarget ):
    if renderTarget is None:
        renderTarget = tcod.console_new( map_.width, map_.height )
        tcod.console_set_default_foreground( renderTarget, tcod.white )
    unknown = set()

    i = 0
    for y in range( map_.height ):
        for x in range( map_.width ):
            c = map_.tileType[ i ]
            if c in tileMap:
                tcod.console_put_char( renderTarget, x, y, tileMap[ c ], tcod.BKGND_NONE )
            else:
                tcod.console_put_char( renderTarget, x, y, '?', tcod.BKGND_NONE )
                unknown.add( c )


            i += 1

    print( unknown )
    return renderTarget
