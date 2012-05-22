"""
The entity module provides all of the mixin entity classes that "mixed in" to more specific classes.
Also provided in this module are a few utility objects, such as a gravity vector.

Mixin classes are never intended to be instanciated directly, only through a subclass calling its
superconstructor.  Thus, all subclasses of any mixin(s) should take a keyword argument (**kwargs)
as a parameter, and call 'super().__init__(**kwargs)' in order to ensure its parent mixin(s)
are properly instanciated.

Globals:
    Gravity (Vector):
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
    Shaped(object):         Shaped objects have a 'shape'(Shape) attribute.
    Collidable(Entity):     Collidable objects have mass and can be invalidated through
                                manual changes of position/velocity/acceleration.
    Movable(Entity):        Movable objects have velocity and acceleration.
    Blitable(Entity):       Blitable objects have an image that can be blit to the screen.
    LineRenderable(object): LineRenderable objects have a 'render_shape' attribute (used to draw lines)

"""

import pygame

import util
from util import Vector, Shape, Position
import physics
from debug import debug

# Gravity acceleration is the default acceleration used for an entity.
Gravity = Vector(0, -2e-4)

# Lists containing all objects of each type (use these to iterate)
Entities = []
Collidables = []
Movables = []
Projectiles = []
Blitables = []
LineRenderables = []

class Entity:
    """Entity objects are things that have a position in the world."""

    def position_update(self, old, new):
        """Override to be notified of a position update."""
        pass

    def __init__(self, provider, position=None, **kwargs):
        """Instanciate an entity with position (defaults to (0, 0))."""
        self.provider = provider
        if position is None:
            self.position = Vector(0, 0)
        else:
            self.position = position

        Entities.append(self)
        super().__init__(**kwargs)

class Shaped(Entity):
    """Shaped objects are things that occupy space."""

    def position_update(self, old, new):
        try:
            del self._pos_shape
        except AttributeError:
            pass
        super().position_update(old, new)

    @property
    def pos_shape(self):
        if hasattr(self, '_pos_shape'):
            if self.provider.game_time == self._pos_shape_time:
                return self._pos_shape
        self._pos_shape = Shape(self.shape)
        self._pos_shape.offset(self.position)
        self._pos_shape_time = self.provider.game_time

        return self._pos_shape

    def __init__(self, shape, enclosed=True, **kwargs):
        if isinstance(shape, Shape):
            self.shape = shape
        else:
            self.shape = Shape(shape, enclosed)
        super().__init__(**kwargs)

class Collidable(Shaped, Entity):
    """Collidable objects are objects that can be collided with."""

    @property
    def velocity(self):
        return Vector()

    @property
    def acceleration(self):
        return Vector()

    def invalidate_intersections(self):
        for intersection in self.intersections:
            intersection.invalid = True
        self.intersections = [intersection for intersection in self.intersections if not intersection.invalid]

    def find_intersections(self, exclude=None):
        return physics.find_intersections(self, exclude=exclude)

    def __init__(self, mass=None, **kwargs):
        """Instanciate a collidable with mass (defaults to INFINITY)."""
        self.intersections = []
        self.mass = mass
        if mass is None:
            self.mass = util.INFINITY
        Collidables.append(self)
        super().__init__(**kwargs)

class Movable(Entity):
    """Movable objects are objects with velocity and acceleration."""

    @property
    def position(self):
        return util.Position(self._position, self._velocity, self.acceleration, self.provider.game_time - self._valid_time)

    @position.setter
    def position(self, position):
        """Updating position inherently invalidates all collisions, but does not take care of doing this."""
        old = self.position
        self._position = position
        self._valid_time = self.provider.game_time
        super().position_update(old, position)

    @property
    def velocity(self):
        return self._velocity + (self.provider.game_time - self._valid_time) * self.acceleration

    @velocity.setter
    def velocity(self, velocity):
        """Updating velocity inherently invalidates all collisions, but does not take care of doing this."""
        self.position = self.position
        self._velocity = velocity

    @property
    def acceleration(self):
        return self._acceleration

    @acceleration.setter
    def acceleration(self, acceleration):
        self._acceleration = acceleration

    def __init__(self, velocity=None, acceleration=None, **kwargs):
        """
        Instanciate a movable with velocity and acceleration (and then indirectly with position).
        Velocity defaults to (0, 0), and acceleration to Gravity.

        """
        self._position = kwargs.get('position') or Vector()
        self._valid_time = kwargs.get('provider').game_time
        self._velocity, self._acceleration = velocity, acceleration
        if velocity is None:
            self._velocity = Vector(0, 0)

        if acceleration is None:
            # Copy of Gravity vector, so as not to modify it.
            self._acceleration = Vector(Gravity)

        Movables.append(self)
        super().__init__(**kwargs)

class Projectile(Movable, Collidable, Shaped):
    """Projectile objects occupy space, can collide with objects, and move around."""

    def __init__(self, **kwargs):
        Projectiles.append(self)
        super().__init__(**kwargs)

class Blitable(Entity):
    """Blitables are objects with an image."""

    def draw(self, surface):
        """Blits the blitable to the specified surface."""
        if debug.DrawOutlines and hasattr(self, "shape"):
            for line in self.pos_shape.lines:
                surface.draw_aaline((0, 0, 0), line.p, line.q)
        else:
            surface.blit(self)

    def __init__(self, image, **kwargs):
        """Instanciate a blitable with an image (required, can be str or pygame Surface)."""
        if isinstance(image, pygame.Surface):
            self.image = image
        else:
            self.image = pygame.image.load(image)
        self.flipped = False
        Blitables.append(self)
        super().__init__(**kwargs)

class LineRenderable(Entity):
    """LineRenderables are objects that are drawn as a simple collection of lines."""

    def draw(self, surface):
        """Draws the individual lines of the line renderable to the specified surface."""
        for line in self.render_shape.lines:
            if hasattr(line, "color"):
                surface.draw_line(line.color, line.p + self.position, line.q + self.position)
            else:
                surface.draw_line(self.color, line.p + self.position, line.q + self.position)

    def __init__(self, render_shape, color=None, **kwargs):
        """Instanciate a line renderable with a list of lines."""
        self.render_shape, self.color = Shape(render_shape, kwargs.get("enclosed", None)), color

        if color is None:
            self.color = (0, 0, 0)

        LineRenderables.append(self)
        super().__init__(**kwargs)
