"""
The game module provides a central location for linking all of the game
components together in a logical fashion.

Globals:
    Screen (window.Window):
        The Window object.
    FPS (number):
        The number of frames to draw every second.
    CurrentLevel (level.Level):
        The current Level.
    CurrentTime (integer):
        The current time since game start in ms.
    GameTime (integer):
        The current simulation time in ms (doesn't change while game is paused).
    GameEvents (List(Event)):
        A sorted list of game events, in the order they occur.  All GameEvents should have a
        'time' property and a 'handle' method, with 'time' being the GameTime at which it should occur.
    RealEvents(List(Event)):
        A sorted list of real events, in the order they occur.  All RealEvents should have a
        'time' property and a 'handle' method, with 'time' being the RealTime at which it should occur.


Functions:
    run: Start the event loop.
    init: Initialize game modules.
    
Classes:
    Game: Represents the game's state.
"""

# standard modules
import os
import math
from collections import deque

# 3rd party modules
import pygame

class _Game:
    """
    Represents the state of the game.
    
    """

    @property
    def speed(self):
        """The current game speed (ignoring paused state)."""
        if not self.paused:
            return self._speed
        else:
            return self._real_speed

    @speed.setter
    def speed(self, speed):
        """Set the current game speed."""
        if not self.paused:
            self._speed = speed
        else:
            self._real_speed = speed

    @property
    def paused(self):
        """Whether the game is paused."""
        return self._real_speed is not None

    @paused.setter
    def paused(self, pause):
        """pause/unpause (True/False) the game."""
        pause = bool(pause)
        if self.paused is pause:
            # already in the right state
            return
        if pause:
            self._real_speed = self._speed
            self._speed = 0
        else:
            self._speed = self._real_speed
            self._real_speed = None

    def pause(self, paused=None):
        """Pause, unpause, or flip paused state (default)."""
        if paused is None:
            self.paused = not self.paused
        else:
            self.paused = bool(paused)

    def _next_event(self, frame_delta):
        """Get the next event in GameEvents or RealEvents that happens within the next frame_delta ms."""
        # Get next event (or a never-going-to-happen event, if there are no events)
        try:
            game_event = self.game_events[0]
        except IndexError:
            game_event = util.Event()
            game_event.time = util.INFINITY
        try:
            real_event = self.real_events[0]
        except IndexError:
            real_event = util.Event()
            real_event.time = util.INFINITY

        # Get time-to-event
        game_delta_time = game_event.time - self.game_time
        real_delta_time = real_event.time - self.current_time

        if game_event.time < self.game_time - util.EPSILON:
            raise Exception("Event must occur at a future time (%s > %s)" % (game_event.time, self.game_time))
        elif real_event.time < self.current_time:
            raise Exception("Event %s must occur at a future time." % real_event)

        # Normalize game time-to-event to be comparable with real time-to-events
        game_delta_time = util.ZeroDivide(abs(game_delta_time), self._speed)

        if game_delta_time > frame_delta or math.isnan(game_delta_time):
            # Game time events are some time after this frame.
            if real_delta_time > frame_delta:
                return None
            else:
                # Handle the 'real time event'
                return real_event
        else:
            if real_delta_time > frame_delta:
                # Real time events are some time after this frame.
                return game_event
            else:
                if game_delta_time < real_delta_time:
                    # Game time event will happen first.
                    return game_event
                else:
                    # Real time event will happen first.
                    return real_event

    def _calc_next_frame(self):
        while self.current_time < self._next_frame_time:
            ev = self._next_event(self._next_frame_time - self.current_time)
            if len(self.game_events) > 0 and ev is self.game_events[0]:
                # Game time event
                delta_time = (ev.time - self.game_time) / self._speed

                # Put current time at the event time
                self.game_time += delta_time * self._speed
                self.current_time += delta_time

                # Handle event
                ev()
                self.game_events.remove(ev)
            elif len(self.real_events) > 0 and ev is self.real_events[0]:
                # Real time event
                delta_time = ev.time - self.current_time

                # Put current time at the event time
                self.game_time += delta_time * self._speed
                self.current_time += delta_time

                # Handle event
                ev()
                self.real_events.remove(ev)
            elif ev is None:
                # Move time up to current time, this will end the while loop.
                self.game_time += (self._next_frame_time - self.current_time) * self._speed
                self.current_time = self._next_frame_time
            else:
                raise Exception("Invalid event %s from next_event, does not match next GameEvent %s or next RealEvent %s." % (ev, self.game_events[0], self.real_events[0]))
            # Handle mouse and keyboard events after every event
            event.update(pygame.time.get_ticks() - self._delay_time)
            
        self.game_events = [ev for ev in self.game_events if not ev.invalid]
        self.real_events = [ev for ev in self.real_events if not ev.invalid]

    def run(self):
        """Start the main event loop."""

        # Calculate the time in ms to wait in-between each frame.
        delta_frame_time = 1000 / self.fps
        
        # Clear the screen and display it to avoid startup-flicker.
        self.screen.clear()
        pygame.display.flip()
        
        # Get the time after initialization, to use as an offset.
        self._delay_time = pygame.time.get_ticks()
        try:
            while True:
                # Update the time and ignore initialization time.
                self._next_frame_time = pygame.time.get_ticks() - self._delay_time

                # Set timestamp for mouse and keyboard events and put them in the event queue.
                event.update(self._next_frame_time)
                
                delta_time = (self._next_frame_time - self.current_time)
                if delta_time >= delta_frame_time:
                    # It's time (or past time) to update the screen.
                    #
                    # Catch the simulation up to the current time by handling
                    # events in-order, and then draw the next frame.
                    self._calc_next_frame()
                    self.screen.draw_next_frame()
                    pygame.display.flip()
                    
                pygame.time.delay(1)  # Sleep 1 ms

        except controls.Quit:
            # Player has commanded the game to quit.
            print("Game over, man!  GAME OVER!")
        finally:
            # Game is exiting.  Clean up anything we need to before exiting.
            pygame.quit()

    def __init__(self):
        self.screen = None
        self.fps = 60
        self.bounciness = 0.9
        self.current_level = None
        
        self._next_frame_time = 0
        self._delay_time = 0
        self.current_time = 0
        self.game_time = 0
        
        self.game_events = deque()
        self.real_events = deque()
        
        self._speed = 1
        self._real_speed = None

game = _Game()

# library-specific modules
import util
import event
import controls
from window import Window
from level import Level

def init():
    # Resources path
    resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources")

    # Init Window
    game.screen = Window() # Accept default size and title

    # Load First Level
    game.current_level = Level("level_1.todo", resources_path)
