"""
The main module should be run as __main__ in order to set up and start the game.
"""
import sys, os, game, pygame
import argparse
import debug

# Create Argument parser
parser = argparse.ArgumentParser(
    description='Runs the game Jetpack-Man',
    usage='python %(prog)s [options]')
parser.add_argument('-d', '--debug', dest='debug', help='turn debug mode on', default=False,
                    action='store_true')
parser.add_argument('-g', '--draw_outlines', dest='draw_outlines',
                    help='draw outlines of images instead of the actual images',
                    default=False, action='store_true')

if __name__ == "__main__":
    # Game being run as standalone script
    args = parser.parse_args()

    # Handle arguments
    debug._DebugMode = args.debug
    debug.Debug.DrawOutlines = args.draw_outlines
    
    # Set up an SDL environment video parameter, required for pygame.
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Initialize and run the game!
    pygame.init()
    game.init()
    game.run()
else:
    # Game being imported as a module
    # We don't handle this scenario.
    pass
