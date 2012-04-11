"""
The util module provides a large collection of utility objects for the game.

Globals:
  NAN                   NAN is float("nan") -- "Not A Number"
  INFINITY              INFINITY is float("inf").
  EPSILON               EPSILON is a very small number used to test whether
                        two numbers are 'relatively equal'.

Functions:
  Position              Offset a point over a time period.
  FloatEqual            Determine whether two numbers are equal.
  ZeroDivide            Divide two numbers, and get INFINITY or NAN values
                        when dividing by zero.
  Within                Determine if a number if between two others.
  Collinear             Determine if three points lie on the same line.
  SegmentContainsPoint
                        Determine if a point lies in a line segment.

Classes:
  Vector                A 2D mathematical vector in the x, y plane.
  Line                  A 2D mathematical line determined by 2 points.  Can also be used to represent a line segment.
  Rect                  A representation of a rectangle defined by size and bottom-left, shape, or a pygame rect.
  Event                 A simple event type which can be registered to

"""

import math

# These packages are all flattened to provide a nicer namespace.
from util.vector import Vector
from util.line import Line
from util.shape import Shape
from util.rect import Rect

NAN = float("nan")
INFINITY = float("inf")
EPSILON = 1e-8

def Position(position, velocity, acceleration, delta_time):
    """Get a new position given velocity/acceleration and some time in ms."""
    return position + velocity * delta_time + .5 * acceleration * (delta_time ** 2)

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

def SegmentContainsPoint(a, b, c):
    """Returns whether c is within the segment ab."""
    return Collinear(a, b, c) and (Within(a.x, c.x, b.x) if not FloatEqual(a.x, b.x) else
               Within(a.y, c.y, b.y))

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
                raise ValueError("Cannot find roots for equation 0 = 0")
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
        discriminant = b 
    
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

class Event:
    """An event can have any number of handlers, which are called when the event is fired,
    along with any arguments passed.
     * Add to an event's handlers with the += operator or register method.
     * Remove a handler with the -= operator or removeHandler method.
     * Fire an event by calling it, or calling the fire method.
     * Clear all handlers with the clearObjectHandlers method."""
    
    def __iadd__(self, handler):
        """Add an event handler.  The handler must be callable."""
        if not callable(handler):
            raise ValueError("Cannot register non-callable %r object %r" % (type(handler).__name__, handler))
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self.__handlers:
            handler(*args, **kwargs)
        
    register = __iadd__
    removeHandler = __isub__
    fire = __call__

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

    def __init__(self):
        self.__handlers = []
    
class TimeComparable:
    """All TimeComparable objects can be compared according to their 'time' property."""
    def __lt__(self, other):
        return self.time < other.time

    def __le__(self, other):
        return self.time <= other.time

    def __eq__(self, other):
        return self.time == other.time

    def __ne__(self, other):
        return self.time != other.time

    def __gt__(self, other):
        return self.time > other.time

    def __ge__(self, other):
        return self.time >= other.time