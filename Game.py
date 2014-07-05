import libtcodpy as tcod
import random

import Init
import World
import Map
import Systems
import Math2D

import RoomBuilder

BLOCKED = 1

class Game():
    def __init__( self ):
        self.world = World.World( Map.Map( 512, 512 ) )

        root = RoomBuilder.build( self.world._map )

        POINT_11 = Math2D.Point( 1, 1 )

        m = self.world._map

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


        self.renderer = Systems.Renderer( self.world, Init.SCREEN_WIDTH, Init.SCREEN_HEIGHT )
        self.renderer.setMap( self.world._map )

    def run( self ):
        self.isRunning = True

        self.renderer.render()

        while not tcod.console_is_window_closed() and self.isRunning:
            key = tcod.console_wait_for_keypress( True )

            if key.vk == tcod.KEY_ESCAPE:
                self.isRunning = False
            else:
                if key.vk == tcod.KEY_DOWN:
                    self.renderer.moveCamera( 0, 5 )
                elif key.vk == tcod.KEY_UP:
                    self.renderer.moveCamera( 0, -5 )
                elif key.vk == tcod.KEY_LEFT:
                    self.renderer.moveCamera( -5, 0 )
                elif key.vk == tcod.KEY_RIGHT:
                    self.renderer.moveCamera( 5, 0 )
                self.runFrame( key )

    def runFrame( self, key ):
        self.world.process()

        self.renderer.render()
