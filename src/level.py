import os

import pygame
import random

from util import Vector, Shape, Rect, generate_circle
import physics
import entity
import entities

class Level:

    _PlayerPosition = Vector(10, 20)
    _PlayerVelocity = Vector(0, 0)

    def level_1(self):
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
        self.ground = entities.Ground(provider=self.provider, shape=vertices, render_shape=vertices)
        sqr = Rect(size=(10, 10))

    def __init__(self, provider, path, resources_path):
        """Take a file at path, and extract level details."""
        # TODO: Load this in as a file
        self.provider = provider
        width, height = 640, 480
        self.boundary = Rect(size=(width, height))

        image = pygame.image.load(os.path.join(resources_path, "guy2.PNG"))
        shape = Rect(image.get_rect()).shape
        # shape = generate_circle(8, 50)
        self.player = entities.Player(provider=provider, image=image, shape=shape, position=Level._PlayerPosition, velocity=Level._PlayerVelocity)
        self.width, self.height = width, height
        self.level_1()