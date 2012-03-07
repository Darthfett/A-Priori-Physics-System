"""
The entity module provides all of the mixin entity classes that "mixed in" to more specific classes.
Also provided in this module are a few utility objects, such as a gravity vector.

Mixin classes are never intended to be instanciated directly, only through a subclass calling its
superconstructor.  Thus, all subclasses of any mixin(s) should take a keyword argument (**kwargs)
as a parameter, and call 'super().__init__(**kwargs)' in order to ensure its parent mixin(s)
are properly instanciated.

Globals:
    Gravity (util.Vector):
        The universal gravity vector.
    Entities (List(Entity)):
        The list of all Entities.
    Collidables (List(Collidable)):
        The list of all Collidable Entities.
    Movables (List(Movable)):
        The list of all Mobile Entities.
    Projectiles (List(Projectile)):
        The list of all Projectile Entities.
    Blitables (List):
        The list of all Blitable Entities.
    LineRenderables (List(LineRenderable)):
        The list of all LineRenderables.

Classes:
    Entity(object):         Entity objects have position.
    Shape(object):          Shape objects have a 'shape' attribute -- a list of line-segments.
    Collidable(Entity):     Collidable objects have mass and can be invalidated through
                                manual changes of position/velocity/acceleration.
    Movable(Entity):        Movable objects have velocity and acceleration.
    Blitable(Entity):       Blitable objects have an image that can be blit to the screen.
    LineRenderable(object): LineRenderable objects have a 'render_lines' attribute -- a list of
                                lines intended to be drawn to the screen.
"""

from util import *
from debug import Debug
import pygame
import game

# Gravity acceleration is the default acceleration used for an entity.
Gravity = Vector(0, -200)

# A listing of all entities of each type (for enumeration)
Entities = []
Collidables = []
Movables = []
Projectiles = []
Blitables = []
LineRenderables = []

class Entity:
    """Entity objects are things that have a position in the world."""

    def __init__(self, position = None, **kwargs):
        """Instanciate an entity with position (defaults to (0, 0))."""
        self.position = position
        if position is None:
            self.position = Point(0, 0)

        Entities.append(self)
        super().__init__(**kwargs)

class Shape:
    """Shape objects are things that occupy space."""

    def __init__(self, shape, **kwargs):
        self.shape = shape
        super().__init__(**kwargs)

class Collidable(Entity):
    """Collidable objects are objects that can be collided with."""

    def on_position_update(self, position):
        # TODO: Have this method called when position is manually changed.
        self.invalidated = True

    def on_velocity_update(self, velocity):
        # TODO: Have this method called when velocity is manually changed.
        self.invalidated = True

    def on_acceleration_update(self, acceleration):
        # TODO: Have this method called when acceleration is manually changed.
        self.invalidated = True

    def __init__(self, mass = None, **kwargs):
        """Instanciate a collidable with mass (defaults to INFINITY)."""
        self.invalidated = True
        self.intersections = []
        self.mass = mass
        if mass is None:
            self.mass = INFINITY

        Collidables.append(self)
        super().__init__(**kwargs)

class Movable(Entity):
    """Movable objects are objects with velocity and acceleration."""
    
    @property
    def position(self):
        del_time_seconds = (game.Game.GameTime - self._position_valid_time) / 1000
        return self._position + self.velocity * del_time_seconds + .5 * self.acceleration * (del_time_seconds ** 2)
    
    @position.setter
    def position(self, position):
        self._position = position
        self._position_valid_time = game.Game.GameTime

    def __init__(self, velocity = None, acceleration = None, **kwargs):
        """Instanciate a movable with velocity and acceleration (and then indirectly with position).
        velocity defaults to (0, 0), and acceleration to Gravity."""
        self.velocity, self.acceleration = velocity, acceleration
        if velocity is None:
            self.velocity = Vector(0, 0)

        if acceleration is None:
            # Copy Gravity vector
            self.acceleration = Vector(Gravity)

        Movables.append(self)
        super().__init__(**kwargs)

class Projectile(Collidable, Movable, Shape):
    """Projectile objects occupy space, can collide with objects, and move around."""

    def __init__(self, **kwargs):
        Projectiles.append(self)
        super().__init__(**kwargs)
_tmp = 0
class Blitable:
    """Blitables are objects with an image."""

    def draw(self, surface):
        """Blits the blitable to the specified surface."""
        if Debug.DrawOutlines and hasattr(self, "shape"):
            for line in self.shape:
                try:
                    surface.draw_aaline((255, 255, 255), line.p + self.position, line.q + self.position)
                except AttributeError:
                    surface.draw_aaline((255, 255, 255), line.p, line.q)
        else:
            surface.blit(self)

    def __init__(self, image, **kwargs):
        """Instanciate a blitable with an image (required, can be str or pygame Surface)."""
        if isinstance(image, pygame.Surface):
            self.image = image
        else:
            self.image = pygame.image.load(image)

        Blitables.append(self)
        super().__init__(**kwargs)

class LineRenderable:
    """LineRenderables are objects that are drawn as a simple collection of lines."""

    def draw(self, surface):
        """Draws the individual lines of the line renderable to the specified surface."""
        for line in self.render_lines:
            surface.draw_aaline(self.color, line.p, line.q)

    def __init__(self, render_lines, color = None, **kwargs):
        """Instanciate a line renderable with a list of lines."""
        self.render_lines, self.color = render_lines, color

        if render_lines is None:
            self.render_lines = []

        if color is None:
            self.color = (255, 255, 255)

        LineRenderables.append(self)
        super().__init__(**kwargs)
