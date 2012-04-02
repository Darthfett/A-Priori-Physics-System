"""
The physics module contains any functions needed for handling intersections/collisions between
objects.  It also handles the resolution of any collisions.

Globals:
    Intersections (List of all collisions between objects, sorted by intersection time):
        This List contains collisions between pairs of objects, sorted by the occurence time.
        Collisions are (should be) added to this list whenever:
         * A collidable object is created
         * An object's position/velocity/acceleration changes (such as via collision or player controls)
        They are (should be) invalidated only when any of the following occur:
         * An object's position/velocity/acceleration changes (such as via collision or player controls)
         * An object is removed
        They are (should be) removed only when:
         * The game logic encounters a collision marked as invalid
         * The game finishes drawing a frame
            - In this scenario the game will filter this list of any invalid collisions.
        All Intersections will have a valid intersection time and position, but may be marked 'invalid'.

Functions:
    ParabolaLineCollision(pos, vel, acc, p, q):
        Returns a List of Intersection objects representing the collisions between a parabola and a line.
    find_roots(a, b, c):
        Given a quadratic equation ax^2 + bx + c, find the roots of the equation as a list.
    find_intersections(line1, v1, a1, line2, v2, a2, current_time):
        Returns a list of valid Intersections between two lines with velocity/acceleration,
        with time relative to current_time.
    

Classes:
    Intersection: Represents the time and position of an intersection between two objects.
"""

import math
from itertools import chain, product
from collections import deque
from heapq import merge

import util
import entity
import game
import multiprocessing

####################################################################################################

# A List of Intersections, sorted by intersection time.
# Note: Some intersections may be flagged 'invalid'.
Intersections = []

####################################################################################################
        
def resolve_entity(ent, line):
    """Resolves an entity's movement by reflecting velocity off a line."""
    # Reflect e1's velocity off of line
    try:
        ent.velocity = ent.velocity.reflected(~line.direction.normalized()) * game.Game.Friction
    except AttributeError:
        pass

def resolve_entities(ent, other, line):
    normal = ~line.direction.normalized()
    if math.isinf(ent.mass):
        if math.isinf(other.mass):
            raise Exception("What happens when an unstoppable force hits an immovable object?  THIS happens! >:(")
        # For component of other's velocity in 'normal' direction: v_other = 2*v_ent - v_other
        # For component of other's velocity in 'line' direction: v_other = v_other * (1 - friction)
    elif math.isinf(other.mass):
        # For component of ent's velocity in 'normal' direction: v_ent = 2*v_other - v_ent
        # For component of ent's velocity in 'line' direction: v_ent = v_ent * (1 - friction)
        pass

class Intersection(util.TimeComparable):
    """Represents the time and position of an intersection between two objects."""
    __slots__ = ['time', 'pos', 'invalid', 'e1', 'e2', 'line1', 'line2', 'line', 'point']
    
    def __call2__(self):
        """Handles resolving the intersection."""
        if self.invalid:
            # Intersection is invalid, just skip past it
            return
        if not hasattr(self, "e1") or not hasattr(self, "e2"):
            # Intersection somehow has no entities between which there was a collision
            raise Exception("Intersection {0} occurs between nonexistent things".format(self))
    
        if util.FloatEqual(game.Game.GameTime, self.e1.last_collide_time):
            # Collision already handled (this prevents an infinite loop upon collision)
            self.e1.last_collide_time = self.e2.last_collide_time = game.Game.GameTime
            return
        
        # Valid Collision; handle it:
        # All future intersections for both objects will be invalidated and recalculated
        
        # Update collision time to prevent infinite loop
        self.e1.last_collide_time = self.e2.last_collide_time = game.Game.GameTime
        
        resolve_entity(self.e1, self.line)
        resolve_entity(self.e2, self.line)
        
        # Recalculate intersections (exclude e1 from e2, to avoid duplicate calculation)
        self.e1.recalculate_intersections()
        self.e2.recalculate_intersections(self.e1)
    
    def __call__(self):
        """Handles resolving the intersection."""
        if self.invalid:
            # Intersection is invalid, just skip past it
            return
        if not hasattr(self, "e1") or not hasattr(self, "e2"):
            # Intersection somehow has no entities between which there was a collision
            raise Exception("Intersection {0} occurs between nonexistent things".format(self))
    
        if util.FloatEqual(game.Game.GameTime, self.e1.last_collide_time):
            # Collision already handled (this prevents an infinite loop upon collision)
            self.e1.last_collide_time = self.e2.last_collide_time = game.Game.GameTime
            return
        
        # Valid Collision; handle it:
        # All future intersections for both objects will be invalidated and recalculated
        
        # Update collision time to prevent infinite loop
        self.e1.last_collide_time = self.e2.last_collide_time = game.Game.GameTime
        
        line1 = self.line1 + self.e1.position
        line2 = self.line2 + self.e2.position
        
        # Resolve collisions by reflecting each entity's velocity off of the incident line
        if line1.p in line2:
            # collision at line1.p
            resolve_entity(self.e1, line2)
            resolve_entity(self.e2, line2)
        elif line1.q in line2:
            # collision at line1.q
            resolve_entity(self.e1, line2)
            resolve_entity(self.e2, line2)
        elif line2.p in line1:
            # collision at line2.p
            resolve_entity(self.e1, line1)
            resolve_entity(self.e2, line1)
            pass
        elif line2.q in line1:
            # collision at line2.q
            resolve_entity(self.e1, line1)
            resolve_entity(self.e2, line1)
        else:
            # collision not at either line-segments' endpoints
            raise Exception("Intersection {0} occurs, but objects not actually intersecting".format(self))
        
        # Recalculate intersections (exclude e1 from e2, to avoid duplicate calculations)
        self.e1.recalculate_intersections()
        self.e2.recalculate_intersections()#self.e1)
        
    def __repr__(self):
        return "I(%s, %s, %s)" % (format(self.time, '.2f'), self.pos, 'T' if self.invalid else 'F')

    def __init__(self, time = util.INFINITY, pos = None, invalid = False):
        """Instanciate an intersection (with INFINITE 'time', None 'pos', and False 'invalid' default attributes).
        An intersection is considered invalid if some outside factors change its time or position
        validity.  See the physics module documentation on the global Intersections for when this
        occurs."""
        self.time, self.pos, self.invalid = time, pos, invalid
        self.e1, self.e2, self.line1, self.line2 = [None] * 4

def ParabolaLineCollision(pos, vel, acc, p, q):
    """Takes a parabola pos, vel, acc, and a line p q, and returns the intersections between them as a list of
    Intersections.
    Intersections are not necessarily in the line segment pq."""

    # time of intersection is defined by the equation
    # a*time^2 + b*time + c = 0
    
    if acc == util.Vector(0, 0):
        if vel == util.Vector(0, 0):
            return []
        else:
            b = (vel.cross(q) - vel.cross(p))
            c = (pos.cross(q) - pos.cross(p) - p.cross(q))
            roots = [-c / b]
    else:
        a = .5 * (acc.cross(q) - acc.cross(p))
        b = (vel.cross(q) - vel.cross(p))
        c = (pos.cross(q) - pos.cross(p) - p.cross(q))
        try:
            roots = util.find_roots(a, b, c)
        except util.InequalityError:
            roots = []

    if len(roots) == 0:
        return []
    if len(roots) == 1:
        # Intersection time in seconds
        time = roots[0]
        
        # Intersection position
        relative_position = util.Position(pos, vel, acc, time)
        return [Intersection(time * 1000, relative_position)]
        
    # Intersection positions
    relative_positions = [util.Position(pos, vel, acc, time) for time in roots]
    
    return [Intersection(time * 1000, position) for time, position in zip(roots, relative_positions)]
    
# def find_intersections(line1, v1, a1, line2, v2, a2, e1 = None, e2 = None):
# def find_intersections(args):
    # line1, v1, a1, line2, v2, a2 = args[:6]
    # if len(args) > 6:
        # e1 = args[6]
        # if len(args) > 7:
            # e2 = args[7]
        # else:
            # e2 = None
    # else:
        # e1 = None    
def find_intersections(line1, v1, a1, line2, v2, a2):
    """Returns an unsorted list of intersections between line1 and line2."""
    
    # Find collisions with relative velocity/acceleration
    v_line1_line2 = v1 - v2
    a_line1_line2 = a1 - a2
    v_line2_line1 = v2 - v1
    a_line2_line1 = a2 - a1
    i1 = ParabolaLineCollision(line1.p, v_line1_line2, a_line1_line2, *line2)
    i2 = ParabolaLineCollision(line1.q, v_line1_line2, a_line1_line2, *line2)
    i3 = ParabolaLineCollision(line2.p, v_line2_line1, a_line2_line1, *line1)
    i4 = ParabolaLineCollision(line2.q, v_line2_line1, a_line2_line1, *line1)
    
    intersections = []
    for intersection in chain(i1, i2, i3, i4):
        if intersection.time < -util.EPSILON:
            continue
        # A position is invalid if it is not inside one of the two line --segments--
        if (util.Position(line1.p, v_line1_line2, a_line1_line2, intersection.time / 1000) in line2 or
                util.Position(line1.q, v_line1_line2, a_line1_line2, intersection.time / 1000) in line2 or
                util.Position(line2.p, v_line2_line1, a_line2_line1, intersection.time / 1000) in line1 or
                util.Position(line2.q, v_line2_line1, a_line2_line1, intersection.time / 1000) in line1):
            # position is valid
            intersections.append(intersection)
    return intersections

def entity_intersections(ent, collidable):
    """Find all intersections between two entities."""
    intersections = []
    
    # Get all pairs of line segments between the two entities' shapes
    for line1, line2 in product(ent.shape.lines, collidable.shape.lines):
    
        # Find all the intersections and add to the intersections list
        pair_intersections = find_intersections(line1 + ent.position, ent.velocity, ent.acceleration, line2 + collidable.position, collidable.velocity, collidable.acceleration)

        for intersection in pair_intersections:
            intersection.e1 = ent
            intersection.e2 = collidable
            intersection.line1 = line1
            intersection.line2 = line2
            intersections.append(intersection)
    return intersections
    
def entity_intersections2(ent, collidable):
    """Find all intersections between two entities."""
    intersections = []
    
    # Relative velocity and acceleration (v12: velocity of 'ent'(1) relative to 'collidable'(2))
    v12 = ent.velocity - collidable.velocity
    v21 = collidable.velocity - ent.velocity
    a12 = ent.acceleration - collidable.acceleration
    a21 = collidable.acceleration - ent.acceleration
    
    intersections = []
    
    # Get all pairs of line segments between the two entities' shapes
    for point in ent.shape.points:
        for line in collidable.shape.lines:
            point = point + ent.position
            line = line + collidable.position
            point_ints = ParabolaLineCollision(point, v12, a12, *line)
            
            # Filter out and add only valid intersections
            for intersection in point_ints:
                if intersection.time < -util.EPSILON:
                    continue
                # A position is invalid if it is not inside one of the two line --segments--
                if util.Position(point, v12, a12, intersection.time / 1000) in line:
                    intersection.e1 = ent
                    intersection.e2 = collidable
                    intersection.line = line
                    intersection.point = point
                    intersections.append(intersection)
                    
    for point in collidable.shape.points:
        for line in ent.shape.lines:
            point = point + collidable.position
            line = line + ent.position
            point_ints = ParabolaLineCollision(point, v21, a21,  *line)
            
            # Filter out and add only valid intersections
            for intersection in point_ints:
                if intersection.time < -util.EPSILON:
                    continue
                # A position is invalid if it is not inside one of the two line --segments--
                if util.Position(point, v21, a21, intersection.time / 1000) in line:
                    intersection.e1 = collidable
                    intersection.e2 = ent
                    intersection.line = line
                    intersection.point = point
                    intersections.append(intersection)
    r = sorted(intersections, key=lambda I: I.time)
    return r

def update_intersections_pair(ent, collidable):
    """Update Game and each entities' intersections."""
    # Get all intersections between ent and collidable
    intersections = entity_intersections(ent, collidable)
    for intersection in intersections:
        intersection.time += game.Game.GameTime
            
    # intersections need to be sorted so they are evaluated in-order.
    intersections.sort()
    game.Game.GameEvents = deque(merge(game.Game.GameEvents, intersections))
    
    # Entities keep track of their intersections so they can mark them invalid.
    ent.intersections = list(merge(ent.intersections, intersections))
    collidable.intersections = list(merge(collidable.intersections, intersections))
    
def update_intersections(ent, exclude = None):
    """Calculate all intersections between the given entity, and add them to the event list."""
    current_time = game.Game.GameTime
    for collidable in entity.Collidables:
        if ent is collidable or collidable is exclude:
            # don't collide with self
            continue
        update_intersections_pair(ent, collidable)
