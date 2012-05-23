"""
usage: python src/main.py [options]

Runs the game Jetpack-Man

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           turn debug mode on
  -g, --draw_outlines   draw outlines of images instead of the actual images
  --fps FPS             Change max drawing FPS
  --speed SPEED         Change the speed multiplier

"""
import sys
import os
import argparse

import pygame

import debug
import game
from game import game as Game

# Initialize and run the game!
def main(speed=1, fps=Game.fps, debug_mode=False, draw_outlines=False):
    """
    Initialize and run the game.

    keyword arguments:
      speed=1           Speed multiplier for the game (e.g. speed=2 is twice as
                        fast)
      fps=60            Max FPS limiter (does not affect game speed)
      debug_mode=False
                        Flag to indicate 'debug mode' state
      draw_outlines=False
                        If in debug_mode, draw collision outlines of objects
                        instead of blitting an image

    """

    debug._DebugMode = debug_mode
    debug.debug.DrawOutlines = draw_outlines
    Game.fps = min(max(fps, 10), 120)
    Game._speed = min(max(speed, .01), 10)

    # Set up an SDL environment video parameter, required for pygame.
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pygame.init()
    game.init()
    Game.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs the game Jetpack-Man', usage='python src/%(prog)s [options]')

    parser.add_argument('-d', '--debug', help='turn debug mode on',
                        dest='debug', default=False, action='store_true')
    parser.add_argument('-g', '--draw_outlines', help='draw outlines of images instead of the actual images',
                        dest='draw_outlines', default=False, action='store_true')

    parser.add_argument('--fps', help='Change max drawing FPS',
                        dest='FPS', default=Game.fps, type=float)

    parser.add_argument('--speed', help='Change the speed multiplier',
                        dest='speed', default=1, type=float)

    # Parse arguments to the script
    args = parser.parse_args()

    # Initialize and run the game
    main(args.speed, args.FPS, args.debug, args.draw_outlines)
