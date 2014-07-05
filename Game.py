import random
import libtcodpy as tcod
import time

import Init
import World
import Map
import Systems
import Math2D
import Funcs
import Actions
import Character
import Colors

from Entity import *
from Components import *
from Systems import *
from Spells import *

import RoomBuilder
from Constant import *

SpellTurnTime = 10

actionMap = {}
actionMap[ 'move' ] = Actions.Move
actionMap[ 'sleep' ] = Actions.Sleep
actionMap[ 'spawnorb' ] = SpawnOrbAction
actionMap[ 'fireorbs' ] = FireOrbsAction

playerCharacter = Character.Character( 'Player', Character.BaseStats, MoveSpeed = 2.0, RenderColor = Colors.Player )
enemyCharacter = Character.Character( 'Enemy', Character.BaseStats, MoveSpeed = 1.2, RenderColor = Colors.Enemy, BaseHP = 1 )

class Game():
    def __init__( self ):
        self.world = World.World( Map.Map( 512, 512 ) )
        World.curTurn = 0

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
        player.addComponent( CharacterComponent( playerCharacter ) )
        player.addComponent( Renderable( chr(2) ) )
        player.addComponent( SpellCaster() )
        self.world.addEntity( player )
        self.player = player

        for i in range( 4 ):
            self.world.addEntity( MakeOrb( player, i % 2, pos ) )

        def addEnemy( room ):
            if room.isLeaf == False:
                return

            rect = room.rect
            while True:
                pos = rect.p1 + ( rect.dim * Math2D.Point( random.uniform( 0.2, 0.8 ), random.uniform( 0.2, 0.8 ) ) )
                pos = Math2D.IntPoint( pos )

                if not self.world._map.isBlocked( pos.x, pos.y ):
                    break

            enemy = Entity()
            enemy.addComponent( Position( pos.x, pos.y ) )
            enemy.addComponent( TurnTaker( ai = TurnTakerAi() ) )
            enemy.addComponent( Renderable( chr(1) ) )
            enemy.addComponent( CharacterComponent( enemyCharacter ) )
            self.world.addEntity( enemy )

        for i in range( 5 ):
            addEnemy( room )
        #self.root.iterateTree( addEnemy, None )
        self.curTurn = 0

    def handleInput( self, key ):
        if key.c >= 48 and key.c <= 57: #Number keys
            spawnId = key.c - 48
            if spawnId in spawnableOrbs:
                orbType = spawnableOrbs[ spawnId ]

                self.playerAction = Action( self.player, 'spawnorb', orbType )

        elif key.c in ( ord('W'), ord('w') ):
            self.playerAction = Action( self.player, 'move', ( 0, -1 ) )
        elif key.c in ( ord('S'), ord('s') ):
            self.playerAction = Action( self.player, 'move', ( 0, 1 ) )
        elif key.c in ( ord('A'), ord('a') ):
            self.playerAction = Action( self.player, 'move', ( -1, 0 ) )
        elif key.c in ( ord('D'), ord('d') ):
            self.playerAction = Action( self.player, 'move', ( 1, 0 ) )
        elif key.c in ( ord( '.' ), ):
            self.playerAction = Action( self.player, 'sleep', 40 )

    def handleMouseInput( self, mouse ):
        pX = ( mouse.cx - self.renderer.hRW + 2 ) + self.renderer.cameraX
        pY = ( mouse.cy - self.renderer.hRH + 2 ) + self.renderer.cameraY

        if mouse.lbutton_pressed:
            self.playerAction = Action( self.player, 'fireorbs', ( pX, pY ) )

    def run( self ):
        self.isRunning = True

        self.render()
        mouse = tcod.Mouse()
        key = tcod.Key()

        while not tcod.console_is_window_closed() and self.isRunning:
            tcod.sys_check_for_event( tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse )

            if key.vk == tcod.KEY_ESCAPE:
                self.isRunning = False
            else:
                if key.vk is not tcod.KEY_NONE or mouse.lbutton_pressed:
                    if key.vk is not tcod.KEY_NONE:
                        self.handleInput( key )
                    else:
                        self.handleMouseInput( mouse )
                    self.runFrame( key )

    def runFrame( self, key ):
        self.world.process()
        i = 0

        self.waitingOnTurn = True
        self.render()

        startTime = time.time()

        #Take turns
        while True:
            success = self.actionSystem.process( SpellTurnTime )

            while self.curTurn + SpellTurnTime < self.actionSystem.curTurn:
                self.updateTurn()
                self.render()
                time.sleep( 0.10 )

            if not success:
                break

        self.waitingOnTurn = False
        self.render()

    def render( self ):
        #Update camera position
        pos = self.player.getComponent( Position )
        self.renderer.setCamera( pos.x, pos.y )

        self.renderer.render()

    def updateTurn( self ):
        World.curTurn = self.curTurn
        for ent in self.world.getEntityByComponent( SpellComponent ):
            ent.getComponent( SpellComponent ).update()

        self.curTurn += SpellTurnTime
