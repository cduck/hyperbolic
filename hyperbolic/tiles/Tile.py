
import math

from ..poincare import Transform
from ..poincare.shapes import Point, Polygon
from ..poincare.util import radialEuclidToPoincare
from . import Edge


def hypPolyEdgeConstruct(p, q):
    pi, pi2 = math.pi, math.pi*2
    th = pi2/q
    phi = pi2/p
    ang1 = pi-phi/2-th/2-pi/2
    ang2 = th/2 + pi/2
    a = math.sin(ang2)/math.sin(ang1)
    b = math.sin(phi/2)/math.sin(ang1)
    rP = math.sqrt(1/(a**2-b**2))
    rC = a*rP
    rFromC = b*rP
    #return rC, rFromC
    t1 = pi - math.asin(rC / (rFromC / math.sin(phi/2)))
    t2 = pi - t1 - phi/2
    r = math.sin(t2) * (rFromC / math.sin(phi/2))
    return r


class Tile:
    def __init__(self, vertices, touchingSide=None, trans=Transform.identity(),
                 decorator=None):
        self.vertices = vertices
        self.sides = [Edge(vertices[i],vertices[(i+1)%len(self.vertices)])
                      for i in range(len(self.vertices))]
        self.touchingSide = touchingSide
        self.trans = trans
        self.decorator = decorator
    def setSideCodes(self, sideCodes):
        for side, code in zip(self.sides, sideCodes):
            side.code = code
    def copySideCodes(self, sides):
        for side, other in zip(self.sides, sides):
            side.code = other.code
    def toPolygon(self):
        return Polygon.fromVertices(self.vertices)
    def toDrawables(self, elements, **kwargs):
        if self.decorator is None:
            drawVerts = kwargs.get('drawVerts', False)
            if not drawVerts:
                poly = self.toPolygon()
                d = poly.toDrawables(elements, **kwargs)
                return d
            elif drawVerts:
                lst = []
                for v in self.vertices:
                    ds = v.toDrawables(elements, **kwargs)
                    lst.extend(ds)
                return lst
        else:
            return self.decorator.toDrawables(elements, tile=self, **kwargs)
    def getSide(self, sideIndex):
        return self.sides[sideIndex]
    def permutedSides(self, touchingSide=None):
        if touchingSide is None:
            touchingSide = self.touchingSide
        if touchingSide is None:
            return self.sides
        sides = self.sides
        return [sides[(i+touchingSide)%len(sides)]
                for i in range(len(sides))]
    def permutedVertices(self, touchingSide=None):
        if touchingSide is None:
            touchingSide = self.touchingSide
        if touchingSide is None:
            return self.sides
        vertices = self.vertices
        return [vertices[(i+touchingSide)%len(vertices)]
                for i in range(len(vertices))]
    def __len__(self):
        return len(self.vertices)
    def __contains__(self, edgeOrVertex):
        if edgeOrVertex in self.vertices:
            return True
        if edgeOrVertex in self.sides:
            return True
        return False
    def usesEdge(self, edge):
        return edge in self.sides
    def makeNew(self, vertices, touchingSide, trans):
        ''' Override this in subclass if __init__ has a different signature '''
        tile = type(self)(vertices, touchingSide=touchingSide, trans=trans,
                          decorator=self.decorator)
        tile.copySideCodes(self.sides)
        return tile
    def makeTransformed(self, trans):
        newVerts = trans.applyToList(self.vertices)
        totalTrans = Transform.merge(self.trans, trans)
        return self.makeNew(newVerts, touchingSide=self.touchingSide, trans=totalTrans)
    def makePermuted(self, firstSideIndex):
        p = len(self.vertices)
        vertices = [self.vertices[(i+firstSideIndex)%p] for i in range(p)]
        if self.touchingSide is None:
            touchingSide = None
        else:
            touchingSide = self.touchingSide - firstSideIndex
        transToOrigin = Transform.shiftOrigin(self.vertices[0], self.vertices[1])
        corneredVerts = transToOrigin.applyToList(self.vertices)
        transPermuteOrigin = Transform.shiftOrigin(corneredVerts[firstSideIndex],
                                             corneredVerts[(firstSideIndex+1)%p])
        transPermute = Transform.merge(transToOrigin, transPermuteOrigin,
                                       transToOrigin.inverted())
        trans = Transform.merge(trans, transPermute)
        return self.makeNew(vertices, touchingSide=touchingSide, trans=trans)
    @staticmethod
    def makeRegular(p, q=None, innerDeg=None, er=None, hr=None, skip=1):
        assert (q is not None) + (innerDeg is not None) + (er is not None) + (hr is not None) == 1, \
            'Specify exactly one of q, innerDeg, er, or hr'
        # Calculate innerRad
        if innerDeg is not None:
            q = 360/innerDeg
            innerRad = math.radians(innerDeg)
        elif q is not None:
            innerRad = math.pi*2/q
        else:
            if hr is None:
                hr = radialEuclidToPoincare(er)
            thDiv2 = math.pi / p
            innerRad = 2 * math.atan(1 / (math.tan(thDiv2) * math.cosh(hr)))
        # Calculate r
        if q is None:
            if er is None:
                pointConstruct = Point.fromHPolar
                r = hr
            else:
                pointConstruct = Point.fromPolarEuclid
                r = er
        else:
            r = hypPolyEdgeConstruct(p, q)
            pointConstruct = Point.fromPolarEuclid
        # Calculate polygon vertices
        verts = [
            pointConstruct(r, deg=skip*i*360/p)
            for i in range(p)
        ]
        return Tile(verts)

