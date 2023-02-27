import math

from .. import util, poincare
from ..euclid import Circle as ECircle
from . import circle


class Point:
    def __init__(self, x, y, hr=None, theta=None):
        self.x = x
        self.y = y
        # Hyperbolic polar coordinates
        if theta is None:
            theta = math.atan2(y, x)
        if hr is None:
            r = math.hypot(x, y)
            if self.is_ideal():
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
    def is_ideal(self):
        return util.near_zero(math.hypot(self.x, self.y) - 1)
    def polar_angle_to(self, p2, origin=None):
        if origin is None:
            return p2.theta - self.theta
        else:
            assert False, 'TODO'
    def distance_to(self, p2):
        r1, t1 = self.hr, self.theta
        r2, t2 = p2.hr, p2.theta
        d = math.acosh(math.cosh(r1)*math.cosh(r2)
                       - math.sinh(r1)*math.sinh(r2)*math.cos(t2-t1))
        return d
    def midpoint_with(self, p2, frac=0.5):
        d = self.distance_to(p2)
        p_mid = Point.from_h_polar(d*frac, 0)
        return poincare.Transform.translation(self, p2).apply_to_point(p_mid)
    @staticmethod
    def from_euclid(x, y):
        r = math.hypot(x, y)
        if util.near_zero(r - 1.0):
            return Ideal(math.atan2(y, x))
        elif r < 1.0:
            return Point(x, y)
        else:
            raise ValueError(
                    'Euclidean coordinates are outside the unit circle')
    @staticmethod
    def from_polar_euclid(r, rad=None, deg=None):
        assert (rad is None) != (deg is None)
        if rad is None: rad = math.radians(deg)
        if util.near_zero(r - 1.0):
            return Ideal(rad)
        elif r < 1.0:
            return Point(r*math.cos(rad), r*math.sin(rad))
        else:
            raise ValueError(
                    'Euclidean coordinates are outside the unit circle')
    @staticmethod
    def from_h_polar(hr, theta=None, deg=None):
        assert (theta is None) != (deg is None)
        if theta is None: theta = math.radians(deg)
        r = math.tanh(hr/2)
        x, y = r*math.cos(theta), r*math.sin(theta)
        return Point(x, y, hr=hr, theta=theta)
    def __eq__(self, other):
        return (util.near_zero(self.x - other.x)
                and util.near_zero(self.y - other.y))
    def __repr__(self):
        return '{}({}, {})'.format(type(self).__name__,
                round(self.x, 3), round(self.y, 3))
    def to_drawables(self, radius=0, hradius=None, transform=None, **kwargs):
        if hradius is not None and not isinstance(self, Ideal):
            shape = circle.Circle.from_center_radius(
                    Point(self.x, self.y), hradius)
            return shape.to_drawables(transform=transform, **kwargs)
        else:
            x, y = self.x, self.y
            if transform:
                x, y = transform.apply_to_tuple((x, y))
            return ECircle(x, y, radius).to_drawables(**kwargs)


class Ideal(Point):
    def __init__(self, theta):
        self.theta = theta % (2*math.pi)
    @property
    def x(self):
        return math.cos(self.theta)
    @property
    def y(self):
        return math.sin(self.theta)
    def is_ideal(self):
        return True
    @classmethod
    def from_degree(cls, deg):
        return cls(math.radians(deg))
    @classmethod
    def from_radian(cls, rad):
        return cls(rad)
