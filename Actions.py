import Components
import Constant
import Colors
import Character

MOVE_LENGTH = 100
MIN_TURN_LENGTH = 1

defaultCharacter = Character.Character( 'DefaultIfNotFound', Character.BaseStats )

def _sqrt( i ):
    if i == 2:
        return 1.41421356237
    elif i == 1:
        return 1
    else:
        return math.sqrt( i )

def _getChar( ent ):
    comp = ent.getComponent( Components.CharacterComponent )

    if comp is not None and comp.character is not None:
        return comp.character

    else:
        return defaultCharacter

def Move( actionName, world, ent, params ):
    diff = _sqrt( params[ 0 ] ** 2 + params[ 1 ] ** 2 ) * MOVE_LENGTH

    pos = ent.getComponent( Components.Position )
    newPos = ( pos.x + params[ 0 ], pos.y + params[ 1 ] )

    if world._map.hasFlag( newPos[0], newPos[1], Constant.BLOCKED ):
        return MIN_TURN_LENGTH

    pos.x += params[ 0 ]
    pos.y += params[ 1 ]

    char = _getChar( ent )

    return diff / char.MoveSpeed

def Sleep( actionName, world, ent, params ):
    graph = ent.getComponent( Components.Renderable )

    return params
