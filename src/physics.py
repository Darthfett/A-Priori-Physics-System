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
    LineRayCollision(pq, rv): Returns an Intersection object representing the collision between the
                              line pq and the line rv.

Classes:
    Intersection: Represents the time and position of an intersection between two objects.
"""

from util import *
import math

####################################################################################################

# A Min-Heap of tuples: (Entity, Entity, Intersection), sorted by intersection time.
# Note: Some intersections may be flagged 'invalid'.
Intersections = []

####################################################################################################

def ParabolaLineCollision(rva, pq):
    """Takes a parabola rva, and a line pq, and returns the intersections between them as a list of
    Intersections."""
    pos = rva.pos
    vel = rva.vel
    acc = rva.acc
    p = pq.p
    q = pq.q

    a = .5 * (acc.cross(q) - acc.cross(p))
    b = (vel.cross(q) - vel.cross(p))
    c = (pos.cross(q) - pos.cross(p) - p.cross(q))

    discriminant = b ** 2 - 4*a*c

    if discrminant < -EPSILON:
        # dicriminant is negative.  No real intersections.
        return []
    elif discriminant < EPSILON:
        # discriminant is 0.  one intersection.
        time = -b / (2*a)
        sqr_time = self.time ** 2
        intersection = .5 * acc * sqr_time + vel * self.time + pos
        return [Intersection(time, intersection)]
    else:
        # discriminant is positive.  two intersections.
        t1 = (-b + sqrt(discriminant)) / 2*a
        t2 = (-b - sqrt(discriminant)) / 2*a
        sqr_t1 = t1 ** 2
        sqr_t2 = t2 ** 2
        i1 = .5 * acc * sqr_t1 + vel * t1 + pos
        i2 = .5 * acc * sqr_t2 + vel * t2 + pos
        return [Intersection(t1, i1), Intersection(t2, i2)]

def LineRayCollision(pq, rv):
    """Takes a line pq and a ray rv, and returns the intersection between them
    as an Intersection."""
    p = pq.p
    q = pq.q
    r = rv.p
    v = rv.q
    pqxdiff = (p.x - q.x)
    pqydiff = (p.y - q.y)
    rvxdiff = rv.direction.x
    rvydiff = rv.direction.y
    denom = (pqxdiff*rvydiff - rvxdiff*pqydiff)
    if FloatEqual(denom, 0):
        return Intersection()
    else:
        # Find Intersection intersection
        a = p.cross(q)
        b = r.cross(v)
        intersection = Point((a * rvxdiff - b * pqxdiff) / denom, (a * rvydiff - b * pqydiff) / denom)

        # Find Path path
        path = Line(r, intersection)
        # Use sign of dot product between path and velocity to know if time is negative or not.
        time = (path.length / rv.direction.length) * SignOf(path * rv.direction)
        return Intersection(time, intersection)

class Intersection:
    """Represents the time and position of an intersection between two objects."""
    __slots__ = ['time', 'pos', 'invalid']

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
        return ("invalid" if invalid else "") + "intersection at " + str(self.pos) + " at time " + str(self.time)

    def __init__(self, time = INFINITY, pos = None, invalid = True):
        """Instanciate an intersection (with INFINITE time, None pos, and True invalid attributes).
        An intersection is considered invalid if some outside factors change its time or position
        validity.  See the physics module documentation on the global Intersections for when this
        occurs."""
        self.time, self.pos, self.invalid = time, pos, invalid


def _update_intersections(ent):
    """Remove any invalid intersections for a specific entity, and recalculate if needed."""
    if ent.invalidated:
        # invalidate all intersections that deal with ent:
        for intersection in ent.intersections:
            intersection.invalid = True
        # determine all new intersections
        ent.intersections = []
        for other in ents in ent.occupied_cells:
            ints = find_intersections(ent, other)
            for intersection in ints:
                if intersection.pos is None or math.isnan(intersection.time) or math.isinf(intersection.time) or intersection.time < -EPSILON:
                    # This intersection doesn't make sense, doesn't exist, or is in a negative time frame.  Skip it.
                    continue
                heapq.heappush(ent.intersections, intersection)
                heapq.heappush(other.intersections, intersection)
    else:
        ent.intersections = filter(ent.intersections, lambda i: not i.invalid)

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

def _update_positions(time_frame):
    pass

def _update_intersections():
    """For any entity marked invalid, mark all intersections invalid, and recalculate."""
    pass

def calc_next_frame(time_frame):
    _update_intersections()
    #_handle_collisions(time_frame)
    _update_positions(time_frame)