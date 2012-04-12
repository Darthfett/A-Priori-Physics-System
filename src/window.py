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

import util
import entity
from game import game

class Window:

    """
    A wrapper to the pygame display, with some additional functionality for
    translating coordinates, clearing the screen, drawing the next frame, and
    centering on the player.
    
    members:
      DEFAULT_WIDTH     The default width of the game window.
      DEFAULT_HEIGHT    The default height of the game window.
      FollowPlayer      Determines whether the window is always centered on the
                        player during coordinate translation.

    properties:
      title             The title of the window.  Changing this value does not
                        automatically update the window.
      screen            The actual pygame screen onto which everything is
                        drawn.
      size              A Vector that determines the size of the window.
      
    methods:
      to_pygame_coords  
                        Given normal coordinates, translate them into the
                        pygame equivalent.
      to_pyame          Given a blitable object, get the coordinates at which
                        the object should be drawn.
      draw_line         Draw a line at the given normal coordinates.
      draw_aaline       Draw an anti-aliased line at the given normal coords.
      blit              A wrapper for the pygame screen's blit, which
                        automatically translates the blitable's coordinates.
      clear             Clear the screen with the default background color.
      draw_next_frame   Clear the screen, and draw all objects at their current
                        position.
    
    """
    
    DEFAULT_WIDTH = 640
    DEFAULT_HEIGHT = 480
    FollowPlayer = True
    
    def to_pygame_coords(self, coords):
        """
        Converts coordinates into pygame coordinates
        
        
            +x is right, +y is up, (0, 0) is bottom left of screen into:
            +x is right, +y is down, (0, 0) is top left of screen"""
        coords = util.Vector(coords)
        if Window.FollowPlayer:
            # offset coords by screen center
            coords = coords + (self.size * .5)
            # offset coords by centered_obj
            center_point = game.current_level.player.position + util.Vector(game.current_level.player.image.get_size()) * .5
            coords = coords - center_point
        
        coords = util.Vector(0, self.size.y) + util.Vector(coords.x, -coords.y)
        return coords

    def to_pygame(self, blitable):
        """Converts object coordinates into pygame coordinates, given lower left coordinates of an
        object and the object's height."""
        # Get top left corner, and convert to pygame coordinates
        rect = util.Rect(blitable.image.get_rect())
        rect.offset(blitable.position)
        new_position = self.to_pygame_coords(rect.bottom_left)
        new_position = new_position + util.Vector(0, -blitable.image.get_height())
        return new_position

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
    
    def clear(self):
        """Clear the screen."""
        self.screen.fill((255, 255, 255))
        

    def draw_next_frame(self):
        """Draws all objects."""
        self.clear()
        ents = set(entity.Blitables)
        ents = ents.union(entity.LineRenderables)
        for ent in ents:
            ent.draw(self)
    
    def __init__(self, title="Jetpack Man", size=(DEFAULT_WIDTH, DEFAULT_HEIGHT)):
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
            
        self.size = util.Vector(self.screen.get_size())
        pygame.display.set_caption(self.title)