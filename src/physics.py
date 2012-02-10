from util import *
import math

class Intersection:
    __slots__ = ['time', 'pos']

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
        return "intersection at " + str(self.pos) + " at time " + str(self.time)
        
    def __init__(self, time = INFINITY, pos = None):
        self.time, self.pos = time, pos
        
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
