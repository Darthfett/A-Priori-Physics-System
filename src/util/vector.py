import math
import collections

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
        return self - (2 * (normal * self)) * normal

    def normalized(self):
        """Get a vector parallel to self with a length of 1."""
        len_ = self.length
        return Vector(self.x / len_, self.y / len_)

    def cross(self, vec):
        """
        Get the length of the cross-product between self and other.

        Equivalent to double the area of the triangle formed by the two vectors.

        """
        if isinstance(vec, collections.Iterable):
            if len(vec) != 2:
                raise TypeError("cannot cross-product a {type} with a {type_vec} 'vec', where len(vec) != 2.".format(type=type(self).__name__, type_vec=type(vec).__name__))
            try:
                return self.x * vec[1] - self.y * vec[0]
            except TypeError:
                raise TypeError("cannot cross-product a {type} with a {type_vec} 'vec' with elements that do not support integer multiplication.".format(type=type(self).__name__, type_vec=type(vec).__name__))
        else:
            raise TypeError("cannot cross-product between {type} and {type_vec}".format(type=type(self).__name__, type_vec=type(vec).__name__))

    def __setattr__(self, name, value):
        """Vectors are immutable."""
        raise AttributeError('cannot set attribute {name}, {type} is immutable.'.format(name=name, type=type(self).__name__))

    def __hash__(self):
        """Hash the vector."""
        return hash((self.x, self.y))

    def __eq__(self, vec):
        """Determine if self equals vec."""
        if not isinstance(vec, collections.Iterable):
            return False
        else:
            return self.x == vec[0] and self.y == vec[1] and len(vec) == 2

    def __add__(self, vec):
        """Perform element-wise addition with vec."""
        if isinstance(vec, collections.Iterable) and len(vec) == 2:
            try:
                return Vector(self.x + vec[0], self.y + vec[1])
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented

    def __sub__(self, vec):
        """Perform element-wise subtraction with vec."""
        if isinstance(vec, collections.Iterable) and len(vec) == 2:
            try:
                return Vector(self.x - vec[0], self.y - vec[1])
            except TypeError:
                return NotImplemented
        else:
            return NotImplemented

    def __mul__(self, other):
        """Perform dot/scalar product with other."""
        if isinstance(other, collections.Iterable):
            if len(other) != 2:
                raise TypeError("cannot multiply a {type} with a {type_oth} 'other', where len(other) != 2.".format(type=type(self).__name__, type_oth=type(other).__name__))
            try:
                return self.x * other[0] + self.y * other[1]
            except TypeError:
                return NotImplemented
        else:
            try:
                return Vector(self.x * other, self.y * other)
            except TypeError:
                return NotImplemented

    def __truediv__(self, other):
        """Perform dot/scalar division with other."""
        if isinstance(other, collections.Iterable):
            if len(other) != 2:
                raise TypeError("cannot divide a {type} with a {type_oth} 'other', where len(other) != 2.".format(type=type(self).__name__, type_oth=type(other).__name__))
            try:
                return self.x / other[0] + self.y / other[1]
            except TypeError:
                return NotImplemented
        else:
            try:
                return Vector(self.x / other, self.y / other)
            except TypeError:
                return NotImplemented

        def __rsub__(self, vec):
            """Perform element-wise subtraction with vec."""
            if isinstance(other, collections.Iterable) and len(other) == 2:
                try:
                    return Vector(vec[0] - self.x, vec[1] - self.y)
                except TypeError:
                    return NotImplemented
            else:
                return NotImplemented

    def __rtruediv__(self, other):
        """Perform scalar division with scalar."""
        if isinstance(other, collections.Iterable):
            if len(other) != 2:
                raise TypeError("cannot divide a {type} with a {type_oth} 'other', where len(other) != 2.".format(type=type(self).__name__, type_oth=type(other).__name__))
            try:
                return other[0] / self.x + other[1] / self.y
            except TypeError:
                return NotImplemented
        else:
            try:
                return Vector(other / self.x, other / self.y)
            except TypeError:
                return NotImplemented

    __radd__ = __iadd__ = __add__
    __rmul__ = __imul__ = __mul__
    __isub__ = __sub__
    __itruediv__ = __truediv__

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

    def __str__(self):
        return "Vector({0}, {1})".format(format(self.x, '.2f'), format(self.y, '.2f'))

    def __repr__(self):
        return "Vector({0}, {1})".format(self.x, self.y)

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

    def __init__(self, x=None, y=None):
        """Initialize a vector with an iterable of values, or two values, or defaults to (0,0)."""
        if y is None:
            if x is None:
                object.__setattr__(self, 'x', 0)
                object.__setattr__(self, 'y', 0)
            else:
                object.__setattr__(self, 'x', x[0])
                object.__setattr__(self, 'y', x[1])
        else:
            object.__setattr__(self, 'x', x)
            object.__setattr__(self, 'y', y)