
import math
# TODO: Remove dependency on numpy
import numpy.linalg

from .. import util
from .shapes import Circle, Line


class InfiniteIntersections(Exception): pass
class SingleIntersection(Exception): pass
class NoIntersection(Exception): pass
class InsufficientPrecision(Exception): pass

def circleCircle(circ1, circ2):
    ''' Returns two points where CCW around circ1 from (x1,y1) to (x2,y2) is
        the arc of circ1 contained in circ2.

        Throws InfiniteIntersections or SingleIntersection with useful args.
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
    if util.nearZero(d) and util.nearZero(r1-r2):
        raise InfiniteIntersections(circ2 if swap else circ1)
    # Check if circles are concentric
    if util.nearZero(d):
        raise NoIntersection()
    # Check for single intersection
    if util.nearZero(r1+r2-d) or util.nearZero(r2-r1-d):
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
    diffRad = math.acos(t)
    centerRad = math.atan2(dy, dx)
    ix1 = cx2 + r2 * math.cos(centerRad-diffRad)
    iy1 = cy2 + r2 * math.sin(centerRad-diffRad)
    ix2 = cx2 + r2 * math.cos(centerRad+diffRad)
    iy2 = cy2 + r2 * math.sin(centerRad+diffRad)
    if swap:
        return ix1, iy1, ix2, iy2
    else:
        return ix2, iy2, ix1, iy1

def circleLine(circ, line):
    ''' Returns two points.

        Throws SingleIntersection with useful args.
        Can throw NoIntersection or InsufficientPrecision.
    '''
    ldx, ldy = line.x2-line.x1, line.y2-line.y1
    if util.nearZero(ldx) and util.nearZero(ldy):
        raise InsufficientPrecision()
    cx, cy, r = circ.cx, circ.cy, circ.r
    x1, y1, x2, y2 = line.x1-cx, line.y1-cy, line.x2-cx, line.y2-cy
    # Calculate angles and minimum distance from circle center to line
    lineRad = math.atan2(ldy, ldx)
    pRad = math.atan2(y1, x1)
    pMag = math.sqrt(x1**2 + y1**2)
    d = pMag * math.sin(pRad - lineRad)
    negate = d < 0
    if negate: d = -d
    # Check for single intersection (tangent line)
    if util.nearZero(d - r):
        ix, iy = -r*math.sin(lineRad), r*math.cos(lineRad)
        if negate:
            ix, iy = -ix, -iy
        raise SingleIntersection(cx+ix, cy+iy)
    # Check if line is separate from circle
    if d > r:
        raise NoIntersection()
    # Calculate two intersections
    diffRad = math.acos(d / r)
    ix1, iy1 = -r*math.sin(lineRad-diffRad), r*math.cos(lineRad-diffRad)
    ix2, iy2 = -r*math.sin(lineRad+diffRad), r*math.cos(lineRad+diffRad)
    if negate:
        ix1, iy1, ix2, iy2 = -ix1, -iy1, -ix2, -iy2
    return cx+ix1, cy+iy1, cx+ix2, cy+iy2

def lineCircle(line, circ):
    ''' Returns two points on line where a line from (x1,y1) to (x2,y2) would
        be parallel, not antiparallel, to line.

        Can throw NoIntersection or InsufficientPrecision.
    '''
    x1, y1, x2, y2 = circleLine(circ, line)
    l = Line(x1, y1, x2, y2)
    if l.antiparallelTo(line):
        l.reverse()
    return l.x1, l.y1, l.x2, l.y2

def lineLine(line1, line2):
    ''' Returns one point.

        Throws InfiniteIntersections if the lines are approximately the same.
        Otherwise Throws NoIntersection if the lines are approximately
        parallel.
    '''
    rad1 = math.atan2(line1.y2-line1.y1, line1.x2-line1.x1)
    rad2 = math.atan2(line2.y2-line2.y1, line2.x2-line2.x1)
    if util.nearZero((rad1-rad2) % math.pi):
        relRad1 = math.atan2(line2.y1-line1.y1, line2.x1-line1.x1)
        relRad2 = math.atan2(line2.y2-line1.y1, line2.x2-line1.x1)
        if (util.nearZero((rad1-relRad1) % math.pi) or
            util.nearZero((rad1-relRad2) % math.pi)):
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

