from util.vector import Vector

class Point(Vector):
    """A Point is just another name for a Vector."""

    #__slots__ = ['x', 'y']

    def __init__(self, x, y=None):
        """Initialize an x, y Point.  Can take a tuple or individual arguments."""
        super().__init__(x, y)