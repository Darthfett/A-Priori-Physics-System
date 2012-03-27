import entity

class Ground(entity.LineRenderable, entity.Collidable, entity.Shaped):
    """The Ground class is the game's lower-y boundaries."""
    def __init__(self, **kwargs):
        """Instanciate the Ground class.  Required keyword arguments:
               render_shape - A util.Shape to draw
               shape - A util.Shape for collision"""
        super().__init__(**kwargs)
