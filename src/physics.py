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
  find_pair_intersections
                        Add all intersections between two entities to the event
                        queue, and update their respective intersection lists.
  find_intersections
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
    new_vel = ent.velocity.reflected(line.normal) * game.bounciness
    try:
        ent.velocity = new_vel
    except AttributeError:
        pass

class Intersection(GameEvent):
    """
    Represents an intersection between two objects.

    properties:
      time              The game time at which the intersection occurs.
      point_index       Index of the point of ent which is colliding with oth.
      line_index        Index of the line of oth which is colliding with ent.
      ent               One of the entities between which the intersection
                        occurred.
      oth               One of the entities between which the intersection
                        occurred.
      del_time          The relative time from when the intersection was
                        calculated.
      invalid           Whether this intersection is no longer valid.

    """

    @property
    def line(self):
        if hasattr(self, '_line'):
            if self._line_game_time == game.game_time:
                return self._line
        self._line = self.oth.pos_shape.lines[self.line_index]
        self._line_game_time = game.game_time
        return self._line

    @property
    def point(self):
        if hasattr(self, '_point'):
            if self._point_game_time == game.game_time:
                return self._point
        self._point = self.ent.pos_shape.points[self.point_index]
        self._point_game_time = game.game_time
        return self._point

    @property
    def pos(self):
        if hasattr(self, '_pos'):
            if self._pos_game_time == game.game_time:
                return self._pos
        self._pos = Position(self.ent.pos_shape.points[self.point_index], self.ent.velocity - self.oth.velocity, self.ent.acceleration - self.oth.acceleration, self.time - game.game_time)
        self._pos_game_time = game.game_time
        return self._pos

    def __call__(self):
        """Handle resolving the intersection."""

        ## Collision Validation

        if self.invalid:
            # Intersection is invalid, just skip past it
            return [], []
        if FloatEqual(self.del_time, 0):
            # This collision JUST happened
            return [], []
        try:
            if self.ent in self.oth.resters or self.oth in self.ent.resters:
                return [], []
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

        # Valid Collision; handle it

        _resolve_entity(self.ent, self.line)
        _resolve_entity(self.oth, self.line)

        #game.pause()

        # Handled collisions invalidate all intersections dealing with these objects
        # Invalidate all intersections and return all the new ones
        self.ent.invalidate_intersections()
        self.oth.invalidate_intersections()

        intersections = find_pair_intersections(self.ent, self.oth)
        self.ent.intersections.extend(intersections)
        self.oth.intersections.extend(intersections)

        ent_intersections = find_intersections(self.ent, exclude=self.oth)
        oth_intersections = find_intersections(self.oth, exclude=self.ent)

        self.ent.intersections.extend(ent_intersections)
        self.oth.intersections.extend(oth_intersections)

        intersections.extend(ent_intersections)
        intersections.extend(oth_intersections)

        return intersections, []

    def __eq__(self, oth):
        return hash(self) == hash(oth)

    def __hash__(self):
        return hash((self.time, self.del_time, self.point_index, self.line_index, self.ent, self.oth, self.invalid))

    def __str__(self):
        return "Intersection(time={time}, del_time={del_time}, point_index={point_index}, line_index={line_index}, ent={ent}, oth={oth}, invalid={invalid})".format(**self.__dict__)

    def __repr__(self):
        return "Intersection(time={time}, del_time={del_time}, point_index={point_index}, line_index={line_index}, ent={ent}, oth={oth}, invalid={invalid})".format(**self.__dict__)

    def __init__(self, time=util.INFINITY, point_index=None, line_index=None, ent=None, oth=None, del_time=None, invalid=False):
        if del_time is not None:
            self.del_time = del_time
            self.time = time
        else:
            self.del_time = time
            self.time = time + game.game_time
        self.point_index, self.line_index, self.invalid = point_index, line_index, invalid
        self.ent, self.oth = ent, oth

def ParabolaLineCollision(pos_index, vel, acc, line_index, ent, oth):
    """
    Get all intersections between a point pos with velocity vel and
    acceleration acc, and a non-moving line line.

    Returns intersections with both positive and negative time.

    """
    pos = ent.pos_shape.points[pos_index]
    line = oth.pos_shape.lines[line_index]
    # time of intersection is defined by the equation
    # a*time^2 + b*time + c = 0

    p, q = line.p, line.q

    if acc == Vector(0, 0):
        if vel == Vector(0, 0):
            return []
        else:
            # If acceleration is zero, there can only be one or zero roots.
            b = (vel.cross(q) - vel.cross(p))
            c = (pos.cross(q) - pos.cross(p) - p.cross(q))
            if b == 0:
                roots = []
            else:
                roots = [-c / b]
    else:
        # non-zero acceleration, possibly 2 roots.
        a = .5 * (acc.cross(q) - acc.cross(p))
        b = (vel.cross(q) - vel.cross(p))
        c = (pos.cross(q) - pos.cross(p) - p.cross(q))
        try:
            roots = util.find_roots(a, b, c)
        except util.InequalityError:
            roots = []
        except util.EquationIdentity:
            roots = [0]

    return [Intersection(time, pos_index, line_index, ent=ent, oth=oth) for time in roots]

def ParabolaLineSegmentCollision(pos_index, vel, acc, line_index, ent, oth):
    """
    Get all intersections between a point pos with velocity vel and
    acceleration acc, and a non-moving line-segment line.

    Returns intersections with both positive and negative time.

    """

    intersections = ParabolaLineCollision(pos_index, vel, acc, line_index, ent, oth)

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
    args = [(point_index, v12, a12, line_index, ent, oth) for point_index, line_index in product(range(len(ent.pos_shape.points)), range(len(oth.pos_shape.lines)))]
    args += [(point_index, v21, a21, line_index, oth, ent) for point_index, line_index in product(range(len(oth.pos_shape.points)), range(len(ent.pos_shape.lines)))]

    return [i for intersections in map(_parabola_line_collision_wrapper, args) for i in intersections]

def find_pair_intersections(ent, oth):
    """
    Find all intersections between two entities, and update the game event
    queue and each entity's intersection list.

    """

    # Get all intersections between ent and oth
    intersections = entity_intersections(ent, oth)

    return intersections

def find_intersections(ent, exclude = None):
    """
    Find all intersections between all entities and ent, and update the game
    event queue and each entity's intersection list.

    """
    intersections = []
    for oth in entity.Collidables:
        if ent is oth or oth is exclude:
            # don't collide with self
            continue
        intersections.extend(find_pair_intersections(ent, oth))
    return intersections
