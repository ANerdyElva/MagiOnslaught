import random
import libtcodpy as libtcod

class Component():
    def _setEntity( self, ent ):
        self.entity = ent

class Position( Component ):
    def __init__( self, x, y ):
        self.x = x
        self.y = y

class CharacterComponent( Component ):
    def __init__( self, baseCharacter ):
        pass

class Action():
    def __init__( self, entity, name, params ):
        self.entity = entity
        self.name = name
        self.params = params

class Renderable( Component ):
    def __init__( self, char ):
        self.char = char

    def draw( self, camX, camY ):
        pos = self.entity.getComponent( Position )
        libtcod.console_put_char( 0, int( pos.x - camX ), int( pos.y - camY ), self.char, libtcod.BKGND_NONE )

class TurnTaker( Component ):
    def __init__( self, ai = None, timeTillNextTurn = 0 ):
        self.ai = ai
        self.timeTillNextTurn = timeTillNextTurn

    def getNextTurn( self ):
        if self.ai is not None:
            return self.ai( self, self.entity )

_directions = ( ( 1, 0 ), ( 0, 1 ), ( -1, 0 ), ( 0, -1 ) )
class TurnTakerAi():
    def __call__( self, turnComponent, ent ):
        if ent.hasComponent( Position ):
            return Action( ent, 'move', random.choice( _directions ) )
