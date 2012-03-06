import pygame
from util import *
from entity import Entities, LineRenderables
from ground import Ground

import random

class Level:

    def regenerate_ground(self):
        """Randomly generate something that looks like a rough ground terrain."""
        
        # random height between 1 and 64, every 64 pixels        
        interval = 64
        min_height, max_height = 1, 64
        get_height = lambda min, max: random.randrange(min, max)
        
        # generate vertices
        vertices = [(i, get_height(min_height, max_height)) for i in range(0, self.boundary.width, interval)]
        
        # generate lines connecting vertices
        lines = []
        for i, vertex in enumerate(vertices):
            if vertex is vertices[-1]:
                break
            lines.append(Line(vertex, vertices[i+1]))
        
        # set as the shape and render_lines for the ground
        self.ground.render_lines = lines
        self.ground.shape = lines

    def __init__(self, path):
        """Take a file at path, and extract level details."""
        # TODO: Load this in as a file
        width, height = 5000, 5000
        self.boundary = Rect(size=(width, height))
            
        self.ground = Ground(shape = [], render_lines = [])
        self.regenerate_ground()
        Entities.append(self.ground)