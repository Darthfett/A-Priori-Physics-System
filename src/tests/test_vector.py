import unittest
import collections

from util import Vector

class VectorTest(unittest.TestCase):
    def setUp(self):
        self.p = Vector(1, 2)
        self.q = (3, 4)

    def test_add(self):
        r = self.p + self.q
        self.assertEqual(r.x, 4)
        self.assertEqual(r.y, 6)

    def test_sub(self):
        r = self.p - self.q
        self.assertEqual(r.x, -2)
        self.assertEqual(r.y, -2)

    def test_dot_product(self):
        r = self.p * self.q
        self.assertEqual(r, 11)

    def test_scalar_product(self):
        r = self.p * 3
        self.assertEqual(r.x, 3)
        self.assertEqual(r.y, 6)

    def test_dot_div(self):
        r = self.p / self.q
        self.assertEqual(r, 1 / 3 + 2 / 4)

    def test_scalar_div(self):
        r = self.p / 3
        self.assertEqual(r.x, 1 / 3)
        self.assertEqual(r.y, 2 / 3)
        self.p /= 3
        self.assertEqual(r, self.p)

    def test_equals(self):
        r = Vector(3, 4)
        self.assertEqual(r, self.q)
        self.assertNotEqual(r, self.p)

    def test_iter(self):
        self.assertEqual(len(self.p), 2)
        self.assertIsInstance(self.p, collections.Iterable)
        self.assertEqual(self.p[0], self.p.x)
        self.assertEqual(self.p[1], self.p.y)
        self.assertIn(2, self.p)

def load_tests(loader, tests, pattern):
    return tests
