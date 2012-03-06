"""
The game module provides a central location for linking all of the game
components together in a logical fashion.

Globals:
    Screen (window.Window):
        The Window object.
    FPS (number):
        The number of frames to draw every second.
    Speed (number):
        The speed multiplier, which changes how fast the game runs.
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
"""
import pygame
import os
import math

from util import *
from entity import *
import event
from window import Window
from player import Player
from level import Level

# Window object (Screen.screen is the actual window)
Screen = None
FPS = 60
Speed = 1
CurrentLevel = None
_NextFrameTime = 0
CurrentTime = 0
GameTime = 0
GameEvents = []
RealEvents = []

def _update_positions(time_frame):
    """Temporary hack (ignores collisions) to update all Movables' positions."""
    for ent in Movables:
        ent.velocity += time_frame * ent.acceleration
        
        # Quickly hack the shape to also get updated with the image
        # TODO: Have Shape.on_position_update called when position is manually changed.
        if isinstance(ent, Shape):
            Shape.on_position_update(ent, ent.position + time_frame * ent.velocity)
            
        ent.position += time_frame * ent.velocity

def _next_event(frame_delta):
    """Get the next event in GameEvents or RealEvents that happens within the next frame_delta ms."""
    # Get next event (or a never-going-to-happen event, if there are no events)
    try:
        game_event = GameEvents[0]
    except IndexError:
        game_event = event.Event()
        game_event.time = INFINITY
    try:
        real_event = RealEvents[0]
    except IndexError:
        real_event = event.Event()
        real_event.time = INFINITY
        
    # Get time-to-event
    game_delta_time = game_event.time - GameTime
    real_delta_time = real_event.time - CurrentTime
    
    if game_event.time < GameTime:
        raise Exception("Event %s must occur at a future time." % game_event)
    elif real_event.time < CurrentTime:
        raise Exception("Event %s must occur at a future time." % real_event)
    
    # Normalize game time-to-event to be comparable with real time-to-events
    game_delta_time = ZeroDivide(game_delta_time, Speed)
    
    if game_delta_time > frame_delta:
        # Game time events are some time after this frame.
        if real_delta_time > frame_delta:
            if not math.isinf(real_event.time):
                print(real_event)
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

def _calc_next_frame():
    global GameTime
    global CurrentTime
    while CurrentTime < _NextFrameTime:
        ev = _next_event(_NextFrameTime - CurrentTime)
        if len(GameEvents) > 0 and ev is GameEvents[0]:
            # Game time event
            delta_time = (ev.time - GameTime) / Speed
            
            # Put current time at the event time
            GameTime += delta_time * Speed
            CurrentTime += delta_time
            
            # Handle event
            ev.handle()
            GameEvents.pop(0)
        elif len(RealEvents) > 0 and ev is RealEvents[0]:
            # Real time event
            delta_time = ev.time - CurrentTime
            
            # Put current time at the event time
            GameTime += delta_time * Speed
            CurrentTime += delta_time
            
            # Handle event
            ev.handle()
            RealEvents.pop(0)
        elif ev is None:
            GameTime += (_NextFrameTime - CurrentTime) * Speed
            CurrentTime = _NextFrameTime
        else:
            raise Exception("Invalid event %s from next_event, does not match next GameEvent %s or next RealEvent %s." % (ev, GameEvents[0], RealEvents[0]))

def run():
    """Start the main event loop."""
    
    # Main loop    
    delta_frame_time = 1000 / FPS
    try:
        while True:
            global _NextFrameTime
            _NextFrameTime = pygame.time.get_ticks()

            # Handle mouse and keyboard events
            event.update(_NextFrameTime)
            
            delta_time = (_NextFrameTime - CurrentTime)
            current_game_time = GameTime
            if delta_time >= delta_frame_time:
                # calculate the next frame
                _calc_next_frame()
                
                # TODO: Refactor Entity positions be calculated according to last position time.
                # Currently, collisions are never expected, and positions will be wrong if this
                # is not refactored.
                # For now, calculate new positions
                delta_game_time = GameTime - current_game_time
                _update_positions(delta_game_time / 1000)

                # draw the next frame
                Screen.draw_next_frame()

                # Update the Display
                pygame.display.flip()
            pygame.time.delay(1)
                
    except event.GameOver:
        # Game over!  Just quit for now.
        print("Game over, man!  GAME OVER!")
    except event.PlayerQuit:
        # Player has commanded the game to quit.
        print("Game over, man!  GAME OVER!")
    finally:
        pygame.quit()

def init():
    """Initialize the game components -- The window, level, physics engine, entities, etc."""
    
    
    # Resources path
    resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
    
    # Init Window
    global Screen
    Screen = Window() # Accept default size and title

    # Init Entities
    image = pygame.image.load(os.path.join(resources_path, "guy.png"))
    player = Player(image = image, shape = Rect(image.get_rect()).shape, position=Vector(0, 40), velocity=Vector(130, 200))
    Entities.append(player)

    # Center the screen on the player
    Screen.center_on(player)
    
    # Load First Level
    global CurrentLevel
    CurrentLevel = Level("level_1.todo")
