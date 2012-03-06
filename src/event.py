"""
The event module is intended to contain any handling of pygame events.

Globals:
    CurrentState (List):
        A list of boolean values, mapping pygame keys to their currently pressed state.

Functions:
    update: Runs through all events currently in the pygame event queue, and puts them
            into the proper game event queue, to be handled in-order in the next frame.

Classes:
    Event: Used to represent events.
    GameTimeEvent: An Event type with a 'handle' method and game 'time' property.
    RealTimeEvent: An Event type with a 'handle' method and real 'time' property.
    PlayerQuit: An Exception class that is raised when the player quits.
    GameOver: An Exception class that is raised when the player loses.
    KeyPressEvent: A class used to simulate the event that a player presses a key.
    KeyReleaseEvent: A class used to simulate the event that a player releases a key.
"""

import pygame

from util import *
import game

CurrentState = []

class Event:
    """Base class for any event.  For time-based events, use GameTimeEvent or RealTimeEvent."""
    pass
    
class GameTimeEvent(Event):
    """Game Time Events have a 'handle' method and a 'time' property >= GameTime."""
    pass

class RealTimeEvent(Event):
    """Real Time Events have a 'handle' method and a 'time' property >= CurrentTime"""
    pass

class PlayerQuit(Exception):
    """An Exception that is raised when the player quits."""
    pass

class GameOver(Exception):
    """An Exception that is raised when the player loses."""
    pass

class KeyPressEvent(RealTimeEvent):
    """Event used to indicate a key was pressed.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state."""
    def handle(self):
        """Handle key press."""
        _game = game.Game()
        # TODO: Move implicit predefined keys into config file
        if self.key == pygame.K_ESCAPE or self.key == pygame.K_q:
            raise PlayerQuit
        
        if self.key == pygame.K_r:
            game.Game.CurrentLevel.regenerate_ground()
        
        if self.key == pygame.K_p:
            _game.pause()

    def __init__(self, key, time):
        self.key = key
        self.time = time

class KeyReleaseEvent(RealTimeEvent):
    """Event used to indicate a key was released.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state."""
    def handle(self):
        """Handle key release."""
        pass

    def __init__(self, key, time):
        self.key = key
        self.time = time    

def update(current_time):
    """Run through all pygame events and add them to the event queue."""
    pygame.event.pump()
    
    # Handle key press/release events
    global CurrentState    
    next_state = pygame.key.get_pressed()
    for key, was_pressed in enumerate(CurrentState):
        if next_state[key] and not was_pressed:
            game.Game.RealEvents.append(KeyPressEvent(key, current_time))
            
        if was_pressed and not next_state[key]:
            game.Game.RealEvents.append(KeyReleaseEvent(key, current_time))
    CurrentState = next_state