"""
The window module provides functionality for drawing to the screen, as well as functionality for
repositioning the center of the window.

TODO: Support a box centered around the player, as opposed to simply a point position.

Classes:
    Window: A wrapper to the pygame display in order to draw and translate coordinate systems.
"""

import pygame
from util import *

class Window:
    """A wrapper to the pygame display in order to draw to and translate to/from the pygame 
    coordinate system."""
    DEFAULT_WIDTH = 640
    DEFAULT_HEIGHT = 480
    
    def to_pygame(self, coords, height):
        """Converts object coordinates into pygame coordinates, given lower left coordinates of an
        object and the object's height."""
        # Get top left corner, then flip y-axis
        return (coords[0], self.screen.get_height() - (coords[1] + height))
    
    def draw(self, obj):
        """Draws an object to the screen."""
        try:
            # moves the origin to the difference between the position and screen center, and then adds the window half-size to center.
            self.screen.blit(obj.image, self.to_pygame(obj.position - (self.center) + (self.screen.get_width() / 2, self.screen.get_height() / 2), obj.image.get_height()))
        except AttributeError:
            pass

    def __init__(self, title = "Jetpack Man", size = [DEFAULT_WIDTH, DEFAULT_HEIGHT]):
        """Initialize the screen, window size, and title."""
        self.size = size
        self.title = title
        self.center = (0, 0)
        self.screen = pygame.display.set_mode(size) # Accept default flags:
        # Flags (second argument, multiple separated by | ):
            # pygame.FULLSCREEN    create a fullscreen display
            # pygame.DOUBLEBUF     recommended for HWSURFACE or OPENGL
            # pygame.HWSURFACE     hardware accelerated, only in FULLSCREEN
            # pygame.OPENGL        create an opengl renderable display
            # pygame.RESIZABLE     display window should be sizeable
            # pygame.NOFRAME       display window will have no border or controls
        pygame.display.set_caption(self.title)