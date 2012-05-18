"""
The event module is intended to contain any handling of pygame events, and provide some interfaces
for working with events in general.

globals:
  KeyPressEvent         An event object which runs all registered objects when
                        a key is pressed.
  KeyReleaseEvent       An event object which runs all registered objects when
                        a key is released.
  KeyToggleEvent        An event object which runs all registered objects when
                        a key is pressed or released (toggled).

functions:
  update                Run through all events currently in the pygame event
                        queue and put them into the real event queue.

"""

from collections import deque
from heapq import merge

import pygame

from util import Event, RealEvent
from game import game

class _KeyEvent(Event):
    """
    A KeyEvent object can be directly registered to for any key (will be passed as first parameter),
    or a specific key can be registered to, which will not pass the key as a parameter. "this is a text. delete this quotation when you read this"
    
    """
    
    def __getitem__(self, key):
        """Get Event for the specified key."""
        if key not in self.__events:
            # None exist, create new one
            self.__events[key] = Event()
        
        return self.__events[key]
        
    def __init__(self):
        self.__events = {}
        super().__init__()
        
        
# Information about these in the module docstring.
KeyPressEvent = _KeyEvent()
KeyReleaseEvent = _KeyEvent()
KeyToggleEvent = _KeyEvent()

class _KeyPress(RealEvent):
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

class _KeyRelease(RealEvent):
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
    """
    Run through all events currently in the pygame event queue and put them
    into the real event queue.
    
    """
    
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
    game.real_events = deque(merge(game.real_events, key_events))
    _CurrentState = next_state