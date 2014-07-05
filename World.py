import libtcodpy as libtcod

from Components import *

class World():
    def __init__( self, _map ):
        self._isDirty = True
        self.clear()

        self.entityList = []
        self.systems = []

        self._map = _map

    def clear( self ):
        if self._isDirty:
            self._entByComponentCache = {}
            self._entByBaseComponentCache = {}

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
