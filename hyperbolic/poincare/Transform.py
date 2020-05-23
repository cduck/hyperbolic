
import math, cmath
import numpy as np

from .. import util
from .shapes import Point, Ideal
from ..euclid.shapes import Circle, Arc, Line
from ..euclid import intersection


class Transform:
    def __init__(self, a,b,c,d,e=1,conj=False):
        self.abcd = a*e,b*e,c,d
        self.conj = conj
    def __repr__(self):
        return '{}({}, {}, {}, {}{})'.format(type(self).__name__,
                    *map(lambda z:complex(round(z.real,3),round(z.imag,3)),
                         self.abcd),
                    ', conj' if self.conj else '')
    def applyToTuple(self, point):
        z = complex(*point)
        if self.conj:
            z = z.conjugate()
        a,b,c,d = self.abcd
        numer = a*z + b
        denom = c*z + d
        if util.nearZero(abs(denom)):
            zt = numer * 1e5
        else:
            zt = numer / denom
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
    def applyToShape(self, shape):
        ''' Supports Euclidean Circle, Arc, and Line. '''
        if isinstance(shape, (Arc, Line)):
            closed = False
            p1 = shape.startPoint()
            p2 = shape.midpoint()
            p3 = shape.endPoint()
        elif isinstance(shape, Circle):
            closed = True
            p1 = shape.cx+shape.r, shape.cy
            p2 = shape.cx, shape.cy+shape.r
            p3 = shape.cx-shape.r, shape.cy
            if shape.cw:
                p1, p3 = p3, p1
        else:
            raise TypeError('Unsupported shape: {}'.format(shape))
        # Transform
        p1, p2, p3 = self.applyToList((p1, p2, p3))
        # Create shape
        try:
            # See if it is an arc or circle
            out = Arc.fromPoints(*p1, *p3, *p2)
            if closed:  # It's a circle
                out = Circle(out.cx, out.cy, out.r, cw=out.cw)
            return out
        except (intersection.InfiniteIntersections, np.linalg.LinAlgError):
            # It is a line
            return Line(*p1, *p3)
    def __call__(self, *points, verify=False):
        return self.applyToList(points, verify=verify)
    def inverted(self):
        a,b,c,d = self.abcd
        if self.conj:
            a,b,c,d = a.conjugate(), b.conjugate(), c.conjugate(), d.conjugate()
        return Transform(-d,b,c,-a,conj=self.conj)
    def conjugate(self):
        a, b, c, d = self.abcd
        return Transform(a.conjugate(), b.conjugate(),
                         c.conjugate(), d.conjugate(), conj=not self.conj)
    @staticmethod
    def identity():
        return Transform(1,0,0,1,1)
    @staticmethod
    def merge(*transfoms):
        a,b,c,d = 1,0,0,1
        conj = False
        for i, trans in enumerate(transfoms):
            a2,b2,c2,d2 = trans.abcd
            if trans.conj:
                a,b,c,d = a.conjugate(), b.conjugate(), c.conjugate(), d.conjugate()
                conj = not conj
            a,b,c,d = a*a2+c*b2, b*a2+d*b2, a*c2+c*d2, b*c2+d*d2
        return Transform(a,b,c,d,conj=conj)
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
    @staticmethod
    def mirror(p1=None, p2=(0,0)):
        if p1 is None:
            p1, p2 = p2, (1,0)
        transShift = Transform.shiftOrigin(p1, p2)
        return Transform.merge(transShift.conjugate(), transShift.inverted())

    @staticmethod
    def diskToHalf():
        return Transform(1j, -1, -1, 1j)
    @staticmethod
    def halfToDisk():
        return Transform.diskToHalf().inverted()
