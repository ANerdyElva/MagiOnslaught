import random
import libtcodpy as tcod

import Init
import World
import Map
import Systems
import Math2D
import Funcs
import Actions

from Entity import *
from Components import *
from Systems import *

import RoomBuilder
from Constant import *

actionMap = {}
actionMap[ 'move' ] = Actions.Move
actionMap[ 'sleep' ] = Actions.Sleep

class Game():
    def __init__( self ):
        self.world = World.World( Map.Map( 512, 512 ) )

        root = RoomBuilder.build( self.world._map )
        self.root = root

        POINT_11 = Math2D.Point( 1, 1 )

        m = self.world._map
        Funcs.buildMap( m, root )

        self.renderer = Systems.Renderer( self.world, Init.SCREEN_WIDTH, Init.SCREEN_HEIGHT )
        self.renderer.setMap( self.world._map )

        room = self.root.pickRandomRoom( lambda: random.random() < 0.5 )
        pos = Math2D.IntPoint( room.rect.center )

        self.actionSystem = ActionSystem( self.world, actionMap )

        self.playerAction = None
        def playerAction( __, _ ):
            ret = self.playerAction
            self.playerAction = None
            return ret

        player = Entity()
        player.addComponent( Position( pos.x, pos.y ) )
        player.addComponent( TurnTaker( ai = playerAction ) )
        player.addComponent( Renderable( '@' ) )
        self.world.addEntity( player )
        self.player = player

        def addEnemy( room ):
            rect = room.rect
            while True:
                pos = rect.p1 + ( rect.dim * Math2D.Point( random.uniform( 0.2, 0.8 ), random.uniform( 0.2, 0.8 ) ) )
                pos = Math2D.IntPoint( pos )

                if not self.world._map.isBlocked( pos.x, pos.y ):
                    break

            enemy = Entity()
            enemy.addComponent( Position( pos.x, pos.y ) )
            enemy.addComponent( TurnTaker( ai = TurnTakerAi() ) )
            enemy.addComponent( Renderable( '?' ) )
            self.world.addEntity( enemy )

        #for i in range( 200 ):
        #    addEnemy( room )
        self.root.iterateTree( addEnemy, None )

    def handleInput( self, key ):
            if key.c in ( ord('W'), ord('w') ):
                self.playerAction = Action( self.player, 'move', ( 0, -1 ) )
            elif key.c in ( ord('S'), ord('s') ):
                self.playerAction = Action( self.player, 'move', ( 0, 1 ) )
            elif key.c in ( ord('A'), ord('a') ):
                self.playerAction = Action( self.player, 'move', ( -1, 0 ) )
            elif key.c in ( ord('D'), ord('d') ):
                self.playerAction = Action( self.player, 'move', ( 1, 0 ) )

    def run( self ):
        self.isRunning = True

        self.render()

        while not tcod.console_is_window_closed() and self.isRunning:
            key = tcod.console_wait_for_keypress( True )

            if key.vk == tcod.KEY_ESCAPE:
                self.isRunning = False
            else:
                self.handleInput( key )
                self.runFrame( key )

    def runFrame( self, key ):
        self.world.process()
        i = 0

        #Take turns
        while self.playerAction is not None:
            success = self.actionSystem.process()

            i += 1
            if i % 10 == 0:
                self.render()
        self.render()

    def render( self ):
        #Update camera position
        pos = self.player.getComponent( Position )
        self.renderer.setCamera( pos.x, pos.y )

        self.renderer.render()
