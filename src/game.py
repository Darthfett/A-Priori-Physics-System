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
from operator import attrgetter
from itertools import filterfalse
from heapq import merge

# 3rd party modules
import pygame

class GameStateProvider:
    _CurrentState = None

    def update(self, new_state):
        GameStateProvider._CurrentState = new_state

    def __getattr__(self, name):
        # GameState object properties are immutable, so this can't cause issues
        return getattr(GameStateProvider._CurrentState, name)

# library-specific modules
from util import INFINITY, EPSILON
import event
from event import GameEvent, RealEvent
import controls
from window import Window
from level import Level

class GameState:
    
    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, name):
        return self.__dict__[name]

    def __init__(self, state=None, fps=None, bounciness=None, speed=None, game_events=None, real_events=None, game_time=None, real_time=None, _next_frame_time=None, paused=None):
        """Set the default state of the game."""
        if state is None:
            self.screen = None
            self.current_level = None
            if fps is None:
                self.fps = 60
            else:
                self.fps = fps
            if bounciness is None:
                self.bounciness = 0.9
            else:
                self.bounciness = bounciness
            if speed is None:
                self.speed = 1
            else:
                self.speed = speed
            self.paused = False
            
            self._next_frame_time = 0
            self._init_time = 0
            self.real_time = 0
            self.game_time = 0
            
            self.game_events = ()
            self.real_events = ()
        else:
            self.__dict__.update(**state)
            
            if game_events is None:
                self.game_events = tuple(self.game_events)
            else:
                self.game_events = tuple(game_events)
                
            if real_events is None:
                self.real_events = tuple(self.real_events)
            else:
                self.real_events = tuple(real_events)
                
            if game_time is not None:
                self.game_time = game_time
            
            if real_time is not None:
                self.real_time = real_time
            
            if _next_frame_time is not None:
                self._next_frame_time = _next_frame_time
            
            if paused is not None:
                self.paused = paused

def _next_event(game_state):
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
    if game_state.game_events and not game_state.paused:
        game_event = game_state.game_events[0]
    else:
        # No events in queue (or game is paused), create a dummy event that will never happen
        game_event = GameEvent(INFINITY)

    if game_state.real_events:
        real_event = game_state.real_events[0]
    else:
        # No events in queue, create a dummy event that will never happen
        real_event = RealEvent(INFINITY)

    # events are guaranteed to have current or future time.
    assert game_event.delta_time > -EPSILON
    assert real_event.delta_time > -EPSILON
    
    next_event = sorted((real_event, game_event))[0]
    
    assert not math.isnan(next_event.real_time)
    
    if next_event.real_time > game_state._next_frame_time:
        return None
    else:
        return next_event
            
def _next_frame(game_state):
    """
    nextframe(GameState) -> GameState
    
    Get an updated GameState, by repeatedly handling game/real events,
    fast-forwarding to the time at which they occur until caught up with
    _next_frame_time.
    
    """
    while game_state.real_time <= game_state._next_frame_time:
        ev = _next_event(game_state)
        
        # update the game state
        if ev and ev is game_state.game_events[0]:
            game_state = GameState(game_state, game_events = game_state.game_events[1:])
        elif ev and ev is game_state.real_events[0]:
            game_state = GameState(game_state, real_events = game_state.real_events[1:])
        else:
            assert ev is None
            # No events to handle this frame.
            
            # Update game state and time
            if game_state.paused:
                game_time = game_state.game_time
            else:
                # use current speed and delta time to find game time at next frame
                game_time = game_state.game_time + (game_state._next_frame_time - game_state.real_time) * game_state.speed
            
            
            real_time = game_state._next_frame_time
            
            # Remove invalid events
            game_events=filterfalse(attrgetter('invalid'), game_state.game_events)
            real_events=filterfalse(attrgetter('invalid'), game_state.real_events)
            
            # Update game state
            game_state = GameState(game_state, game_events=game_events, real_events=real_events, game_time=game_time, real_time=real_time)
            break

        # Fast forward time to the event time
        game_state.game_time = ev.game_time
        game_state.real_time = ev.real_time
        
        # Handle the event
        game_events, real_events = ev(game_state)
        if game_events or real_events:
            game_state = GameState(game_state, game_events=merge(game_events, game_state.game_events), real_events=merge(real_events, game_state.real_events))
    
    # Post-conditions
    ev = _next_event(game_state)
    assert ev is None
    assert game_state.real_time == game_state._next_frame_time
    
    return game_state

def run(game_state):
    """
    Start the main event loop.
    
    This handles delegation of tasks to check for user-input, update the
    game state, and draw the game to the screen.
    
    """

    delta_frame_time = 1000 / game_state.fps
    
    # avoid startup-flicker.
    game_state.screen.clear()
    pygame.display.flip()
    
    _init_time = pygame.time.get_ticks()
    new_events = []
    try:
        while True:
            # Update the time and ignore initialization time.
            current_time = pygame.time.get_ticks() - _init_time
            
            new_events.extend(event.check_for_new_events(current_time))
            
            time_since_last_frame = (current_time - game_state.real_time)
            if time_since_last_frame >= delta_frame_time:
                game_state = GameState(game_state, real_events=merge(new_events, game_state.real_events), _next_frame_time=current_time)
                # Catch the simulation up to the current time by handling
                # events in-order, and then draw the next frame.
                GameStateProvider().update(game_state)
                game_state = _next_frame(game_state)
                GameStateProvider().update(game_state)
                assert game_state.real_time == game_state._next_frame_time
                                
                game_state.screen.draw_next_frame()
                pygame.display.flip()
                
            pygame.time.delay(1)  # Sleep 1 ms

    except controls.Quit:
        # Player has commanded the game to quit.
        print("Game over, man!  GAME OVER!")
    finally:
        # Game is exiting.  Clean up anything we need to before exiting.
        pygame.quit()

def init(game_state):
    # Resources path
    resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources")

    # Init Window
    game_state.screen = Window(game_state=game_state) # Accept default size and title

    # Load First Level
    game_state.current_level = Level("level_1.todo", resources_path, game_state=game_state)
    
    # Init Controls
    controls.init(game_state)
