import math

from .. import util
from ..euclid import Circle as ECircle
from .util import radial_euclid_to_poincare, radial_poincare_to_euclid
from . import point


class Horocycle:
    def __init__(self, proj_shape, closest_point=None, surround_origin=None):
        if not isinstance(proj_shape, ECircle):
            raise ValueError('proj_shape must be a euclidean circle')
        cr = math.hypot(proj_shape.cx, proj_shape.cy)
        if not util.near_zero(proj_shape.r + cr - 1):
            raise ValueError('proj_shape must be tangent to the unit circle')
        self.proj_shape = proj_shape
        if closest_point is None:
            theta = math.atan2(proj_shape.cy, proj_shape.cx)
            epr = cr - proj_shape.r
            closest_point = point.Point.from_polar_euclid(epr, theta)
        if surround_origin is None:
            surround_origin = proj_shape.r > cr
        elif surround_origin != (proj_shape.r > cr):
            raise ValueError(
                    'proj_shape is not consistent with surround_origin')
        self.closest_point = closest_point
    @staticmethod
    def from_closest_point(pt, surround_origin=False, cw=True):
        epr = math.hypot(pt.x, pt.y)
        theta = pt.theta
        if surround_origin:
            epr = -epr
            theta += math.pi
        er = (1 - epr) / 2
        ecr = epr + er
        x = ecr * math.cos(theta)
        y = ecr * math.sin(theta)
        shape = ECircle(x, y, er, cw=cw)
        return Horocycle(
                shape, closest_point=pt, surround_origin=surround_origin)
    @classmethod
    def from_closest_point_h_polar(cls, hr, theta, cw=True):
        p = point.Point.from_h_polar(hr, theta)
        return cls.from_closest_point(p, surround_origin=hr<0, cw=cw)
    @classmethod
    def from_closest_point_e_polar(cls, er, theta, cw=True):
        p = point.Point.from_polar_euclid(er, theta)
        return cls.from_closest_point(p, surround_origin=er<0, cw=cw)
    def to_drawables(self, hwidth=None, transform=None, **kwargs):
        import drawsvg as draw
        if hwidth is None:
            shape = self.proj_shape
            if transform:
                shape = transform.apply_to_shape(shape)
            return shape.to_drawables(**kwargs)
        else:
            try:
                hwidth1, hwidth2 = hwidth
                if not self.proj_shape.cw:
                    hwidth1, hwidth2 = -hwidth2, -hwidth1
            except TypeError:
                hwidth = float(hwidth)
                hwidth1, hwidth2 = hwidth/2, -hwidth/2
            theta = self.closest_point.theta
            cr = math.hypot(self.proj_shape.cx, self.proj_shape.cy)
            epr = cr - self.proj_shape.r
            hpr = radial_euclid_to_poincare(epr)
            pr_inner = hpr - hwidth1
            pr_outer = hpr - hwidth2
            if pr_outer > pr_inner:
                pr_inner, pr_outer = pr_outer, pr_inner
            p_inner = point.Point.from_h_polar(pr_inner, theta)
            p_outer = point.Point.from_h_polar(pr_outer, theta)
            circ_inner = Horocycle.from_closest_point_h_polar(
                    pr_inner, theta, cw=True).proj_shape
            circ_outer = Horocycle.from_closest_point_h_polar(
                    pr_outer, theta, cw=False).proj_shape
            path = draw.Path(**kwargs)
            if transform:
                circ_inner = transform.apply_to_shape(circ_inner)
                circ_outer = transform.apply_to_shape(circ_outer)
            circ_inner.draw_to_path(path, include_m=True)
            circ_outer.draw_to_path(path, include_m=False, include_l=True)
            path.Z()
            return (path,)
