from util.vector import Vector

class Point(Vector):
    __doc__ = Vector.__doc__

    __slots__ = ['x', 'y']

    def __init__(self, x, y=None):
        """Initialize a point with an iterable of values, or two values."""
        super().__init__(x, y)