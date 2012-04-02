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
    Shaped(object):         Shaped objects have a 'shape'(util.Shape) attribute.
    Collidable(Entity):     Collidable objects have mass and can be invalidated through
                                manual changes of position/velocity/acceleration.
    Movable(Entity):        Movable objects have velocity and acceleration.
    Blitable(Entity):       Blitable objects have an image that can be blit to the screen.
    LineRenderable(object): LineRenderable objects have a 'render_shape' attribute (used to draw lines)
"""

import pygame

import util
import game
import physics
from debug import Debug

# Gravity acceleration is the default acceleration used for an entity.
Gravity = util.Vector(0, -200)

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
            self.position = util.Point(0, 0)

        Entities.append(self)
        super().__init__(**kwargs)

class Shaped:
    """Shaped objects are things that occupy space."""
    
    @property
    def shape(self):
        return self._shape

    def __init__(self, shape, enclosed = True, **kwargs):
        if isinstance(shape, util.Shape):
            self._shape = shape
        else:
            self._shape = util.Shape(shape, enclosed)
        super().__init__(**kwargs)

class Collidable(Shaped, Entity):
    """Collidable objects are objects that can be collided with."""
    
    def __getattr__(self, name):
        if name == "velocity":
            return util.Vector(0, 0)
        if name == "acceleration":
            return util.Vector(0, 0)
        raise AttributeError("%r object has no attribute %r" % (type(self).__name__, name))
        
    def recalculate_intersections(self, exclude = None):
        for intersection in self.intersections:
            intersection.invalid = True
        self.intersections = []
        physics.update_intersections(self, exclude)

    def __init__(self, mass = None, **kwargs):
        """Instanciate a collidable with mass (defaults to INFINITY)."""
        self.intersections = []
        self.mass = mass
        self.last_collide_time = -1
        if mass is None:
            self.mass = util.INFINITY
        Collidables.append(self)
        super().__init__(**kwargs)
        physics.update_intersections(self)

class Movable(Entity):
    """Movable objects are objects with velocity and acceleration."""
    
    @property
    def position(self):
        del_time_seconds = (game.Game.GameTime - self._valid_time) / 1000
        return util.Position(self._position, self._velocity, self.acceleration, del_time_seconds)
    
    @position.setter
    def position(self, position):
        """Updating position inherently invalidates all collisions, but does not take care of doing this."""
        self._position = position
        self._valid_time = game.Game.GameTime
        
    @property
    def velocity(self):
        del_time_seconds = (game.Game.GameTime - self._valid_time) / 1000
        return self._velocity + del_time_seconds * self.acceleration
    
    @velocity.setter
    def velocity(self, velocity):
        """Updating velocity inherently invalidates all collisions, but does not take care of doing this."""
        self.position = self.position
        self._velocity = velocity

    def __init__(self, velocity = None, acceleration = None, **kwargs):
        """Instanciate a movable with velocity and acceleration (and then indirectly with position).
        velocity defaults to (0, 0), and acceleration to Gravity."""
        self._velocity, self.acceleration = velocity, acceleration
        if velocity is None:
            self._velocity = util.Vector(0, 0)

        if acceleration is None:
            # Copy of Gravity vector, so as not to modify it.
            self.acceleration = util.Vector(Gravity)

        Movables.append(self)
        super().__init__(**kwargs)

class Projectile(Movable, Collidable, Shaped):
    """Projectile objects occupy space, can collide with objects, and move around."""

    def __init__(self, **kwargs):
        Projectiles.append(self)
        super().__init__(**kwargs)

class Blitable:
    """Blitables are objects with an image."""

    def draw(self, surface):
        """Blits the blitable to the specified surface."""
        if Debug.DrawOutlines and hasattr(self, "shape"):
            for line in self.shape.lines:
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
        for line in self.render_shape.lines:
            if hasattr(line, "color"):
                surface.draw_aaline(line.color, line.p, line.q)
            else:
                surface.draw_aaline(self.color, line.p, line.q)

    def __init__(self, render_shape, color = None, **kwargs):
        """Instanciate a line renderable with a list of lines."""
        self.render_shape, self.color = util.Shape(render_shape, kwargs.get("enclosed", None)), color

        if color is None:
            self.color = (255, 255, 255)

        LineRenderables.append(self)
        super().__init__(**kwargs)
