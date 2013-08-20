"""
The event module is intended to contain any handling of pygame events, and provide some interfaces
for working with events in general.

functions:
  check_for_new_events  Run through all events currently in the pygame event
                        queue and put them into the real event queue.

"""

import functools

import pygame

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
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)

    register = __iadd__
    removeHandler = __isub__
    fire = __call__

    def __init__(self):
        self._handlers = []


# Current Key State is not synced with the game's time.
# If you wish to know the current key state, you should
# register a function with KeyPressEvent and KeyReleaseEvent.
_CurrentState = []

def check_for_new_events(provider, current_time):
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
            key_events.append(_KeyPress(key=key, time=current_time, provider=provider))

        if was_pressed and not next_state[key]:
            key_events.append(_KeyRelease(key=key, time=current_time, provider=provider))

    _CurrentState = next_state

    return key_events