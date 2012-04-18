"""
The player module provides the player class.  Currently, only a single instance of a player class
is intended to be instanciated at any single point in time.

Classes:
    Player(Movable, Collidable, Blitable, Entity)
"""

import pygame

from util import Vector
import entity
import event

class Player(entity.Blitable, entity.Projectile):
    """The Player class, which is controlled by the physical player through keyboard/mouse events."""
    
    def _jetpack_up(self, on):
        self.velocity = self.velocity
        if on:
            self.acceleration += Vector(0, 300)
        else:
            self.acceleration -= Vector(0, 300)
        self.recalculate_intersections()
    
    def _jetpack_left(self, on):
        self.velocity = self.velocity
        if on:
            self.acceleration += Vector(-200, 0)
        else:
            self.acceleration -= Vector(-200, 0)
        self.recalculate_intersections()
    
    def _jetpack_right(self, on):
        self.velocity = self.velocity
        if on:
            self.acceleration += Vector(200, 0)
        else:
            self.acceleration -= Vector(200, 0)
        self.recalculate_intersections()
    
    def __init__(self, **kwargs):
        """
        Instanciate the Player class.  Required keyword arguments:
            image - A str or pygame Surface
            shape - A list of line segments
        """
        super().__init__(**kwargs)
