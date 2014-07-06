import random
import libtcodpy as libtcod
import Constant
import Colors
from Math2D import *

class Component():
    def _setEntity( self, ent ):
        self.entity = ent

    def __str__( self ):
        return '{%s 0x%X}' % ( type( self ).__name__, hash( self ) )

    def finalize( self ):
        pass

class Position( Component ):
    def __init__( self, x, y ):
        self.x = x
        self.y = y

    def moveTo( self, other ):
        self.x = other.x
        self.y = other.y

    def __str__( self ):
        return '{Position %d/%d}' % ( self.x, self.y )

class CharacterComponent( Component ):
    def __init__( self, baseCharacter ):
        self.character = baseCharacter
        self.data = {}

        for n in baseCharacter.data:
            if n.startswith( 'Base' ):
                self.data[ n[4:] ] = baseCharacter.data[ n ]
            self.data[ n ] = baseCharacter.data[ n ]

    def __getattr__( self, key ):
        return self.data[ key ]
    def set( self, key, val ):
        if key.startswith( 'Base' ):
            raise ValueError( 'Unable to change base values (%s)' % key )

        self.data[ key ] = val

    def takeDamage( self, damageType, damage ):
        #TODO: Take damageType into account
        self.set( 'HP', self.HP - damage )
        print( self.HP )
        if self.HP < 0:
            self.entity.world.removeEntity( self.entity )
            print( 'Aaargh, I died.' )
    def makeWet( self ):
        self.state = 'Wet'
    def makeDry( self ):
        self.state = 'Wet'

class Action():
    def __init__( self, entity, name, params ):
        self.entity = entity
        self.name = name
        self.params = params

    def __str__( self ):
        return '[%s@Ent.%d %s (%s)]' % ( type(self).__name__, self.entity.id, self.name, self.params )

class Renderable( Component ):
    def __init__( self, char ):
        self.char = char
        self.color = Colors.White

    def draw( self, camX, camY ):
        pos = self.entity.getComponent( Position )
        libtcod.console_put_char_ex( 0, int( pos.x - camX ), int( pos.y - camY ), self.char, self.color, libtcod.BKGND_NONE )

    def __str__( self ):
        return '{Renderable %d}' % ( ord( self.char ) )

    def finalize( self ):
        char = self.entity.getComponent( CharacterComponent )
        if char is not None and char.RenderColor is not None:
            self.color = char.RenderColor


class TurnTaker( Component ):
    def __init__( self, ai = None, timeTillNextTurn = 0 ):
        self.ai = ai
        self.timeTillNextTurn = timeTillNextTurn

    def getNextTurn( self ):
        if self.ai is not None:
            return self.ai( self, self.entity )

    def finalize( self ):
        if self.entity.hasComponent( CharacterComponent ):
            self.randomRange = self.entity.getComponent( CharacterComponent ).TurnRandomRange
        else:
            self.randomRange = 0

_directions = ( ( 1, 0 ), ( 0, 1 ), ( -1, 0 ), ( 0, -1 ) )
class TurnTakerAi():
    def __call__( self, turnComponent, ent ):
        pos = Point( ent.getComponent( Position ) )
        targetPos = Point( ent.target.getComponent( Position ) )

        if ( targetPos - pos ).squaredLength < 2:
            return Action( ent, 'attack', ent.target )
        elif ( targetPos - pos ).squaredLength < 20 * 20:
            path = ent.world._map.findPath( pos, targetPos )

            if path is not None and len( path ) > 2:
                nextPoint = path[ -2 ]

                _x = int(math.floor(pos.x))
                _y = int(math.floor(pos.y)) 

                move = ( nextPoint[0] - _x, nextPoint[1] - _y )
                return Action( ent, 'move', move )

        return Action( ent, 'sleep', 400 )
