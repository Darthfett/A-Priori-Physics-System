"""
The player module provides the player class.  Currently, only a single instance of a player class
is intended to be instanciated at any single point in time.

Classes:
    Player(Movable, Collidable, Blitable, Entity)
"""

import pygame
from util import *
import entity
import event

class Player(entity.Blitable, entity.Projectile):
    """The Player class, which is controlled by the physical player through keyboard/mouse events."""
    
    def a_pressed(self):
        self.velocity = self.velocity
        self.acceleration += Vector(-200, 0)
        self.recalculate_intersections()
        
    def a_released(self):
        self.velocity = self.velocity
        self.acceleration -= Vector(-200, 0)
        self.recalculate_intersections()
    
    def d_pressed(self):
        self.velocity = self.velocity
        self.acceleration += Vector(200, 0)
        self.recalculate_intersections()
        
    def d_released(self):
        self.velocity = self.velocity
        self.acceleration -= Vector(200, 0)
        self.recalculate_intersections()
    
    def __init__(self, **kwargs):
        """Instanciate the Player class.  Required keyword arguments:
               image - A str or pygame Surface
               shape - A list of line segments"""
        event.KeyPressEvent[pygame.K_a].register(self.a_pressed)
        event.KeyReleaseEvent[pygame.K_a].register(self.a_released)
        event.KeyPressEvent[pygame.K_d].register(self.d_pressed)
        event.KeyReleaseEvent[pygame.K_d].register(self.d_released)
        super().__init__(**kwargs)
