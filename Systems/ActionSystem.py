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

        if listEnd == 0:
            tp.append( ent )
            return

        while end >= begin:
            mid = begin + ( ( end - begin ) // 2 )

            comp = tp[ mid ].__nextTurn

            if comp > key:
                begin = mid + 1
            elif comp < key:
                end = mid - 1
            else:
                break

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


    def process( self, maxTime ):
        if len( self.toProcessList ) == 0:
            self.updateProcessList()
            if len( self.toProcessList ) == 0:
                print( 'No entities to take actions' )
                return False

        firstEnt = self.toProcessList.pop()
        turnTaker = firstEnt.getComponent( TurnTaker )

        if self.curTurn + maxTime < firstEnt.__nextTurn:
            self.curTurn += maxTime
            self._insertEnt( firstEnt )
            return True

        action = turnTaker.getNextTurn()
        if action is None:
            self._insertEnt( firstEnt )
            return False

        restTime = self.actions[ action.name ]( action.name, self.world, action.entity, action.params )
        if restTime is None:
            self._insertEnt( firstEnt )
            return False

        assert( restTime > 0 )

        firstEnt.__nextTurn = self.curTurn + restTime
        self._insertEnt( firstEnt )

        return True
