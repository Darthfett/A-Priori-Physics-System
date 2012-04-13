import os

import pygame
import random

from util import Vector, Shape, Rect, generate_circle
from game import game
import physics
import entity
import entities

class Level:

    _PlayerPosition = Vector(10, 20)
    _PlayerVelocity = Vector(0, 0)

    def regenerate_ground(self):
        """Randomly generate something that looks like a rough ground terrain."""

        # random height between 1 and 64, every 64 pixels
        interval = 64
        min_height, max_height = 1, 128
        get_height = lambda min, max: random.randrange(min, max)

        # generate vertices
        vertices = [(i, get_height(min_height, max_height)) for i in range(0, self.boundary.width+1, interval)]
        enclosed = False
        
        # Rectangle:
        # vertices = []
        # vertices.append(Vector(10, 10))
        # vertices.append(Vector(self.width - 10, 10))
        # vertices.append(Vector(self.width - 10, self.height - 10))
        # vertices.append(Vector(10, self.height - 10))
        # enclosed = True
        
        # set as the shape and render_shape for the ground
        self.ground.render_shape = Shape(vertices, enclosed)
        self.ground._shape = self.ground.render_shape
        self.ground.recalculate_intersections()
    
    def reset_player(self):
        self.player.position = Level._PlayerPosition
        self.player.velocity = Level._PlayerVelocity
        self.player.recalculate_intersections()
    
    def level_2(self):
        vertices = []
        vertices.extend([Vector(0, 0),
                         Vector(500, 0),
                         Vector(500, 100),
                         Vector(1000, 100),
                         Vector(1350, 0),
                         Vector(1500, 0),
                         Vector(1500, 500),
                         Vector(1000, 500),
                         Vector(150, 650),
                         Vector(150, 1000),
                         Vector(500, 1000),
                         Vector(1000, 950),
                        
                         Vector(1000, 1150),
                         Vector(0, 1150),
                         Vector(0, 500),
                         Vector(1000, 250),
                         Vector(1350, 250),
                         Vector(0, 250)])
        self.ground = entities.Ground(shape = vertices, render_shape = vertices)
                        
                        

    def __init__(self, path, resources_path):
        """Take a file at path, and extract level details."""
        # TODO: Load this in as a file
        width, height = 640, 480
        self.boundary = Rect(size=(width, height))
        
        image = pygame.image.load(os.path.join(resources_path, "jetpack_guy.PNG"))
        shape = Rect(image.get_rect()).shape
        # shape = generate_circle(8, 50)
        self.player = entities.Player(image=image, shape=shape, position=Level._PlayerPosition, velocity=Level._PlayerVelocity)
        self.width, self.height = width, height
        self.level_2()
        #self.ground = entities.Ground(shape=[], render_shape=[])
        #self.regenerate_ground()
        
        physics.update_intersections(self.ground)