"""
The physics module contains any functions needed for handling collision
detection and collision resolution.

globals:
  Intersections         A sorted list containing all currently known future
                        intersections between pairs of entities.  New
                        collisions are calculated and old ones invalidated as
                        they are handled, as objects' trajectories update, etc.

classes:
  Intersection          Represents a collision between two objects at a
                        specific point in time.

functions:
  ParabolaLineCollision
                        Find all intersections between a point with velocity
                        and acceleration and non-moving line as a list.
  ParabolaLineSegmentCollision
                        Find all intersections between a point with velocity
                        and acceleration and a non-moving line-segment as a
                        list.
  entity_intersections
                        Find all intersections between two entities as a sorted
                        list.
  update_intersections_pair
                        Add all intersections between two entities to the event
                        queue, and update their respective intersection lists.
  update_intersections
                        Add all intersections between all entities and a
                        specific entity to the event queue, and update their
                        respective intersection lists.
    
"""

import math
from itertools import chain, product
from collections import deque
from heapq import merge

import util
from util import Vector, Position
import entity
from game import game

Intersections = []
        
def _resolve_entity(ent, line):
    """Resolves an entity intersection by reflecting its velocity off a line."""
    # Reflect e1's velocity off of line
    try:
        ent.velocity = ent.velocity.reflected(~line.direction.normalized()) * game.bounciness
    except AttributeError:
        pass

def _resolve_entities(ent, other, line):
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
    """
    Represents an intersection between two objects.
    
    properties:
      time              The game time at which the intersection occurs.
      pos               Relative to the non-moving 'line', this is where the
                        intersection occurs.
      line              The line onto which the entities collided.  This is
                        offset by the owning entity's position at the time of
                        the intersection's calculation.
      invalid           Whether this intersection is no longer valid.
      e1                One of the entities between which the intersection
                        occurred.
      e2                One of the entities between which the intersection
                        occurred.
    
    """
    
    def __call__(self):
        """Handle resolving the intersection."""
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
        
        _resolve_entity(self.e1, self.line)
        _resolve_entity(self.e2, self.line)
        
        # Recalculate intersections (exclude e1 from e2, to avoid duplicate calculation)
        self.e1.recalculate_intersections()
        self.e2.recalculate_intersections(self.e1)
        
    def __str__(self):
        return "Intersection({0}, {1})".format(format(self.time, '.2f'), self.pos)
        
    def __repr__(self):
        return "Intersection({0}, {1})".format(self.time, self.pos)

    def __init__(self, time = util.INFINITY, pos = None, line = None, invalid = False, del_time = None):
        self.time, self.pos, self.line, self.invalid = time, pos, line, invalid
        self.e1 = self.e2 = None
        self.del_time = time

def ParabolaLineCollision(pos, vel, acc, line):
    """
    Get all intersections between a point pos with velocity vel and
    acceleration acc, and a non-moving line line.
    
    Returns intersections with both positive and negative time.
    
    """
    # time of intersection is defined by the equation
    # a*time^2 + b*time + c = 0
    
    p, q = line.p, line.q
    
    if acc == Vector(0, 0):
        if vel == Vector(0, 0):
            return []
        else:
            b = (vel.cross(q) - vel.cross(p))
            c = (pos.cross(q) - pos.cross(p) - p.cross(q))
            if b == 0:
                roots = []
            else:
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
        relative_position = Position(pos, vel, acc, time)
        return [Intersection(time * 1000, relative_position, line)]
        
    # Intersection positions
    relative_positions = [Position(pos, vel, acc, time) for time in roots]
    
    return [Intersection(time * 1000, position, line) for time, position in zip(roots, relative_positions)]

def ParabolaLineSegmentCollision(pos, vel, acc, line):
    """
    Get all intersections between a point pos with velocity vel and
    acceleration acc, and a non-moving line-segment line.
    
    Returns intersections with both positive and negative time.
    
    """

    intersections = ParabolaLineCollision(pos, vel, acc, line)
    intersections = [i for i in intersections if i.pos in i.line]
            
    return intersections

def _parabola_line_collision_wrapper(args):
    return [i for i in ParabolaLineSegmentCollision(*args) if i.time > -util.EPSILON]
    
def entity_intersections(ent, collidable):
    """Get all future intersections between two entities as a sorted list."""
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
    """
    Find all intersections between two entities, and update the game event
    queue and each entity's intersection list.
    
    """
    # import pdb; pdb.set_trace()
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
    """
    Find all intersections between all entities and ent, and update the game
    event queue and each entity's intersection list.
    
    """
    current_time = game.game_time
    for collidable in entity.Collidables:
        if ent is collidable or collidable is exclude:
            # don't collide with self
            continue
        update_intersections_pair(ent, collidable)
