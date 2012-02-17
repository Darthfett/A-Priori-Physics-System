"""
The util module is intended to provide a large collection of utility objects for the game.

Globals:
    NAN:
        NAN is float("nan").
    INFINITY:
        INFINITY is float("inf").
    EPSILON:
        EPSILON is a very small number used to test whether two floats are 'relatively equal'.
        This is required because of the inaccuracy in representing floating point numbers.

Functions:
    SignOf: Get the sign of a number (for use in multiplication).
    FloatEqual: Determine whether two floats are equal (within EPSILON).
    ZeroDivide: When potentially dividing by zero, use this function in order to get
                the more mathematical answer.
                a/b , b ~= 0:
                    INFINITY if a > 0, -INFINITY if a < 0, NAN if a ~= 0
    Within(a, b, c): Determines whether b is between a and c (inclusive).
    Collinear(p, q, r): Determines whether p, q, and r all lie upon the same line.
    RayContainsPoint(r, dp, p): Returns p is on the ray from point r in direction dp.
    SegmentContainsPoint(a, b, c): Returns whether c is within the segment between a and b.
    
Classes:
    Vector: A 2D mathematical vector in the x, y plane.
    Point: A subclass of Vector, identical in everything but name (useful for clarifying intent).
    Line: A 2D mathematical line determined by 2 points.  Can also be used to represent a line segment.
    Ray: A 2D mathematical ray determined by a point and direction vector.
"""

import math

NAN = float("nan")
INFINITY = float("inf")
EPSILON = 1e-10

def SignOf(a):
    """Get the sign of a number (positive: 1, negative: -1).
    VERY small negative numbers are positive."""
    if a < -EPSILON:
        return -1
    else:
        return 1

def FloatEqual(a, b):
    """Returns if difference between a and b is below EPSILON."""
    return -EPSILON < a-b < EPSILON

def ZeroDivide(a, b):
    """Returns more mathematical values for a / b if b ~= 0."""
    if FloatEqual(b, 0):
        if FloatEqual(a, 0):
            return NAN
        if a >= EPSILON:
            return INFINITY
        return -INFINITY
    return a / b

def Within(a, b, c):
    """Return true iff b is between a and c (inclusive)."""
    return a <= b <= c or c <= b <= a or FloatEqual(a, b) or FloatEqual(b, c)

def Collinear(p, q, r):
    """Returns whether p, q, and r are collinear."""
    return FloatEqual((q - p).cross(r - p), 0)

def RayContainsPoint(r, dp, p):
    """Returns whether the ray from r to dp contains point p."""
    b = Collinear(r, dp, p)
    b = b and (p.x >= r.x - EPSILON if dp.x - r.x > 0 else p.x <= r.x + EPSILON)
    return b and (p.y >= r.y - EPSILON if dp.y - r.y > 0 else p.y <= r.y + EPSILON)

def SegmentContainsPoint(a, b, c):
    """Returns whether c is within the segment ab."""
    return Collinear(a, b, c) and (Within(a.x, c.x, b.x) if not FloatEqual(a.x, b.x) else
               Within(a.y, c.y, b.y))

class Vector:
    """A Vector is a 2 dimensional [x, y] pair.
    Supports access through [] operator, as well as x, y members.
    Also provides many typical operations between 2D vectors."""
    
    __slots__ = ['x', 'y']
    
    @property
    def length(self):
        """The mathematical length of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    @property
    def sqr_length(self):
        """The mathematical squared length of the vector."""
        return self.x * self.x + self.y * self.y
        
    def normalize(self):
        len = self.length
        self.x = self.x / len
        self.y = self.y / len
        return self
        
    def normalized(self):
        """Returns a vector in the same direction, of length 1."""
        len = self.length
        return Vector(self.x / len, self.y / len)
        
    def cross(self, other):
        """Length of the perpendicular vector on the z-axis. 
        Also equivalent to the area of the triangle formed by the two vectors."""
        return self.x * other[1] - self.y * other[0]
    
    def collinear(self, q, r):
        """Returns whether q, and r are collinear with the point."""
        return FloatEqual((q - self).cross(r - self), 0)
        
    def projected_onto(self, line):
        """Returns the closest point on the line."""
        s_to_p = Line(self, line.p)
        d = ((line.direction.x) * (s_to_p.direction.y) -
             (s_to_p.direction.x) * (line.direction.y)) / line.length
        return line.p + line.direction.normalized() * d
    
    def project_onto(self, line):
        """Converts this point into the closest point on the line."""
        self.x, self.y = self.projected_onto(line)
        
#Operators:
        
    def __add__(self, vec):
        return Vector(self.x + vec[0], self.y + vec[1])

    def __sub__(self, vec):
        return Vector(self.x - vec[0], self.y - vec[1])
        
    def __mul__(self, other):
        """__mul__ operator performs dot product with another subscriptable, or scalar product with
        a scalar."""
        try:
            # try dot product
            return self.x * other[0] + self.y * other[1]
        except AttributeError:
            # try scalar product
            return Vector(self.x * other, self.y * other)
        
    def __rmul__(self, other):
        """__rmul__ operator performs dot product with another subscriptable, or scalar product with
        a scalar."""
        try:
            # try dot product
            return self.x * other[0] + self.y * other[1]
        except AttributeError:
            # try scalar product
            return Vector(self.x * other, self.y * other)
        
    def __div__(self, scalar):
        """__div__ operator performs scalar division with a scalar."""
        return Vector(self.x / scalar, self.y / scalar)
        
    def __rdiv__(self, scalar):
        """__rdiv__ operator performs scalar division with a scalar."""
        return Vector(self.x / scalar, self.y / scalar)
        
    def __imul__(self, other):
        """__imul__ operator performs scalar product with a scalar."""
        self.x *= scalar
        self.y *= scalar
        return self
        
    def __idiv__(self, scalar):
        """__idiv__ operator performs scalar division with a scalar."""
        self.x /= scalar
        self.y /= scalar
        return self

    def __iadd__(self, vec):
        self.x += vec[0]
        self.y += vec[1]
        return self

    def __isub__(self, vec):
        self.x -= vec[0]
        self.y -= vec[1]
        return self
        
    def __neg__(self):
        return Vector(-self.x, -self.y)
    
    def __pos__(self):
        return Vector(self.x, self.y)
        
    def __abs__(self):
        return Vector(abs(self.x), abs(self.y))
    
    def __invert__(self):
        """2D 'perp' operation: (x, y) -> (-y, x) i.e. the perpendicular vector (counter-clockwise)."""
        return Vector(-self.y, self.x)

    def __len__(self):
        return 2

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __getitem__(self, item):
        """Supports getting coordinate by index, like an x, y tuple."""
        return [self.x, self.y][item]
        
    def __init__(self, x, y = None):
        """Initialize an x, y Vector.  Can take a tuple or individual arguments."""
        if y is None:
            self.x, self.y = x
        else:
            self.x, self.y = x, y

class Point(Vector):
    """A Point is just another name for a Vector."""
    
    __slots__ = ['x', 'y']

    def __init__(self, x, y = None):
        """Initialize an x, y Point.  Can take a tuple or individual arguments."""
        super().__init__(x, y)
        
class Line:
    """A Line is defined with two Points, p and q.  This class supports many typical operations
    performed on a line, and it is possible to use this class to represent a line segment.  This 
    can be done by using the 'in' operator to determine if a specific point is on the line and 
    between the two points that define the segment."""
    
    __slots__ = ['p', 'q']
    
    def collinear(self, r):
        """Returns whether a Point r is collinear with the line."""
        return FloatEqual((self.q - self.p).cross(r - self.p), 0)
        
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
        if FloatEqual(p.x, q.x):
            return p.x
        return self.p.y - (self.slope * self.p.x)
    
    @property
    def slope(self):
        """The slope (i.e. m in y = mx + b) of the line.  If the line is vertical,
        then this will be an infinite value."""
        return ZeroDivide(self.q.y - self.p.y, self.q.x - self.p.x)

    def __repr__(self):
        return "[" + str(self.p) + " to " + str(self.q) + "]"

    def __getitem__(self, item):
        """Returns a point in p, q."""
        return [self.p, self.q][item]
        
    def __contains__(self, c):
        """Returns whether this segment contains a point c"""
        if isinstance(c, Vector):
            return SegmentContainsPoint(self.p, self.q, c)
        elif isinstance(c, Line):
            return SegmentContainsPoint(self.p, self.q, c.p) and SegmentContainsPoint(self.p, self.q, c.q)
    
    def __init__(self, p, q = None):
        """Can be defined with a tuple of points, another Line, or two points."""
        if q is None:
            if isinstance(p, Line):
                # defining with a line
                self.p, self.q = p
            else:
                # defining with a tuple of points
                self.p, self.q = (p[0] if isinstance(p[0], Vector) else Point(p[0])), (p[1] if isinstance(p[1], Vector) else Point(p[1]))
        else:
            # defining with two tuples
            self.p, self.q = (p if isinstance(p, Vector) else Point(p)), (q if isinstance(q, Vector) else Point(q))

class Ray(Line):
    """A Ray is a point and a direction vector.  For most purposes, it can also be treated as a line."""
    
    __slots__ = ['p', 'direction']
    
    @property
    def q(self):
        """The 'second point' on the line.  This doesn't make sense for a ray, but is included for
        compatibility with its parent, Line"""
        return self.p + self.direction
    
    @property
    def slope(self):
        """The slope (i.e. m in y = mx + b) of the line.  If the line is vertical,
        then this will be an infinite value."""
        return ZeroDivide(self.direction.y, self.direction.x)

    def __getitem__(self, item):
        """Accessing a ray by index doesn't typically make sense.
        For compatibility with its parent, Line, this will return a value in p, q."""
        return [self.p, self.q][item]
    
    def __init__(self, p, d = None):
        """Can be defined with a tuple of a point and direction, another Line,
        or a point and a direction."""
        if d is None:
            if isinstance(p, Line):
                # defining with a line
                self.p, self.direction = p.p, p.direction
            else:
                # defining with a tuple of points
                self.p, self.direction = (p[0] if isinstance(p[0], Vector) else Point(p[0])), (p[1] if isinstance(p[1], Vector) else Vector(p[1]))
        else:
            # defining with two tuples
            self.p, self.direction = (p if isinstance(p, Vector) else Point(p)), (d if isinstance(d, Vector) else Vector(d))
        