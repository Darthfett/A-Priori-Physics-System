import unittest
import collections

import game
from physics import ParabolaLineCollision, ParabolaLineSegmentCollision, _parabola_line_collision_wrapper, Intersection
from util import Vector, Line

class PLCTest(unittest.TestCase):
    """Test ParabolaLineCollision(pos, vel, acc, line, ent=None, oth=None)"""

    def setUp(self):
        self.maxDiff=None

    def _test_case(self, iter_):
        return ParabolaLineCollision(*iter_)

    @unittest.expectedFailure
    def test_parallel(self):

        # case 1: parallel, accelerating parallel, initial velocity
        # case 2: parallel, not accelerating
        # case 3: not accelerating or moving
        # case 4: 0-width parabola (turning around)
        # case 5: non-horizontal line
        case_1 = [Vector(0, 0), Vector(1, 0), Vector(2, 0), Line(Vector(0, 1), Vector(1, 1))]
        case_2 = [Vector(0, 0), Vector(1, 0), Vector(0, 0), Line(Vector(0, 1), Vector(1, 1))]
        case_3 = [Vector(0, 0), Vector(0, 0), Vector(0, 0), Line(Vector(0, 1), Vector(1, 1))]
        case_4 = [Vector(0, 0), Vector(1, 0), Vector(-2, 0), Line(Vector(0, 1), Vector(1, 1))]
        case_5 = [Vector(0, 0), Vector(1, 1), Vector(-2, -2), Line(Vector(0, 1), Vector(1, 2))]

        case_1_result = self._test_case(case_1)
        case_2_result = self._test_case(case_2)
        case_3_result = self._test_case(case_2)
        case_4_result = self._test_case(case_1)
        case_5_result = self._test_case(case_2)

        self.assertFalse(case_1_result)
        self.assertFalse(case_2_result)
        self.assertFalse(case_3_result)
        self.assertFalse(case_4_result)
        self.assertFalse(case_5_result)

    @unittest.expectedFailure
    def test_no_collision(self):

        # All parabolas should go through (0, 0)

        # case 1: peak of parabola, never reaches line (accelerating away)
        # case 2: past peak
        # case 3: before peak
        case_1 = [Vector(0, 0), Vector(1, 0), Vector(0, -1), Line(Vector(0, 1), Vector(1, 1))]
        case_2 = [Vector(1, -1), Vector(1, -1.5), Vector(0, -1), Line(Vector(0, 1), Vector(1, 1))]
        case_3 = [Vector(-1, -1), Vector(1, 1.5), Vector(0, -1), Line(Vector(0, 1), Vector(1, 1))]

        case_1_result = self._test_case(case_1)
        case_2_result = self._test_case(case_2)
        case_3_result = self._test_case(case_2)

        self.assertFalse(case_1_result, "peak of parabola collision failing with {n} collisions (expected: 0)".format(n=len(case_1_result)))
        self.assertFalse(case_2_result, "past peak of parabola collision failing with {n} collisions (expected: 0)".format(n=len(case_1_result)))
        self.assertFalse(case_3_result, "before peak of parabola collision failing with {n} collisions (expected: 0)".format(n=len(case_1_result)))

    @unittest.expectedFailure
    def test_one_collision(self):

        # case 1: line
        # case 2: parabola
        case_1 = [Vector(0, 0), Vector(1, 1), Vector(0, 0), Line(Vector(0, 1), Vector(1, 1))]
        case_2 = [Vector(-1, -1), Vector(1, 2), Vector(0, -2), Line(Vector(0, 0), Vector(1, 0))]

        case_1_result = self._test_case(case_1)
        case_2_result = self._test_case(case_2)

        self.assertTrue(case_1_result, "line collision failing")
        self.assertTrue(case_2_result, "parabola collision failing")

        self.assertEqual(len(case_1_result), 1, "line collision failing with {n} collisions (expected: 1): {collisions}".format(n=len(case_1_result), collisions=case_1_result))
        self.assertEqual(len(case_2_result), 1, "parabola collision failing with {n} collisions (expected: 1): {collisions}".format(n=len(case_2_result), collisions=case_2_result))

        self.assertEqual(case_1_result[0].time, 1, "line collision failing with time={time} (expected: 1)".format(time=case_1_result[0].time))
        self.assertEqual(case_2_result[0].time, 1, "parabola collision failing with time={time} (expected: 1)".format(time=case_2_result[0].time))

    @unittest.expectedFailure
    def test_two_collisions(self):

        # case 1: real example (near zero)
        case_1 = (Vector(-2, -2), Vector(1, 4), Vector(0, -2), Line(Vector(-2, -1), Vector(2, -1)))
        # times are 2 +/- sqrt(3)
        case_1_expected = [Intersection(time=3.732050807568877, del_time=3.732050807568877, pos=Vector(1.73, -1.00), line=Line(Vector(-2.00, -1.00), Vector(2.00, -1.00)), ent=None, oth=None, invalid=False),
                           Intersection(time=0.2679491924311227, del_time=0.2679491924311227, pos=Vector(-1.73, -1.00), line=Line(Vector(-2.00, -1.00), Vector(2.00, -1.00)), ent=None, oth=None, invalid=False)]

        case_1_results = self._test_case(case_1)

        e = map(repr, case_1_expected)
        a = map(repr, case_1_results)

        self.assertCountEqual(e, a)

def load_tests(loader, tests, pattern):
    return tests