
from .shapes import Line


class OriginLine(Line):
    def __init__(self, px, py):
        self.px = px
        self.py = py
    def toLine(self):
        return Line(0, 0, self.px, self.py)
    @property
    def x1(self): return 0
    @property
    def y1(self): return 0
    @property
    def x2(self): return self.px
    @property
    def y2(self): return self.py
    def __repr__(self):
        return '{}({}, {})'.format(type(self).__name__,
                    round(self.px, 3), round(self.py, 3))
    def reverse(self):
        self.px, self.py = -self.px, -self.py
    def reversed(self):
        return OriginLine(-self.px, -self.py)
    @staticmethod
    def fromPoints(x1, y1, **kwargs):
        return OriginLine(x1, y1, **kwargs)
    def toDrawables(self, elements, **kwargs):
        return (elements.Line(self.x1, self.y1, self.x2, self.y2, **kwargs),)

