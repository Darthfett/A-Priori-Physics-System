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
from collections import deque

# 3rd party modules
import pygame

class _Game:
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
      bounciness        The bounciness of objects in a collision.
      current_level     The current level.
      real_time         The current time of the game.  Used for real events.
      game_time         The current game time.  Used for game events.
      game_events       A sorted list of game events in the order they occur.
      real_events       A sorted list of real events in the order they occur.
    
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
        """Set the paused/unpaused state of the game."""
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
        """Pause, unpause, or flip the game paused state (default)."""
        if paused is None:
            self.paused = not self.paused
        else:
            self.paused = bool(paused)

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
            game_event = self.game_events[0]
        except IndexError:
            # No events in queue, create a dummy event that will never happen
            game_event = GameEvent(INFINITY)
        # Get the next real event:
        try:
            real_event = self.real_events[0]
        except IndexError:
            # No events in queue, create a dummy event that will never happen
            real_event = RealEvent(INFINITY)

        # events are guaranteed to have current or future time.
        assert(game_event.delta_time > -EPSILON)
        assert(real_event.delta_time > -EPSILON)
        
        next_event = sorted((game_event, real_event))[0]
        
        if next_event.real_time > self._next_frame_time or math.isnan(next_event.real_time):
            return None, None
        
        if next_event is game_event:
            return next_event, self.game_events
        else:
            return next_event, self.real_events

    def _calc_next_frame(self):
        """
        Update the game state by repeatedly handling game/real events,
        fast-forwarding to the time at which they occur until caught up with
        _next_frame_time.
        
        """
        while self.real_time < self._next_frame_time:
            ev, ev_queue = self._next_event()
            if ev is None:
                # No events to handle this frame.
                self.game_time += (self._next_frame_time - self.real_time) * self._speed
                self.real_time = self._next_frame_time
                break

            # Fast forward time to the event time
            self.game_time = ev.game_time
            self.real_time = ev.real_time
            
            # Handle and remove the event
            ev()
            ev_queue.remove(ev)
            
            # Handle mouse and keyboard events after every event
            event.update(pygame.time.get_ticks() - self._delay_time)
        
        # Remove all invalid events from the event queues.
        # This avoids long-term events from wasting space in the queue.
        self.game_events = [ev for ev in self.game_events if not ev.invalid]
        self.real_events = [ev for ev in self.real_events if not ev.invalid]

    def run(self):
        """
        Start the main event loop.
        
        This handles delegation of tasks to check for user-input, update the
        game state, and draw the game to the screen.
        
        """

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
                
                delta_time = (self._next_frame_time - self.real_time)
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
        """Set the default state of the game."""
        self.screen = None
        self.fps = 60
        self.bounciness = 0.9
        self.current_level = None
        
        self._next_frame_time = 0
        self._delay_time = 0
        self.real_time = 0
        self.game_time = 0
        
        self.game_events = deque()
        self.real_events = deque()
        
        self._speed = 1
        self._real_speed = None

game = _Game()

# library-specific modules
from util import INFINITY, EPSILON
import event
from event import GameEvent, RealEvent
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
    
    # Init Controls
    controls.init()
