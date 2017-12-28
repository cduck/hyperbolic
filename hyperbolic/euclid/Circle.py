
import math
import numpy.linalg

from .. import util
from . import shapes


class Circle:
    def __init__(self, cx, cy, r, cw=False):
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
    def trimmed(self, x1, y1, x2, y2, cw=None, chooseShorter=None, **kwargs):
        ''' Assumes that the given points are on the circle
            Returns an Arc '''
        assert cw is None or chooseShorter is None
        if cw is None: cw = self.cw
        cx, cy, r = self.cx, self.cy, self.r
        startDeg = math.degrees(math.atan2(y1-cy, x1-cx))
        endDeg = math.degrees(math.atan2(y2-cy, x2-cx))
        if chooseShorter:
            cw = (endDeg - startDeg) % 360 > 180
        return shapes.Arc(cx, cy, r, startDeg, endDeg, cw=cw)
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
    def fromPoints(cls, x1, y1, x2, y2, x3, y3, **kwargs):
        cx, cy, rad = cls._centerRadFromPoints(x1, y1, x2, y2, x3, y3)
        return cls(cx, cy, rad, **kwargs)
    def toDrawables(self, elements, **kwargs):
        return (elements.Circle(self.cx, self.cy, self.r, **kwargs),)
    def drawToPath(self, path, cutDeg=0, includeM=True, includeL=False):
        path.arc(self.cx, self.cy, self.r, cutDeg, cutDeg+180,
                 cw=self.cw, includeM=includeM, includeL=includeL)
        path.arc(self.cx, self.cy, self.r, cutDeg+180, cutDeg,
                 cw=self.cw, includeM=False, includeL=False)

