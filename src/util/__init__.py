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
    EventListener: A metaclass which allows classes to watch properties for changes.
"""

import math

# These packages are all flattened to provide a nicer namespace.
from util.vector import *
from util.point import *
from util.line import *
from util.rect import *

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