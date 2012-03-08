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
        print("%s intersected with %s" % (self.e1, self.e2))
        self.e1.intersections = []
        self.e2.intersections = []
        game.Game().pause()
        #update_intersections(self.e1)
        #update_intersections(self.e2)

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

    def __init__(self, time = INFINITY, pos = None, invalid = True):
        """Instanciate an intersection (with INFINITE time, None pos, and True invalid attributes).
        An intersection is considered invalid if some outside factors change its time or position
        validity.  See the physics module documentation on the global Intersections for when this
        occurs."""
        self.time, self.pos, self.invalid, self.e1, self.e2 = time, pos, invalid, None, None

def RayLineCollision(point_pos, point_vel, pq):
    pos = point_pos
    vel = point_vel
    p = pq.p
    q = pq.q
    
    denom = vel.cross(p) - vel.cross(q)
    
    if FloatEqual(denom, 0):
        return None
        
    numerator = pos.cross(q) - pos.cross(p) + q.cross(p)
    
    time = numerator / denom
    if time < 0:
        return None
    return Intersection(time, pos + time * vel, False)

def ParabolaLineCollision(point_pos, point_vel, point_acc, pq):
    """Takes a parabola point_pos, point_vel, point_acc, and a line pq, and returns the intersections between them as a list of
    Intersections."""
    if point_acc.x == point_acc.y == 0:
        # Not a parabola
        intersection = RayLineCollision(point_pos, point_vel, pq)
        if intersection is not None:
            return [intersection]
        else:
            return []
    pos = point_pos
    vel = point_vel
    acc = point_acc
    p = pq.p
    q = pq.q

    a = .5 * (acc.cross(q) - acc.cross(p))
    b = (vel.cross(q) - vel.cross(p))
    c = (pos.cross(q) - pos.cross(p) - p.cross(q))

    discriminant = b ** 2 - 4*a*c

    if discriminant < -EPSILON:
        # dicriminant is negative.  No real intersections.
        return []
    elif discriminant < EPSILON:
        # discriminant is 0.  one intersection.
        if FloatEqual(a, 0):
            # No intersection
            return []
        time = (-b / (2*a)) / 1000
        sqr_time = time ** 2
        intersection = .5 * acc * sqr_time + vel * time + pos
        if intersection in pq:
            return [Intersection(time, intersection, False)]
        else:
            return []
    else:
        # discriminant is positive.  two intersections.
        t1 = ((-b + math.sqrt(discriminant)) / 2*a) / 1000
        t2 = ((-b - math.sqrt(discriminant)) / 2*a) / 1000
        sqr_t1 = t1 ** 2
        sqr_t2 = t2 ** 2
        i1 = .5 * acc * sqr_t1 + vel * t1 + pos
        i2 = .5 * acc * sqr_t2 + vel * t2 + pos
        if i1 in pq:
            if i2 in pq:
                return [Intersection(t1, i1, False), Intersection(t2, i2, False)]
            else:
                return [Intersection(t1, i1, False)]
        else:
            if i2 in pq:
                return [Intersection(t2, i2, False)]
            else:
                return []
        
def find_intersections(line1, v1, a1, line2, v2, a2):
    """Returns an unsorted list of intersections between line1 and line2."""
    vel_line1_rel_line2 = v1 - v2
    acc_line1_rel_line2 = a1 - a2
    vel_line2_rel_line1 = v2 - v1
    acc_line2_rel_line1 = a2 - a1
    i1 = ParabolaLineCollision(line1.p, vel_line1_rel_line2, acc_line1_rel_line2, line2)
    i2 = ParabolaLineCollision(line1.q, vel_line1_rel_line2, acc_line1_rel_line2, line2)
    i3 = ParabolaLineCollision(line2.p, vel_line2_rel_line1, acc_line1_rel_line2, line1)
    i4 = ParabolaLineCollision(line2.q, vel_line2_rel_line1, acc_line1_rel_line2, line1)
    intersections = i1 + i2 + i3 + i4
    intersections = list(filter(lambda i: i.time >= 0, intersections))
    if len(intersections):
        line1.color = (255, 0, 0)
        line2.color = (255, 0, 0)
    return intersections
    
def update_intersections(ent):
    for collidable in entity.Collidables:
        if ent is collidable:
            continue
        intersections = []
        pairs = [(line1, line2) for line1 in ent.shape for line2 in collidable.shape]
        for line1, line2 in pairs:
            for intersection in find_intersections(line1, ent.velocity, ent.acceleration, line2, collidable.velocity, collidable.acceleration):
                intersection.e1 = ent
                intersection.e2 = collidable
                heappush(intersections, intersection)
                print(intersection)
                
        intersections.sort()
        ent.intersections = list(merge(ent.intersections, intersections))
        collidable.intersections = list(merge(collidable.intersections, intersections))
        game.Game.GameEvents = list(merge(game.Game.GameEvents, intersections))

def _handle_collisions(time_frame):
    """Update entities' positions and handle any collisions for time_frame ms."""
    # Update all intersections
    for ent in Entities:
        if ent.invalidated:
            _update_intersections(ent)

    # Get all entities with valid intersections
    # valid = filter(Entities, lambda ent: len(ent.intersections) > 0)

    # Sort entities by first intersection time
    # valid.sort(key = lambda ent: ent.intersections[0].time)

    I = Intersections[0]
    while I.intersection.time <= time_frame:
        intersection, ent, other = I
        time, position, invalid = intersection
        if time > time_frame:
            break

        if intersection.invalid:
            Intersections.pop(0)
            intersection = Intersections[0]
            continue

        # Handle intersection
        if -EPSILON <= intersection.time < EPSILON:
            # Handle collisions at time 0
            if FloatEqual(ent.velocity, other.velocity) and FloatEqual(ent.acceleration, other.acceleration):
                # Not going to collide, ignore this collision
                Intersections.pop(0)
                intersection = Intersections[0]
                continue
            elif FloatEqual(ent.velocity, other.velocity):
                # Equal acceleration
                pass
            elif FloatEqual(ent.acceleration, other.acceleration):
                # Equal acceleration
                pass
            else:
                # Unequal acceleration and velocity
                pass
        # TODO: Handle collisions at time > 0

def _update_intersections():
    """For any entity marked invalid, mark all intersections invalid, and recalculate."""
    pass