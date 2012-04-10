import util
from util.vector import Vector
from util.point import Point

class Line:
    """A Line is defined with two Points, p and q.  This class supports many typical operations
    performed on a line, and it is possible to use this class to represent a line segment.  This
    can be done by using the 'in' operator to determine if a specific point is on the line and
    between the two points that define the segment."""

    #__slots__ = ['p', 'q', 'color']

    def collinear(self, r):
        """Returns whether a Point r is collinear with the line."""
        return util.FloatEqual((self.q - self.p).cross(r - self.p), 0)

    @property
    def direction(self):
        """A Vector representing the direction of the line (from p to q)."""
        return self.q - self.p

    @property
    def length(self):
        """The length of the line segment, i.e. the distance between p and q."""
        return self.direction.length

    @property
    def y_intercept(self):
        """The y-intercept (i.e. b in y = mx + b) of the line.  If the line is vertical,
        then this will be the x-value of both p and q."""
        if util.FloatEqual(p.x, q.x):
            return p.x
        return self.p.y - (self.slope * self.p.x)
    
    # def __getstate__(self):
        # return {name: getattr(self, name) for name in self.__slots__}

    # def __setstate__(self, state):
        # for name, value in state.items():
            # object.__setattr__(self, name, value)

    # def __setattr__(self, name, value):
        # raise AttributeError("Cannot assign values to object {0} of type {1}".format(self, type(self)))

    @property
    def slope(self):
        """The slope (i.e. m in y = mx + b) of the line.  If the line is vertical,
        then this will be an infinite value."""
        return util.ZeroDivide(self.q.y - self.p.y, self.q.x - self.p.x)
        
    def __hash__(self):
        return hash((self.p, self.q))

    #def __setattr__(self, name, value):
    #    raise AttributeError("Cannot assign values to object {0} of type {1}".format(self, type(self)))
        
    def __add__(self, other):
        return util.line.Line(self.p + other, self.q + other)
        
    def __sub__(self, other):
        return Line(self.p - other, self.q - other)

    def __repr__(self):
        return "L[{0} to {1}]".format(self.p, self.q)

    def __getitem__(self, item):
        """Returns a point in p, q."""
        return [self.p, self.q][item]

    def __contains__(self, c):
        """Returns whether this segment contains a point c"""
        if isinstance(c, Vector):
            return util.SegmentContainsPoint(self.p, self.q, c)
        elif isinstance(c, Line):
            return util.SegmentContainsPoint(self.p, self.q, c.p) and util.SegmentContainsPoint(self.p, self.q, c.q)

    def __init__(self, p, q = None):
        """Can be defined with a tuple of points, another Line, or two points."""
        if q is None:
            if isinstance(p, Line):
                # defining with a line
                object.__setattr__(self, 'p', p[0])
                object.__setattr__(self, 'q', p[1])
            else:
                # defining with a tuple of points
                object.__setattr__(self, 'p', p[0] if isinstance(p[0], Vector) else Point(p[0]))
                object.__setattr__(self, 'q', p[1] if isinstance(p[1], Vector) else Point(p[1]))
        else:
            # defining with two tuples
            object.__setattr__(self, 'p', p if isinstance(p, Vector) else Point(p))
            object.__setattr__(self, 'q', q if isinstance(q, Vector) else Point(q))
        object.__setattr__(self, 'color', (0, 0, 0))
