import pygame

from util.vector import Vector
from util.line import Line

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
            clamped.center = Vector(rect.center[0], clamped.center.y)
        
        if clamped.height > rect.height:
            clamped.center = Vector(clamped.center.x, rect.center[1])
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
        return [Vector(self.bottom_left),
                Vector(self.bottom_right),
                Vector(self.top_right),
                Vector(self.top_left)]
             
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
        return Vector(self._bottom_left + (0, self.height))

    @top_left.setter
    def top_left(self, tr):
        self._bottom_left = Vector(Vector(tr) - self.size)

    @property
    def bottom_right(self):
        return Vector(self._bottom_left + (self.width, 0))

    @bottom_right.setter
    def bottom_right(self, br):
        self._bottom_left = Vector(br)
        self._bottom_left.x -= self.width

    @property
    def top_right(self):
        return Vector(self._bottom_left + self.size)

    @top_right.setter
    def top_right(self, tr):
        self.bottom_left = Vector(tr) - self.size

    @property
    def bottom_left(self):
        return Vector(self._bottom_left)

    @bottom_left.setter
    def bottom_left(self, bl):
        self._bottom_left = Vector(bl)

    @property
    def center_left(self):
        return Vector(self._bottom_left + (0, self.height * .5))

    @center_left.setter
    def center_left(self, cl):
        self._bottom_left = Vector(cl)
        self._bottom_left.y -= self.height * .5

    @property
    def center_bottom(self):
        return Vector(self._bottom_left + (self.width * .5, 0))

    @center_bottom.setter
    def center_bottom(self, cb):
        self._bottom_left = Vector(cb)
        self._bottom_left.x -= self.width * .5

    @property
    def center_top(self):
        return Vector(self._bottom_left + (self.width * .5, self.height))

    @center_top.setter
    def center_top(self, ct):
        self._bottom_left = Vector(ct)
        self._bottom_left -= (self.width * .5, self.height)

    @property
    def center_left(self):
        return Vector(self._bottom_left + (self.width, self.height * .5))

    @center_left.setter
    def center_left(self, cl):
        self._bottom_left = Vector(cl)
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
        self.bottom_left = Vector(c) - self._size * .5

    def __init__(self, rect=None, **k):
        """Instanciate a rect by copying another, or with a bottom_left and size, or with a shape."""
        
        if rect is not None:
            # Rect is a copy
            if isinstance(rect, pygame.Rect):
                self._bottom_left = Vector(rect.topleft)
            else:
                self._bottom_left = Vector(rect.bottom_left)
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
                    self._bottom_left = Vector(0, 0)
                else:
                    self._bottom_left = Vector(bottom_left)

                if size is None:
                    self._size = Vector(0, 0)
                else:
                    self._size = Vector(size)
