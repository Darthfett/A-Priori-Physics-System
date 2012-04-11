from util.line import Line
from util.vector import Vector

class Shape:
    """A list of points that represents an object."""
    @property
    def lines(self):
        return [Line(self.points[i-1], self.points[i]) for i in range((1-int(self.enclosed)), len(self.points))]
        
    def __repr__(self):
        return 'Shape(' + str(self.points) + ', ' + str(enclosed) + ')'

    def __init__(self, points, enclosed=None):
        if isinstance(points, Shape):
            self.points = points.points
            if enclosed is None or type(enclosed) is not bool:
                self.enclosed = points.enclosed
            else:
                self.enclosed = enclosed
        else:
            self.points = [Vector(point) for point in points]
            if enclosed is None:
                self.enclosed = True
            else:
                if not isinstance(enclosed, bool):
                    raise TypeError("'enclosed' must be of type bool, not {0}".format(type(enclosed)))
                self.enclosed = enclosed