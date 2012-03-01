from util.point import Point
from util.vector import Vector
from util.line import Line
import pygame

class Rect:

    def clamp(self, rect):
        if self.left < rect.left:
            self.left = rect.left
        
        if self.right > rect.right:
            self.right = rect.right
        
        if self.top > rect.top:
            self.top = rect.top
        
        if self.bottom < rect.bottom:
            self.bottom = rect.bottom
        
        if self.width > rect.width:
            self.center.x = rect.center[0]
        
        if self.height > rect.height:
            self.center.y = rect.center[1]
    
    def clamped(self, rect):
        clamped = Rect(self)
        if clamped.left < rect.left:
            clamped.left = rect.left
        
        if clamped.right > rect.right:
            clamped.right = rect.right
        
        if clamped.top > rect.top:
            clamped.top = rect.top
        
        if clamped.bottom < rect.bottom:
            clamped.bottom = rect.bottom
        
        if clamped.width > rect.width:
            clamped.center = Point(rect.center[0], clamped.center.y)
        
        if clamped.height > rect.height:
            clamped.center = Point(clamped.center.x, rect.center[1])
        return clamped

    def offset(self, offset):
        self._bottom_left += offset
    
    def offsetted(self, offset):
        offsetted = Rect(self)
        offsetted._bottom_left += offset
        return offsetted
    
    @property
    def shape(self):
        """Returns a rectangle composed of four lines."""
        return [Line(self.bottom_left, self.bottom_right),
                Line(self.bottom_right, self.top_right),
                Line(self.top_right, self.top_left),
                Line(self.top_left, self.bottom_left)]
             
    @shape.setter
    def shape(self, shape):
        min_line_x = lambda l: min(l.p.x, l.q.x)
        min_line_y = lambda l: min(l.p.y, l.q.y)
        max_line_x = lambda l: max(l.p.x, l.q.x)
        max_line_y = lambda l: max(l.p.y, l.q.y)
        
        left = min_line_x(shape[0])
        right = max_line_x(shape[0])
        bottom = min_line_y(shape[0])
        top = max_line_y(shape[0])
        
        for line in shape:
            left = min(min_line_x(line), left)
            right = max(max_line_x(line), right)
            bottom = min(min_line_y(line), bottom)
            top = max(max_line_y(line), top)
        
        self._bottom_left = Point(left, bottom)
        self._size = Vector(right-left, top-bottom)
             
    @property
    def top(self):
        return self._bottom_left.y + self.height

    @top.setter
    def top(self, t):
        self._bottom_left.y = t - self.height

    @property
    def bottom(self):
        return self._bottom_left.y

    @bottom.setter
    def bottom(self, b):
        self._bottom_left.y = b

    @property
    def left(self):
        return self._bottom_left.x

    @left.setter
    def left(self, l):
        self._bottom_left.x = l

    @property
    def right(self):
        return self._bottom_left.x + self.width

    @right.setter
    def right(self, r):
        self._bottom_left.x = r - self.width

    @property
    def top_left(self):
        return Point(self._bottom_left + (0, self.height))

    @top_left.setter
    def top_left(self, tr):
        self._bottom_left = Point(Point(tr) - self.size)

    @property
    def bottom_right(self):
        return Point(self._bottom_left + (self.width, 0))

    @bottom_right.setter
    def bottom_right(self, br):
        self._bottom_left = Point(br)
        self._bottom_left.x -= self.width

    @property
    def top_right(self):
        return Point(self._bottom_left + self.size)

    @top_right.setter
    def top_right(self, tr):
        self.bottom_left = Point(tr) - self.size

    @property
    def bottom_left(self):
        return Point(self._bottom_left)

    @bottom_left.setter
    def bottom_left(self, bl):
        self._bottom_left = Point(bl)

    @property
    def center_left(self):
        return Point(self._bottom_left + (0, self.height * .5))

    @center_left.setter
    def center_left(self, cl):
        self._bottom_left = Point(cl)
        self._bottom_left.y -= self.height * .5

    @property
    def center_bottom(self):
        return Point(self._bottom_left + (self.width * .5, 0))

    @center_bottom.setter
    def center_bottom(self, cb):
        self._bottom_left = Point(cb)
        self._bottom_left.x -= self.width * .5

    @property
    def center_top(self):
        return Point(self._bottom_left + (self.width * .5, self.height))

    @center_top.setter
    def center_top(self, ct):
        self._bottom_left = Point(ct)
        self._bottom_left -= (self.width * .5, self.height)

    @property
    def center_left(self):
        return Point(self._bottom_left + (self.width, self.height * .5))

    @center_left.setter
    def center_left(self, cl):
        self._bottom_left = Point(cl)
        self._bottom_left -= (self.width, self.height * .5)

    @property
    def width(self):
        return self.size.x

    @width.setter
    def width(self, w):
        self.size.x = w

    @property
    def height(self):
        return self.size.y

    @height.setter
    def height(self, h):
        self.size.y = h

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, s):
        self._size = Vector(s)

    @property
    def center(self):
        return self.bottom_left + self._size * .5

    @center.setter
    def center(self, c):
        self.bottom_left = Point(c) - self._size * .5

    def __init__(self, rect = None, **k):
        """Instanciate a rect by copying another, or with a bottom_left and size, or with a shape."""
        
        if rect is not None:
            # Rect is a copy
            if isinstance(rect, pygame.Rect):
                self._bottom_left = Point(rect.bottomleft)
            else:
                self._bottom_left = Point(rect.bottom_left)
            self._size = Vector(rect.size)
        else:
            # New rect
            size = k.get("size")
            bottom_left = k.get("bottom_left")
            
            shape = k.get("shape")
            
            if size is None and bottom_left is None and shape is not None:
                # Rect is Bound box for Shape
                self.shape = shape
                
            else:
                # Rect is bottom_left and size
                if bottom_left is None:
                    self._bottom_left = Point(0, 0)
                else:
                    self._bottom_left = Point(bottom_left)

                if size is None:
                    self._size = Vector(0, 0)
                else:
                    self._size = Vector(size)
