import math

from .. import util
from . import circle


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(type(self).__name__,
                    round(self.x1, 3), round(self.y1, 3),
                    round(self.x2, 3), round(self.y2, 3))
    def reverse(self):
        self.x1, self.y1, self.x2, self.y2 = self.x2, self.y2, self.x1, self.y1
    def reversed(self):
        return Line(self.x2, self.y2, self.x1, self.y1)
    def atan2(self):
        return math.atan2(self.y2-self.y1, self.x2-self.x1)
    def length(self):
        return ((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2) ** 0.5
    def parallel_to(self, line2):
        return util.near_zero(math.pi/2 -
                (self.atan2() - line2.atan2() + math.pi/2) % math.pi)
    def parallel_dir_to(self, line2):
        return util.near_zero(math.pi -
                (self.atan2() - line2.atan2() + math.pi) % (math.pi*2))
    def antiparallel_to(self, line2):
        return util.near_zero(math.pi -
                (self.atan2() - line2.atan2()) % (math.pi*2))
    def start_point(self):
        return self.x1, self.y1
    def end_point(self):
        return self.x2, self.y2
    def trimmed(self, x1, y1, x2, y2, **kwargs):
        '''Return a new line with these endpoints, assuming that the given
        points are on this line.
        '''
        return Line(x1, y1, x2, y2)
    def midpoint(self):
        return (self.x1 + self.x2)/2, (self.y1 + self.y2)/2
    def make_perpendicular(self, x, y, length=1):
        '''Return a line through (x,y) rotated 90deg clockwise from self.'''
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
        swap = util.near_zero(x-x1) and util.near_zero(y-y1)
        if swap:
            x1, y1, x2, y2 = x2, y2, x1, y1
        line_ang = math.atan2(y2-y1, x2-x1)
        d = math.hypot(x-x1, y-y1)
        ang = math.atan2(y-y1, x-x1)
        d_along = d * math.cos(ang - line_ang)
        px1 = d_along * math.cos(line_ang)
        py1 = d_along * math.sin(line_ang)
        d2 = math.hypot(d_along, length)
        ang2 = math.atan2(length, d_along) + line_ang
        px2 = d2 * math.cos(ang2)
        py2 = d2 * math.sin(ang2)
        if swap:
            px2 = 2*px1 - px2
            py2 = 2*py1 - py2
        return Line(x1+px1, y1+py1, x1+px2, y1+py2)
    def make_parallel(self, x, y, length=1):
        perp = self.make_perpendicular(x, y)
        return perp.make_perpendicular(x, y, length)
    def is_point_on_segment(self, x, y):
        '''Tests if the point is between the segment endpoints, assuming it is
        already on the infinite-length line.
        '''
        # Dot product of vectors start_point->(x,y) and start_point->end_point
        k1 = ((x - self.x1) * (self.x2 - self.x1)
                + (y - self.y1) * (self.y2 - self.y1))
        # Dot product of vectors end_point->(x,y) and endpoint->start_point
        k2 = ((x - self.x2) * (self.x1 - self.x2)
                + (y - self.y2) * (self.y1 - self.y2))
        return k1 >= 0 and k2 >= 0
    @staticmethod
    def from_points(x1, y1, x2, y2, **kwargs):
        return Line(x1, y1, x2, y2, **kwargs)
    @staticmethod
    def radical_axis(circ1, circ2):
        '''Return the radical axis for two circles (or points).

        If one input is a line, the output is this line.
        '''
        if not isinstance(circ1, (circle.Circle, Line)):
            circ1 = circle.Circle(*circ1, 0)
        if not isinstance(circ2, (circle.Circle, Line)):
            circ2 = circle.Circle(*circ2, 0)
        if isinstance(circ1, Line) and isinstance(circ2, Line):
            raise ValueError('No radical axis exists for two lines')
        elif isinstance(circ1, Line):
            # TODO: Possibly correct direction to be consistent
            return circ1
        elif isinstance(circ2, Line):
            # TODO: Possibly correct direction to be consistent
            return circ2
        else:
            cx1, cy1, r1 = circ1.cx, circ1.cy, circ1.r
            cx2, cy2, r2 = circ2.cx, circ2.cy, circ2.r
            d = math.hypot(cx2-cx1, cy2-cy1)
            if util.near_zero(d):
                raise ValueError('Circles are concentric')
            d1 = (d**2 + r1**2 - r2**2) / (2*d)
            ratio = d1 / d
            mx = cx1 + ratio * (cx2 - cx1)
            my = cy1 + ratio * (cy2 - cy1)
            return Line(cx1, cy1, cx2, cy2).make_perpendicular(mx, my, length=1)
    def to_drawables(self, **kwargs):
        import drawsvg as draw
        return (draw.Line(self.x1, self.y1, self.x2, self.y2, **kwargs),)
    def draw_to_path(self, path, include_m=True, include_l=False):
        if include_l:
            path.L(self.x1, self.y1)
        elif include_m:
            path.M(self.x1, self.y1)
        path.L(self.x2, self.y2)
