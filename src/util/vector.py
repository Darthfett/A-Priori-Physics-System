import math
from collections import Iterable

import util
import debug

class Vector:
    """
    Represents a 2d value with magnitude and direction
    
    properties:
      x                 The length of the vector in the x-direction
      y                 The length of the vector in the y-direction
      length            The length of the vector
      sqr_length        The square of the length of the vector (faster
                        calculation than than vec.length ** 2)
    
    methods:
      reflected         Returns a vector reflected across the specified normal
      normalized        Returns a vector in the same direction with length 1
      cross             Returns the length of the cross-product between this 
                        vector and the specified vector

    """

    __slots__ = ['x', 'y']

    @property
    def length(self):
        """The length of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    @property
    def sqr_length(self):
        """The squared length of the vector."""
        return self.x * self.x + self.y * self.y
        
    def reflected(self, normal):
        """Get the vector that is the reflection of self across normal."""
        return self - (2 * normal * self) * normal

    def normalized(self):
        """Get a vector parallel to self with a length of 1."""
        len = self.length
        return Vector(self.x / len, self.y / len)

    def cross(self, other):
        """
        Get the length of the cross-product between self and other.
        
        Equivalent to double the area of the triangle formed by the two vectors.
        
        """
        
        return self.x * other[1] - self.y * other[0]

    def __setattr__(self, name, value):
        raise AttributeError("Cannot assign values to object {0} of type {1}".format(self, type(self)))
        
    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, vec):
        return self.x == vec.x and self.y == vec.y

    def __add__(self, vec):
        return Vector(self.x + vec[0], self.y + vec[1])

    def __sub__(self, vec):
        return Vector(self.x - vec[0], self.y - vec[1])

    def __mul__(self, other):
        """Perform dot/scalar product with other."""        
        if isinstance(other, Iterable):
            # dot product
            return self.x * other[0] + self.y * other[1]
        else:
            # scalar product
            return Vector(self.x * other, self.y * other)

    def __rmul__(self, other):
        """Perform dot/scalar product with other."""        
        if isinstance(other, Iterable):
            # dot product
            return self.x * other[0] + self.y * other[1]
        else:
            # scalar product
            return Vector(self.x * other, self.y * other)

    def __div__(self, scalar):
        """Perform scalar division with scalar."""
        return Vector(self.x / scalar, self.y / scalar)

    def __rdiv__(self, scalar):
        """Perform scalar division with scalar."""
        return Vector(self.x / scalar, self.y / scalar)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __pos__(self):
        return Vector(self.x, self.y)

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y))

    def __invert__(self):
        """
        Get the inverted/perpendicular vector, rotated counter-clockwise.
        
        >>> ~Vector(3, 4) == Vector(-4, 3)
        
        """
        
        return Vector(-self.y, self.x)

    def __len__(self):
        return 2

    def __repr__(self):
        if debug.Debug:
            return "Vector({0}, {1})".format(self.x, self.y)
        else:
            return "Vector({0}, {1})".format(format(self.x, '.2f'), format(self.y, '.2f'))

    def __getitem__(self, index):
        """Access the coordinates of this vector by index."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError
    
    def __iter__(self):
        yield self.x
        yield self.y

    def __bool__(self):
        return bool(self.x or self.y)
        
    def __init__(self, x, y=None):
        """Initialize a vector with an iterable of values, or two values."""
        if y is None:
            object.__setattr__(self, 'x', x[0])
            object.__setattr__(self, 'y', x[1])
        else:
            object.__setattr__(self, 'x', x)
            object.__setattr__(self, 'y', y)
