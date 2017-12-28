
import math

from .. import util
from .shapes import Circle


class Arc(Circle):
    def __init__(self, cx, cy, r, startDeg, endDeg, cw=False):
        super().__init__(cx, cy, r)
        self.startDeg = startDeg
        self.endDeg = endDeg
        self.cw = cw
    def __repr__(self):
        return '{}({},{}, {}, {},{},{})'.format(type(self).__name__,
                    round(self.cx, 3), round(self.cy, 3), round(self.r, 3),
                    round(self.startDeg, 3), round(self.endDeg, 3),
                    self.cw)
    def startPoint(self):
        x = self.r * math.cos(math.radians(self.startDeg))
        y = self.r * math.sin(math.radians(self.startDeg))
        return self.cx+x, self.cy+y
    def endPoint(self):
        x = self.r * math.cos(math.radians(self.endDeg))
        y = self.r * math.sin(math.radians(self.endDeg))
        return self.cx+x, self.cy+y
    def midDegree(self):
        if self.cw:
            startDeg, endDeg = self.endDeg, self.startDeg
        else:
            startDeg, endDeg = self.startDeg, self.endDeg
        diffDeg = (endDeg - startDeg) % 360
        return (startDeg + diffDeg/2) % 360
    def midpoint(self):
        ang = math.radians(self.midDegree())
        return self.cx + self.r * math.cos(ang), self.cy + self.r * math.sin(ang)
    def reverse(self):
        self.startDeg, self.endDeg = self.endDeg, self.startDeg
        self.cw = not self.cw
    def reversed(self):
        return Arc(self.cx, self.cy, self.r, self.endDeg, self.startDeg,
                   cw=not self.cw)
    @classmethod
    def fromPoints(cls, sx, sy, ex, ey, mx, my, excludeMid=False, **kwargs):
        cx, cy, rad = cls._centerRadFromPoints(sx, sy, ex, ey, mx, my)
        sx, ex, mx = sx-cx, ex-cx, mx-cx
        sy, ey, my = sy-cy, ey-cy, my-cy
        startDeg = math.degrees(math.atan2(sy, sx))
        endDeg = math.degrees(math.atan2(ey, ex))
        midDeg = math.degrees(math.atan2(my, mx))
        # Clockwise around circle if midDeg is not between start and end
        cw = (midDeg-startDeg)%360 > (endDeg-startDeg)%360
        cw = cw ^ excludeMid
        return cls(cx, cy, rad, startDeg, endDeg, cw=cw, **kwargs)
    @classmethod
    def fromPointsWithCenter(cls, sx, sy, ex, ey, cx, cy,
                             r=None, cw=False, **kwargs):
        sx, sy, ex, ey = sx-cx, sy-cy, ex-cx, ey-cy
        sr = math.hypot(sx, sy)
        er = math.hypot(ex, ey)
        if r is None:
            r = (sr + er) / 2
        assert util.nearZero(sr-r) and util.nearZero(er-r), 'Rounding error'
        startDeg = math.degrees(math.atan2(sy, sx))
        endDeg = math.degrees(math.atan2(ey, ex))
        return cls(cx, cy, r, startDeg, endDeg, cw=cw, **kwargs)
    def toDrawables(self, elements, **kwargs):
        return (elements.Arc(self.cx, self.cy, self.r, self.startDeg,
                         self.endDeg, cw=self.cw, **kwargs),)
    def drawToPath(self, path, includeM=True, includeL=False):
        path.arc(self.cx, self.cy, self.r, self.startDeg, self.endDeg,
                 cw=self.cw, includeM=includeM, includeL=includeL)

