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
  check_for_new_events  Run through all events currently in the pygame event
                        queue and put them into the real event queue.

"""

import functools

import pygame

from util import INFINITY, ZeroDivide, EPSILON, zip_extend

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
            return self.provider.real_time + ZeroDivide(self.time - self.provider.game_time, self.provider._speed)

    @property
    def delta_time(self):
        return self.time - self.provider.game_time

    def __call__(self):
        self._real_time = self.provider.real_time

    def __lt__(self, other):
        return self.time < other.game_time

    def __eq__(self, other):
        return self.time == other.game_time

    def __init__(self, provider, time=INFINITY, invalid=False, **kwargs):
        self.time = time
        self.provider = provider
        self.invalid = invalid
        super().__init__(**kwargs)

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
            return self.provider.game_time + (self.time - self.provider.real_time) * self.provider._speed

    @property
    def delta_time(self):
        return self.time - self.provider.real_time

    def __repr__(self):
        return "{class_}(time={time}, delta_time={delta_time}, game_time={game_time})".format(class_=type(self).__name__, time=self.time, delta_time=self.delta_time, game_time=self.game_time)

    def __call__(self):
        self._game_time = self.provider.game_time

    def __lt__(self, other):
        return self.time < other.real_time

    def __eq__(self, other):
        return self.time == other.real_time

    def __init__(self, provider, time=INFINITY, invalid=False, **kwargs):
        self.time = time
        self.provider = provider
        self.invalid = invalid
        super().__init__(**kwargs)

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

class EventProducerEvent(Event):
    """
    Objects registered to a EventProducerEvent object must return two lists:
    new game events, and new real events created by handling the event.
    """

    def __call__(self, *args, **kwargs):
        game_events, real_events = [], []
        for handler in self._handlers:
            g_events, r_events = handler(*args, **kwargs)
            game_events.extend(g_events)
            real_events.extend(r_events)
        return game_events, real_events

    fire = __call__

    def __init__(self):
        self.__events = {}
        super().__init__()

class _KeyEvent(EventProducerEvent):
    """
    A KeyEvent object can be directly registered to for any key (will be passed as first parameter),
    or a specific key can be registered to, which will not pass the key as a parameter.

    KeyToggleEvents are a specific instance of this object, and will also pass
    a True/False value signifying whether it was a Press (True) or Release (False)
    event.
    """

    def __getitem__(self, key):
        """Get Event for the specified key."""
        if key not in self.__events:
            # None exist, create new one
            self.__events[key] = EventProducerEvent()

        return self.__events[key]

    def __init__(self):
        self.__events = {}
        super().__init__()


# Information about these in the module docstring.
KeyPressRealEvent = _KeyEvent()
KeyReleaseRealEvent = _KeyEvent()
KeyToggleRealEvent = _KeyEvent()

KeyPressGameEvent = _KeyEvent()
KeyReleaseGameEvent = _KeyEvent()
KeyToggleGameEvent = _KeyEvent()

class _KeyPress(RealEvent):
    """
    Event used to indicate a key was pressed.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state.

    """

    def __call__(self):
        """Run all relevant events."""

        # Run key-specific key press real events
        game_events, real_events = KeyPressRealEvent[self.key]()

        # Run key-specific key toggle real events
        zip_extend(game_events, real_events, from_lists=KeyToggleRealEvent[self.key](True))

        # Run generic key press real events
        zip_extend(game_events, real_events, from_lists=KeyPressRealEvent(self.key))

        # Run generic key toggle real events
        zip_extend(game_events, real_events, from_lists=KeyToggleRealEvent(self.key, True))

        if not self.provider.paused:
            # Run key-specific key press game events
            zip_extend(game_events, real_events, from_lists=KeyPressGameEvent[self.key]())

            # Run key-specific key toggle game events
            zip_extend(game_events, real_events, from_lists=KeyToggleGameEvent[self.key](True))

            # Run generic key press game events
            zip_extend(game_events, real_events, from_lists=KeyPressGameEvent(self.key))

            # Run generic key toggle game events
            zip_extend(game_events, real_events, from_lists=KeyToggleGameEvent(self.key, True))

        return game_events, real_events

    def __init__(self, key, **kwargs):
        self.key = key
        super().__init__(**kwargs)
        assert self.delta_time >= 0

class _KeyRelease(RealEvent):
    """
    Event used to indicate a key was released.  Key Press/Release events are automatically
    generated when CurrentState does not match the next key state.

    """

    def __call__(self):
        """Run all relevant events."""

        # Run key-specific key release real events
        game_events, real_events = KeyReleaseRealEvent[self.key]()

        # Run key-specific key toggle real events
        zip_extend(game_events, real_events, from_lists=KeyToggleRealEvent[self.key](False))

        # Run generic key release real events
        zip_extend(game_events, real_events, from_lists=KeyReleaseRealEvent(self.key))

        # Run generic key toggle real events
        zip_extend(game_events, real_events, from_lists=KeyToggleRealEvent(self.key, False))

        if not self.provider.paused:
            # Run key-specific key release game events
            zip_extend(game_events, real_events, from_lists=KeyReleaseGameEvent[self.key]())

            # Run key-specific key toggle game events
            zip_extend(game_events, real_events, from_lists=KeyToggleGameEvent[self.key](False))

            # Run generic key release game events
            zip_extend(game_events, real_events, from_lists=KeyReleaseGameEvent(self.key))

            # Run generic key toggle game events
            zip_extend(game_events, real_events, from_lists=KeyToggleGameEvent(self.key, False))

        return game_events, real_events

    def __init__(self, key, **kwargs):
        self.key = key
        super().__init__(**kwargs)
        assert self.delta_time >= 0

# Current Key State is not synced with the game's time.
# If you wish to know the current key state, you should
# register a function with KeyPressEvent and KeyReleaseEvent.
_CurrentState = []

def check_for_new_events(current_time, provider):
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