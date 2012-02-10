from util import *

class Collidable:
    def __init__(self):
        pass

class Drawable:
    def __init__(self):
        pass

class Movable:   
    def __init__(self, velocity = None, acceleration = None):
        self.velocity = (Vector(0, 0) if velocity == None else velocity)
        self.acceleration = (Vector(0, 0) if acceleration == None else acceleration)

class Entity:
    def __init__(self, position = None):
        self.position = (Point(0, 0) if position == None else position)
