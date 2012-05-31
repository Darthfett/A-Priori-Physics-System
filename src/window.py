"""
The window module provides functionality for drawing to the screen, as well as
functionality for repositioning the center of the window.

It also handles all translation of coordinates from pygame to more normal
coordinates, where the lower left is (0, 0), and Up is the positive-y
direction.

classes:
  Window                Wraps the pygame display to translate coordinates, and
                        center the screen on the player.

"""

import pygame

from util import Vector, Rect

DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480

def to_pygame_coords(coords, window_size, center=Vector(), height=0):
    coords = Vector(coords)

    # offset coords by screen center
    coords += .5 * window_size

    # offset coords to center
    coords -= center

    # Convert from world to window/pygame coordinates
    coords = Vector(coords.x, window_size.y - coords.y - height

def blitable_pygame_position(blitable, window_size, center=Vector())
    return to_pygame_coords(Rect(blitable.image.get_rect()).bottom_left + blitable.position, window_size, center, height=blitable.image.get_height())

class Window:

    def clear(self):
        """Clear the screen."""
        self.screen.fill((255, 255, 255))

    def blit(self, surface, coords):
        coords = to_pygame_coords(coords, self.size, height=surface.get_height())

        self.screen.blit(surface, coords)

    def draw_blitable(self, blitable, center=Vector()):
        image = blitable.image
        flip = blitable.flipped
        coords = blitable_pygame_position(blitable, self.size, center)

        self.screen.blit(pygame.transform.flip(image, flip, False), coords)

    def draw_line(self, color, start_pos, end_pos, width=1):
        start = to_pygame_coords(start_pos, self.size)
        end = to_pygame_coords(end_pos, self.size)

        pygame.draw.line(self.screen, color, start, end, width)

    def draw_aaline(self, color, start_pos, end_pos, blend=1):
        start = to_pygame_coords(start_pos, self.size)
        end = to_pygame_coords(end_pos, self.size)

        pygame.draw.line(self.screen, color, start, end, blend)

    def __getattr__(self, name):
        return getattr(self.screen, name)

    def __init__(self, screen):
        self.screen = screen
        self.size = Vector(self.screen.get_size())