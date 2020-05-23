
import math

from .. import util
from ..euclid.shapes import Circle, Arc, Line as ELine, OriginLine
from ..euclid import intersection
from ..euclid.intersection import InfiniteIntersections, SingleIntersection, \
                                  NoIntersection
from .shapes import Point
from . import shapes as poincare


class Hypercycle:
    def __init__(self, projShape, segment=False):
        assert isinstance(projShape, (Circle, Arc, ELine, OriginLine))
        if segment and not isinstance(projShape, (Arc, ELine)):
            raise ValueError('Not enough information to determine segment endpoints')
        unit = Circle(0,0,1)
        if segment:
            if isinstance(projShape, Arc):
                # TODO: Trim if arc extends outside unit circle
                pass
            elif isinstance(projShape, ELine):
                # TODO: Trim if arc extends outside unit circle
                pass
            else:
                raise ValueError('Unknown type')
        else:
            if isinstance(projShape, Circle):
                x1, y1, x2, y2 = intersection.circleCircle(projShape, unit)
                if projShape.cw:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                projShape = Arc.fromPointsWithCenter(x1, y1, x2, y2,
                                    projShape.cx, projShape.cy, r=projShape.r,
                                    cw=projShape.cw)
            elif isinstance(projShape, ELine):
                x1, y1, x2, y2 = intersection.circleLine(unit, projShape)
                # Keep direction of line the same
                origAng = math.atan2(projShape.y2-projShape.y1,
                                     projShape.x2-projShape.x1)
                newAng = math.atan2(y2-y1, x2-x1)
                angDiff = (newAng - origAng) % (math.pi*2)
                if math.pi/2 < angDiff < 3*math.pi/2:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                projShape = ELine(x1, y1, x2, y2)
            else:
                raise ValueError('Unknown type')
        self.projShape = projShape
        self.segment = segment
    def startPoint(self):
        return Point(*self.projShape.startPoint())
    def endPoint(self):
        return Point(*self.projShape.endPoint())
    def intersectionsWithHcycle(self, hcycle2):
        ''' Returns list of intersections in the unit circle '''
        x2, y2 = 1, 1  # Default, invalid
        try:
            if isinstance(self.projShape, Circle):
                if isinstance(hcycle2.projShape, Circle):
                    x1, y1, x2, y2 = intersection.circleCircle(
                                        self.projShape, hcycle2.projShape)
                else:
                    x1, y1, x2, y2 = intersection.circleLine(
                                        self.projShape, hcycle2.projShape)
            else:
                if isinstance(hcycle2.projShape, Circle):
                    x1, y1, x2, y2 = intersection.circleLine(
                                        hcycle2.projShape, self.projShape)
                else:
                    x1, y1 = intersection.lineLine(
                                self.projShape, hcycle2.projShape)
        except InfiniteIntersections as e:
            raise e from None
        except SingleIntersection as e:
            x1, y1 = e.args
        except NoIntersection:
            x1, y1 = 1, 1  # Invalid
        pts = []
        try:
            pts.append(Point.fromEuclid(x1, y1))
        except ValueError: pass
        try:
            pts.append(Point.fromEuclid(x2, y2))
        except ValueError: pass
        return pts
    def trimmed(self, x1, y1, x2, y2, **kwargs):
        ''' Returns a segment of this hypercycle going from x1,y1
            to x2,y2 (assuming that x1,y1 and x2,y2 are on the
            hypercycle) '''
        trimmedShape = self.projShape.trimmed(x1, y1, x2, y2, **kwargs)
        return type(self)(trimmedShape, segment=True)
    def midpointEuclid(self):
        x, y = self.projShape.midpoint()
        return Point(x, y)
    def reverse(self):
        self.projShape.reverse()
    def reversed(self):
        newShape = self.projShape.reversed()
        newObj = type(self)(newShape, segment=True)
        newObj.segment = self.segment
        return newObj
    def makePerpendicular(self, x, y):
        if util.nearZero(x) and util.nearZero(y):
            radical1 = None
        else:
            radical1 = ELine.radicalAxis(Circle(0,0,1), (x,y))
        radical2 = ELine.radicalAxis(self.projShape, (x,y))
        if radical1 is None or radical1.parallelTo(radical2):
            # Infinite radius circle
            shape = radical2.makePerpendicular(x,y)
            # Ensure correct direction
            if isinstance(self.projShape, ELine):
                if shape.antiparallelTo(self.projShape):
                    shape.reverse()
            else:  # projShape is a Circle
                radial = ELine.fromPoints(x, y, self.projShape.cx, self.projShape.cy)
                if radial.antiparallelTo(shape) ^ self.projShape.cw:
                    shape.reverse()
            return poincare.Line(shape, segment=False)
        else:
            cx, cy = intersection.lineLine(radical1, radical2)
            r = math.hypot(cy-y, cx-x)
            shape = Circle(cx, cy, r)
            # Ensure correct direction
            shape.cw = False
            if isinstance(self.projShape, ELine):
                x1, y1, x2, y2 = intersection.lineCircle(self.projShape, shape)
            else:  # projShape is a Circle
                x1, y1, x2, y2 = intersection.circleCircle(self.projShape, shape)
                shape.cw = shape.cw ^ self.projShape.cw
            if math.hypot(x1, y1) <= math.hypot(x2, y2):
                shape.cw = not shape.cw
            return poincare.Line(shape, segment=False)
    def makeCap(self, point):
        if point.isIdeal():
            return point
        else:
            return self.makePerpendicular(*point)
    def makeOffset(self, offset):
        return Hypercycle.fromHypercycleOffset(self, offset)
    @classmethod
    def fromHypercycleOffset(cls, hcycle, offset, unit=Circle(0,0,1)):
        dh = offset #dh = math.asinh(offset/2)
        if isinstance(hcycle.projShape, Circle):
            # May throw if bad geometry
            x1, y1, x2, y2 = intersection.circleCircle(hcycle.projShape, unit)
            cx, cy = hcycle.projShape.cx, hcycle.projShape.cy
            r, cw = hcycle.projShape.r, hcycle.projShape.cw
            if cw:
                x1, y1, x2, y2 = x2, y2, x1, y1
            rc = math.hypot(cx, cy)
            deMid = rc - r
            dhMid = 2 * math.atanh(deMid)
            sign = -1 if cw else 1
            t = math.tanh((dhMid + sign*dh)/2)
            xOff, yOff = t * cx / rc, t * cy / rc
        else:
            # May throw if bad geometry
            x1, y1, x2, y2 = intersection.lineCircle(hcycle.projShape, unit)
            lineAng = math.atan2(y2-y1, x2-x1)
            mx, my = (x1+x2)/2, (y1+y2)/2  # Midpoint
            if util.nearZero(mx) and util.nearZero(my):
                ang = math.atan2(y2-y1, x2-x1) + math.pi/2
            else:
                ang = math.atan2(my, mx)
            # Test if the line goes clockwise around the origin
            cw = (ang - lineAng) % (math.pi*2) < math.pi
            rm = math.hypot(mx, my)
            deMid = rm
            dhMid = 2 * math.atanh(deMid)
            sign = 1 if cw else -1
            t = math.tanh((dhMid + sign*dh)/2)
            xOff, yOff = t * math.cos(ang), t * math.sin(ang)
        return cls.fromPoints(x1, y1, x2, y2, xOff, yOff, segment=False, excludeMid=False)
    @staticmethod
    def _pointsInlineWithOrigin(x1, y1, x2, y2):
        if ((util.nearZero(x1) and util.nearZero(x2)) or
            (util.nearZero(y1) and util.nearZero(y2)) or
            (util.nearZero(x1) and util.nearZero(y1)) or
            (util.nearZero(x2) and util.nearZero(y2))):
            return True
        elif ((util.nearZero(x1) or util.nearZero(x2)) and
              (util.nearZero(y1) or util.nearZero(y2))):
            return False
        elif util.nearZero(x1) or util.nearZero(x2):
            return util.nearZero(x1/y1 - x2/y2)
        else:
            return util.nearZero(y1/x1 - y2/x2)
    @classmethod
    def fromPoints(cls, sx, sy, ex, ey, mx, my, segment=False, excludeMid=False, **kwargs):
        ''' Start xy, end xy, other xy; pass excludeMid=True if other point is
            not between start and end '''
        if util.nearZero(sx-ex) and util.nearZero(sy-ey):
            assert False, 'Start and end points are the same'
        if util.nearZero(sx-mx) and util.nearZero(sy-my):
            assert False, 'Start and mid points are the same'
        if util.nearZero(mx-ex) and util.nearZero(my-ey):
            assert False, 'Mid and end points are the same'
        if cls._pointsInlineWithOrigin(sx-mx, sy-my, ex-mx, ey-my):
            shape = ELine(sx, sy, ex, ey)
        else:
            shape = Arc.fromPoints(sx, sy, ex, ey, mx, my,
                                   excludeMid=excludeMid)
        return cls(shape, segment=segment, **kwargs)
    def toDrawables(self, elements, hwidth=None, transform=None, **kwargs):
        if hwidth is not None:
            try:
                hwidth1, hwidth2 = hwidth
            except TypeError:
                hwidth = float(hwidth)
                hwidth1, hwidth2 = hwidth/2, -hwidth/2
            if self.segment:
                edges = []
                edges.append(self.makeOffset(hwidth1))
                edges.append(self.makeCap(self.startPoint()))
                edges.append(self.makeOffset(hwidth2))
                edges.append(self.makeCap(self.endPoint()))
                poly = poincare.Polygon.fromEdges(edges, join=True)
                return poly.toDrawables(elements, transform=transform, **kwargs)
            else:
                edge1 = Hypercycle.fromHypercycleOffset(self, hwidth1).projShape
                edge2 = Hypercycle.fromHypercycleOffset(self, hwidth2).projShape
                edge2.reverse()
                path = elements.Path(**kwargs)
                if transform:
                    edge1 = transform.applyToShape(edge1)
                    edge2 = transform.applyToShape(edge2)
                edge1.drawToPath(path, includeM=True)
                edge2.drawToPath(path, includeM=False)
                path.Z()
                return (path,)
        else:
            shape = self.projShape
            if transform:
                shape = transform.applyToShape(shape)
            return shape.toDrawables(elements, **kwargs)
    def drawToPath(self, path, transform=None, **kwargs):
        shape = self.projShape
        if transform:
            shape = transform.applyToShape(shape)
        return shape.drawToPath(path, **kwargs)

