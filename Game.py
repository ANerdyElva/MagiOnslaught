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

playerCharacter = Character.Character( 'Player', Character.BaseStats, MoveSpeed = 1.0, RenderColor = Colors.Player )
enemyCharacter = [
        Character.Character( 'Orc', Character.BaseStats, MoveSpeed = 0.8, RenderColor = Colors.Orc, BaseHP = 4, Damge = 3, TurnRandomRange = 10, SleepColor = Colors.OrcSleeping, MoveColor = Colors.OrcMoving ),
        Character.Character( 'Goblin', Character.BaseStats, MoveSpeed = 1.2, RenderColor = Colors.Goblin, BaseHP = 2, Damage = 1, TurnRandomRange = 10, SleepColor = Colors.GoblinSleeping, MoveColor = Colors.GoblinMoving ),
        ]

class Game():
    def __init__( self ):
        self.world = World.World( Map.Map( 512, 512 ) )
        World.curTurn = 0

        root = RoomBuilder.build( self.world._map )
        self.root = root

        POINT_11 = Math2D.Point( 1, 1 )

        Funcs.buildMap( self.world._map, root )
        self.world._map.buildTcodMap()

        self.renderer = Systems.Renderer( self.world, Init.SCREEN_WIDTH, Init.SCREEN_HEIGHT )
        self.renderer.setMap( self.world._map )

        playerRoom = self.root.pickRandomRoom( lambda: random.random() < 0.5 )
        pos = Math2D.IntPoint( playerRoom.rect.center )

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

        def addEnemy( room ):
            if room.isLeaf == False:
                return
            if room == playerRoom:
                return

            prob = 1.4

            while random.random() < prob:
                rect = room.rect
                while True:
                    pos = rect.p1 + ( rect.dim * Math2D.Point( random.uniform( 0.2, 0.8 ), random.uniform( 0.2, 0.8 ) ) )
                    pos = Math2D.IntPoint( pos )

                    if not self.world._map.isBlocked( pos.x, pos.y ):
                        break

                enemy = Entity()
                enemy.target = player
                enemy.addComponent( Position( pos.x, pos.y ) )
                enemy.addComponent( TurnTaker( ai = TurnTakerAi() ) )
                enemy.addComponent( Renderable( chr(1) ) )
                enemy.addComponent( CharacterComponent( random.choice( enemyCharacter ) ) )
                self.world.addEntity( enemy )

                prob *= 0.7

        #for i in range( 5 ):
        #    addEnemy( room )
        self.root.iterateTree( addEnemy, None )
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

        #Take turns
        while True:
            success = self.actionSystem.process( SpellTurnTime )

            while self.curTurn + SpellTurnTime < self.actionSystem.curTurn:
                self.updateTurn()
                self.render()


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

        startTime = time.time()
        entList = self.world.getEntityByComponent( SpellComponent )
        for ent in entList:
            ent.getComponent( SpellComponent ).update()

        endTime = time.time()
        sleepTime = 0.01
        if len( entList ) > 0 and ( endTime - startTime ) < sleepTime:
            time.sleep( sleepTime - ( endTime - startTime ) )

        self.curTurn += SpellTurnTime
