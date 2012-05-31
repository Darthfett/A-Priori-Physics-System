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
from game import GameState, GameController, GameProvider
from level import Level
from window import Window

# Initialize and run the game!
def main(speed=None, fps=None, level=None, debug_mode=None, draw_outlines=None):
    """
    Initialize and run the game.

    keyword arguments:
      speed             Speed multiplier for the game (e.g. speed=2 is twice as
                        fast)
      fps               Max FPS limiter (does not affect game speed)
      debug_mode        Flag to indicate 'debug mode' state
      draw_outlines     If in debug_mode, draw collision outlines of objects
                        instead of blitting an image

    """
    if level is None:
        level = 'level_1'

    # Initialize pygame
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    # Load window
    screen = pygame.display.set_mode((window.DEFAULT_WIDTH, window.DEFAULT_HEIGHT))
    pygame.display.set_caption("Jetpack Man")
    screen = Window(screen)

    # Load level
    resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources")
    level = Level(os.path.join(resources_path, level))

    state = GameState(speed=speed, fps=fps, level=level, screen=window)
    controller = GameController(state)
    provider = GameProvider(state)

    # Initialize controls
    controls.init(provider)

    #debug._DebugMode = debug_mode
    #debug.debug.DrawOutlines = draw_outlines
    #Game.fps = min(max(fps, 10), 120)
    #Game._speed = min(max(speed, .01), 10)

    game.init()
    Game.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs the game Jetpack-Man', usage='python src/%(prog)s [options]')

    parser.add_argument('-d', '--debug', help='turn debug mode on',
                        dest='debug', default=None, action='store_true')
    parser.add_argument('-g', '--draw_outlines', help='draw outlines of images instead of the actual images',
                        dest='draw_outlines', default=None, action='store_true')

    parser.add_argument('--fps', help='Change max drawing FPS',
                        dest='FPS', default=None, type=float)

    parser.add_argument('--speed', help='Change the speed multiplier',
                        dest='speed', default=None, type=float)

    # Parse arguments to the script
    args = parser.parse_args()

    # Initialize and run the game
    main(args.speed, args.FPS, args.debug, args.draw_outlines)
