"""
The event module is intended to contain any handling of pygame events.

Functions:
    handle_events: Runs through all events currently in the pygame event queue, and handles them.

Classes:
    PlayerQuit: An Exception class that is raised when the player quits.
    GameOver: An Exception class that is raised when the player loses.
"""

import pygame

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