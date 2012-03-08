"""
The physics module contains any functions needed for handling intersections/collisions between
objects.  It also handles the resolution of any collisions.

Globals:
    Intersections (MinHeap List of all collisions between objects, sorted by intersection time):
        This List contains collisions between pairs of objects, sorted by the occurence time.
        The collisions are added whenever any line of any object enters into a new cell.
        They are removed only when any of the following occur:
            - An object collides with another object (invalidated/handled).
            - An object enters into a -new- cell, and a collision between any pair of lines
              between the two objects already exists.
                - In this scenario, the existing intersection's collision time between should be
                  within EPSILON of a new calculation, and thus a collision detection between
                  the pair of lines is not needed.
        All will have a valid intersection time and position, but may be marked 'invalid' if:
            - Either of the two objects has been directly moved
            - Either of the two objects has had its velocity directly changed
            - Either of the two objects has had its acceleration directly changed
            - Either of the two objects is removed/deleted

Functions:
    ParabolaLineCollision(rva, pq): Returns a List of Intersection objects representing the
                                    the collisions between the parabola rva and line pq.

Classes:
    Intersection: Represents the time and position of an intersection between two objects.
"""

from util import *
import math
from heapq import merge, heappush
from itertools import chain
import functools
import entity
import game

####################################################################################################

# A Min-Heap of tuples: (Entity, Entity, Intersection), sorted by intersection time.
# Note: Some intersections may be flagged 'invalid'.
Intersections = []

####################################################################################################

class Intersection:
    """Represents the time and position of an intersection between two objects."""
    __slots__ = ['time', 'pos', 'invalid', 'e1', 'e2']
    
    def handle(self):
        if self.invalid:
            return
        if not hasattr(self, "e1") or not hasattr(self, "e2"):
            raise Exception("Intersection %s occurs between nonexistent things" % self)
        for i in chain(self.e1.intersections, self.e2.intersections):
            i.invalid = True
        self.e1.intersections = []
        self.e2.intersections = []
        
        game.Game().pause()

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

    def __repr__(self):
        return "Intersection(%s, %s, %s)" % (self.time, self.pos, self.invalid)

    def __init__(self, time = INFINITY, pos = None, invalid = False):
        """Instanciate an intersection (with INFINITE 'time', None 'pos', and False 'invalid' default attributes).
        An intersection is considered invalid if some outside factors change its time or position
        validity.  See the physics module documentation on the global Intersections for when this
        occurs."""
        self.time, self.pos, self.invalid, self.e1, self.e2 = time, pos, invalid, None, None

def RayLineCollision(pos, vel, p, q):
    pos = point_pos
    vel = point_vel
    
    denom = vel.cross(p) - vel.cross(q)
    
    if FloatEqual(denom, 0):
        return None
        
    numerator = pos.cross(q) - pos.cross(p) + q.cross(p)
    
    time = numerator / denom
    if time < 0:
        return None
    return Intersection(time, pos + time * vel, False)
    
def find_roots(a, b, c):
    """Find the roots to a quadratic equation."""
    
    if FloatEqual(a, 0):
        if FloatEqual(b, 0):
            if FloatEqual(c, 0):
                raise Exception("Cannot find roots for equation identity.")
            else:
                raise Exception("Cannot find roots for a non-equation.")
        return [-c / b]
    
    # discriminant reveals information about how many solutions there are
    discriminant = b ** 2 - 4*a*c
    
    if discriminant < 0:
        # No real solution
        return []
    if discriminant < EPSILON:
        # One real solution
        return [-b / (2 * a)]
    # Two real solutions
    return [(-b + math.sqrt(discriminant)) / (2*a), (-b - math.sqrt(discriminant)) / (2*a)]

def ParabolaLineCollision(pos, vel, acc, p, q):
    """Takes a parabola pos, vel, acc, and a line p q, and returns the intersections between them as a list of
    Intersections.
    Intersections are not necessarily in the line segment pq."""

    # time of intersection is defined by the equation
    # a*time^2 + b*time + c = 0
    a = .5 * (acc.cross(q) - acc.cross(p))
    b = (vel.cross(q) - vel.cross(p))
    c = (pos.cross(q) - pos.cross(p) - p.cross(q))
    
    roots = find_roots(a, b, c)
    if len(roots) == 0:
        return []
    if len(roots) == 1:
        # Intersection time in seconds
        time = roots[0]
        
        # Intersection position relative to p
        relative_position = (.5 * acc * (time ** 2) + vel * time + pos) - p
        return [Intersection(time * 1000, relative_position)]
        
    # Intersection times in seconds
    seconds = [time for time in roots]
    # Intersection positions relative to p
    relative_positions = [(.5 * acc * (sec ** 2) + vel * sec + pos) - p for sec in seconds]
        
    return [Intersection(time * 1000, position) for time, position in zip(roots, relative_positions)]


        
def find_intersections(line1, v1, a1, line2, v2, a2):
    """Returns an unsorted list of intersections between line1 and line2."""
    
    # Find collisions with relative velocity/acceleration
    vel_line1_rel_line2 = v1 - v2
    acc_line1_rel_line2 = a1 - a2
    vel_line2_rel_line1 = v2 - v1
    acc_line2_rel_line1 = a2 - a1
    i1 = ParabolaLineCollision(line1.p, vel_line1_rel_line2, acc_line1_rel_line2, *line2)
    i2 = ParabolaLineCollision(line1.q, vel_line1_rel_line2, acc_line1_rel_line2, *line2)
    i3 = ParabolaLineCollision(line2.p, vel_line2_rel_line1, acc_line1_rel_line2, *line1)
    i4 = ParabolaLineCollision(line2.q, vel_line2_rel_line1, acc_line1_rel_line2, *line1)
    
    # Filter function to remove any collisions not in the segment, and with negative time.
    def intersection_filter(line, intersection):
        if intersection.time < 0:
            return False
        if not SegmentContainsPoint(line.p, line.q, line.p + intersection.pos):
            return False
        return True
    
    # filter with filter function for the specified line
    valid_int_1 = list(filter(functools.partial(intersection_filter, line2), chain(i1, i2)))
    valid_int_2 = list(filter(functools.partial(intersection_filter, line1), chain(i3, i4)))

    # combine into one list
    intersections = valid_int_1 + valid_int_2
    
    # intersections were calculated from current time, change to absolute time
    for i in intersections:
        i.time += game.Game.GameTime
    
    return intersections
    
def update_intersections(ent):
    """Calculate all intersections between the given entity, and add them to the event list."""
    for collidable in entity.Collidables:
        if ent is collidable:
            # don't collide with self
            continue
        intersections = []
        # Get all pairs of line segments between the two entities' shapes
        pairs = [(line1 + ent.position, line2 + collidable.position) for line1, line2 in zip(ent.shape, collidable.shape)]
        for line1, line2 in pairs:
            # Find all the intersections and add to the intersections list
            for intersection in find_intersections(line1, ent.velocity, ent.acceleration, line2, collidable.velocity, collidable.acceleration):
                intersection.e1 = ent
                intersection.e2 = collidable
                heappush(intersections, intersection)
                
        # Sort all the intersections, and add to gave event list
        intersections.sort()
        game.Game.GameEvents = list(merge(game.Game.GameEvents, intersections))
        
        # Entities keep track of their intersections so they can mark them invalid.
        ent.intersections = list(merge(ent.intersections, intersections))
        collidable.intersections = list(merge(collidable.intersections, intersections))
