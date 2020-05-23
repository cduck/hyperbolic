
import math

from .. import util
from ..euclid.shapes import Circle as ECircle
from .util import radialEuclidToPoincare, radialPoincareToEuclid
from .shapes import Point, Ideal


class Horocycle:
    def __init__(self, projShape, closestPoint=None, surroundOrigin=None):
        if not isinstance(projShape, ECircle):
            raise ValueError('projShape must be a euclidean circle')
        cr = math.hypot(projShape.cx, projShape.cy)
        if not util.nearZero(projShape.r + cr - 1):
            raise ValueError('projShape must be tangent to the unit circle')
        self.projShape = projShape
        if closestPoint is None:
            theta = math.atan2(projShape.cy, projShape.cx)
            epr = cr - projShape.r
            closestPoint = Point.fromPolarEuclid(epr, theta)
        if surroundOrigin is None:
            surroundOrigin = projShape.r > cr
        elif surroundOrigin != (projShape.r > cr):
            raise ValueError('projShape is not consistent with surroundOrigin')
        self.closestPoint = closestPoint
    @staticmethod
    def fromClosestPoint(point, surroundOrigin=False, cw=False):
        epr = math.hypot(point.x, point.y)
        theta = point.theta
        if surroundOrigin:
            epr = -epr
            theta += math.pi
        er = (1 - epr) / 2
        ecr = epr + er
        x = ecr * math.cos(theta)
        y = ecr * math.sin(theta)
        shape = ECircle(x, y, er, cw=cw)
        return Horocycle(shape, closestPoint=point, surroundOrigin=surroundOrigin)
    @classmethod
    def fromClosestPointHPolar(cls, hr, theta, cw=False):
        p = Point.fromHPolar(hr, theta)
        return cls.fromClosestPoint(p, surroundOrigin=hr<0, cw=cw)
    @classmethod
    def fromClosestPointEPolar(cls, er, theta, cw=False):
        p = Point.fromPolarEuclid(er, theta)
        return cls.fromClosestPoint(p, surroundOrigin=er<0, cw=cw)
    def toDrawables(self, elements, hwidth=None, transform=None, **kwargs):
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
            theta = self.closestPoint.theta
            cr = math.hypot(self.projShape.cx, self.projShape.cy)
            epr = cr - self.projShape.r
            hpr = radialEuclidToPoincare(epr)
            prInner = hpr - hwidth1
            prOuter = hpr - hwidth2
            if prOuter > prInner:
                prInner, prOuter = prOuter, prInner
            pInner = Point.fromHPolar(prInner, theta)
            pOuter = Point.fromHPolar(prOuter, theta)
            circInner = Horocycle.fromClosestPointHPolar(prInner, theta, cw=False).projShape
            circOuter = Horocycle.fromClosestPointHPolar(prOuter, theta, cw=True).projShape
            path = elements.Path(**kwargs)
            if transform:
                circInner = transform.applyToShape(circInner)
                circOuter = transform.applyToShape(circOuter)
            circInner.drawToPath(path, includeM=True)
            circOuter.drawToPath(path, includeM=False, includeL=True)
            path.Z()
            return (path,)
