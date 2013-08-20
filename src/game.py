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
pass

# 3rd party modules
import pygame

# local modules
from util import immutable

@immutable
class GameData:    
    @immutable.constructor
    def __init__(self, screen, level, time=0, next_frame_time):
        self.screen, self.level = screen, level
        self.time, self.next_frame_time = time, next_frame_time

@immutable
class GameModifiers:    
    @immutable.constructor
    def __init__(self, fps=60, speed=1, paused=False):
        self.fps, self.speed, self.paused = fps, speed, paused

@immutable
class GameFlags:    
    @immutable.constructor
    def __init__(self, debug=False, draw_outlines=False):
        self.debug, self.draw_outlines = debug, draw_outlines

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

    def next_frame(self, data, modifiers, flags):
        """
        Update the game state by repeatedly handling game/real events,
        fast-forwarding to the time at which they occur until caught up with
        next_frame_time.

        """
        while self.state.real_time <= self.state.next_frame_time:
            ev, ev_queue = self._next_event()
            if ev is None:
                # No events to handle this frame.
                self.state.game_time += (self.state.next_frame_time - self.state.real_time) * self.state._speed
                self.state.real_time = self.state.next_frame_time
                break

            # Fast forward time to the event time
            self.state.game_time = ev.game_time
            self.state.real_time = ev.real_time

            # Handle and remove the event
            heapq.heappop(ev_queue)
            g_events, r_events = ev(self.provider)
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
        assert self.state.real_time == self.state.next_frame_time

    def run(self, data, modifiers, flags):
        """
        Start the main event loop.

        This handles delegation of tasks to check for user-input, update the
        game state, and draw the game to the screen.

        """
        # avoid startup-flicker.
        self.state.screen.clear()
        pygame.display.flip()

        init_time = pygame.time.get_ticks()
        self.state.next_frame_time += init_time
        try:
            while True:
                # Update the time and ignore initialization time.
                current_time = pygame.time.get_ticks() - init_time

                key_events = event.check_for_new_events(self.provider, current_time)
                self.state.real_events.extend(key_events)
                heapq.heapify(self.state.real_events)

                if current_time >= self.state.next_frame_time:
                    # Catch the simulation up to the current time by handling
                    # events in-order, and then draw the next frame.
                    self._next_frame()
                    assert self.state.real_time == self.state.next_frame_time

                    self.state.screen.draw_next_frame()

                    delta_frame_time = 1000 / self.state.fps
                    self.state.next_frame_time += delta_frame_time

                    pygame.display.flip()

                pygame.time.delay(1)  # Sleep 1 ms

        except controls.Quit:
            # Player has commanded the game to quit.
            print("Game over, man!  GAME OVER!")
        finally:
            # Game is exiting.  Clean up anything we need to before exiting.
            pygame.quit()

    def __init__(self, state, provider):
        """Set the default state of the game."""
        self.state = state
        self.provider = provider