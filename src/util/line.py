import collections

import util
from util.vector import Vector

class Line:
    """
    Represents a line between two points.

    properties:
      p                 The first point defining the line
      q                 The second point defining the line
      length            The length of the line
      direction         The vector direction of the line
      normal            The normal of the line

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

    @property
    def normal(self):
        """The normal of the line."""
        return ~self.direction.normalized()

    def __hash__(self):
        return hash((self.p, self.q))

    def __eq__(self, other):
        if not isinstance(other, collections.Iterable):
            return False
        else:
            return self.p == other[0] and self.q == other[1] and len(other) == 2

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
        if index == 0:
            return self.p
        elif index == 1:
            return self.q
        raise IndexError

    def __len__(self):
        return 2

    def __iter__(self):
        yield self.p
        yield self.q

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
            object.__setattr__(self, 'p', p[0] if isinstance(p[0], Vector) else Vector(p[0]))
            object.__setattr__(self, 'q', p[1] if isinstance(p[1], Vector) else Vector(p[1]))
        else:
            # defining with two points
            object.__setattr__(self, 'p', p if isinstance(p, Vector) else Vector(p))
            object.__setattr__(self, 'q', q if isinstance(q, Vector) else Vector(q))

        object.__setattr__(self, 'color', (0, 0, 0))
