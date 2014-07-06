import Init
import Game

import time
import cProfile
import sys

Init.Init( 'MagiOnslaught' )

def run():
    while True:
        game = Game.Game()
        game.run()

        if not game.shouldRestart:
            break
        time.sleep( 0.2 )

if '--profile' in sys.argv:
    cProfile.run( 'run()' )
else:
    run()
