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
import physics

class Player(entity.Blitable, entity.Projectile):
    """The Player class, which is controlled by the physical player through keyboard/mouse events."""

    def _jetpack_up(self, on):
        self.velocity = self.velocity
        if on:
            self.acceleration += Vector(0, 3e-4)
        else:
            self.acceleration -= Vector(0, 3e-4)
        self.invalidate_intersections()
        ints = physics.find_intersections(self.provider, self)
        self.intersections.extend(ints)
        return ints, []

    def _jetpack_left(self, on):
        self.flipped = True
        self.velocity = self.velocity
        if on:
            self.acceleration += Vector(-2e-4, 0)
        else:
            self.acceleration -= Vector(-2e-4, 0)
        self.invalidate_intersections()
        ints = physics.find_intersections(self.provider, self)
        self.intersections.extend(ints)
        return ints, []

    def _jetpack_right(self, on):
        self.flipped = False
        self.velocity = self.velocity
        if on:
            self.acceleration += Vector(2e-4, 0)
        else:
            self.acceleration -= Vector(2e-4, 0)
        self.invalidate_intersections()
        ints = physics.find_intersections(self.provider, self)
        self.intersections.extend(ints)
        return ints, []

    def __init__(self, **kwargs):
        """
        Instanciate the Player class.  Required keyword arguments:
            image - A str or pygame Surface
            shape - A list of line segments
        """
        super().__init__(**kwargs)
