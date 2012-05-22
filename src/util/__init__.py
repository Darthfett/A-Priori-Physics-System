"""
The util module provides a large collection of utility objects for the game.

globals:
  NAN                   NAN is float("nan") -- "Not A Number"
  INFINITY              INFINITY is float("inf").
  EPSILON               EPSILON is a very small number used to test whether
                        two numbers are 'relatively equal'.

functions:
  Position              Offset a point over a time period.
  FloatEqual            Determine whether two numbers are equal.
  ZeroDivide            Divide two numbers, and get INFINITY or NAN values
                        when dividing by zero.
  Within                Determine if a number if between two others.
  Collinear             Determine if three points lie on the same line.
  SegmentContainsPoint
                        Determine if a point lies in a line segment.

classes:
  Vector                A 2D mathematical vector in the x, y plane.
  Line                  A 2D mathematical line determined by 2 points.  Can also be used to represent a line segment.
  Rect                  A representation of a rectangle defined by size and bottom-left, shape, or a pygame rect.
  Event                 A simple event type which can be registered to

"""

import math

from debug import debug

# These packages are all flattened to provide a nicer namespace.
from util.vector import Vector
from util.line import Line
from util.shape import Shape
from util.rect import Rect

NAN = float("nan")
INFINITY = float("inf")
EPSILON = 1e-8



def zip_extend(*into_lists, from_lists):
    for into_list, from_list in zip(into_lists, from_lists):
        into_list.extend(from_list)


def merge_into(*args, into=None):
    """Merge iterables into into, maintaining into's sorted-ness."""
    if into is None:
        into = []
    for list_ in args:
        into.extend(sorted(list_))

    into.sort() # Take advantage of timsort working well with partially sorted lists
    return into

def Position(position, velocity, acceleration, delta_time):
    """Get a new position given velocity/acceleration and some time in ms."""
    return position + velocity * delta_time + acceleration * (.5 * delta_time ** 2)

def FloatEqual(a, b):
    """Returns if difference between a and b is below EPSILON."""
    #return -EPSILON < a-b < EPSILON



    largest = max(abs(a), abs(b))
    diff = EPSILON * largest
    if largest < EPSILON:
        return -EPSILON < a-b < EPSILON
    return -diff < a-b < diff

def ZeroDivide(a, b):
    """Returns more mathematical values for a / b if b ~= 0."""
    if b == 0:
        if a == 0:
            return NAN
        return math.copysign(INFINITY, a)
    return a / b

def Within(a, b, c):
    """Return true iff b is between a and c (inclusive)."""
    return a <= b <= c or c <= b <= a or FloatEqual(a, b) or FloatEqual(b, c)

def Collinear(p, q, r):
    """Returns whether p, q, and r are collinear."""
    return FloatEqual((q - p).cross(r - p), 0)

def SegmentContainsPoint(a, b, c):
    """Returns whether c is within the segment ab."""
    return Collinear(a, b, c) and (Within(a.x, c.x, b.x) if not FloatEqual(a.x, b.x) else
               Within(a.y, c.y, b.y))

class EquationIdentity(ValueError):
    """An EquationIdentity occurs when 'find_roots' is called with the identity 0 = 0."""
    pass

class InequalityError(ValueError):
    """An InequalityError occurs when 'find_roots' is called with an inequality, e.g. 1 = 0."""
    pass

def find_roots(a, b, c):
    """Find the roots to a quadratic equation, i.e. find x | ax^2 + bx + c = 0."""

    if a == 0:
        if b == 0:
            if c == 0:

                # 0x^2 + 0x + 0 = 0
                #             0 = 0
                raise EquationIdentity("Cannot find roots for equation 0 = 0")
                return []
            else:

                # 0x^2 + 0x + c = 0, c != 0
                #             c = 0, c != 0
                # Undefined root
                raise InequalityError("Cannot find roots for equation {0} = 0.".format(c))
                return []

        # 0x^2 + bx + c = 0
        #        bx     = -c
        #         x     = -c / b
        return [-c / b]

    # discriminant reveals information about how many solutions there are
    tmp = not (c == 0)
    if tmp:
        discriminant = (b * b) - 4 * a * c
    else:
        if b == 0:
            return [0]
        discriminant = abs(b)

    if discriminant < 0:
        # No real solution
        return []
    if tmp:
        if discriminant == 0:
            # One real solution
            return [-b / (2 * a)]
        else:
            # Two real solutions
            x1 = (-b - math.copysign(math.sqrt(discriminant), b)) / (2 * a)
            x2 = c / (a * x1)
    else:
        if discriminant == 0:
            # One real solution
            return [-b / (2 * a)]
        else:
            # Two real solutions
            x1 = -b / a
            x2 = 0
    return [x1, x2]

def generate_circle(n, radius):
    """Generates a circle with n sides, with radius radius."""
    center = Vector(radius, radius)
    vertices = []
    for i in range(n):
        vertex = center + Vector(radius * math.sin((i / n) * 2 * math.pi), radius * math.cos((i / n) * 2 * math.pi))
        vertices.append(vertex)
    return vertices