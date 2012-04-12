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
from game import game

####################################################################################################

# A List of Intersections, sorted by intersection time.
# Note: Some intersections may be flagged 'invalid'.
Intersections = []

####################################################################################################
        
def resolve_entity(ent, line):
    """Resolves an entity's movement by reflecting velocity off a line."""
    # Reflect e1's velocity off of line
    try:
        ent.velocity = ent.velocity.reflected(~line.direction.normalized()) * game.bounciness
    except AttributeError:
        pass

def resolve_entities(ent, other, line):
    normal = ~line.direction.normalized()
    if math.isinf(ent.mass):
        if math.isinf(other.mass):
            raise Exception("What happens when an unstoppable force hits an immovable object?  THIS happens! >:(")
        # For component of other's velocity in 'normal' direction: v_other = 2*v_ent - v_other
        # For component of other's velocity in 'line' direction: v_other = v_other * (1 - Bounciness)
    elif math.isinf(other.mass):
        # For component of ent's velocity in 'normal' direction: v_ent = 2*v_other - v_ent
        # For component of ent's velocity in 'line' direction: v_ent = v_ent * (1 - Bounciness)
        pass

class Intersection(util.TimeComparable):
    """Represents the time and position of an intersection between two objects."""
    __slots__ = ['time', 'pos', 'line', 'invalid', 'e1', 'e2']
    
    def __call__(self):
        """Handles resolving the intersection."""
        if self.invalid:
            # Intersection is invalid, just skip past it
            return
        if not hasattr(self, "e1") or not hasattr(self, "e2"):
            # Intersection somehow has no entities between which there was a collision
            raise Exception("Intersection {0} occurs between nonexistent things".format(self))
    
        if util.FloatEqual(game.game_time, self.e1.last_collide_time):
            # Collision already handled (this prevents an infinite loop upon collision)
            self.e1.last_collide_time = self.e2.last_collide_time = game.game_time
            return
        
        # Valid Collision; handle it:
        # All future intersections for both objects will be invalidated and recalculated
        
        # Update collision time to prevent infinite loop
        self.e1.last_collide_time = self.e2.last_collide_time = game.game_time
        
        resolve_entity(self.e1, self.line)
        resolve_entity(self.e2, self.line)
        
        # Recalculate intersections (exclude e1 from e2, to avoid duplicate calculation)
        self.e1.recalculate_intersections()
        self.e2.recalculate_intersections(self.e1)
        
    def __repr__(self):
        return "Intersection({0}, {1}, {2})".format(format(self.time, '.2f'), self.pos, self.invalid)

    def __init__(self, time = util.INFINITY, pos = None, line = None, invalid = False):
        """Instanciate an intersection (with INFINITE 'time', None 'pos', and False 'invalid' default attributes).
        An intersection is considered invalid if some outside factors change its time or position
        validity.  See the physics module documentation on the global Intersections for when this
        occurs."""
        self.time, self.pos, self.line, self.invalid = time, pos, line, invalid
        self.e1, self.e2 = [None] * 2

def ParabolaLineCollision(pos, vel, acc, line):
    """Takes a parabola pos, vel, acc, and a line p q, and returns the intersections between them as a list of
    Intersections.
    Intersections are not necessarily in the line segment pq."""

    # time of intersection is defined by the equation
    # a*time^2 + b*time + c = 0
    
    p, q = line.p, line.q
    
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
        return [Intersection(time * 1000, relative_position, line)]
        
    # Intersection positions
    relative_positions = [util.Position(pos, vel, acc, time) for time in roots]
    
    return [Intersection(time * 1000, position, line) for time, position in zip(roots, relative_positions)]

def ParabolaLineSegmentCollision(pos, vel, acc, line):
    intersections = ParabolaLineCollision(pos, vel, acc, line)
    intersections = [i for i in intersections if i.time > -util.EPSILON and i.pos in i.line]
            
    return intersections

def _parabola_line_collision_wrapper(args):
    return ParabolaLineSegmentCollision(*args)
    
def entity_intersections(ent, collidable):
    """Find all intersections between two entities."""
    intersections = []
    
    # Relative velocity and acceleration (v12: velocity of 'ent'(1) relative to 'collidable'(2))
    v12 = ent.velocity - collidable.velocity
    v21 = -v12
    a12 = ent.acceleration - collidable.acceleration
    a21 = -a12
    
    args = [(point + ent.position, v12, a12, line + collidable.position) for point, line in product(ent.shape.points, collidable.shape.lines)]
    args += [(point + collidable.position, v21, a21, line + ent.position) for point, line in product(collidable.shape.points, ent.shape.lines)]
    
    return sorted([i for intersections in map(_parabola_line_collision_wrapper, args) for i in intersections])

def update_intersections_pair(ent, collidable):
    """Update Game and each entities' intersections."""
    # Get all intersections between ent and collidable
    intersections = entity_intersections(ent, collidable)
    
    for intersection in intersections:
        intersection.time += game.game_time
        intersection.e1 = ent
        intersection.e2 = collidable
            
    game.game_events = deque(merge(game.game_events, intersections))
    
    # Entities keep track of their intersections so they can mark them invalid.
    ent.intersections = list(merge(ent.intersections, intersections))
    collidable.intersections = list(merge(collidable.intersections, intersections))
    
def update_intersections(ent, exclude = None):
    """Calculate all intersections between the given entity, and add them to the event list."""
    current_time = game.game_time
    for collidable in entity.Collidables:
        if ent is collidable or collidable is exclude:
            # don't collide with self
            continue
        update_intersections_pair(ent, collidable)
