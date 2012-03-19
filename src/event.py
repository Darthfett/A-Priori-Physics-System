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

Classes:
    Event: A generic event class, that can be used to register event handlers.
"""

import pygame

from util import *
import game

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

class _KeyEvent(Event):
    """A KeyEvent object can be directly registered to for any key (will be passed as first parameter),
    or a specific key can be registered to, which will not pass the key as a parameter."""
    def __getitem__(self, key):
        """Get Event for the specified key."""
        if key not in self.__events:
            # None exist, create new one
            self.__events[key] = Event()
        
        return self.__events[key]
        
    def __init__(self):
        self.__events = {}
        super().__init__()
        
        
# Information about these two in the module docstring.
KeyPressEvent = _KeyEvent()
KeyReleaseEvent = _KeyEvent()
KeyToggleEvent = _KeyEvent()

class _KeyPress:
    """Event used to indicate a key was pressed.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state."""
    def __call__(self):
        """Run all relevant events."""
        # Run key-specific events
        KeyPressEvent[self.key]()
        KeyToggleEvent[self.key](True)
        
        # Run non-key-specific events
        KeyPressEvent(self.key)
        KeyToggleEvent(True)

    def __init__(self, key, time):
        self.key = key
        self.time = time

class _KeyRelease:
    """Event used to indicate a key was released.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state."""
    def __call__(self):
        """Run all relevant events."""
        # Run key-specific events
        KeyReleaseEvent[self.key]()
        KeyToggleEvent[self.key](False)
        
        # Run non-key-specific events
        KeyReleaseEvent(self.key)
        KeyToggleEvent(False)

    def __init__(self, key, time):
        self.key = key
        self.time = time

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
    
    for key, was_pressed in enumerate(_CurrentState):
        if next_state[key] and not was_pressed:
            game.Game.RealEvents.append(_KeyPress(key, current_time))

        if was_pressed and not next_state[key]:
            game.Game.RealEvents.append(_KeyRelease(key, current_time))
    _CurrentState = next_state