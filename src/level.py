import pygame
from util import *
from entity import Entities, LineRenderables
from ground import Ground

import random
import physics
import game

class Level:

    def regenerate_ground(self):
        """Randomly generate something that looks like a rough ground terrain."""

        # random height between 1 and 64, every 64 pixels
        interval = 64
        min_height, max_height = 1, 128
        get_height = lambda min, max: random.randrange(min, max)

        # generate vertices
        vertices = [(i, get_height(min_height, max_height)) for i in range(0, self.boundary.width+1, interval)]

        # generate lines connecting vertices
        lines = []
        for i, vertex in enumerate(vertices):
            if vertex is vertices[-1]:
                break
            lines.append(Line(vertex, vertices[i+1]))

        # set as the shape and render_lines for the ground
        self.ground.render_lines = lines
        self.ground.shape = lines
        game.Game().pause(False)
        self.ground.recalculate_intersections()

    def __init__(self, path):
        """Take a file at path, and extract level details."""
        # TODO: Load this in as a file
        width, height = 640, 480
        self.boundary = Rect(size=(width, height))

        self.ground = Ground(shape = [], render_lines = [])
        self.regenerate_ground()
        physics.update_intersections(self.ground)