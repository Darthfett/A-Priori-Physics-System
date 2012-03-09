import math
import util

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
        return util.FloatEqual((q - self).cross(r - self), 0)

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

    def __eq__(self, vec):
        return util.FloatEqual(self.x, vec.x) and util.FloatEqual(self.y, vec.y)

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
        except (TypeError, AttributeError):
            # try scalar product
            return Vector(self.x * other, self.y * other)

    def __rmul__(self, other):
        """__rmul__ operator performs dot product with another subscriptable, or scalar product with
        a scalar."""
        try:
            # try dot product
            return self.x * other[0] + self.y * other[1]
        except (TypeError, AttributeError):
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
        return "(%s, %s)"% (format(self.x, '.2f'), format(self.y, '.2f'))

    def __getitem__(self, item):
        """Supports getting coordinate by index, like an x, y tuple."""
        return [self.x, self.y][item]

    def __init__(self, x, y = None):
        """Initialize an x, y Vector.  Can take a tuple or individual arguments."""
        if y is None:
            self.x, self.y = x
        else:
            self.x, self.y = x, y
