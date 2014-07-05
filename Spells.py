import libtcodpy as tcod
from WeakList import *
import math

import World
from Entity import *
from Constant import *
from Components import *
from Math2D import *

WaterOrb = 0
FireOrb = 1

RotateDist = 7

spawnableOrbs = {
        1: WaterOrb,
        2: FireOrb,
        }
orbNames = {
        WaterOrb: "Water",
        FireOrb: "Fire",
        }
orbColors = {
        WaterOrb: ( tcod.Color( 0, 0, 255 ), chr( 7 ) ),
        FireOrb: ( tcod.Color( 255, 0, 0 ), chr( 15 ) ),
        }

orbDamage = {
        WaterOrb: 2,
        FireOrb: 5,
        }
EnemyCollisionId = -1
StopCollisionId = -2 #For when the velocity of an orb is close to 0

CollisionTypes = {
        ( WaterOrb, EnemyCollisionId ): lambda orb, enemy, char: ( char.makeWet(), char.takeDamage( WaterOrb, orbDamage[WaterOrb] ) ),
        ( FireOrb, EnemyCollisionId ): lambda orb, enemy, char: ( char.makeDry(), char.takeDamage( WaterOrb, orbDamage[WaterOrb] ) ),
        }

OrbList = WeakList()

class SpellCaster( Component ):
    def __init__( self ):
        self.orbList = []

    def addOrb( self, orb ):
        self.orbList.append( orb )

        for orb in self.orbList:
            orb.updateOrb()

    def removeOrb( self, orb ):
        orb.parent = None
        orb.caster = None
        orb.parentPos = None

        orb.updateOrb()

        self.orbList.remove( orb )

        for orb in self.orbList:
            orb.updateOrb()

class SpellComponent( Component ):
    def __init__( self, orbType, parent ):
        self.parent = parent
        self.orbType = orbType

        self.vel = Point( 0, 0 )
        self._isUpdated = False

    def finalize( self ):
        self.pos = self.entity.getComponent( Position )

        self.parentPos = self.parent.getComponent( Position )

        self.caster = self.parent.getComponent( SpellCaster )
        self.caster.addOrb( self )

    def update( self ):
        self.updateCollision()
        self.updateVel()

    def fireTo( self, x, y ):
        if self.caster is not None:
            self.caster.removeOrb( self )

        delta = Point( self.pos.x - x, self.pos.y  - y )
        self.vel = delta * -0.1

    def updateCollision( self ):
        p = Point( self.pos )
        v = Point( self.vel )

        if v.x == 0 or v.y == 0:
            return

        m = self.entity.world._map

        distance = 0
        m = self.entity.world._map
        while True:
            wall = p.floor() + Point( 0.5, 0.5 ) + v.copysign( 0.5 )
            delta = wall - p
            time = delta / v

            remaining = 1.0 - distance
            if time.x < 0.00001:
                time.x = 2000000000000
            if time.y < 0.00001:
                time.y = 2000000000000

            if time.x > remaining:
                time.x = remaining
            if time.y > remaining:
                time.y = remaining

            minTime = min( time.x, time.y )
            assert( minTime > -0.001 )
            distance += minTime
            print( time, minTime, remaining, v * minTime )

            if distance > 1:
                break

            nP = ( p + v * ( minTime ) ).floor()
            nP = nP.int()
            
            wallBlocked = m.hasFlag( nP.x, nP.y, BLOCKED )
            entAtPos = self.getCollidingEnts( nP ) if not wallBlocked else tuple()

            if wallBlocked or len( entAtPos ) > 0:
                self.onCollide( wallBlocked, entAtPos )
                if time.x < time.y:
                    v.x = v.x * -0.9
                else:
                    v.y = v.y * -0.9
            p += self.vel * ( minTime + 0.001 )
            

            if distance >= 1:
                break



        self.pos.x = p.x
        self.pos.y = p.y
        self.vel.x = v.x
        self.vel.y = v.y

    def getCollidingEnts( self, nP ):
        ents = self.entity.world.getEntitiesAtPos( nP )
        ret = []

        for ent in ents:
            if self.entity == ent:
                continue
            if self.parent == ent:
                continue

            otherSpell = ent.getComponent( SpellComponent )
            if otherSpell is not None:
                if otherSpell.parent == self.parent:
                    continue

            ret.append( ent )
        return ret



    def onCollide( self, wallBlocked, entAtPos ):
        if self.caster is not None:
            self.caster.removeOrb( self )

        for other in entAtPos:
            spell = other.getComponent( SpellComponent )
            char = other.getComponent( CharacterComponent )

            if char is not None:
                self._doCollide( self.orbType, EnemyCollisionId, other, char )
            if spell is not None:
                self._doCollide( self.orbType, spell.orbType, other, spell )

            print( 'KABOOM', wallBlocked, other, other.getComponent( SpellComponent ), other.getComponent( CharacterComponent ) )
            break
    def _doCollide( self, a, b, other, extraParam ):
        col = ( a, b )
        if col in CollisionTypes:
            CollisionTypes[ col ]( self, other, extraParam )
        elif ( b, a ) in CollisionTypes:
            CollisionTypes[ ( b, a ) ]( other, self, extraParam )

    def updateVel( self ):
        if self.parentPos is None:
            return

        targetPos = PointFromAngle( ( self.orbI * 2.0 * math.pi ) / self.orbLen + ( World.curTurn * 0.005 ), RotateDist )
        targetPos += Point( self.parentPos.x, self.parentPos.y )

        pos = Point( self.pos.x, self.pos.y )
        targetVel = ( targetPos - pos ) * 0.2

        self.vel = ( self.vel * 4 + targetVel ) * 0.2

        self._isUpdated = True


    def updateOrb( self ):
        if self.caster is not None:
            self.entity.getComponent( SpellRenderable ).char = chr( 7 )
            self.orbI = self.caster.orbList.index( self )
            self.orbLen = len( self.caster.orbList )

            OrbList.append( self )

            if not self._isUpdated:
                self._isUpdated = True
                targetPos = PointFromAngle( ( self.orbI * 2.0 * math.pi ) / self.orbLen + ( World.curTurn * 0.005 ), RotateDist + 2 )
                targetPos += Point( self.parentPos.x, self.parentPos.y )
                self.pos.x = targetPos.x
                self.pos.y = targetPos.y
        else:
            self.entity.getComponent( SpellRenderable ).char = chr( 15 )


class SpellRenderable( Renderable ):
    def __init__( self, orbType, parent ):
        self.parent = parent
        self.orbType = orbType
        super().__init__( chr( 7 ) )

    def draw( self, camX, camY ):
        libtcod.console_put_char_ex(
                0,
                int( self.pos.x - camX ), int( self.pos.y - camY ),
                self.char,
                orbColors[ self.orbType ][ 0 ],
                libtcod.BKGND_NONE )

    def finalize( self ):
        self.pos = self.entity.getComponent( Position )


def MakeOrb( parent, orbType, pos ):
    orb = Entity()
    orb.addComponent( Position( pos.x, pos.y ) )
    orb.addComponent( SpellComponent( orbType, parent ) )
    orb.addComponent( SpellRenderable( orbType, parent ) )
    return orb

def SpawnOrbAction( actionName, world, ent, params ):
    world.addEntity( MakeOrb( ent, params, ent.getComponent( Position ) ) )
    print( 'Creating orb: %s (%d)' % ( orbNames[ params ], params ) )
    return 5
def FireOrbsAction( actionName, world, ent, params ):
    caster = ent.getComponent( SpellCaster )
    spell = caster.orbList

    if len( spell ) == 0:
        print( 'No orb to release!' )
        return 1

    p = Point( *params )

    closestI = 0
    closestDist = ( Point( spell[0].entity.getComponent( Position ) ) - p ).squaredLength

    for i in range( 1, len( spell ) ):
        dist = ( Point( spell[i].entity.getComponent( Position ) ) - p ).squaredLength
        if dist < closestDist:
            closestDist = dist
            closestI = i

    spell = spell[ closestI ]
    caster.removeOrb( spell )

    spell.fireTo( params[ 0 ], params[ 1 ] )
    return 25
