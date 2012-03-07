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

class Game:
    __shared_state = {}

    # Window object (Screen.screen is the actual window)
    Screen = None
    FPS = 60
    CurrentLevel = None
    _NextFrameTime = 0
    CurrentTime = 0
    GameTime = 0
    GameEvents = []
    RealEvents = []

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
            game_event = Game.GameEvents[0]
        except IndexError:
            game_event = event.Event()
            game_event.time = INFINITY
        try:
            real_event = Game.RealEvents[0]
        except IndexError:
            real_event = event.Event()
            real_event.time = INFINITY

        # Get time-to-event
        game_delta_time = game_event.time - Game.GameTime
        real_delta_time = real_event.time - Game.CurrentTime

        if game_event.time < Game.GameTime:
            raise Exception("Event %s must occur at a future time." % game_event)
        elif real_event.time < Game.CurrentTime:
            raise Exception("Event %s must occur at a future time." % real_event)

        # Normalize game time-to-event to be comparable with real time-to-events
        game_delta_time = ZeroDivide(game_delta_time, self._speed)

        if game_delta_time > frame_delta:
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
        while Game.CurrentTime < Game._NextFrameTime:
            ev = self._next_event(Game._NextFrameTime - Game.CurrentTime)
            if len(Game.GameEvents) > 0 and ev is Game.GameEvents[0]:
                # Game time event
                delta_time = (ev.time - Game.GameTime) / self._speed

                # Put current time at the event time
                Game.GameTime += delta_time * self._speed
                Game.CurrentTime += delta_time

                # Handle event
                ev.handle()
                Game.GameEvents.pop(0)
            elif len(Game.RealEvents) > 0 and ev is Game.RealEvents[0]:
                # Real time event
                delta_time = ev.time - Game.CurrentTime

                # Put current time at the event time
                Game.GameTime += delta_time * self._speed
                Game.CurrentTime += delta_time

                # Handle event
                ev.handle()
                Game.RealEvents.pop(0)
            elif ev is None:
                Game.GameTime += (Game._NextFrameTime - Game.CurrentTime) * self._speed
                Game.CurrentTime = Game._NextFrameTime
            else:
                raise Exception("Invalid event %s from next_event, does not match next GameEvent %s or next RealEvent %s." % (ev, Game.GameEvents[0], Game.RealEvents[0]))

    def run(self):
        """Start the main event loop."""

        # Main loop
        delta_frame_time = 1000 / Game.FPS
        try:
            while True:
                Game._NextFrameTime = pygame.time.get_ticks()

                # Handle mouse and keyboard events
                event.update(Game._NextFrameTime)

                delta_time = (Game._NextFrameTime - Game.CurrentTime)
                current_game_time = Game.GameTime
                if delta_time >= delta_frame_time:
                    # calculate the next frame
                    self._calc_next_frame()

                    # draw the next frame
                    Game.Screen.draw_next_frame()

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

    def __init__(self, speed=1):
        self.__dict__ = self.__shared_state
        if not hasattr(self, "_speed"):
            self._speed = speed
            self._real_speed = None

def init():
    # Resources path
    resources_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")

    # Init Window
    Game.Screen
    Game.Screen = Window() # Accept default size and title

    # Init Entities
    image = pygame.image.load(os.path.join(resources_path, "guy.png"))
    player = Player(image = image, shape = Rect(image.get_rect()).shape, position=Vector(0, 0), velocity=Vector(130, 200))
    Entities.append(player)

    # Center the screen on the player
    Game.Screen.center_on(player)

    # Load First Level
    Game.CurrentLevel = Level("level_1.todo")
