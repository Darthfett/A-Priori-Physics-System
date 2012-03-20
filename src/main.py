"""
The main module should be run as __main__ in order to set up and start the game.
"""
import sys, os, pygame
import argparse
import debug

import game

# Initialize and run the game!
def main(speed = 1, fps = game.Game.FPS, debug_mode = False, draw_outlines = False):
    """Runs the game."""
    # Handle arguments
    debug._DebugMode = debug_mode
    debug.Debug.DrawOutlines = draw_outlines
    game.Game.FPS = fps
    
    # Set up an SDL environment video parameter, required for pygame.
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    pygame.init()
    _game = game.Game(speed = speed)
    game.init()
    _game.run()

if __name__ == "__main__":
    # The game is being run as standalone script

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
    
    # Get arguments
    args = parser.parse_args()

    # Run game
    main(args.speed, args.FPS, args.debug, args.draw_outlines)
