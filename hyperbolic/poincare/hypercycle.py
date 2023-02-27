import math

from .. import util
from ..euclid import (
    Circle as ECircle,
    Arc as EArc,
    Line as ELine,
    OriginLine,
    intersection,
)
from ..euclid.intersection import (
    InfiniteIntersections, SingleIntersection, NoIntersection
)
from . import point, line, polygon


class Hypercycle:
    def __init__(self, proj_shape, segment=False):
        assert isinstance(proj_shape, (ECircle, EArc, ELine, OriginLine))
        if segment and not isinstance(proj_shape, (EArc, ELine)):
            raise ValueError(
                    'Not enough information to determine segment endpoints')
        unit = ECircle(0,0,1)
        if segment:
            if isinstance(proj_shape, EArc):
                # TODO: Trim if arc extends outside unit circle
                pass
            elif isinstance(proj_shape, ELine):
                # TODO: Trim if arc extends outside unit circle
                pass
            else:
                raise ValueError('Unknown type')
        else:
            if isinstance(proj_shape, ECircle):
                x1, y1, x2, y2 = intersection.circle_circle(proj_shape, unit)
                if not proj_shape.cw:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                proj_shape = EArc.from_points_with_center(
                        x1, y1, x2, y2,
                        proj_shape.cx, proj_shape.cy, r=proj_shape.r,
                        cw=proj_shape.cw)
            elif isinstance(proj_shape, ELine):
                x1, y1, x2, y2 = intersection.circle_line(unit, proj_shape)
                # Keep direction of line the same
                orig_ang = math.atan2(
                        proj_shape.y2-proj_shape.y1,
                        proj_shape.x2-proj_shape.x1)
                new_ang = math.atan2(y2-y1, x2-x1)
                ang_diff = (new_ang - orig_ang) % (math.pi*2)
                if math.pi/2 < ang_diff < 3*math.pi/2:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                proj_shape = ELine(x1, y1, x2, y2)
            else:
                raise ValueError('Unknown type')
        self.proj_shape = proj_shape
        self.segment = segment
    def start_point(self):
        return point.Point(*self.proj_shape.start_point())
    def end_point(self):
        return point.Point(*self.proj_shape.end_point())
    def intersections_with_hcycle(self, hcycle2):
        '''Return the list of intersection points within the hyperbolic space.

        Assumes the hypercycles are infinite length, not segments.
        '''
        x2, y2 = 1, 1  # Default, invalid
        try:
            if isinstance(self.proj_shape, ECircle):
                if isinstance(hcycle2.proj_shape, ECircle):
                    x1, y1, x2, y2 = intersection.circle_circle(
                            self.proj_shape, hcycle2.proj_shape)
                else:
                    x1, y1, x2, y2 = intersection.circle_line(
                            self.proj_shape, hcycle2.proj_shape)
            else:
                if isinstance(hcycle2.proj_shape, ECircle):
                    x1, y1, x2, y2 = intersection.circle_line(
                            hcycle2.proj_shape, self.proj_shape)
                else:
                    x1, y1 = intersection.line_line(
                            self.proj_shape, hcycle2.proj_shape)
        except InfiniteIntersections as e:
            raise e from None
        except SingleIntersection as e:
            x1, y1 = e.args
        except NoIntersection:
            x1, y1 = 1, 1  # Invalid
        pts = []
        try:
            pts.append(point.Point.from_euclid(x1, y1))
        except ValueError: pass
        try:
            pts.append(point.Point.from_euclid(x2, y2))
        except ValueError: pass
        return pts
    def is_point_on_segment(self, x, y):
        return self.proj_shape.is_point_on_segment(x, y)
    def segment_intersections_with_hcycle(self, hcycle2):
        '''Return the list of intersections points within the hyperbolic space.

        Only returns points actually on the segments, not their infinite
        extension.
        '''
        valid = [
            p
            for p in self.intersections_with_hcycle(hcycle2)
            if (self.is_point_on_segment(*p)
                and hcycle2.is_point_on_segment(*p))
        ]
        return valid
    def trimmed(self, x1, y1, x2, y2, **kwargs):
        '''Return a segment of this hypercycle going from Poincare disk
        coordinates x1,y1 to x2,y2.

        Assumes x1,y1 and x2,y2 are on the hypercycle.
        '''
        trimmed_shape = self.proj_shape.trimmed(x1, y1, x2, y2, **kwargs)
        return type(self)(trimmed_shape, segment=True)
    def midpoint_euclid(self):
        x, y = self.proj_shape.midpoint()
        return point.Point(x, y)
    def reverse(self):
        self.proj_shape.reverse()
    def reversed(self):
        new_shape = self.proj_shape.reversed()
        new_obj = type(self)(new_shape, segment=True)
        new_obj.segment = self.segment
        return new_obj
    def make_perpendicular(self, x, y):
        if util.near_zero(x) and util.near_zero(y):
            radical1 = None
        else:
            radical1 = ELine.radical_axis(ECircle(0,0,1), (x,y))
        radical2 = ELine.radical_axis(self.proj_shape, (x,y))
        if radical1 is None or radical1.parallel_to(radical2):
            # Infinite radius circle
            shape = radical2.make_perpendicular(x,y)
            # Ensure correct direction
            if isinstance(self.proj_shape, ELine):
                if shape.antiparallel_to(self.proj_shape):
                    shape.reverse()
            else:  # proj_shape is an ECircle
                radial = ELine.from_points(
                        x, y, self.proj_shape.cx, self.proj_shape.cy)
                if radial.antiparallel_to(shape) ^ (not self.proj_shape.cw):
                    shape.reverse()
            return line.Line(shape, segment=False)
        else:
            cx, cy = intersection.line_line(radical1, radical2)
            r = math.hypot(cy-y, cx-x)
            shape = ECircle(cx, cy, r)
            # Ensure correct direction
            shape.cw = True
            if isinstance(self.proj_shape, ELine):
                x1, y1, x2, y2 = intersection.line_circle(
                        self.proj_shape, shape)
            else:  # proj_shape is an ECircle
                x1, y1, x2, y2 = intersection.circle_circle(
                        self.proj_shape, shape)
                shape.cw = shape.cw ^ (not self.proj_shape.cw)
            if math.hypot(x1, y1) > math.hypot(x2, y2):
                shape.cw = not shape.cw
            return line.Line(shape, segment=False)
    def make_cap(self, pt):
        if pt.is_ideal():
            return pt
        else:
            return self.make_perpendicular(*pt)
    def make_offset(self, offset):
        return Hypercycle.from_hypercycle_offset(self, offset)
    @classmethod
    def from_hypercycle_offset(cls, hcycle, offset, unit=ECircle(0,0,1)):
        dh = -offset  # Account for clockwise rotating from +x to +y
        if isinstance(hcycle.proj_shape, ECircle):
            # May throw if bad geometry
            x1, y1, x2, y2 = intersection.circle_circle(hcycle.proj_shape, unit)
            cx, cy = hcycle.proj_shape.cx, hcycle.proj_shape.cy
            r, cw = hcycle.proj_shape.r, hcycle.proj_shape.cw
            if not cw:
                x1, y1, x2, y2 = x2, y2, x1, y1
            rc = math.hypot(cx, cy)
            de_mid = rc - r
            dh_mid = 2 * math.atanh(de_mid)
            sign = 1 if cw else -1
            t = math.tanh((dh_mid + sign*dh)/2)
            x_off, y_off = t * cx / rc, t * cy / rc
        else:
            # May throw if bad geometry
            x1, y1, x2, y2 = intersection.line_circle(hcycle.proj_shape, unit)
            line_ang = math.atan2(y2-y1, x2-x1)
            mx, my = (x1+x2)/2, (y1+y2)/2  # Midpoint
            if util.near_zero(mx) and util.near_zero(my):
                ang = math.atan2(y2-y1, x2-x1) + math.pi/2
            else:
                ang = math.atan2(my, mx)
            # Test if the line goes clockwise around the origin
            cw = (ang - line_ang) % (math.pi*2) >= math.pi
            rm = math.hypot(mx, my)
            de_mid = rm
            dh_mid = 2 * math.atanh(de_mid)
            sign = -1 if cw else 1
            t = math.tanh((dh_mid + sign*dh)/2)
            x_off, y_off = t * math.cos(ang), t * math.sin(ang)
        return cls.from_points(
                x1, y1, x2, y2, x_off, y_off, segment=False, exclude_mid=False)
    @staticmethod
    def _pointsInlineWithOrigin(x1, y1, x2, y2):
        if ((util.near_zero(x1) and util.near_zero(x2)) or
            (util.near_zero(y1) and util.near_zero(y2)) or
            (util.near_zero(x1) and util.near_zero(y1)) or
            (util.near_zero(x2) and util.near_zero(y2))):
            return True
        elif ((util.near_zero(x1) or util.near_zero(x2)) and
              (util.near_zero(y1) or util.near_zero(y2))):
            return False
        elif util.near_zero(x1) or util.near_zero(x2):
            return util.near_zero(x1/y1 - x2/y2)
        else:
            return util.near_zero(y1/x1 - y2/x2)
    @classmethod
    def from_points(cls, sx, sy, ex, ey, mx, my, segment=False,
                    exclude_mid=False, **kwargs):
        '''Return a Hypercycle through the three Poincare disk points.

        Arguments are start xy, end xy, and other xy.  Pass exclude_mid=True if
        the third point is not between start and end.
        '''
        if util.near_zero(sx-ex) and util.near_zero(sy-ey):
            assert False, 'Start and end points are the same'
        if util.near_zero(sx-mx) and util.near_zero(sy-my):
            assert False, 'Start and mid points are the same'
        if util.near_zero(mx-ex) and util.near_zero(my-ey):
            assert False, 'Mid and end points are the same'
        if cls._pointsInlineWithOrigin(sx-mx, sy-my, ex-mx, ey-my):
            shape = ELine(sx, sy, ex, ey)
        else:
            shape = EArc.from_points(
                    sx, sy, ex, ey, mx, my,
                    exclude_mid=exclude_mid)
        return cls(shape, segment=segment, **kwargs)
    def to_drawables(self, hwidth=None, transform=None, **kwargs):
        import drawsvg as draw
        if hwidth is not None:
            try:
                hwidth1, hwidth2 = hwidth
            except TypeError:
                hwidth = float(hwidth)
                hwidth1, hwidth2 = hwidth/2, -hwidth/2
            if self.segment:
                edges = []
                edges.append(self.make_offset(hwidth1))
                edges.append(self.make_cap(self.start_point()))
                edges.append(self.make_offset(hwidth2))
                edges.append(self.make_cap(self.end_point()))
                poly = polygon.Polygon.from_edges(edges, join=True)
                return poly.to_drawables(transform=transform, **kwargs)
            else:
                edge1 = Hypercycle.from_hypercycle_offset(
                        self, hwidth1).proj_shape
                edge2 = Hypercycle.from_hypercycle_offset(
                        self, hwidth2).proj_shape
                edge2.reverse()
                path = draw.Path(**kwargs)
                if transform:
                    edge1 = transform.apply_to_shape(edge1)
                    edge2 = transform.apply_to_shape(edge2)
                edge1.draw_to_path(path, include_m=True)
                edge2.draw_to_path(path, include_m=False)
                path.Z()
                return (path,)
        else:
            shape = self.proj_shape
            if transform:
                shape = transform.apply_to_shape(shape)
            return shape.to_drawables(**kwargs)
    def draw_to_path(self, path, transform=None, **kwargs):
        shape = self.proj_shape
        if transform:
            shape = transform.apply_to_shape(shape)
        return shape.draw_to_path(path, **kwargs)
