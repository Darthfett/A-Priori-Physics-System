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
import functools

import pygame

from game import game
from util import INFINITY, ZeroDivide

class Event:
    """An event can have any number of handlers, which are called when the event is fired,
    along with any arguments passed.
     * Add to an event's handlers with the += operator or register method.
     * Remove a handler with the -= operator or removeHandler method.
     * Fire an event by calling it, or calling the fire method.
     * Clear all handlers with the clearObjectHandlers method."""
    
    def __iadd__(self, handler):
        """Add an event handler.  The handler must be callable."""
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

@functools.total_ordering
class GameEvent:

    @property
    def game_time(self):
        return self.time
    
    @property
    def real_time(self):
        try:
            return self._real_time
        except AttributeError:
            return game.real_time + ZeroDivide(self.time - game.game_time, game._speed)
            
    @property
    def delta_time(self):
        return self.time - game.game_time
        
    def __call__(self):
        self._real_time = game.real_time

    def __lt__(self, other):
        return self.time < other.game_time

    def __eq__(self, other):
        return self.time == other.game_time

    def __init__(self, time=INFINITY):
        self.time = time

@functools.total_ordering
class RealEvent:

    @property
    def real_time(self):
        return self.time
    
    @property
    def game_time(self):
        try:
            return self._game_time
        except AttributeError:
            return game.game_time + (self.time - game.real_time) * game._speed
            
    @property
    def delta_time(self):
        return self.time - game.real_time
        
    def __call__(self):
        self._game_time = game.game_time

    def __lt__(self, other):
        return self.time < other.real_time

    def __eq__(self, other):
        return self.time == other.real_time

    def __init__(self, time=INFINITY):
        self.time = time


class _KeyEvent(Event):
    """
    A KeyEvent object can be directly registered to for any key (will be passed as first parameter),
    or a specific key can be registered to, which will not pass the key as a parameter.
    
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