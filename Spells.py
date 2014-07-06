import libtcodpy as tcod
from WeakList import *
import math

import World
from Entity import *
from Constant import *
from Components import *
from Math2D import *
import Funcs

OrbList = WeakList()

def MakeOrb( parent, orbType, pos ):
    orb = Entity()
    orb.addComponent( Position( pos.x, pos.y ) )
    orb.addComponent( SpellComponent( orbType, parent ) )
    orb.addComponent( SpellRenderable( orbType, parent ) )
    return orb

def damage( orb, char ):
    char.takeDamage( orb, orbDamage[ orb ] )

def destroy( orb ):
    orb.world.removeEntity( orb )

def merge( orb1, orb2, newOrb ):
    _orb1 = orb1.getComponent( SpellComponent )
    _orb2 = orb2.getComponent( SpellComponent )
    if _orb1.orbType == _orb2.orbType:
        Funcs.AddLog( 'Two %s orbs merged into a %s orb.' % ( orbNames[_orb1.orbType], orbNames[newOrb] ) )
    else:
        Funcs.AddLog( 'A %s orb and a %s orb have merged into a %s orb.' % ( orbNames[_orb1.orbType], orbNames[_orb2.orbType], orbNames[newOrb] ) )

    if hasattr( orb1, 'isMerged' ) or hasattr( orb2, 'isMerged' ):
        print( 'Aborting merge.' )

    world = orb1.world
    world.removeEntity( orb1 )
    world.removeEntity( orb2 )

    orb1.isMerged = True
    orb2.isMerged = True

    pos1 = orb1.getComponent( Position )
    pos2 = orb2.getComponent( Position )

    newOrb1 = MakeOrb( None, newOrb, pos1 )
    newOrb2 = MakeOrb( None, newOrb, pos2 )

    diff = ( Point( pos1 ) - Point( pos2 ) ).normalized()
    newOrb1.getComponent( SpellComponent ).vel = diff * 3
    newOrb2.getComponent( SpellComponent ).vel = diff * -3

    world.addEntity( newOrb1 )
    world.addEntity( newOrb2 )


CollisionTypes = {
        ( WaterOrb, EnemyCollisionId ): lambda orb, enemy, char: ( char.makeWet(), damage( WaterOrb, char ) ),
        ( FireOrb, EnemyCollisionId ): lambda orb, enemy, char: ( char.makeDry(), damage( FireOrb, char ) ),
        ( EarthOrb, EnemyCollisionId ): lambda orb, enemy, char: ( damage( EarthOrb, char ) ),
        ( AirOrb, EnemyCollisionId ): lambda orb, enemy, char: ( damage( AirOrb, char ) ),
        ( SteamOrb, EnemyCollisionId ): lambda orb, enemy, char: ( damage( SteamOrb, char ) ),
        ( LightningOrb, EnemyCollisionId ): lambda orb, enemy, char: ( damage( LightningOrb, char ) ),

        ( WaterOrb, FireOrb ): lambda orb1, orb2, extra: ( merge( orb1, orb2, SteamOrb ) ),
        ( WaterOrb, SteamOrb ): lambda orb1, orb2, extra: ( merge( orb1, orb2, SteamOrb ) ),
        ( FireOrb, SteamOrb ): lambda orb1, orb2, extra: ( merge( orb1, orb2, SteamOrb ) ),

        ( FireOrb, AirOrb ): lambda orb1, orb2, extra: ( merge( orb1, orb2, LightningOrb ) ),
        ( FireOrb, LightningOrb ): lambda orb1, orb2, extra: ( merge( orb1, orb2, LightningOrb ) ),
        ( AirOrb, LightningOrb ): lambda orb1, orb2, extra: ( merge( orb1, orb2, LightningOrb ) ),

        ( WaterOrb, LightningOrb ): lambda orb1, orb2, _: ( destroy( orb1 ), destroy( orb2 ) ),
        ( SteamOrb, LightningOrb ): lambda orb1, orb2, _: ( destroy( orb1 ), destroy( orb2 ) ),
        ( EarthOrb, LightningOrb ): lambda orb1, orb2, _: ( destroy( orb1 ), destroy( orb2 ) ),

        ( EarthOrb, WallCollisionId ): lambda orb1, _, __: destroy( orb1 ),
        StopCollisionId: lambda orb1: destroy( orb1 ),
        }


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

        if self.parent is not None:
            self.parentPos = self.parent.getComponent( Position )

            self.caster = self.parent.getComponent( SpellCaster )
            self.caster.addOrb( self )
        else:
            self.parentPos = None
            self.caster = None

    def update( self ):
        self.updateCollision()
        self.updateVel()

    def fireTo( self, x, y ):
        if self.caster is not None:
            self.caster.removeOrb( self )

        delta = Point( self.pos.x - x, self.pos.y  - y )
        self.vel = delta * -0.1

    def updateCollision( self ):
        m = self.entity.world._map
        traveled = 0

        def p():
            return Point( int( math.floor( self.pos.x ) ), int( math.floor( self.pos.y ) ) )

        pP = None
        lP = p()

        isBlocked = False
        wallBlocked = False
        entList = []
        def checkBlock():
            nonlocal isBlocked
            nonlocal wallBlocked
            nonlocal entList

            wallBlocked = m.hasFlag( lP.x, lP.y, BLOCKED )
            entList = self.getCollidingEnts( lP ) if not wallBlocked else tuple()

            isBlocked = wallBlocked or len( entList ) > 0

        checkBlock()
        if wallBlocked:
            self._doCollide( self.orbType, StopCollisionId, self.vel, None )
            print( 'Spawned in a wall :(' )
            return

        #Aaaaargh this is a bloody stupid implementation but it works, gamejam ho!
        while not isBlocked and traveled <= 1:
            self.pos.x += self.vel.x * 0.2
            self.pos.y += self.vel.y * 0.2
            traveled += 0.2

            pP = lP
            lP = p()
            checkBlock()

        if isBlocked:
            self.onCollide( wallBlocked, entList )

            self.pos.x -= self.vel.x * 0.25
            self.pos.y -= self.vel.y * 0.25

            if pP is not None:
                if pP.x != lP.x: #Go back on the X axis
                    self.vel.x *= -0.9
                else:
                    self.vel.y *= -0.9
        else:
            if self.caster is not None:
                return

            for otherEnt in self.entity.world.getEntityByComponent( Position, SpellComponent ):
                otherPos = otherEnt.getComponent( Position )
                if Point( otherPos.x - self.pos.x, otherPos.y - self.pos.y ).squaredLength < 2 * 2:
                    self.onCollide( False, ( otherEnt, ) )

            self.vel *= 0.95
            if self.vel.squaredLength < 0.1 * 0.1:
                self._doCollide( self.orbType, StopCollisionId, self.vel, None )


    def getCollidingEnts( self, nP ):
        ents = self.entity.world.getEntitiesAtPos( nP, 2 )
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

        if wallBlocked:
            self._doCollide( self.orbType, WallCollisionId, self.pos, None )

        for other in entAtPos:
            spell = other.getComponent( SpellComponent )
            char = other.getComponent( CharacterComponent )

            if char is not None:
                self._doCollide( self.orbType, EnemyCollisionId, other, char )
            if spell is not None:
                self._doCollide( self.orbType, spell.orbType, other, spell )

            #print( 'KABOOM', wallBlocked, other, other.getComponent( SpellComponent ), other.getComponent( CharacterComponent ) )
            break
    def _doCollide( self, a, b, other, extraParam ):
        ent = self.entity
        col = ( a, b )
        if col in CollisionTypes:
            CollisionTypes[ col ]( ent, other, extraParam )
        elif ( b, a ) in CollisionTypes:
            CollisionTypes[ ( b, a ) ]( other, ent, extraParam )
        elif b < 0 and b in CollisionTypes:
            CollisionTypes[ b ]( ent )

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
        if self.parent is None:
            self.char = orbColors[ self.orbType ][ 1 ]


def SpawnOrbAction( actionName, world, ent, params ):
    world.addEntity( MakeOrb( ent, params, ent.getComponent( Position ) ) )
    Funcs.AddLog( 'Creating a %s orb.' % ( orbNames[ params ] ) )
    return 5
def FireOrbsAction( actionName, world, ent, params ):
    caster = ent.getComponent( SpellCaster )
    spell = caster.orbList

    if len( spell ) == 0:
        Funcs.AddLog( 'No orb to release!' )
        return None

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
