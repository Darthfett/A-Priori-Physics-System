from util.line import Line
from util.vector import Vector

class Shape:
    """A list of points that represents an object."""
    
    def offset(self, offset):
        for point in self.points:
            point += offset
    
    @property
    def lines(self):
        """
        A list of lines that connect each adjacent point.
        
        If the shape is enclosed, the last point will also be connected to the
        first point.
        
        """
        
        return [Line(self.points[i-1], self.points[i]) for i in range((1-int(self.enclosed)), len(self.points))]
        
    def __repr__(self):
        return 'Shape(' + str(self.points) + ', ' + str(enclosed) + ')'

    def __init__(self, points, enclosed=None):
        if isinstance(points, Shape):
            self.points = [Vector(point) for point in points.points]
            if enclosed is None:
                self.enclosed = points.enclosed
            else:
                self.enclosed = bool(enclosed)
        else:
            self.points = [Vector(point) for point in points]
            if enclosed is None:
                self.enclosed = True
            else:
                enclosed = bool(enclosed)
                self.enclosed = enclosed