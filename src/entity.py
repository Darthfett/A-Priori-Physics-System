"""


"""

import pygame

# Gravity acceleration is the default acceleration used for an entity.
Gravity = Vector(0, -2e-4)

class Entity:
    """Entity objects are things that have a position in the world."""

    def position_update(self, old, new):
        """Override to be notified of a position update."""
        pass

    def __repr__(self):
        return '{type}({params})'.format(type=type(self).__name__, params=', '.join('{name}={value}'.format(name=name, value=value) for name, value in self.__dict__.items()))

    def __init__(self, provider, position=None, **kwargs):
        """Instanciate an entity with position (defaults to (0, 0))."""
        self.provider = provider
        if position is None:
            self.position = Vector(0, 0)
        else:
            self.position = position
        super().__init__(**kwargs)


class Collidable:
    """Collidable objects are objects that can be collided with."""
    
    def __init__(self, mass=None, restitution=.883, **kwargs):
        """Instanciate a collidable with mass (defaults to INFINITY)."""
        self.mass = mass
        self.restitution = restitution
        if mass is None:
            self.mass = util.INFINITY
        super().__init__(**kwargs)
