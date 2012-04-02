import pygame
import os
import random

import util
import game
import physics
import entity
import player
from ground import Ground

class Level:

    _PlayerPosition = util.Vector(30, 350)
    _PlayerVelocity = util.Vector(0, 0)

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
        # vertices.append(util.Point(10, 10))
        # vertices.append(util.Point(self.width - 10, 10))
        # vertices.append(util.Point(self.width - 10, self.height - 10))
        # vertices.append(util.Point(10, self.height - 10))
        # enclosed = True
        
        # set as the shape and render_shape for the ground
        self.ground.render_shape = util.Shape(vertices, enclosed)
        self.ground._shape = self.ground.render_shape
        self.ground.recalculate_intersections()
    
    def reset_player(self):
        self.player.position = Level._PlayerPosition
        self.player.velocity = Level._PlayerVelocity
        self.player.recalculate_intersections()

    def __init__(self, path, resources_path):
        """Take a file at path, and extract level details."""
        # TODO: Load this in as a file
        width, height = 640, 480
        self.boundary = util.Rect(size=(width, height))
        
        image = pygame.image.load(os.path.join(resources_path, "guy.png"))
        # shape = util.Rect(image.get_rect()).shape
        shape = util.generate_circle(6, 50)
        self.player = player.Player(image = image, shape = shape, position=Level._PlayerPosition, velocity=Level._PlayerVelocity)
        self.width, self.height = width, height
        self.ground = Ground(shape = [], render_shape = [])
        self.regenerate_ground()
        
        physics.update_intersections(self.ground)