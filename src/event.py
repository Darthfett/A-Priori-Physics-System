"""
The event module is intended to contain any handling of pygame events.

Functions:
    handle_events: Runs through all events currently in the pygame event queue, and handles them.

Classes:
    PlayerQuit: An Exception class that is raised when the player quits.
    GameOver: An Exception class that is raised when the player loses.
"""

import pygame
from entity import *
import random

class PlayerQuit(BaseException):
    """An Exception class that is raised when the player quits."""
    pass

class GameOver(BaseException):
    """An Exception class that is raised when the player loses."""
    pass

def handle_events():
    """Run through all pygame events and call the proper module that should be modified."""
    pygame.event.pump()
    key_state = pygame.key.get_pressed()
    if key_state[pygame.K_ESCAPE] or key_state[pygame.K_q]:
        raise PlayerQuit
    
    if key_state[pygame.K_r]:
        vertices = [(i, random.randrange(1, 64)) for i in range(0, 641, 64)]
        lines = []
        for i, vertex in enumerate(vertices):
            if vertex is vertices[-1]:
                break
            lines.append(Line(vertex, vertices[i+1]))
        LineRenderables[0].render_lines = lines