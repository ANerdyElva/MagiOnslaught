import libtcodpy as libtcod

from Components import TurnTaker

class ActionSystem():
    def __init__( self, world, actions ):
        self.toProcessList = []
        self.world = world
        self.actions = actions
        self.curTurn = 0

    def updateProcessList( self ):
        entities = self.world.getEntityByComponent( TurnTaker )
        self.toProcessList = []

        for ent in entities:
            turnTaker = ent.getComponent( TurnTaker )
            ent.__nextTurn = turnTaker.timeTillNextTurn

            self._insertEnt( ent )

    def _insertEnt( self, ent ):
        tp = self.toProcessList
        if ent in self.toProcessList:
            tp.pop( tp.index( ent ) )
        
        begin = 0
        end = len( tp ) - 1
        listEnd = len( tp )

        key = ent.__nextTurn
        #print()
        #print()
        #print( 'key: ', key )
        #print( [ ent.__nextTurn for ent in self.toProcessList ] )

        if listEnd == 0:
            tp.append( ent )
            return

        while end >= begin:
            mid = begin + ( ( end - begin ) // 2 )
            #print( '-- %d, %d, %d' % ( begin, mid, end ) )

            comp = tp[ mid ].__nextTurn

            if comp > key:
                begin = mid + 1
            elif comp < key:
                end = mid - 1
            else:
                break

            #print( '++ %d, %d, %d' % ( begin, mid, end ) )

        #Key not found, check if to insert before or after the current index
        if comp > key:
            tp.insert( mid + 1, ent )
        else:
            tp.insert( mid, ent )

        
    def resetTurnCount( self ):
        if self.curTurn > 100:
            for ent in self.toProcessList:
                ent.__nextTurn -= self.curTurn
            self.curTurn = 0


    def process( self ):
        if len( self.toProcessList ) == 0:
            self.updateProcessList()

        firstEnt = self.toProcessList.pop()
        turnTaker = firstEnt.getComponent( TurnTaker )

        action = turnTaker.getNextTurn()
        if action is None:
            self._insertEnt( firstEnt )
            return False

        self.curTurn = firstEnt.__nextTurn

        assert( action.name in self.actions )
        restTime = self.actions[ action.name ]( action.name, action.entity, action.params )
        assert( restTime is not None and restTime > 0 )

        firstEnt.__nextTurn = self.curTurn + restTime
        self._insertEnt( firstEnt )

        return True
