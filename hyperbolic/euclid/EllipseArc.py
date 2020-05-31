
import math

from .. import util
from .shapes import Ellipse


class EllipseArc(Ellipse):
    def __init__(self, cx, cy, rx, ry, rotDeg, startDeg, endDeg, cw=False):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
        self.rotDeg = rotDeg
        self.startDeg = startDeg
        self.endDeg = endDeg
        self.cw = cw

    def startPoint(self):
        return self.pointAtAngle(self.startDeg)

    def endPoint(self):
        return self.pointAtAngle(self.endDeg)

    def midDegree(self):
        if self.cw:
            startDeg, endDeg = self.endDeg, self.startDeg
        else:
            startDeg, endDeg = self.startDeg, self.endDeg
        diffDeg = (endDeg - startDeg) % 360
        return (startDeg + diffDeg/2) % 360

    def midpoint(self):
        return self.pointAtAngle(self.midDegree())

    def reversed(self):
        return EllipseArc(self.cx, self.cy, self.rx, self.ry, self.rotDeg,
                          self.endDeg, self.startDeg, cw=not self.cw)

    @staticmethod
    def fromBoundingQuad(x0, y0, x1, y1, x2, y2, x3, y3, sx, sy, ex, ey, mx, my,
                         excludeMid=False):
        e = Ellipse.fromBoundingQuad(x0, y0, x1, y1, x2, y2, x3, y3)
        if e is None:
            return None  # Degenerate ellipse
        sx, ex, mx = sx-e.cx, ex-e.cx, mx-e.cx
        sy, ey, my = sy-e.cy, ey-e.cy, my-e.cy
        startDeg = math.degrees(math.atan2(sy, sx))
        endDeg = math.degrees(math.atan2(ey, ex))
        midDeg = math.degrees(math.atan2(my, mx))
        # Clockwise around ellipse if midDeg is not between start and end
        cw = (midDeg-startDeg)%360 > (endDeg-startDeg)%360
        cw = cw ^ excludeMid
        return EllipseArc(e.cx, e.cy, e.rx, e.ry, e.rotDeg, startDeg, endDeg,
                          cw=cw)

    def drawToPath(self, path, includeM=True, includeL=False):
        sx, sy = self.startPoint()
        ex, ey = self.endPoint()
        largeArc = (self.endDeg - self.startDeg) % 360 > 180
        if includeL:
            path.L(sx, sy)
        elif includeM:
            path.M(sx, sy)
        path.A(self.rx, self.ry, -self.rotDeg, largeArc^self.cw, self.cw,
               ex, ey)

    def toDrawables(self, elements, **kwargs):
        path = elements.Path(**kwargs)
        self.drawToPath(path, includeM=True)
        return (path,)
