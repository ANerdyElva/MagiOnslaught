import Math2D
from Constant import *
import random

def buildMap( m, root ):
    POINT_11 = Math2D.Point( 1, 1 )

    for i in range( m.width * m.height ):
        m.tileType[ i ] = 0
        m.tileData[ i ] = BLOCKED


    data = m.newByteArray()
    for room in root.roomList:
        for i in m.iterateRect( Math2D.Rect( room.p1, room.p2 ), inclusive = True ):
            data[i] = 1

    _px = m.I( 1, 0 )
    _mx = m.I( -1, 0 )
    _py = m.I( 0, 1 )
    _my = m.I( 0, -1 )

    walls = []

    for i in m.iterateRect( Math2D.Rect( 2, 2, m.width - 2, m.height - 2 ), inclusive = True ):
        if data[ i ] == 0: #Closed tile
            tile = ( data[ i + _px ] << 0 ) | ( data[ i + _mx ] << 1 ) | ( data[ i + _py ] << 2 ) | ( data[ i + _my ] << 3 )
        else: #Open tile
            tile = 0x20
            m.tileData[ i ] = 0
        m.tileType[ i ] = tile

    for i in range( m.width * m.height ):
        if m.tileType[ i ] == 0:
            rand = random.random()

            if rand < 0.025:
                m.tileType[ i ] = 0x12
            elif rand < 0.05:
                m.tileType[ i ] = 0x11
            else:
                m.tileType[ i ] = 0x10

