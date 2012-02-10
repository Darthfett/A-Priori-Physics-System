import math

NAN = float("nan")
INFINITY = float("inf")
EPSILON = 1e-10

def SignOf(a):
    if a < -EPSILON:
        return -1
    else
        return 1

def FloatEqual(a, b):
    """Returns if difference between a and b is below EPSILON"""
    return -EPSILON < a-b < EPSILON

def ZeroDivide(a, b):
    """Returns more mathematical values for a / b if b == 0"""
    try:
        return a / b
    except ZeroDivisionError:
        if a == 0:
            return NAN
        if a > 0:
            return INFINITY
        return -INFINITY

def Within(p, q, r):
    "Return true iff q is between p and r (inclusive)."
    return p <= q <= r or r <= q <= p

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
    Supports access through [] operator, as well as x, y members."""
    
    __slots__ = ['x', 'y']
    
    @property
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    @property
    def sqr_length(self):
        """Gets the squared length."""
        return self.x * self.x + self.y * self.y
        
    def normalize(self):
        len = self.length
        self.x = self.x / len
        self.y = self.y / len
        return self
        
    def normalized(self):
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
        """Returns the closest point on the line"""
        s_to_p = Line(self, line.p)
        d = ((line.direction.x) * (s_to_p.direction.y) -
             (s_to_p.direction.x) * (line.direction.y)) / line.length
        return line.p + line.direction.normalized() * d
    
    def project_onto(self, line):
        self.x, self.y = self.projected_onto(line)
        
#Operators:
        
    def __add__(self, vec):
        return Vector(self.x + vec[0], self.y + vec[1])

    def __sub__(self, vec):
        return Vector(self.x - vec[0], self.y - vec[1])
        
    def __mul__(self, other):
        try:
            # try dot product
            return self.x * other[0] + self.y * other[1]
        except AttributeError:
            # try scalar product
            return Vector(self.x * other, self.y * other)
        
    def __rmul__(self, other):
        try:
            # try dot product
            return self.x * other[0] + self.y * other[1]
        except AttributeError:
            # try scalar product
            return Vector(self.x * other, self.y * other)
        
    def __div__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)
        
    def __rdiv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)
        
    def __imul__(self, other):
        self.x *= scalar
        self.y *= scalar
        return self
        
    def __idiv__(self, scalar):
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
        """ 2D 'perp' operation """
        return Vector(-self.y, self.x)

    def __len__(self):
        return 2

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __getitem__(self, item):
        """ Supports getting coordinate by index """
        return [self.x, self.y][item]
        
    def __init__(self, x, y = None):
        if y is None:
            self.x, self.y = x
        else:
            self.x, self.y = x, y

class Point(Vector):
    """A Point is just another name for a Vector."""
    
    __slots__ = ['x', 'y']

    def __init__(self, x, y = None):
        super().__init__(x, y)
        
class Line:
    """A Line is defined with two Points."""
    
    __slots__ = ['p', 'q']
    
    def collinear(self, r):
        """Returns whether r is collinear with the line."""
        return FloatEqual((self.q - self.p).cross(r - self.p), 0)
        
    @property
    def direction(self):
        return self.q - self.p
    
    @property
    def length(self):
        return (self.q - self.p).length
        
    @property
    def y_intercept(self):
        return self.p.y - (self.slope * self.p.x)
    
    @property
    def slope(self):
        return ZeroDivide(self.q.y - self.p.y, self.q.x - self.p.x)

    def __repr__(self):
        return "[" + str(self.p) + " to " + str(self.q) + "]"

    def __getitem__(self, item):
        return [self.p, self.q][item]
        
    def __contains__(self, c):
        """Returns whether this segment contains a point c"""
        if isinstance(c, Vector):
            return SegmentContainsPoint(self.p, self.q, c)
        elif isinstance(c, Line):
            return SegmentContainsPoint(self.p, self.q, c.p) and SegmentContainsPoint(self.p, self.q, c.q)
    
    def __init__(self, p, q = None):
        """All Lines (and subclasses) are guaranteed two points: p and q."""
        if q is None:
            if isinstance(p, Line):
                # defining with a line
                self.p, self.q = p
            else:
                # defining with a tuple of points
                self.p, self.q = (p[0] if isinstance(p[0], Vector) else Point(p[0])), (p[1] if isinstance(p[1], Vector) else Point(p[1]))
        else:
            if isinstance(p, Vector) and isinstance(q, Vector):
                # defining with two points
                self.p, self.q = p, q
            else:
                # defining with two tuples
                self.p, self.q = (p if isinstance(p, Vector) else Point(p)), (q if isinstance(q, Vector) else Point(q))

class Ray(Line):
    """A Ray is a point and a direction vector."""
    
    __slots__ = ['p', 'direction']
    
    @property
    def q(self):
        return self.p + self.direction
    
    @property
    def slope(self):
        return ZeroDivide(self.direction.y, self.direction.x)

    def __getitem__(self, item):
        return [self.p, self.q][item]
    
    def __init__(self, p, d = None):
        if d is None:
            if isinstance(p, Line):
                # defining with a line
                self.p, self.direction = p.p, p.direction
            else:
                # defining with a tuple of points
                self.p, self.direction = (p[0] if isinstance(p[0], Vector) else Point(p[0])), (p[1] if isinstance(p[1], Vector) else Vector(p[1]))
        else:
            if isinstance(p, Vector) and isinstance(d, Vector):
                # defining with two points
                self.p, self.direction = p, d
            else:
                # defining with two tuples
                self.p, self.direction = (p if isinstance(p, Vector) else Point(p)), (d if isinstance(d, Vector) else Vector(d))
        
class Parabola:

    def __getitem__(self, item):
        return [self.pos, self.vel, self.acc][item]

    

    def __init__(self, pos, vel = None, acc = None):
        if vel is None and acc is None:
            self.pos, self.vel, self.acc = *pos
        if vel is None or acc is None:
            self.pos = pos
            self.vel, self.acc = (vel if acc is None else acc)
        else:
            self.pos, self.vel, self.acc = pos, vel, acc