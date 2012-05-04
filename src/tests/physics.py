import unittest
import collections

import game
from physics import ParabolaLineCollision, ParabolaLineSegmentCollision, _parabola_line_collision_wrapper, Intersection
from util import Vector, Line

class PLCTest(unittest.TestCase):
    """Test ParabolaLineCollision(pos, vel, acc, line, ent=None, oth=None)"""
    
    def setUp(self):
        self.maxDiff=None
        pass
    
    def _test_case(self, iter_):
        return ParabolaLineCollision(*iter_)
    
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
        case_1 = (Vector(10.0, 7.967966086381749e-21), Vector(-0.0, 8.033252840490174e-06), Vector(0, -200), Line(Vector(500.00, 0.00), Vector(0.00, 0.00)))
        
        case_1_result = self._test_case(case_1)
        
        self.assertCountEqual(case_1_result, [Intersection(time=8.033252939677466e-08, del_time=8.033252939677466e-08, pos=Vector(10.00, 0.00), line=Line(Vector(500.00, 0.00), Vector(0.00, 0.00)), ent=None, oth=None, invalid=False), Intersection(time=-9.918729244820295e-16, del_time=-9.918729244820295e-16, pos=Vector(10.00, 0.00), line=Line(Vector(500.00, 0.00), Vector(0.00, 0.00)), ent=None, oth=None, invalid=False)])
        
def load_tests(loader, tests, pattern):
    return tests