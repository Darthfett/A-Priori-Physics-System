from entity import Entity, Drawable, Movable, Collidable

class Player(Entity, Drawable, Movable, Collidable):
    def __init__(self, position = None, velocity = None, acceleration = None):
        pass
