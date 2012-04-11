import util
from util.vector import Vector
from util.point import Point

class Line:
    """
    Represents a line between two points.

    properties:
      p                 The first point defining the line
      q                 The second point defining the line
      length            The length of the line
      direction         The vector direction of the line

    """

    __slots__ = ['p', 'q', 'color']

    @property
    def direction(self):
        """A Vector representing the direction of the line (from p to q)."""
        return self.q - self.p

    @property
    def length(self):
        """The length of the line segment, i.e. the distance between p and q."""
        return self.direction.length
        
    def __add__(self, other):
        """Get a new line by offsetting the line toward other."""
        return Line(self.p + other, self.q + other)
        
    def __sub__(self, other):
        """Get a new line by offsetting the line away from other."""
        return Line(self.p - other, self.q - other)

    def __repr__(self):
        return "Line({0}, {1})".format(self.p, self.q)

    def __getitem__(self, index):
        """Access the points of this line by index."""
        return [self.p, self.q][index]

    def __contains__(self, c):
        """Get whether a point c lies on the line."""
        if isinstance(c, Vector):
            return util.SegmentContainsPoint(self.p, self.q, c)
        elif isinstance(c, Line):
            return util.SegmentContainsPoint(self.p, self.q, c.p) and util.SegmentContainsPoint(self.p, self.q, c.q)

    def __init__(self, p, q = None):
        """Initialize a line with an iterable of points, or two points."""
        if q is None:
            # defining with an iterable of points
            object.__setattr__(self, 'p', p[0] if isinstance(p[0], Vector) else Point(p[0]))
            object.__setattr__(self, 'q', p[1] if isinstance(p[1], Vector) else Point(p[1]))
        else:
            # defining with two points
            object.__setattr__(self, 'p', p if isinstance(p, Vector) else Point(p))
            object.__setattr__(self, 'q', q if isinstance(q, Vector) else Point(q))

        object.__setattr__(self, 'color', (0, 0, 0))
