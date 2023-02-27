import math
import numpy.linalg

from .. import util
from . import arc


class Circle:
    def __init__(self, cx, cy, r, cw=True):
        self.cx = cx
        self.cy = cy
        if r < 0:
            r = -r
            cw = not cw
        self.r = r
        self.cw = cw
    def __repr__(self):
        return '{}({},{}, {}, {})'.format(type(self).__name__,
                round(self.cx, 3), round(self.cy, 3),
                round(self.r, 3), self.cw)
    def reverse(self):
        if self.cw is not None:
            self.cw = not self.cw
    def reversed(self):
        if self.cw is not None:
            cw = not self.cw
        else:
            cw = None
        return Circle(self.cx, self.cy, self.r, cw=cw)
    def is_point_on_segment(self, x, y):
        '''Return True if (x, y) is on this arc, assuming the given point is on
        the circle.
        '''
        return True
    def trimmed(self, x1, y1, x2, y2, cw=None, choose_shorter=None, **kwargs):
        '''Return an arc of the circle, assuming the given points is on the
        circle.
        '''
        assert cw is None or choose_shorter is None
        if cw is None: cw = self.cw
        cx, cy, r = self.cx, self.cy, self.r
        start_deg = math.degrees(math.atan2(y1-cy, x1-cx))
        end_deg = math.degrees(math.atan2(y2-cy, x2-cx))
        if choose_shorter:
            cw = (end_deg - start_deg) % 360 <= 180
        return arc.Arc(cx, cy, r, start_deg, end_deg, cw=cw)
    @staticmethod
    def _centerRadFromPoints(x1, y1, x2, y2, x3, y3):
        c1 = 2*x1 - 2*x2
        c2 = 2*y1 - 2*y2
        c3 = x2**2 - x1**2 + y2**2 - y1**2
        c4 = 2*x1 - 2*x3
        c5 = 2*y1 - 2*y3
        c6 = x3**2 - x1**2 + y3**2 - y1**2
        cx, cy = numpy.linalg.solve([[c1,c2],[c4,c5]], [-c3,-c6])
        rad = math.hypot(x1-cx, y1-cy)
        return cx, cy, rad
    @classmethod
    def from_points(cls, x1, y1, x2, y2, x3, y3, **kwargs):
        cx, cy, rad = cls._centerRadFromPoints(x1, y1, x2, y2, x3, y3)
        return cls(cx, cy, rad, **kwargs)
    def to_drawables(self, **kwargs):
        import drawsvg as draw
        return (draw.Circle(self.cx, self.cy, self.r, **kwargs),)
    def draw_to_path(self, path, cut_deg=0, include_m=True, include_l=False):
        path.arc(self.cx, self.cy, self.r, cut_deg, cut_deg+180,
                 cw=self.cw, include_m=include_m, include_l=include_l)
        path.arc(self.cx, self.cy, self.r, cut_deg+180, cut_deg,
                 cw=self.cw, include_m=False, include_l=False)
