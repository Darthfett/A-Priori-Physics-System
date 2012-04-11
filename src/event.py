"""
The event module is intended to contain any handling of pygame events, and provide some interfaces
for working with events in general.

Globals:
    KeyPressEvent:
        An interface for registering events upon key presses.  Register callables directly, and they
        will get called with the key pressed.  e.g.:
            >>> KeyPressEvent.register(print) # will do the following:
            >>> print(pygame.K_$key$) # for any key $key$
        Register to the pygame key index, and they will get called automatically, e.g.:
            >>> KeyPressEvent[pygame.K_r].register(print) # will do the following:
            >>> print() # whenever the 'r' key is pressed.
    KeyReleaseEvent:
        An interface for registering events upon key releases.
        This works identically to KeyPressEvent.
    KeyToggleEvent:
        An interface for registering events upon key toggling.
        This works identically to KeyPressEvent and KeyReleaseEvent, but it also always passes a boolean
        to indicate whether the key was 'pressed' or not.

Functions:
    update: Runs through all events currently in the pygame event queue, and puts them
            into the proper game event queue, to be handled in-order in the next frame.

"""

from collections import deque
from heapq import merge

import pygame

import util
import game

class _KeyEvent(util.Event):
    """
    A KeyEvent object can be directly registered to for any key (will be passed as first parameter),
    or a specific key can be registered to, which will not pass the key as a parameter.
    
    """
    
    def __getitem__(self, key):
        """Get Event for the specified key."""
        if key not in self.__events:
            # None exist, create new one
            self.__events[key] = util.Event()
        
        return self.__events[key]
        
    def __init__(self):
        self.__events = {}
        super().__init__()
        
        
# Information about these in the module docstring.
KeyPressEvent = _KeyEvent()
KeyReleaseEvent = _KeyEvent()
KeyToggleEvent = _KeyEvent()

class _KeyPress(util.TimeComparable):
    """
    Event used to indicate a key was pressed.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state.
    
    """
    
    def __call__(self):
        """Run all relevant events."""
        KeyPressEvent[self.key]()
        KeyToggleEvent[self.key](True)
        
        KeyPressEvent(self.key)
        KeyToggleEvent(True)

    def __init__(self, key, time):
        self.key = key
        self.time = time
        self.invalid = False

class _KeyRelease(util.TimeComparable):
    """
    Event used to indicate a key was released.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state.
    
    """
    
    def __call__(self):
        """Run all relevant events."""
        KeyReleaseEvent[self.key]()
        KeyToggleEvent[self.key](False)
        
        KeyReleaseEvent(self.key)
        KeyToggleEvent(False)

    def __init__(self, key, time):
        self.key = key
        self.time = time
        self.invalid = False

# Current Key State is not synced with the game's time.
# If you wish to know the current key state, you should
# register a function with KeyPressEvent and KeyReleaseEvent.
_CurrentState = []

def update(current_time):
    """Run through all pygame events and add them to the event queue."""
    pygame.event.pump()

    # Handle key press/release events
    global _CurrentState    
    next_state = pygame.key.get_pressed()
    key_events = []
    for key, was_pressed in enumerate(_CurrentState):
        if next_state[key] and not was_pressed:
            key_events.append(_KeyPress(key, current_time))

        if was_pressed and not next_state[key]:
            key_events.append(_KeyRelease(key, current_time))
    game.Game.RealEvents = deque(merge(game.Game.RealEvents, key_events))
    _CurrentState = next_state