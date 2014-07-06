import libtcodpy as libtcod
import functools

from Components import *
from Math2D import Point

world = None

class World():
    def __init__( self, _map ):
        global world
        world = World

        self._isDirty = True
        self.clear()

        self.entityList = []
        self.systems = []

        self._map = _map
        self.onRemove = []

    def clear( self ):
        if self._isDirty:
            self._entByComponentCache = {}
            self._entByBaseComponentCache = {}

    def removeEntity( self, ent ):
        if ent not in self.entityList:
            print( "Trying to remove entity %s but it's not in the list" % ent )
            return

        self.entityList.remove( ent )
        for n in self.onRemove:
            n( ent )
        for n in ent.onRemove:
            n( ent )

        self._isDirty = True

    def addEntity( self, ent ):
        assert( ent not in self.entityList )

        ent.setWorld( self )
        self.entityList.append( ent )
        self._isDirty = True

    def addSystem( self, system ):
        self.systems.append( system )

    def markDirty( self ):
        self._isDirty = True

    def getEntityByBaseComponent( self, *components ):
        self.clear()

        return self._getEntityByCb( components, lambda comp: [ ent
                for ent
                in self.entityList
                if comp in ent.componentBaseMap ], self._entByBaseComponentCache )

    def getEntityByComponent( self, *components ):
        self.clear()

        return self._getEntityByCb( components, lambda comp: [ ent
                for ent
                in self.entityList
                if comp in ent.componentMap ], self._entByComponentCache )

    def getEntitiesAtPos( self, checkPos, radius = 1 ):
        checkPos = Point( checkPos )

        baseList = self.getEntityByComponent( Position )
        retList = []

        radius = radius ** 2

        for ent in baseList:
            pos = Point( ent.getComponent( Position ) )

            if ( checkPos - pos ).squaredLength < radius:
                retList.append( ent )

        return retList

    def _getEntityByCb( self, components, callback, cache ):
        def get( comp ):
            if comp in cache:
                return cache[ comp ]

            ret = set( callback( comp ) )
            cache[ comp ] = ret

            return ret

        ret = get( components[ 0 ] )

        for i in range( 1, len( components ) ):
            comp = components[ i ]
            ret = ret.intersection( get( comp ) )

        if len( components ) > 0:
            cache[ components ] = ret

        return ret

    def process( self ):
        for system in self.systems:
            system.process()
