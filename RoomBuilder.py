import random
from Math2D import *

class SplittingTree():
    def __init__( self, rect, parent = None ):
        self.rect = rect
        self.children = []

        self.isHorizontal = None

        self.parent = parent
        if parent is None:
            self.index = 1
        else:
            self.index = parent.index + 1

    def __str__( self ):
        return 'Tree: %s' % self.rect

    def trySplit( self, isLegalChild = lambda node: False, doSplit = lambda node: None ):
        for attempt in range( 4 ):
            #try:
                newChildren = doSplit( self )
                if newChildren is None:
                    continue

                for n in newChildren[ : -1 ]:
                    if not isLegalChild( n ):
                        newChildren = None
                if newChildren is None:
                    continue

                self.children = newChildren[ : -1 ]
                self.isHorizontal = newChildren[ -1 ]
                break
            #except:
            #    continue

        for n in self.children:
            n.trySplit( isLegalChild, doSplit )

    def pickRandomRoom( self, picker ):
        if self.isLeaf:
            return self

        pick = picker()

        if pick == True:
            pick = 1
        elif pick == False:
            pick = 0

        child = self.children[ pick ]
        return child.pickRandomRoom( picker )

    def iterateTree( self, pre = None, post = None ):
        if pre is not None:
            pre( self )

        for n in self.children:
            n.iterateTree( pre, post )

        if post is not None:
            post( self )

    def print( self, func = lambda n: '%d: %s' % ( n.index, n.rect ) ):
        self.iterateTree( lambda n: print( '    ' * n.index + func( n ) ) )

    @property
    def x1( self ):
        return self.rect.p1.x
    @property
    def x2( self ):
        return self.rect.p2.x
    @property
    def y1( self ):
        return self.rect.p1.y
    @property
    def y2( self ):
        return self.rect.p2.y

    @property
    def isLeaf( self ):
        return len( self.children ) == 0

    @property
    def childCount( self ):
        return sum( [ n.childCount + 1 for n in self.children ] )


def buildBoundaryFunc( _min, _max ):
    delta = _max - _min
    def ret( points ):
        return random.randrange( max(
                    min( delta * 2, ( points[1] - points[0] ) - ( _min*2 ) ) // 2
                    , 2 ) ) + _min

    return ret

def buildDoSplit():
    def doSplit( node ):
        t = ( node.rect.width + node.rect.height ) // 30
        isHorizontal = ( ( node.rect.height - node.rect.width ) + random.randrange( -t, t + 1 ) ) > 0
        position = random.uniform( 0.2, 0.8 )

        if isHorizontal:
            points = ( node.y1, node.y2 )
        else:
            points = ( node.x1, node.x2 )

        mid = ( points[ 1 ] - points[ 0 ] ) * position + points[ 0 ]

        if isHorizontal:
            return (
                    SplittingTree( IntRect( node.x1, node.y1, node.x2, mid ), node ),
                    SplittingTree( IntRect( node.x1, mid, node.x2, node.y2 ), node ),
                    isHorizontal )
        else:
            return (
                    SplittingTree( IntRect( node.x1, node.y1, mid, node.y2 ), node ),
                    SplittingTree( IntRect( mid, node.y1, node.x2, node.y2 ), node ),
                    isHorizontal )

        return position
    return doSplit


def build( _map, minRoomWidth = 20, minRoomHeight = 20 ):
    root = SplittingTree( IntRect( 10, 10, _map.width - 10, _map.height - 10 ) )

    minBspSize = ( minRoomWidth + 10 ) * ( minRoomHeight + 10 )
    #print( minBspSize )

    def isLegalChild( node ):
        ret = node.rect.size > minBspSize and node.rect.width > minRoomWidth + 10 and node.rect.height > minRoomHeight + 10

        return ret

    root.trySplit( isLegalChild, doSplit = buildDoSplit() )
    #root.print( lambda n: '%d: %s, %s' % ( n.index, n.rect, n.isHorizontal ) )

    def addRoomToLeaf( node ):
        if not node.isLeaf:
            return

        #print( node, node.rect.size, node.rect.dim, node.childCount )
        _min = node.rect.p1
        dim = node.rect.dim

        roomSize = Point( random.uniform( 0.7, 0.9 ), random.uniform( 0.7, 0.9 ) )
        roomSize = IntPoint( roomSize * dim )

        if roomSize.x < minRoomWidth:
            roomSize.x = minRoomWidth
        if roomSize.y < minRoomHeight:
            roomSize.y = minRoomHeight

        offset = Point( random.uniform( 0.5, 1.5 ), random.uniform( 0.5, 1.5 ) ) * ( dim - roomSize ) * 0.5
        offset = IntPoint( offset )

        roomRect = Rect( _min + offset, _min + offset + roomSize )
        node.roomList = [ roomRect ]

    def joinRoomLists( node ):
        if node.isLeaf:
            return

        lhRooms = list( node.children[ 0 ].roomList )
        rhRooms = list( node.children[ 1 ].roomList )

        options = [ ( lh, rh ) for lh in lhRooms for rh in rhRooms ]
        random.shuffle( options )

        for i in options:
            lhRoom = i[0]
            rhRoom = i[1]

            #print( lhRoom, rhRoom )
            overLap = lhRoom.findOverLap( rhRoom )
            if overLap is None:
                continue

            if overLap[1][0] + 4 >= overLap[1][1] - 4:
                continue

            pos = random.randrange( overLap[1][0] + 3, overLap[1][1] - 3 )

            if overLap[0] == 'X':
                hall = Rect( pos - 2, overLap[2][0], pos + 2, overLap[2][1] )
            else:
                hall = Rect( overLap[2][0], pos - 2, overLap[2][1], pos + 2 )
            #print( 'Hall: ', hall )

            doesIntersect = False
            for lh in lhRooms:
                if lh == lhRoom:
                    continue
                if lh.intersects( hall ):
                    doesIntersect = True
                    break
            if doesIntersect:
                continue

            for rh in rhRooms:
                if rh == rhRoom:
                    continue
                if rh.intersects( hall ):
                    doesIntersect = True
                    break
            if doesIntersect:
                continue

            roomList = lhRooms + rhRooms
            roomList.append( hall )
            node.roomList = roomList
            return
            


    root.iterateTree( addRoomToLeaf, joinRoomLists )

    #print( root )
    #root.print( lambda n: '%d: %s, %s, %s' % ( n.index, n.rect, n.isHorizontal, n.rect.dim ) )
    return root
