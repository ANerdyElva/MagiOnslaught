import libtcodpy as tcod
import Colors

tileMap = {
        0x10: ( ' ', Colors.Background ),
        0x11: ( '\'', Colors.Background ),
        0x12: ( '\"', Colors.Background ),
        1: ( chr( 179 ), Colors.Wall ), #Vertical wall
        2: ( chr( 179 ), Colors.Wall ), #Vertical wall
        3: ( chr( 179 ), Colors.Wall ), #Vertical wall
        4: ( chr( 196 ), Colors.Wall ), #Horizontal wall
        5: ( chr( 217 ), Colors.Wall ), #Corner up and left
        6: ( chr( 192 ), Colors.Wall ), #Corner up and right
        7: ( chr( 179 ), Colors.Wall ), #Vertical wall
        8: ( chr( 196 ), Colors.Wall ), #Horizontal wall
        9: ( chr( 191 ), Colors.Wall ), #Corner down and left
        10: ( chr( 218 ), Colors.Wall ), #Corner down and right
        11: ( chr( 179 ), Colors.Wall ), #Vertical wall
        12: ( chr( 196 ), Colors.Wall ), #Horizontal wall
        13: ( chr( 196 ), Colors.Wall ), #Horizontal wall, end piece
        14: ( chr( 196 ), Colors.Wall ), #Horizontal wall, end piece
        0x20: ' ', #Empty room tile
        }

for n in tileMap:
    if not isinstance( tileMap[ n ], tuple ):
        tileMap[ n ] = ( tileMap[ n ], Colors.White )


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
                tcod.console_put_char_ex( renderTarget, x, y, tileMap[ c ][ 0 ], tileMap[ c ][ 1 ], tcod.BKGND_NONE )
            else:
                tcod.console_put_char( renderTarget, x, y, '?', tcod.BKGND_NONE )
                unknown.add( c )


            i += 1

    if len( unknown ) > 0:
        print( unknown )

    return renderTarget
