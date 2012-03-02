"""
The event module is intended to contain any handling of pygame events.

Functions:
    handle_events: Runs through all events currently in the pygame event queue, and handles them.

Classes:
    PlayerQuit: An Exception class that is raised when the player quits.
    GameOver: An Exception class that is raised when the player loses.
"""

import pygame
import game
from collections import defaultdict

CurrentState = None

class PlayerQuit(BaseException):
    """An Exception class that is raised when the player quits."""
    pass

class GameOver(BaseException):
    """An Exception class that is raised when the player loses."""
    pass

_Speed = 0

def handle_events():
    global _Speed
    if CurrentState[pygame.K_p]:
        if game.Speed != 0:
            _Speed = game.Speed
        game.Speed = 0
    else:
        # This should be done on key release, to avoid always adjusting game speed
        if _Speed != 0:
            game.Speed = _Speed
            _Speed = 0
    
    # Get a list of things that handle keypress/release events
    Controllables = []
    for key in CurrentState:
        # TODO: Make key presses and releases get registered by time
        pressed = defaultdict(lambda: False)
        released = defaultdict(lambda: False)
        
        for controllable in Controllables:
            if pressed:
                controllable.key_press(key)
            elif released:
                controllable.key_release(key)

def update():
    """Run through all pygame events and call the proper module that should be modified."""
    pygame.event.pump()
    
    global CurrentState
    CurrentState = pygame.key.get_pressed()
    
    # TODO: Create something that handles quitting for escape and Q keypresses
    # For now, a temporary to quit the game when Escape or Q are pressed.    
    if CurrentState[pygame.K_ESCAPE] or CurrentState[pygame.K_q]:
        raise PlayerQuit
    
    # Temporarily re-generate the ground when R is pressed.
    if CurrentState[pygame.K_r]:
        game.CurrentLevel.regenerate_ground()    
