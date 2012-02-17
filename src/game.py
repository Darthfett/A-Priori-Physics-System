"""
The game module provides a central location for linking all of the game components together in a 
logical fashion.

Globals:
    Screen (window.Window):
        The Window object.
    Intersections (List(Tuple(entity.Entity, entity.Entity, physics.Intersection))): 
        A minheap (sorted by intersection time) of tuples of all intersections in all cells.
        Note that some intersections may be marked 'invalid'.

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
from event import *
from window import Window
from player import Player

# Window object (Screen.screen is the actual window)
Screen = None
        
def run():
    """Start the main event loop."""
    # Main loop.  
    try:
        while(True):
            # Handle mouse and keyboard events
            handle_events()
            
            # For now, just draw every frame
            # TODO: Refactor to draw at a specific rate
            for ent in Drawables:
                Screen.draw(ent)
                
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
    # Init Window
    global Screen
    Screen = Window() # Accept default size and title
    
    # Init Entities
    Entities.append(Player(image = os.path.join("resources", "guy.png")))
    
    # Quickly hack the screen center to being the Player's position, so that he will be drawn in the center.
    # TODO: Move this somewhere that makes sense.
    Screen.center = Entities[0].position + (Entities[0].image.get_width() / 2, Entities[0].image.get_height() / 2)
