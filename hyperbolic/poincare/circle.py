import math

from ..euclid import Circle as ECircle
from . import util, point


class Circle:
    def __init__(self, proj_shape, center=None, r=None):
        if not isinstance(proj_shape, ECircle):
            raise ValueError('proj_shape must be a euclidean circle')
        self.proj_shape = proj_shape
        if r is None or center is None:
            de0 = math.hypot(proj_shape.cx, proj_shape.cy)
            de1 = de0 - proj_shape.r
            de2 = de0 + proj_shape.r
            dh1 = util.radial_euclid_to_poincare(de1)
            dh2 = util.radial_euclid_to_poincare(de2)
        if r is None:
            r = (dh2 - dh1) / 2
        if center is None:
            cr = (dh2 + dh1) / 2
            theta = math.atan2(proj_shape.cy, proj_shape.cx)
            center = point.Point.from_h_polar(cr, theta)
        self.r = r
        self.center = center
    @staticmethod
    def from_center_radius(pt, radius, cw=True):
        '''Create a hyperbolic circle from a hyperbolic point and length within
        the hyperbolic plane.
        '''
        if radius < 0:
            radius = -radius
            cw = not cw
        cr = pt.hr
        dh1 = cr - radius
        dh2 = cr + radius
        de1 = util.radial_poincare_to_euclid(dh1)
        de2 = util.radial_poincare_to_euclid(dh2)
        er = (de2 - de1) / 2
        ecr = (de2 + de1) / 2
        x = ecr * math.cos(pt.theta)
        y = ecr * math.sin(pt.theta)
        shape = ECircle(x, y, er, cw=cw)
        return Circle(shape, center=pt, r=radius)
    def to_drawables(self, hwidth=None, positive_radius=False,
                    transform=None, **kwargs):
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
            r_inner = self.r - hwidth1
            r_outer = self.r - hwidth2
            if r_outer < r_inner:
                r_inner, r_outer = r_outer, r_inner
            if positive_radius:
                if r_inner <= 0 and r_outer <= 0:
                    x, y = self.proj_shape.cx, self.proj_shape.cy
                    if transform:
                        x, y = transform.apply_to_tuple((x, y))
                    return ECircle(x, y, 0).to_drawables(**kwargs)
                if r_inner <= 0:
                    circ_outer = Circle.from_center_radius(
                            self.center, r_outer).proj_shape
                    if transform:
                        circ_outer = transform.apply_to_shape(circ_outer)
                    return circ_outer.to_drawables(**kwargs)
            circ_inner = Circle.from_center_radius(
                    self.center, r_inner, cw=True).proj_shape
            circ_outer = Circle.from_center_radius(
                    self.center, r_outer, cw=False).proj_shape
            path = draw.Path(**kwargs)
            if transform:
                circ_inner = transform.apply_to_shape(circ_inner)
                circ_outer = transform.apply_to_shape(circ_outer)
            circ_inner.draw_to_path(path, include_m=True)
            circ_outer.draw_to_path(path, include_m=False, include_l=True)
            path.Z()
            return (path,)
