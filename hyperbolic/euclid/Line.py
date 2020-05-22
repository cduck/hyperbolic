
import math

from .. import util
from .shapes import Circle


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(type(self).__name__,
                    round(self.x1, 3), round(self.y1, 3),
                    round(self.x2, 3), round(self.y2, 3))
    def reverse(self):
        self.x1, self.y1, self.x2, self.y2 = self.x2, self.y2, self.x1, self.y1
    def reversed(self):
        return Line(self.x2, self.y2, self.x1, self.y1)
    def atan2(self):
        return math.atan2(self.y2-self.y1, self.x2-self.x1)
    def length(self):
        return ((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2) ** 0.5
    def parallelTo(self, line2):
        return util.nearZero(math.pi/2 -
                (self.atan2() - line2.atan2() + math.pi/2) % math.pi)
    def parallelDirTo(self, line2):
        return util.nearZero(math.pi -
                (self.atan2() - line2.atan2() + math.pi) % (math.pi*2))
    def antiparallelTo(self, line2):
        return util.nearZero(math.pi -
                (self.atan2() - line2.atan2()) % (math.pi*2))
    def startPoint(self):
        return self.x1, self.y1
    def endPoint(self):
        return self.x2, self.y2
    def trimmed(self, x1, y1, x2, y2, **kwargs):
        ''' Assumes that the given points are on the line '''
        return Line(x1, y1, x2, y2)
    def midpoint(self):
        return (self.x1 + self.x2)/2, (self.y1 + self.y2)/2
    def makePerpendicular(self, x, y, length=1):
        ''' Return a line through (x,y), rotated 90deg CCW from self '''
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
        swap = util.nearZero(x-x1) and util.nearZero(y-y1)
        if swap:
            x1, y1, x2, y2 = x2, y2, x1, y1
        lineAng = math.atan2(y2-y1, x2-x1)
        d = math.hypot(x-x1, y-y1)
        ang = math.atan2(y-y1, x-x1)
        dAlong = d * math.cos(ang - lineAng)
        px1 = dAlong * math.cos(lineAng)
        py1 = dAlong * math.sin(lineAng)
        d2 = math.hypot(dAlong, length)
        ang2 = math.atan2(length, dAlong) + lineAng
        px2 = d2 * math.cos(ang2)
        py2 = d2 * math.sin(ang2)
        if swap:
            px2 = 2*px1 - px2
            py2 = 2*py1 - py2
        return Line(x1+px1, y1+py1, x1+px2, y1+py2)
    def makeParallel(self, x, y, length=1):
        perp = self.makePerpendicular(x, y)
        return perp.makePerpendicular(x, y, length)
    @staticmethod
    def fromPoints(x1, y1, x2, y2, **kwargs):
        return Line(x1, y1, x2, y2, **kwargs)
    @staticmethod
    def radicalAxis(circ1, circ2):
        ''' Return the radical axis for two circles (or points)
            If one input is a line, the output is this line '''
        if not isinstance(circ1, (Circle, Line)):
            circ1 = Circle(*circ1, 0)
        if not isinstance(circ2, (Circle, Line)):
            circ2 = Circle(*circ2, 0)
        if isinstance(circ1, Line) and isinstance(circ2, Line):
            raise ValueError('No radical axis exists for two lines')
        elif isinstance(circ1, Line):
            # TODO: Possibly correct direction to be consistent
            return circ1
        elif isinstance(circ2, Line):
            # TODO: Possibly correct direction to be consistent
            return circ2
        else:
            cx1, cy1, r1 = circ1.cx, circ1.cy, circ1.r
            cx2, cy2, r2 = circ2.cx, circ2.cy, circ2.r
            d = math.hypot(cx2-cx1, cy2-cy1)
            if util.nearZero(d):
                raise ValueError('Circles are concentric')
            d1 = (d**2 + r1**2 - r2**2) / (2*d)
            ratio = d1 / d
            mx = cx1 + ratio * (cx2 - cx1)
            my = cy1 + ratio * (cy2 - cy1)
            return Line(cx1, cy1, cx2, cy2).makePerpendicular(mx, my, length=1)
    def toDrawables(self, elements, **kwargs):
        return (elements.Line(self.x1, self.y1, self.x2, self.y2, **kwargs),)
    def drawToPath(self, path, includeM=True, includeL=False):
        if includeL:
            path.L(self.x1, self.y1)
        elif includeM:
            path.M(self.x1, self.y1)
        path.L(self.x2, self.y2)

