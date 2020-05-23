
import math

from ..euclid.shapes import Circle as ECircle
from . import util
from .shapes import Point, Ideal


class Circle:
    def __init__(self, projShape, center=None, r=None):
        if not isinstance(projShape, ECircle):
            raise ValueError('projShape must be a euclidean circle')
        self.projShape = projShape
        if r is None or center is None:
            de0 = math.hypot(projShape.cx, projShape.cy)
            de1 = de0 - projShape.r
            de2 = de0 + projShape.r
            dh1 = util.radialEuclidToPoincare(de1)
            dh2 = util.radialEuclidToPoincare(de2)
        if r is None:
            r = (dh2 - dh1) / 2
        if center is None:
            cr = (dh2 + dh1) / 2
            theta = math.atan2(projShape.cy, projShape.cy)
            center = Point.fromHPolar(cr, theta)
        self.r = r
        self.center = center
    @staticmethod
    def fromCenterRadius(point, radius, cw=False):
        ''' Hyperbolic point, length within the hyperbolic plane '''
        if radius < 0:
            radius = -radius
            cw = not cw
        cr = point.hr
        dh1 = cr - radius
        dh2 = cr + radius
        de1 = util.radialPoincareToEuclid(dh1)
        de2 = util.radialPoincareToEuclid(dh2)
        er = (de2 - de1) / 2
        ecr = (de2 + de1) / 2
        x = ecr * math.cos(point.theta)
        y = ecr * math.sin(point.theta)
        shape = ECircle(x, y, er, cw=cw)
        return Circle(shape, center=point, r=radius)
    def toDrawables(self, elements, hwidth=None, positiveRadius=False,
                    transform=None, **kwargs):
        if hwidth is None:
            shape = self.projShape
            if transform:
                shape = transform.applyToShape(shape)
            return shape.toDrawables(elements, **kwargs)
        else:
            try:
                hwidth1, hwidth2 = hwidth
                if self.projShape.cw:
                    hwidth1, hwidth2 = -hwidth2, -hwidth1
            except TypeError:
                hwidth = float(hwidth)
                hwidth1, hwidth2 = hwidth/2, -hwidth/2
            rInner = self.r - hwidth1
            rOuter = self.r - hwidth2
            if rOuter < rInner:
                rInner, rOuter = rOuter, rInner
            if positiveRadius:
                if rInner <= 0 and rOuter <= 0:
                    x, y = self.projShape.cx, self.projShape.cy
                    if transform:
                        x, y = transform.applyToTuple((x, y))
                    return ECircle(x, y, 0).toDrawables(elements, **kwargs)
                if rInner <= 0:
                    circOuter = Circle.fromCenterRadius(self.center, rOuter).projShape
                    if transform:
                        circOuter = transform.applyToShape(circOuter)
                    return circOuter.toDrawables(elements, **kwargs)
            circInner = Circle.fromCenterRadius(self.center, rInner, cw=False).projShape
            circOuter = Circle.fromCenterRadius(self.center, rOuter, cw=True).projShape
            path = elements.Path(**kwargs)
            if transform:
                circInner = transform.applyToShape(circInner)
                circOuter = transform.applyToShape(circOuter)
            circInner.drawToPath(path, includeM=True)
            circOuter.drawToPath(path, includeM=False, includeL=True)
            path.Z()
            return (path,)

