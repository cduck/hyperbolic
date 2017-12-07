
import math, cmath

from .. import util
from .shapes import Point, Ideal


class Transform:
    def __init__(self, a,b,c,d,e=1):
        self.abcd = a*e,b*e,c,d
    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(type(self).__name__,
                    *map(lambda z:complex(round(z.real,3),round(z.imag,3)),
                         self.abcd))
    def applyToTuple(self, point):
        z = complex(*point)
        a,b,c,d = self.abcd
        zt = (a*z + b) / (c*z + d)
        return zt.real, zt.imag
    def applyToPoint(self, point):
        return Point(*self.applyToTuple(point))
    def applyToIdeal(self, point, verify=False):
        x, y = self.applyToTuple(point)
        if verify and not util.nearZero(math.hypot(x, y) - 1):
            raise ValueError('Invalid transform')
        return Ideal(math.atan2(y, x))
    def applyToList(self, points, verify=False):
        if len(points) > 0:
            if isinstance(points[0], Ideal):
                if verify:
                    def f(p): return self.applyToIdeal(p, verify=True)
                else:
                    f = self.applyToIdeal
            elif isinstance(points[0], Point):
                f = self.applyToPoint
            else:
                f = self.applyToTuple
        return [f(p) for p in points]
    def __call__(self, *points, verify=False):
        self.applyToList(points, verify=verify)
    def inverted(self):
        a,b,c,d = self.abcd
        return Transform(-d,b,c,-a)
    @staticmethod
    def identity():
        return Transform(1,0,0,1,1)
    @staticmethod
    def merge(*transfoms):
        a,b,c,d = 1,0,0,1
        for trans in transfoms:
            a2,b2,c2,d2 = trans.abcd
            a,b,c,d = a*a2+c*b2, b*a2+d*b2, a*c2+c*d2, b*c2+d*d2
        return Transform(a,b,c,d)
    @staticmethod
    def shiftOrigin(newOrigin, newX=None):
        z0 = complex(*newOrigin)
        a,b,c,d = 1,-z0,(-z0).conjugate(),1
        if newX is not None:
            z1 = complex(*newX)
            e = (c*z1 + d) / (a*z1 + b)
            e /= abs(e)
        else:
            e = 1
        return Transform(a,b,c,d,e)
    @classmethod
    def translation(cls, offset, rotation=None):
        return cls.shiftOrigin(offset, newX=rotation).inverted()
    @staticmethod
    def rotation(rad=None, deg=None, vec=None):
        assert (rad is None) + (deg is None) + (vec is None) == 2
        if vec is not None:
            z = complex(*vec)
            e = z / abs(z)
        else:
            if deg is not None:
                rad = math.radians(deg)
            e = cmath.rect(1, rad)
        return Transform(1,0,0,1,e)

