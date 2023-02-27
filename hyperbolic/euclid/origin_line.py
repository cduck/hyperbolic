from . import line


class OriginLine(line.Line):
    def __init__(self, px, py):
        self.px = px
        self.py = py
    def to_line(self):
        return line.Line(0, 0, self.px, self.py)
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
    def from_points(x1, y1, **kwargs):
        return OriginLine(x1, y1, **kwargs)
    def to_drawables(self, **kwargs):
        import drawsvg as draw
        return (draw.Line(self.x1, self.y1, self.x2, self.y2, **kwargs),)
