"""
The entities module contains all user-defined entity objects.  They are
typically derived from classes in the entity module.

Classes:
  Ground                An entity that acts as a boundary for moving objects.
  Player                An entity that is controlled by the player.

"""

import entity

# Resolve namespace of Player to improve the namespace access
from entities.player import Player

class Bouncy(entity.LineRenderable, entity.Projectile):
    """
    Represents an object that bounces against other objects.

    inherits from:
      entity.LineRenderable
      entity.Projectile

    """
    def __init__(self, **kwargs):
        """
        Instanciate a Bouncy object.

        keyword arguments:
          render_shape      A util.Shape for drawing
          shape             A list of line segments
        """

        super().__init__(**kwargs)

class Ground(entity.LineRenderable, entity.Collidable, entity.Shaped):
    """
    Represents an object that acts as a boundary to moving objects.

    inherits from:
      entity.LineRenderable
      entity.Collidable
      entity.Shaped

    """

    def __init__(self, **kwargs):
        """
        Instanciate a Ground boundary.

        keyword arguments:
          render_shape      A util.Shape for drawing
          shape             A util.Shape for collision detection/resolution

        """

        super().__init__(**kwargs)
