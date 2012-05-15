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
from util import Vector, Position, FloatEqual, EPSILON
from event import GameEvent
import entity
from game import game
from debug import debug

Intersections = []
RESTING_THRESHOLD = 200 # ms between next collision (?)
        
def _resolve_entity(ent, line):
    """Resolves an entity intersection by reflecting its velocity off a line."""
    # Reflect ent's velocity off of line
    try:
        ent.velocity = ent.velocity.reflected(line.normal) * game.bounciness
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

class Intersection(GameEvent):
    """
    Represents an intersection between two objects.
    
    properties:
      time              The game time at which the intersection occurs.
      del_time          The relative time from when the intersection was
                        calculated.
      pos               Relative to the non-moving 'line', this is where the
                        intersection occurs.
      line              The line onto which the entities collided.  This is
                        offset by the owning entity's position at the time of
                        the intersection's calculation.
      invalid           Whether this intersection is no longer valid.
      ent               One of the entities between which the intersection
                        occurred.
      oth               One of the entities between which the intersection
                        occurred.
    
    """
    
    def __call__(self):
        """Handle resolving the intersection."""
        
        ## Collision Validation
        
        if self.invalid:
            # Intersection is invalid, just skip past it
            return
        if FloatEqual(self.del_time, 0):
            # This collision JUST happened
            return
        self.ent.last_collide_time = self.oth.last_collide_time = game.game_time
        try:
            if self.ent in self.oth.resters or self.oth in self.ent.resters:
                return
        except AttributeError: pass

        
        ## Resting State
        
        # get normal to line (in the opposite direction that ent is striking oth)
        norm = self.line.normal
        if norm * self.ent.velocity > 0:
            # normal is in same direction, reverse normal
            norm = -norm
        
        # Get the magnitude of ent's velocity/acceleration in the direction normal to the line
        norm_vel_mag = -(norm * self.ent.velocity)
        norm_acc_mag = -(norm * self.ent.acceleration)
        
        # Check for resting state
        
        if norm_vel_mag * norm_acc_mag > 0:
            # Possible resting state if velocity and acceleration are both toward the line.
            if (2 * (norm_vel_mag * game.bounciness) / norm_acc_mag) < RESTING_THRESHOLD:
                # Coming to rest due to small next-collision time
                # acc and vel have same direction relative to line (both toward line)
                # Get relative velocity in normal direction
                if self.ent not in entity.Movables:
                    ent = self.oth
                    oth = self.ent
                else:
                    ent = self.ent
                    oth = self.oth
                
                oth_vel = oth.velocity * norm
                ent_vel = ent.velocity * norm
                ent.velocity += (oth_vel - ent_vel) * norm
                
                oth_acc = oth.acceleration * norm
                ent_acc = ent.acceleration * norm
                ent.acceleration += (oth_acc - ent_acc) * norm
                
                if not hasattr(ent, 'resters'):
                    ent.resters = []
                if not hasattr(oth, 'resters'):
                    oth.resters = []
                
                ent.resters.append(oth)
                oth.resters.append(ent)
        
        # TODO: Does resolving a collision make sense if entering the resting state?
        
        # Valid Collision; handle it, and invalidate future intersections
        _resolve_entity(self.ent, self.line)
        _resolve_entity(self.oth, self.line)
        
        # Recalculate intersections (exclude ent from oth, to avoid duplicate calculation)
        self.ent.recalculate_intersections()
        self.oth.recalculate_intersections(self.ent)
        
    def __eq__(self, oth):
        return self.time == oth.time and self.del_time == oth.del_time and self.pos == oth.pos and self.line == oth.line and self.ent == oth.ent and self.oth == oth.oth and self.invalid == oth.invalid
    
    def __hash__(self):
        return hash((self.time, self.del_time, self.pos, self.line, self.ent, self.oth, self.invalid))
        
    def __str__(self):
        return "Intersection(time={time}, del_time={del_time}, pos={pos}, line={line}, ent={ent}, oth={oth}, invalid={invalid})".format(**self.__dict__)
        
    def __repr__(self):
        return "Intersection(time={time}, del_time={del_time}, pos={pos}, line={line}, ent={ent}, oth={oth}, invalid={invalid})".format(**self.__dict__)

    def __init__(self, time=util.INFINITY, pos=None, line=None, ent=None, oth=None, del_time=None, invalid=False):
        if del_time is not None:
            self.del_time = del_time
            self.time = time
        else:
            self.del_time = time
            self.time = time + game.game_time
        self.pos, self.line, self.invalid = pos, line, invalid
        self.ent, self.oth = ent, oth

def ParabolaLineCollision(pos, vel, acc, line, ent=None, oth=None):
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
        except util.EquationIdentity:
            roots = [0]

    if len(roots) == 0:
        return []
    if len(roots) == 1:
        # Intersection time in ms
        time = roots[0]
        
        # Intersection position
        relative_position = Position(pos, vel, acc, time)
        return [Intersection(time, relative_position, line, ent=ent, oth=oth)]
        
    # Intersection positions
    relative_positions = [Position(pos, vel, acc, time) for time in roots]
    
    return [Intersection(time, position, line, ent=ent, oth=oth) for time, position in zip(roots, relative_positions)]

def ParabolaLineSegmentCollision(pos, vel, acc, line, ent=None, oth=None):
    """
    Get all intersections between a point pos with velocity vel and
    acceleration acc, and a non-moving line-segment line.
    
    Returns intersections with both positive and negative time.
    
    """

    intersections = ParabolaLineCollision(pos, vel, acc, line, ent, oth)
        
    valid = [i for i in intersections if i.pos in i.line]
    
            
    return valid

def _parabola_line_collision_wrapper(args):
    return [i for i in ParabolaLineSegmentCollision(*args) if i.del_time > -util.EPSILON]
    
def entity_intersections(ent, oth):
    """Get all future intersections between two entities as a sorted list."""
    intersections = []
    
    # Relative velocity and acceleration (v12: velocity of 'ent'(1) relative to 'oth'(2))
    v12 = ent.velocity - oth.velocity
    v21 = -v12
    a12 = ent.acceleration - oth.acceleration
    a21 = -a12
    args = [(point, v12, a12, line, ent, oth) for point, line in product(ent.pos_shape.points, oth.pos_shape.lines)]
    args += [(point, v21, a21, line, oth, ent) for point, line in product(oth.pos_shape.points, ent.pos_shape.lines)]
    
    return sorted([i for intersections in map(_parabola_line_collision_wrapper, args) for i in intersections])

def update_intersections_pair(ent, oth):
    """
    Find all intersections between two entities, and update the game event
    queue and each entity's intersection list.
    
    """
    
    # Get all intersections between ent and oth
    intersections = entity_intersections(ent, oth)
            
    game.game_events = deque(merge(game.game_events, intersections))
    
    # Entities keep track of their intersections so they can mark them invalid.
    ent.intersections = list(merge(ent.intersections, intersections))
    oth.intersections = list(merge(oth.intersections, intersections))
    
def update_intersections(ent, exclude = None):
    """
    Find all intersections between all entities and ent, and update the game
    event queue and each entity's intersection list.
    
    """
    current_time = game.game_time
    for oth in entity.Collidables:
        if ent is oth or oth is exclude:
            # don't collide with self
            continue
        update_intersections_pair(ent, oth)
