from util import *
from entity import *

class Ground(LineRenderable, Collidable, Shape):
    """The Ground class is the game's lower-y boundaries."""
    def __init__(self, **kwargs):
        """Instanciate the Ground class.  Required keyword arguments:
               render_lines - A list of line segments
               shape - A list of line segments"""
        super().__init__(**kwargs)
