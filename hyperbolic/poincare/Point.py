
import math

from .. import util
from ..euclid.shapes import Circle as ECircle
from .. import poincare as module
from . import shapes


class Point:
    def __init__(self, x, y, hr=None, theta=None):
        self.x = x
        self.y = y
        # Hyperbolic polar coordinates
        if theta is None:
            theta = math.atan2(y, x)
        if hr is None:
            r = math.hypot(x, y)
            if self.isIdeal():
                hr = float('inf')
            else:
                hr = 2 * math.atanh(r)
        self.theta = theta
        self.hr = hr
    def __iter__(self):
        return iter((self.x, self.y))
    def __getitem__(self, i):
        return (self.x, self.y)[i]
    def __len__(self):
        return 2
    def isIdeal(self):
        return util.nearZero(math.hypot(self.x, self.y) - 1)
    def polarAngleTo(self, p2, origin=None):
        if origin is None:
            return p2.theta - self.theta
        else:
            assert False, 'TODO'
    def distanceTo(self, p2):
        r1, t1 = self.hr, self.theta
        r2, t2 = p2.hr, p2.theta
        d = math.acosh(math.cosh(r1)*math.cosh(r2)
                       - math.sinh(r1)*math.sinh(r2)*math.cos(t2-t1))
        return d
    def midpointWith(self, p2, frac=0.5):
        d = self.distanceTo(p2)
        pMid = Point.fromHPolar(d*frac, 0)
        return module.Transform.translation(self, p2).applyToPoint(pMid)
    @staticmethod
    def fromEuclid(x, y):
        r = math.hypot(x, y)
        if util.nearZero(r - 1.0):
            return Ideal(math.atan2(y, x))
        elif r < 1.0:
            return Point(x, y)
        else:
            raise ValueError('Euclidean coordinates are outside the unit circle')
    @staticmethod
    def fromPolarEuclid(r, rad=None, deg=None):
        assert (rad is None) != (deg is None)
        if rad is None: rad = math.radians(deg)
        if util.nearZero(r - 1.0):
            return Ideal(rad)
        elif r < 1.0:
            return Point(r*math.cos(rad), r*math.sin(rad))
        else:
            raise ValueError('Euclidean coordinates are outside the unit circle')
    @staticmethod
    def fromHPolar(hr, theta=None, deg=None):
        assert (theta is None) != (deg is None)
        if theta is None: theta = math.radians(deg)
        r = math.tanh(hr/2)
        x, y = r*math.cos(theta), r*math.sin(theta)
        return Point(x, y, hr=hr, theta=theta)
    def __eq__(self, other):
        return util.nearZero(self.x - other.x) and util.nearZero(self.y - other.y)
    def __repr__(self):
        return '{}({}, {})'.format(type(self).__name__,
                    round(self.x, 3), round(self.y, 3))
    def toDrawables(self, elements, radius=0, hradius=None, transform=None,
                    **kwargs):
        if hradius is not None and not isinstance(self, Ideal):
            shape = shapes.Circle.fromCenterRadius(Point(self.x, self.y), hradius)
            return shape.toDrawables(elements, transform=transform, **kwargs)
        else:
            x, y = self.x, self.y
            if transform:
                x, y = transform.applyToTuple((x, y))
            return ECircle(x, y, radius).toDrawables(elements, **kwargs)

class Ideal(Point):
    def __init__(self, theta):
        self.theta = theta % (2*math.pi)
    @property
    def x(self):
        return math.cos(self.theta)
    @property
    def y(self):
        return math.sin(self.theta)
    def isIdeal(self):
        return True
    @classmethod
    def fromDegree(cls, deg):
        return cls(math.radians(deg))
    @classmethod
    def fromRadian(cls, rad):
        return cls(rad)

