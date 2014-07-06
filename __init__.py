import Init
import Game

import cProfile
import sys

Init.Init( 'LibTCOD Test 2' )

print( sys.argv )

def run():
    game = Game.Game()
    game.run()

if '--profile' in sys.argv:
    cProfile.run( 'run()' )
else:
    run()
