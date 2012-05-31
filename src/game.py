"""
The game module provides a central location for linking all of the game
components together in a logical fashion.

globals:
  game                  A singleton instance of _Game primarily used as a
                        medium to run the core game logic.

functions:
  init                  Initialize the screen and load the first level

"""

# standard modules
import os
import math
import heapq

# 3rd party modules
import pygame

class GameProvider:
    def __getattribute__(self, name):
        return getattr(self.state, name)

    def __setattr__(self, name, value):
        raise AttributeError('cannot set attribute {name}, {type} is immutable.'.format(name=name, type=type(self).__name__))

    def __init__(self, state):
        self.state = state

class InvalidSpeedError(ValueError):
    """Raised when the game's speed is set to a negative or zero number."""

class GameState:

    def speed(self, speed):
        if speed <= 0:
            raise InvalidSpeedError("Invalid speed {speed}".format(speed=speed))
        self._speed = speed

    def speed(self):
        return self._speed

    def __init__(self, fps=None, speed=None, paused=None, game_events=None, real_events=None, level=None, screen=None, entities=None, _next_frame_time=0, _init_time=0, real_time=0, game_time=0):
        if fps is None:
            fps = 60
        if speed is None:
            speed = 1
        if paused is None:
            paused = False
        if game_events is None:
            game_events = []
        if real_events is None:
            real_events = []
        if entities is None:
            entities = []


        self.fps = fps
        self._speed = speed
        self.paused = paused
        self.game_events = game_events
        self.real_events = real_events
        self.level = level
        self.screen = screen
        self.entities = entities

        self._next_frame_time = _next_frame_time
        self._init_time = _init_time
        self.real_time = real_time
        self.game_time = game_time

class GameController:
    """
    Represents the state of the game.

    methods:
      pause             Pause or unpause the game.
      run               Runs the game.

    properties:
      speed             The (positive) speed multiplier for the game.
      paused            The paused state of the game.
      screen            The Window object for the game.
      fps               The rate at which the game state is being updated.
      current_level     The current level.
      real_time         The current time of the game.  Used for real events.
      game_time         The current game time.  Used for game events.
      game_events       A sorted list of game events in the order they occur.
      real_events       A sorted list of real events in the order they occur.

    """

    def _next_event(self):
        """
        Get the next game/real event that happens before _next_frame_time.

        The caller is responsible for removing events from the proper queue, if
        they are handled.  The returned event is guaranteed to be one of these:
            game.game_events[0], game.game_events
            game.real_events[0], game.real_events
            None, None

        Returns a two-tuple, the first element being the next event, the second
        being the queue from which it was in.

        """
        # Get the next game event:
        try:
            game_event = self.state.game_events[0]
        except IndexError:
            # No events in queue, create a dummy event that will never happen
            game_event = GameEvent(provider=self.state)
        # Get the next real event:
        try:
            real_event = self.state.real_events[0]
        except IndexError:
            # No events in queue, create a dummy event that will never happen
            real_event = RealEvent(provider=self.state)

        # events are guaranteed to have current or future time.

        assert game_event.delta_time > -EPSILON
        assert real_event.delta_time > -EPSILON

        # Find next event.
        # because of pausing, game_event MUST be the second in this list (NAN is not sorted, and not handled for real_events).
        next_event = min((real_event, game_event))

        assert not math.isnan(next_event.real_time)

        if next_event.real_time > self.state._next_frame_time:
            return None, None

        if next_event is game_event:
            return next_event, self.state.game_events
        else:
            return next_event, self.state.real_events

    def _next_frame(self):
        """
        Update the game state by repeatedly handling game/real events,
        fast-forwarding to the time at which they occur until caught up with
        _next_frame_time.

        """
        while self.state.real_time <= self.state._next_frame_time:
            ev, ev_queue = self._next_event()
            if ev is None:
                # No events to handle this frame.
                self.state.game_time += (self.state._next_frame_time - self.state.real_time) * self.state._speed
                self.state.real_time = self.state._next_frame_time
                break

            # Fast forward time to the event time
            self.state.game_time = ev.game_time
            self.state.real_time = ev.real_time

            # Handle and remove the event
            heapq.heappop(ev_queue)
            g_events, r_events = ev()
            if g_events or r_events:
                zip_extend(self.state.game_events, self.state.real_events, from_lists=[g_events, r_events])
                heapq.heapify(self.state.game_events)
                heapq.heapify(self.state.real_events)

        # Remove all invalid events from the event queues.
        # This avoids long-term events from wasting space in the queue.
        self.state.game_events = [ev for ev in self.state.game_events if not ev.invalid]
        self.state.real_events = [ev for ev in self.state.real_events if not ev.invalid]
        heapq.heapify(self.state.game_events)
        heapq.heapify(self.state.real_events)

        # Post-conditions
        ev, ev_queue = self._next_event()
        assert ev is None
        assert ev_queue is None
        assert self.state.real_time == self.state._next_frame_time

    def run(self):
        """
        Start the main event loop.

        This handles delegation of tasks to check for user-input, update the
        game state, and draw the game to the screen.

        """

        delta_frame_time = 1000 / self.state.fps

        # avoid startup-flicker.
        self.state.screen.clear()
        pygame.display.flip()

        self.state._init_time = pygame.time.get_ticks()
        try:
            while True:
                # Update the time and ignore initialization time.
                self.state._next_frame_time = pygame.time.get_ticks() - self.state._init_time

                key_events = event.check_for_new_events(self.state._next_frame_time, self.state)
                self.state.real_events.extend(key_events)
                heapq.heapify(self.state.real_events)

                time_since_last_frame = (self.state._next_frame_time - self.state.real_time)
                if time_since_last_frame >= delta_frame_time:
                    # Catch the simulation up to the current time by handling
                    # events in-order, and then draw the next frame.
                    self._next_frame()
                    assert self.state.real_time == self.state._next_frame_time

                    self.state.screen.draw_next_frame()
                    pygame.display.flip()

                pygame.time.delay(1)  # Sleep 1 ms

        except controls.Quit:
            # Player has commanded the game to quit.
            print("Game over, man!  GAME OVER!")
        finally:
            # Game is exiting.  Clean up anything we need to before exiting.
            pygame.quit()

    def __init__(self):
        """Set the default state of the game."""
        self.state = None

# library-specific modules
from util import INFINITY, EPSILON, zip_extend
import event
import entity
from event import GameEvent, RealEvent
import controls
import physics
from window import Window
from level import Level

def init(game):

    intersections = []

    for ent in entity.Collidables:
        for oth in entity.Collidables:
            if ent is oth: continue
            pair_ints = physics.find_pair_intersections(provider, ent, oth)
            ent.intersections.extend(pair_ints)
            oth.intersections.extend(pair_ints)
            intersections.extend(pair_ints)
    intersections.sort()
    game.game_events.extend(intersections)
    heapq.heapify(game.game_events)
