import unittest
import collections

from physics import ParabolaLineCollision as plc, ParabolaLineSegmentCollision, _parabola_line_collision_wrapper, Intersection
from util import Vector, Line

class DummyProvider:
    game_time = 0

class DummyEntShape:
    points = [Vector(0, 0), Vector(1, -1), Vector(-1, -1), Vector(-2, -2)]

class DummyOthShape:
    lines = [Line(Vector(0, 1), Vector(1, 1)),
             Line(Vector(0, 1), Vector(1, 2)),
             Line(Vector(0, 0), Vector(1, 0)),
             Line(Vector(-2, -1), Vector(2, -1))]

class DummyEnt:
    pos_shape = DummyEntShape

class DummyOth:
    pos_shape = DummyOthShape

class PLCTest(unittest.TestCase):
    """Test ParabolaLineCollision(pos, vel, acc, line, ent=None, oth=None)"""

    def setUp(self):
        self.maxDiff=None

    def _test_case(self, *args, **kwargs):
        return plc(*args, **kwargs)

    def test_parallel(self):

        # case 1: parallel, accelerating parallel, initial velocity
        # case 2: parallel, not accelerating
        # case 3: not accelerating or moving
        # case 4: 0-width parabola (turning around)
        # case 5: non-horizontal line
        case_1 = {'provider': DummyProvider,
                  'velocity': Vector(1, 0),
                  'acceleration': Vector(2, 0),
                  'point_index': 0,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        case_2 = {'provider': DummyProvider,
                  'velocity': Vector(1, 0),
                  'acceleration': Vector(0, 0),
                  'point_index': 0,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        case_3 = {'provider': DummyProvider,
                  'velocity': Vector(0, 0),
                  'acceleration': Vector(0, 0),
                  'point_index': 0,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        case_4 = {'provider': DummyProvider,
                  'velocity': Vector(1, 0),
                  'acceleration': Vector(-2, 0),
                  'point_index': 0,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        case_5 = {'provider': DummyProvider,
                  'velocity': Vector(1, 1),
                  'acceleration': Vector(-2, -2),
                  'point_index': 0,
                  'line_index': 1,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }

        case_1_result = self._test_case(**case_1)
        case_2_result = self._test_case(**case_2)
        case_3_result = self._test_case(**case_3)
        case_4_result = self._test_case(**case_4)
        case_5_result = self._test_case(**case_5)

        self.assertFalse(case_1_result)
        self.assertFalse(case_2_result)
        self.assertFalse(case_3_result)
        self.assertFalse(case_4_result)
        self.assertFalse(case_5_result)

    def test_no_collision(self):

        # All parabolas should go through (0, 0)

        # case 1: peak of parabola, never reaches line (accelerating away)
        # case 2: past peak
        # case 3: before peak
        case_1 = {'provider': DummyProvider,
                  'velocity': Vector(1, 0),
                  'acceleration': Vector(0, -1),
                  'point_index': 0,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        case_2 = {'provider': DummyProvider,
                  'velocity': Vector(1, -1.5),
                  'acceleration': Vector(0, -1),
                  'point_index': 1,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        case_3 = {'provider': DummyProvider,
                  'velocity': Vector(1, 1.5),
                  'acceleration': Vector(0, -1),
                  'point_index': 2,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }

        case_1_result = self._test_case(**case_1)
        case_2_result = self._test_case(**case_2)
        case_3_result = self._test_case(**case_2)

        self.assertFalse(case_1_result, "peak of parabola collision failing with {n} collisions (expected: 0)".format(n=len(case_1_result)))
        self.assertFalse(case_2_result, "past peak of parabola collision failing with {n} collisions (expected: 0)".format(n=len(case_1_result)))
        self.assertFalse(case_3_result, "before peak of parabola collision failing with {n} collisions (expected: 0)".format(n=len(case_1_result)))

    def test_one_collision(self):

        # case 1: line
        # case 2: parabola
        case_1 = {'provider': DummyProvider,
                  'velocity': Vector(1, 1),
                  'acceleration': Vector(0, 0),
                  'point_index': 0,
                  'line_index': 0,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        case_2 = {'provider': DummyProvider,
                  'velocity': Vector(1, 2),
                  'acceleration': Vector(0, -2),
                  'point_index': 2,
                  'line_index': 2,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }

        case_1_result = self._test_case(**case_1)
        case_2_result = self._test_case(**case_2)

        self.assertTrue(case_1_result, "line collision failing")
        self.assertTrue(case_2_result, "parabola collision failing")

        self.assertEqual(len(case_1_result), 1, "line collision failing with {n} collisions (expected: 1): {collisions}".format(n=len(case_1_result), collisions=case_1_result))
        self.assertEqual(len(case_2_result), 1, "parabola collision failing with {n} collisions (expected: 1): {collisions}".format(n=len(case_2_result), collisions=case_2_result))

        self.assertEqual(case_1_result[0].time, 1, "line collision failing with time={time} (expected: 1)".format(time=case_1_result[0].time))
        self.assertEqual(case_2_result[0].time, 1, "parabola collision failing with time={time} (expected: 1)".format(time=case_2_result[0].time))

    def test_two_collisions(self):

        # case 1: real example (near zero)
        case_1 = {'provider': DummyProvider,
                  'velocity': Vector(1, 4),
                  'acceleration': Vector(0, -2),
                  'point_index': 3,
                  'line_index': 3,
                  'ent': DummyEnt,
                  'oth': DummyOth
                 }
        # times are 2 +/- sqrt(3)
        case_1_expected = [Intersection(provider=DummyProvider, time=3.732050807568877, del_time=3.732050807568877, point_index=3, line_index=3, ent=DummyEnt, oth=DummyOth, invalid=False),
                           Intersection(provider=DummyProvider, time=0.2679491924311227, del_time=0.2679491924311227, point_index=3, line_index=3, ent=DummyEnt, oth=DummyOth, invalid=False)]

        case_1_results = self._test_case(**case_1)

        e = map(repr, case_1_expected)
        a = map(repr, case_1_results)

        self.assertCountEqual(e, a)

def load_tests(loader, tests, pattern):
    return tests