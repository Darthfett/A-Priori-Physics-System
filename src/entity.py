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
    Drawables (List(Drawable)):
        The list of all Drawable Entities.

Classes:
    Entity(object): Mixin class that has position.
    Collidable(Entity): Mixin class that has mass.
    Movable(Entity): Mixin class that has position, velocity, and acceleration.
    Drawable(Entity): Mixin class that has position and an image.
"""

from util import *
import pygame

# Gravity acceleration is the default acceleration used for an entity.
Gravity = Vector(0, -.0981)

# A listing of all entities of each type (for enumeration)
Entities = []
Collidables = []
Movables = []
Drawables = []

class Entity:
    """The Entity mixin class gives subclasses a position attribute."""
    
    def __init__(self, position = None, **kwargs):
        """Instanciate an entity with position (defaults to (0, 0))."""
        self.position = position
        if position is None:
            self.position = Point(0, 0)
        Entities.append(self)
        super().__init__(**kwargs)
    
class Collidable:
    """The Collidable mixin class gives subclasses a mass attribute."""
    
    def __init__(self, mass = None, **kwargs):
        """Instanciate a collidable with mass (defaults to INFINITY)."""
        self.mass = mass
        if mass is None:
            self.mass = INFINITY
        self.invalidated = True # A collidable is invalidated if it needs to recalculate collisions.
        Collidables.append(self)
        super().__init__(**kwargs)

class Movable(Entity):
    """The Movable mixin class gives subclasses a position, velocity, and acceleration attribute."""
        
    def __init__(self, velocity = None, acceleration = None, **kwargs):
        """Instanciate a movable with velocity and acceleration (and then indirectly with position).
        velocity defaults to (0, 0), and acceleration to Gravity."""
        self.velocity, self.acceleration = velocity, acceleration
        if velocity is None:
            self.velocity = Vector(0, 0)
        if acceleration is None:
            self.acceleration = Vector(Gravity) # Copy
        Movables.append(self)
        super().__init__(**kwargs)

class Drawable(Entity):
    """The Drawable mixin class gives subclasses a position and image attribute."""
    
    def __init__(self, image, **kwargs):
        """Instanciate a drawable with an image (required, can be str or pygame Surface)."""
        if isinstance(image, pygame.Surface):
            self.image = image
        else:
            self.image = pygame.image.load(image)
        Drawables.append(self)
        super().__init__(**kwargs)
        