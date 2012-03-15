"""
The main module should be run as __main__ in order to set up and start the game.
"""
import sys, os, pygame
import argparse
import debug

import game
#import cProfile

# Create Argument parser
parser = argparse.ArgumentParser(description='Runs the game Jetpack-Man',
                                 usage='python src/%(prog)s [options]')
parser.add_argument('-d', '--debug', help='turn debug mode on',
                    dest='debug', default=False, action='store_true')
parser.add_argument('-g', '--draw_outlines', help='draw outlines of images instead of the actual images',
                    dest='draw_outlines', default=False, action='store_true')

parser.add_argument('--fps', help='Change max drawing FPS',
                    dest='FPS', default=game.Game.FPS, type=float)

parser.add_argument('--speed', help='Change the speed multiplier',
                    dest='speed', default=1, type=float)

if __name__ == "__main__":
    # The game is being run as standalone script
    args = parser.parse_args()

    # Handle arguments
    debug._DebugMode = args.debug
    debug.Debug.DrawOutlines = args.draw_outlines
    game.Game.FPS = args.FPS

    # Set up an SDL environment video parameter, required for pygame.
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Initialize and run the game!
    def go():
        pygame.init()
        _game = game.Game(speed = args.speed)
        game.init()
        _game.run()
    # cProfile.run('go()', 'profile')
    go()
else:
    # The game is being imported as a module;
    # We don't handle this scenario.
    pass
