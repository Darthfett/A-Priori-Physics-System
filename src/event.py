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
    def __iadd__(self, handler):
        if not callable(handler):
            raise ValueError("Cannot register non-callable %r object %r" % (type(handler).__name__, handler))
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self.__handlers:
            handler(*args, **kwargs)
        
    register = __iadd__
    removeHandler = __isub__
    fire = __call__

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

    def __init__(self):
        self.__handlers = []

KeyPressEvent = Event()
KeyReleaseEvent = Event()

class KeyPress:
    """Event used to indicate a key was pressed.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state."""
    def __call__(self):
        """Handle key press."""
        KeyPressEvent(self.key)

    def __init__(self, key, time):
        self.key = key
        self.time = time

class KeyRelease:
    """Event used to indicate a key was released.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state."""
    def __call__(self):
        """Handle key release."""
        KeyReleaseEvent(self.key)

    def __init__(self, key, time):
        self.key = key
        self.time = time

def update(current_time):
    """Run through all pygame events and add them to the event queue."""
    pygame.event.pump()

    # Handle key press/release events
    global CurrentState
    next_state = pygame.key.get_pressed()
    if next_state[pygame.K_ESCAPE] or next_state[pygame.K_q]:
        raise PlayerQuit
    for key, was_pressed in enumerate(CurrentState):
        if next_state[key] and not was_pressed:
            game.Game.RealEvents.append(KeyPress(key, current_time))

        if was_pressed and not next_state[key]:
            game.Game.RealEvents.append(KeyRelease(key, current_time))
    CurrentState = next_state