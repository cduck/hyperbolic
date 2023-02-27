import math

import numpy.linalg

from .. import util
from .circle import Circle
from .line import Line


class InfiniteIntersections(Exception): pass
class SingleIntersection(Exception): pass
class NoIntersection(Exception): pass
class InsufficientPrecision(Exception): pass

def circle_circle(circ1, circ2):
    '''Return two points where clockwise around circ1 from (x1,y1) to (x2,y2) is
    the arc of circ1 contained in circ2.

    Throw InfiniteIntersections or SingleIntersection with useful args.
    Can also throw NoIntersection.
    '''
    swap = circ1.r > circ2.r
    if swap:  # Ensure that circ1 is smaller
        circ1, circ2 = circ2, circ1
    r1, cx1, cy1 = circ1.r, circ1.cx, circ1.cy
    r2, cx2, cy2 = circ2.r, circ2.cx, circ2.cy
    # Center-to-center distance
    dx, dy = cx1 - cx2, cy1 - cy2
    d = math.sqrt(dx**2 + dy**2)
    # Check if circles are the same
    if util.near_zero(d) and util.near_zero(r1-r2):
        raise InfiniteIntersections(circ2 if swap else circ1)
    # Check if circles are concentric
    if util.near_zero(d):
        raise NoIntersection()
    # Check for single intersection
    if util.near_zero(r1+r2-d) or util.near_zero(r2-r1-d):
        x = (dx / d) * r2 + cx2
        y = (dy / d) * r2 + cy2
        raise SingleIntersection(x, y)
    # Check if small circle fully contained or separate
    if d+r1 < r2 or r1+r2 < d:
        raise NoIntersection()
    # Calculate two intersections
    t = (r1**2 - d**2 - r2**2) / (-2 * d * r2)  # Law of cosines
    if t > 1: t = 1
    elif t < -1: t = -1
    diff_rad = math.acos(t)
    center_rad = math.atan2(dy, dx)
    ix1 = cx2 + r2 * math.cos(center_rad-diff_rad)
    iy1 = cy2 + r2 * math.sin(center_rad-diff_rad)
    ix2 = cx2 + r2 * math.cos(center_rad+diff_rad)
    iy2 = cy2 + r2 * math.sin(center_rad+diff_rad)
    if swap:
        return ix1, iy1, ix2, iy2
    else:
        return ix2, iy2, ix1, iy1

def circle_line(circ, line):
    '''Return the two intersection points.

    Throws SingleIntersection with useful args.  Can throw NoIntersection or
    InsufficientPrecision.
    '''
    ldx, ldy = line.x2-line.x1, line.y2-line.y1
    if util.near_zero(ldx) and util.near_zero(ldy):
        raise InsufficientPrecision()
    cx, cy, r = circ.cx, circ.cy, circ.r
    x1, y1, x2, y2 = line.x1-cx, line.y1-cy, line.x2-cx, line.y2-cy
    # Calculate angles and minimum distance from circle center to line
    line_rad = math.atan2(ldy, ldx)
    p_rad = math.atan2(y1, x1)
    p_mag = math.sqrt(x1**2 + y1**2)
    d = p_mag * math.sin(p_rad - line_rad)
    negate = d < 0
    if negate: d = -d
    # Check for single intersection (tangent line)
    if util.near_zero(d - r):
        ix, iy = -r*math.sin(line_rad), r*math.cos(line_rad)
        if negate:
            ix, iy = -ix, -iy
        raise SingleIntersection(cx+ix, cy+iy)
    # Check if line is separate from circle
    if d > r:
        raise NoIntersection()
    # Calculate two intersections
    diff_rad = math.acos(d / r)
    ix1, iy1 = -r*math.sin(line_rad-diff_rad), r*math.cos(line_rad-diff_rad)
    ix2, iy2 = -r*math.sin(line_rad+diff_rad), r*math.cos(line_rad+diff_rad)
    if negate:
        ix1, iy1, ix2, iy2 = -ix1, -iy1, -ix2, -iy2
    return cx+ix1, cy+iy1, cx+ix2, cy+iy2

def line_circle(line, circ):
    '''Return two points on line where a line from (x1,y1) to (x2,y2) would
    be parallel, not antiparallel, to line.

    Can throw NoIntersection or InsufficientPrecision.
    '''
    x1, y1, x2, y2 = circle_line(circ, line)
    l = Line(x1, y1, x2, y2)
    if l.antiparallel_to(line):
        l.reverse()
    return l.x1, l.y1, l.x2, l.y2

def line_line(line1, line2):
    '''Return one intersection point.

    Throw InfiniteIntersections if the lines are approximately the same.
    Otherwise throw NoIntersection if the lines are approximately parallel.
    '''
    rad1 = math.atan2(line1.y2-line1.y1, line1.x2-line1.x1)
    rad2 = math.atan2(line2.y2-line2.y1, line2.x2-line2.x1)
    if util.near_zero((rad1-rad2) % math.pi):
        rel_rad1 = math.atan2(line2.y1-line1.y1, line2.x1-line1.x1)
        rel_rad2 = math.atan2(line2.y2-line1.y1, line2.x2-line1.x1)
        if (util.near_zero((rad1-rel_rad1) % math.pi) or
                util.near_zero((rad1-rel_rad2) % math.pi)):
            raise InfiniteIntersections(line1)
        raise NoIntersection()
    c1 = line1.x2 - line1.x1
    c2 = -line2.x2 + line2.x1
    c3 = line2.x1 - line1.x1
    c4 = line1.y2 - line1.y1
    c5 = -line2.y2 + line2.y1
    c6 = line2.y1 - line1.y1
    a, b = numpy.linalg.solve([[c1,c2],[c4,c5]], [c3,c6])
    ix = line1.x1 + a * (line1.x2 - line1.x1)
    iy = line1.y1 + a * (line1.y2 - line1.y1)
    return ix, iy
