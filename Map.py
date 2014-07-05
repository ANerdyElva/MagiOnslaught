import Constant

class Map():
    def __init__( self, width, height ):
        self.width = width
        self.height = height

        self.tileType = self.newByteArray()
        self.tileData = self.newByteArray()

    def I( self, x, y ):
        return ( y * self.width ) + x

    def setI( self, i, tile ):
        if type(tile) is str:
            self.tileType[ i ] = ord( tile[ 0 ] )
        else:
            self.tileType[ i ] = tile

    def set( self, x, y, tile ):
        if type(tile) is str:
            self.tileType[ self.I( x, y ) ] = ord( tile[ 0 ] )
        else:
            self.tileType[ self.I( x, y ) ] = tile

    def setFlagI( self, i, flag ):
        if flag < 0:
            self.tileData[ i ] &= ~(-flag)
        else:
            self.tileData[ i ] |= flag
    def setFlagsI( self, i, flag ):
        self.tileData[ i ] = flag

    def setFlag( self, x, y, flag ):
        self.setFlagI( self.I( x, y ), flag )
    def setFlags( self, x, y, flag ):
        self.setFlagsI( self.I( x, y ), flag )

    def hasFlag( self, x, y, flag ):
        f = self.getFlags( x, y )
        return ( f & flag ) > 0

    def getFlagsI( self, i ):
        return self.tileData[ i ]
    def getFlags( self, x, y ):
        return self.getFlagsI( self.I( x, y ) )

    def iterateLine( self, xStart, xEnd, y ):
        i = self.I( 0, y )
        return range( i + xStart, i + xEnd )

    def newByteArray( self ):
        return bytearray( self.width * self.height )

    def iterateRect( self, rect, inclusive = True ):
        #>>> [(x,y) for x in range(5,10) for y in range(x+15,x+20)]
        _x1 = rect.p1.x
        _y1 = rect.p1.y
        _x2 = rect.p2.x
        _y2 = rect.p2.y

        if inclusive:
            _x2 += 1
            _y2 += 1

        return [ i for y in range(_y1,_y2) for i in self.iterateLine(_x1,_x2,y) ]

    def isBlocked( self, x, y ):
        return self.hasFlag( x, y, Constant.BLOCKED )
