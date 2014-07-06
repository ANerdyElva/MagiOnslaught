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

SpellTurnTime = 20

actionMap = {}
actionMap[ 'move' ] = Actions.Move
actionMap[ 'sleep' ] = Actions.Sleep
actionMap[ 'spawnorb' ] = SpawnOrbAction
actionMap[ 'fireorbs' ] = FireOrbsAction
actionMap[ 'attack' ] = Actions.Attack

playerCharacter = Character.Character( 'Player', Character.BaseStats, Name = 'You', MoveSpeed = 1.0, RenderColor = Colors.Player, BaseHP = 20 )
enemyCharacterBase = [
        Character.Character( 'Orc', Character.BaseStats, Name = 'Orc', MoveSpeed = 0.8, RenderColor = Colors.Orc, BaseHP = 4, Damge = 3, TurnRandomRange = 10, SleepColor = Colors.OrcSleeping, MoveColor = Colors.OrcMoving ),
        Character.Character( 'Goblin', Character.BaseStats, Name = 'Goblin', MoveSpeed = 1.2, RenderColor = Colors.Goblin, BaseHP = 2, Damage = 1, TurnRandomRange = 10, SleepColor = Colors.GoblinSleeping, MoveColor = Colors.GoblinMoving ),
        ]
weapons = [ 'Sword', 'Mace', 'Axe' ]
enemyCharacter = [ Character.Character( base.name, base, Weapon = weapon ) for weapon in weapons for base in enemyCharacterBase ]

class Game():
    def __init__( self ):
        self.world = World.World( Map.Map( 512, 512 ) )
        self.score = 0
        self.shouldRestart = False
        self.autoSleep = False
        World.curTurn = 0

        root = RoomBuilder.build( self.world._map )
        self.root = root

        POINT_11 = Math2D.Point( 1, 1 )

        Funcs.buildMap( self.world._map, root )

        self.renderer = Systems.Renderer( self.world, Init.SCREEN_WIDTH, Init.SCREEN_HEIGHT )
        self.renderer.setMap( self.world._map )
        self.world._map.buildTcodMap()

        playerRoom = self.root.pickRandomRoom( lambda: random.random() < 0.5 )
        pos = Math2D.IntPoint( playerRoom.rect.center )

        self.actionSystem = ActionSystem( self.world, actionMap )

        self.playerAction = None
        def playerAction( __, _, wasBlocked ):
            ret = self.playerAction
            self.playerAction = None
            return ret

        player = Entity()
        player.addComponent( Position( pos.x, pos.y ) )
        player.addComponent( TurnTaker( ai = playerAction ) )
        player.addComponent( CharacterComponent( playerCharacter ) )
        player.addComponent( Renderable( chr(2) ) )
        player.addComponent( SpellCaster() )
        player.onRemove.append( self.playerDeath )
        self.world.addEntity( player )
        self.player = player

        self.renderer.player = player
        self.renderer.playerChar = player.getComponent( CharacterComponent )

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
                enemy.onRemove.append( self.addScore )
                enemy.addComponent( Position( pos.x, pos.y ) )
                enemy.addComponent( TurnTaker( ai = TurnTakerAi() ) )
                enemy.addComponent( Renderable( chr(1) ) )
                enemy.addComponent( CharacterComponent( random.choice( enemyCharacter ) ) )
                self.world.addEntity( enemy )

                prob *= 0.7

        #t = playerRoom
        #playerRoom = None
        #addEnemy( t )
        self.root.iterateTree( addEnemy, None )
        self.curTurn = 0

        self.render()

    def addScore( self, ent ):
        self.score += 10

        if len( [ ent for ent in self.world.getEntityByComponent( CharacterComponent ) if not ent == self.player ] ) == 0:
            startTime = time.time()
            def renderScreen( panel ):
                tcod.console_clear( panel )

                tcod.console_set_default_background( panel, tcod.Color( 210, 125, 44 ) )
                tcod.console_rect( panel, 0, 0, 40, 20, True, tcod.BKGND_SET )

                tcod.console_set_default_background( panel, tcod.Color( 132,126,135 ) )
                tcod.console_rect( panel, 1, 1, 38, 18, True, tcod.BKGND_SET )

                tcod.console_print_ex( panel, 20, 4, tcod.BKGND_NONE, tcod.CENTER, 'You won!' )
                tcod.console_print_ex( panel, 20, 6, tcod.BKGND_NONE, tcod.CENTER, 'You scored %d points.' % ( self.score ) )

                if time.time() - startTime > 2:
                    tcod.console_print_ex( panel, 20, 14, tcod.BKGND_NONE, tcod.CENTER, 'Press escape to restart.' )

            self.autoSleep = True
            self.shouldRestart = True
            self.renderer.panels.append( CreatePanel( self.renderer.renderWidth / 2 - 20, self.renderer.renderHeight / 2 - 10, 40, 20, renderScreen ) )



    def playerDeath( self, ent ):
        for ent in self.world.getEntityByComponent( TurnTaker, CharacterComponent ):
            ent.target = None

        startTime = time.time()
        def renderScreen( panel ):
            tcod.console_clear( panel )

            tcod.console_set_default_background( panel, tcod.Color( 210, 125, 44 ) )
            tcod.console_rect( panel, 0, 0, 40, 20, True, tcod.BKGND_SET )

            tcod.console_set_default_background( panel, tcod.Color( 132,126,135 ) )
            tcod.console_rect( panel, 1, 1, 38, 18, True, tcod.BKGND_SET )

            tcod.console_print_ex( panel, 20, 4, tcod.BKGND_NONE, tcod.CENTER, 'You died...' )
            tcod.console_print_ex( panel, 20, 6, tcod.BKGND_NONE, tcod.CENTER, 'You scored %d points.' % ( self.score ) )

            if time.time() - startTime > 2:
                tcod.console_print_ex( panel, 20, 14, tcod.BKGND_NONE, tcod.CENTER, 'Press escape to restart.' )

        self.shouldRestart = True
        self.renderer.panels.append( CreatePanel( self.renderer.renderWidth / 2 - 20, self.renderer.renderHeight / 2 - 10, 40, 20, renderScreen ) )

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

            if self.isRunning:
                self.runFrame( key )

    def runFrame( self, key ):
        self.world.process()
        i = 0

        self.waitingOnTurn = True
        self.render()
        startTime = time.time()
        if self.autoSleep:
            self.playerAction = Action( self.player, 'sleep', 100 )

        #Take turns
        while True:
            success = self.actionSystem.process( SpellTurnTime )

            while self.curTurn + SpellTurnTime < self.actionSystem.curTurn:
                self.updateTurn()
                self.render()

            if time.time() - startTime > 0.2:
                break
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
