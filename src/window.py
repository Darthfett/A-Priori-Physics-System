"""
The window module provides functionality for drawing to the screen, as well as functionality for
repositioning the center of the window.

TODO: Support a box centered around the player, as opposed to simply a point position.

Classes:
    Window: A wrapper to the pygame display in order to draw and translate coordinate systems.
"""

import pygame
from util import *
from entity import *

class Window:
    """A wrapper to the pygame display in order to draw to and translate to/from the pygame
    coordinate system."""
    DEFAULT_WIDTH = 640
    DEFAULT_HEIGHT = 480

    def to_pygame(self, blitable):
        """Converts object coordinates into pygame coordinates, given lower left coordinates of an
        object and the object's height."""
        # Get top left corner, then flip y-axis
        rect = Rect(blitable.image.get_rect())
        rect.offset(blitable.position)
        rect.top = self.size.y - rect.bottom
        return rect.top_left
    
    def to_pygame_coords(self, coords):
        v = Vector(coords)
        v.y = self.size.y - v.y
        return v

    def draw_line(self, color, start_pos, end_pos, width=1):
        start = self.to_pygame_coords(start_pos)
        end = self.to_pygame_coords(end_pos)
        pygame.draw.line(self.screen, color, start, end, width)

    def draw_aaline(self, color, start_pos, end_pos, blend=1):
        start = self.to_pygame_coords(start_pos)
        end = self.to_pygame_coords(end_pos)
        pygame.draw.line(self.screen, color, start, end, blend)

    def blit(self, blitable):
        """Draws an object to the screen."""
        # blit blitable to screen
        self.screen.blit(blitable.image, self.to_pygame(blitable))

    def draw_next_frame(self):
        """Draws all objects."""
        self.screen.fill((0, 0, 0))
        ents = set(Blitables)
        ents = ents.union(LineRenderables)
        for ent in ents:
            ent.draw(self)

    def __init__(self, title = "Jetpack Man", size = (DEFAULT_WIDTH, DEFAULT_HEIGHT)):
        """Initialize the screen, window size, and title."""
        self.title = title
        self.screen = pygame.display.set_mode(size) # Accept default flags:
            
        # Flags (second argument, multiple separated by | ):
            # pygame.FULLSCREEN    create a fullscreen display
            # pygame.DOUBLEBUF     recommended for HWSURFACE or OPENGL
            # pygame.HWSURFACE     hardware accelerated, only in FULLSCREEN
            # pygame.OPENGL        create an opengl renderable display
            # pygame.RESIZABLE     display window should be sizeable
            # pygame.NOFRAME       display window will have no border or controls
            
        self.size = Vector(self.screen.get_size())
        pygame.display.set_caption(self.title)