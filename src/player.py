"""
The player module provides the player class.  Currently, only a single instance of a player class
is intended to be instanciated at any single point in time.

Classes:
    Player(Movable, Collidable, Drawable, Entity)
"""

from util import *
from entity import *

class Player(Movable, Collidable, Drawable, Entity):
    """The Player class, which is controlled by the physical player through keyboard/mouse events."""
    def __init__(self, **kwargs):
        """Instanciate the Player class.  Required keyword arguments:
               image - A str or pygame Surface"""
        super().__init__(**kwargs)
