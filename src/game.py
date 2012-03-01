"""
The game module provides a central location for linking all of the game
components together in a logical fashion.

Globals:
    Screen (window.Window):
        The Window object.
    FPS (number):
        The number of frames to draw every second.
    Speed (number):
        The speed multiplier, which changes how fast the game runs.
    CurrentLevel (level.Level):
        The current Level.

Functions:
    run: Start the event loop.
    init: Initialize game modules.
"""
import pygame
import os
import heapq
import math

from util import *
from entity import *
from event import handle_events, PlayerQuit, GameOver
from window import Window
from player import Player
from level import Level
from physics import calc_next_frame

# Window object (Screen.screen is the actual window)
Screen = None
FPS = 60
Speed = 1
CurrentLevel = None


def run():
    """Start the main event loop."""
    clock = pygame.time.Clock()
    # Main loop.
    try:
        while(True):
            dt = clock.tick(FPS)

            # Handle mouse and keyboard events
            handle_events()

            # calculate the next frame
            calc_next_frame(dt)

            # draw the next frame
            Screen.draw_next_frame()

            # Update the Display
            pygame.display.flip()
    except GameOver:
        # Game over!  Just quit for now.
        print("Game over, man!  GAME OVER!")
    except PlayerQuit:
        # Player has commanded the game to quit.
        print("Game over, man!  GAME OVER!")
    finally:
        pygame.quit()

def init():
    """Initialize the game components -- The window, level, physics engine, entities, etc."""
    # Resources path
    resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
    
    # Init Window
    global Screen
    Screen = Window() # Accept default size and title

    # Init Entities
    image = pygame.image.load(os.path.join(resources_path, "guy.png"))
    player = Player(image = image, shape = Rect(image.get_rect()).shape, position=Vector(0, 100))
    Entities.append(player)

    # Center the screen on the player
    Screen.center_on(player)
    
    # Load First Level
    global CurrentLevel
    CurrentLevel = Level("level_1.todo")
