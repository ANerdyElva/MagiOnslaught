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

orbColors = {
        WaterOrb: ( tcod.Color( 0, 0, 255 ), chr( 7 ) ),
        FireOrb: ( tcod.Color( 255, 0, 0 ), chr( 15 ) ),
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
        self.updatePos()

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

            minTime = min( time.x, time.y )
            assert( minTime > 0 )
            distance += minTime

            if distance > 1:
                break

            nP = ( p + v * ( minTime ) ).floor()
            if m.hasFlag( int( nP.x ), int( nP.y ), BLOCKED ):
                p -= self.vel * ( minTime + 0.001 )
                if time.x < time.y:
                    v.x = v.x * -0.9
                else:
                    v.y = v.y * -0.9
                p += self.vel * ( minTime + 0.001 )
                self.onCollide()


        self.pos.x = p.x
        self.pos.y = p.y
        self.vel.x = v.x
        self.vel.y = v.y

    def onCollide( self ):
        if self.caster is not None:
            self.caster.removeOrb( self )
            self.entity.getComponent( SpellRenderable ).orbType = 1
        else:
            print( 'KABOOM' )

    def updateVel( self ):
        if self.parentPos is None:
            return

        targetPos = PointFromAngle( ( self.orbI * 2.0 * math.pi ) / self.orbLen + ( World.curTurn * 0.005 ), RotateDist )
        targetPos += Point( self.parentPos.x, self.parentPos.y )

        pos = Point( self.pos.x, self.pos.y )
        targetVel = ( targetPos - pos ) * 0.2

        self.vel = ( self.vel * 4 + targetVel ) * 0.2

        self._isUpdated = True
    def updatePos( self ):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y


    def updateOrb( self ):
        if self.caster is not None:
            self.orbI = self.caster.orbList.index( self )
            self.orbLen = len( self.caster.orbList )

            OrbList.append( self )

            if not self._isUpdated:
                targetPos = PointFromAngle( ( self.orbI * 2.0 * math.pi ) / self.orbLen + ( World.curTurn * 0.005 ), RotateDist + 2 )
                targetPos += Point( self.parentPos.x, self.parentPos.y )
                self.pos.x = targetPos.x
                self.pos.y = targetPos.y


class SpellRenderable( Renderable ):
    def __init__( self, orbType, parent ):
        self.parent = parent
        self.orbType = orbType
        self.orbType = 0
        super().__init__( '=' )

    def draw( self, camX, camY ):
        libtcod.console_put_char_ex(
                0,
                int( self.pos.x - camX ), int( self.pos.y - camY ),
                chr( 7 ),
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
