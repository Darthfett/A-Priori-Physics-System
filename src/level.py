import pygame, os
from util import *
from entity import Entities, LineRenderables
from ground import Ground

import random
import physics
import game
import player

def generate_circle(n, radius):
    center = Point(radius, radius)
    vertices = []
    for i in range(n):
        vertex = center + Vector(radius * math.sin((i/n) * 2 * math.pi), radius * math.cos((i/n) * 2 * math.pi))
        vertices.append(vertex)
    lines = []
    for i, vertex in enumerate(vertices):
        if vertex is vertices[-1]:
            break
        lines.append(Line(vertex, vertices[i+1]))
    lines.append(Line(vertices[-1], vertices[0]))
    return lines

class Level:

    _PlayerPosition = Vector(30, 350)
    _PlayerVelocity = Vector(0, 0)

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
        
        # Rectangle:
        # lines = []
        # lines.append(Line((10, 10), (self.width - 10, 10)))
        # lines.append(Line((self.width - 10, 10), (self.width - 10, self.height - 10)))
        # lines.append(Line((self.width - 10, self.height - 10), (10, self.height - 10)))
        # lines.append(Line((10, self.height - 10), (10, 10)))
        
        # set as the shape and render_lines for the ground
        self.ground.render_lines = lines
        self.ground.shape = lines
        game.Game().pause(False)
        self.ground.recalculate_intersections()
    
    def reset_player(self):
        self.player.position = Level._PlayerPosition
        self.player.velocity = Level._PlayerVelocity
        game.Game().pause(False)
        self.player.recalculate_intersections()

    def __init__(self, path, resources_path):
        """Take a file at path, and extract level details."""
        # TODO: Load this in as a file
        width, height = 640, 480
        self.boundary = Rect(size=(width, height))
        
        image = pygame.image.load(os.path.join(resources_path, "guy_transp.png"))
        # shape = Rect(image.get_rect()).shape
        shape = generate_circle(6, 50)
        self.player = player.Player(image = image, shape = shape, position=Level._PlayerPosition, velocity=Level._PlayerVelocity)
        self.width, self.height = width, height
        self.ground = Ground(shape = [], render_lines = [])
        self.regenerate_ground()
        
        physics.update_intersections(self.ground)