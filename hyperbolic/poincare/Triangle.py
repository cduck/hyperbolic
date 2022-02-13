
import math
from ..euclid import intersection
from ..euclid.shapes import Arc, Circle as ECircle
from .shapes import Point, Hypercycle, Circle, Polygon
from . import Transform

def capIntersections(cap1, hcycle2):
    if not isinstance(cap1, Hypercycle) or not isinstance(hcycle2, Hypercycle):
        return []
    else:
        return cap1.segmentIntersectionsWithHcycle(hcycle2)

class DoubleIntersections(Exception): pass

class Triangle(Polygon):
    def __init__(self, edges=None, join=False, vertices=None):
        if not edges==None:
            if len(edges)!=3:
                raise ValueError('The number of edges needs to be 3')
        if not vertices==None:
            if len(vertices)!=3:
                raise ValueError('The number of vertices needs to be 3')
        super().__init__(edges=edges, join=join, vertices=vertices)
    def isIdeal(self):
        '''returns True when all vertices are ideal points'''
        return (self.vertices[0].isIdeal() and self.vertices[1].isIdeal() and self.vertices[2].isIdeal())
    def isCCW(self):
        '''returns True for a counter-clock-wise triangle'''
        if self.isIdeal():
            Deg0 = math.degrees(self.vertices[0].theta)
            Deg1 = math.degrees(self.vertices[1].theta)
            Deg2 = math.degrees(self.vertices[2].theta)
            ccw = (Deg2-Deg0)%360 >= (Deg1-Deg0)%360
        else:
            vertNumOfPoints = [i for i,p in enumerate(self.vertices) if not p.isIdeal()]
            k=vertNumOfPoints[0]
            trans = Transform.shiftOrigin(self.vertices[k], self.vertices[(k+1)%len(self.vertices)])
            p2 = Transform.applyToPoint(trans, self.vertices[(k-1)%len(self.vertices)])
            ccw = math.degrees(p2.theta)%360<=180
        return ccw
    def offsetEdge(self, edgeNum, offset, inner=True):
        '''returns the offset hypercycle of the edge closer (or further) to the inside of the triangle'''
        if ((self.isCCW() and offset<=0) or (not self.isCCW() and offset>=0)):
            offset = -offset
        if inner:
            return Hypercycle.fromHypercycleOffset(self.edges[edgeNum%len(self.edges)], offset)
        else:
            return Hypercycle.fromHypercycleOffset(self.edges[edgeNum%len(self.edges)], -offset)
    def isDeltaslim(self, delta):
        '''returns True when the delta-neigbourhood of any two edges already covers the last one'''
        for i, edge in enumerate(self.edges):
            #tiny delta for ideal triangles will remove all points
            ip1 = [p 
                    for p in edge.segmentIntersectionsWithHcycle(self.offsetEdge(i-1, delta))  
                    if not p.isIdeal()]
            #tiny delta for ideal triangles will remove all points
            ip2 = [p 
                    for p in edge.segmentIntersectionsWithHcycle(self.offsetEdge(i+1, delta))
                    if not p.isIdeal()]
            # Whole edge is covered by on of the sides deltaNbh or problem above
            if len(ip1) <= 0 or len(ip2) <= 0:
                continue
            # May throw if bad geometry and rounding errors
            elif len(ip1) > 1 or len(ip2) > 1:
                raise DoubleIntersections()
            else:
                p1, p2 = ip1[0], ip2[0]
                s1 = self.vertices[i]
                if edge.trimmed(*s1, *p1).isPointOnSegment(*p2):
                    continue
                else:
                    return False
        return True
    def approx(self, precision=32):
        '''returns the smallest delta for which the triangle is delta-slim'''
        i=1
        k=0
        delta=1    
        while self.isDeltaslim(delta)==False:
            delta=delta*2
            k=k+1
        while i-k<precision:
            if self.isDeltaslim(delta)==True:
                delta=delta-2**(k-i)
                i=i+1
            else:
                delta=delta+2**(k-i)
                i=i+1
        if self.isDeltaslim(delta)==False:
            delta=delta+2**(k-i+1)
        return delta
    def surroundingIdealTriangle(self):
        if self.isIdeal():
            return self
        else:
            unit=ECircle(0,0,1)
            edge0, edge1, edge2 = self.edges[0].projShape, self.edges[1].projShape, self.edges[2].projShape
            if isinstance(edge0, (ECircle,Arc)):
                e0x1, e0y1, e0x2, e0y2 = intersection.circleCircle(edge0, unit)
                if (edge0.cw and not self.isCCW()) or (not edge0.cw and self.isCCW()):
                    e0x1, e0y1, e0x2, e0y2 = e0x2, e0y2, e0x1, e0y1
            else:
                e0x1, e0y1, e0x2, e0y2 = intersection.lineCircle(edge0, unit)
                if self.isCCW():
                    e0x1, e0y1, e0x2, e0y2 = e0x2, e0y2, e0x1, e0y1
            if isinstance(edge1, (ECircle,Arc)):
                e1x1, e1y1, e1x2, e1y2 = intersection.circleCircle(edge1, unit)
                if (edge1.cw and not self.isCCW()) or (not edge1.cw and self.isCCW()):
                    e1x1, e1y1, e1x2, e1y2 = e1x2, e1y2, e1x1, e1y1
            else:
                e1x1, e1y1, e1x2, e1y2 = intersection.lineCircle(edge1, unit)
                if self.isCCW():
                    e1x1, e1y1, e1x2, e1y2 = e1x2, e1y2, e1x1, e1y1
            if isinstance(edge2, (ECircle,Arc)):
                e2x1, e2y1, e2x2, e2y2 = intersection.circleCircle(edge2, unit)
                if (edge2.cw and  not self.isCCW()) or (not edge2.cw and self.isCCW()):
                    e2x1, e2y1, e2x2, e2y2 = e2x2, e2y2, e2x1, e2y1
            else:
                e2x1, e2y1, e2x2, e2y2 = intersection.lineCircle(edge2, unit)
                if self.isCCW():
                    e2x1, e2y1, e2x2, e2y2 = e2x2, e2y2, e2x1, e2y1
            if self.isCCW():
                arc0 = Arc.fromPointsWithCenter(e0x2, e0y2, e2x1, e2y1, 0, 0, 1)
                arc1 = Arc.fromPointsWithCenter(e1x2, e1y2, e0x1, e0y1, 0, 0, 1)
                arc2 = Arc.fromPointsWithCenter(e2x2, e2y2, e1x1, e1y1, 0, 0, 1)
            else:
                arc0 = Arc.fromPointsWithCenter(e2x2, e2y2, e0x1, e0y1, 0, 0, 1)
                arc1 = Arc.fromPointsWithCenter(e0x2, e0y2, e1x1, e1y1, 0, 0, 1)
                arc2 = Arc.fromPointsWithCenter(e1x2, e1y2, e2x1, e2y1, 0, 0, 1)
            p0 = self.vertices[0] if self.vertices[0].isIdeal() else Point.fromEuclid(*arc0.midpoint())
            p1 = self.vertices[1] if self.vertices[1].isIdeal() else Point.fromEuclid(*arc1.midpoint())
            p2 = self.vertices[2] if self.vertices[2].isIdeal() else Point.fromEuclid(*arc2.midpoint())
            return Triangle.fromVertices([p0, p1, p2])
    def offsetVertice(self, vertNum, edgeNum, offset, inner=False, onEdge=False):
        '''returns offset vertice on (outer) offseEdge
        or returns offset vertice on Edge '''
        if edgeNum%len(self.edges)==(vertNum+1)%len(self.vertices):
            raise ValueError('The vertice must be startPoint or endPoint of the edge')
        vert = self.vertices[vertNum%len(self.vertices)]
        if vert.isIdeal():
            return vert        
        edge = self.edges[edgeNum%len(self.edges)]
        offsetEdge = self.offsetEdge(edgeNum, offset, inner=inner)
        perp = edge.makePerpendicular(*vert)
        if onEdge:
            if ((vertNum%len(self.vertices)==edgeNum%len(self.edges) and offset>=0) or 
                (vertNum%len(self.vertices)!=edgeNum%len(self.edges) and offset<=0)):
                pts = edge.intersectionsWithHcycle(perp.makeOffset(-offset))
            else:
                pts = edge.intersectionsWithHcycle(perp.makeOffset(offset))
            assert len(pts)==1
        else:
            pts = offsetEdge.intersectionsWithHcycle(perp)
            assert len(pts)==1
        return pts[0]
    def offsetEdgeIntersectionPoint(self, edgeNum, offset):
        hc1 = self.offsetEdge(edgeNum+1, offset)
        hc2 = self.offsetEdge(edgeNum-1, offset)
        pts = [p for p in hc1.intersectionsWithHcycle(hc2) if not p.isIdeal()]
        # May throw if bad geometry
        assert len(pts)==1
        return pts[0]
    def endCap(self, vertNum, edgeNum, offset):
        vert = self.vertices[vertNum%len(self.vertices)]
        if vert.isIdeal():
            return vert
        sp = self.offsetVertice(vertNum, edgeNum, offset, inner=True)
        mp = self.offsetVertice(vertNum, edgeNum, offset, onEdge=True)
        ep = self.offsetVertice(vertNum, edgeNum, offset, inner=False)
        if sp.isIdeal() or mp.isIdeal() or ep.isIdeal():
            idealpts=[p for p in [sp,mp,ep] if p.isIdeal()]
            return idealpts[0]
        else:
            return Hypercycle(Arc.fromPoints(*sp, *ep, *mp, excludeMid=True), segment=True)
    def midCap(self, vertNum, offset):
        vert = self.vertices[vertNum%len(self.vertices)]
        if vert.isIdeal():
            return vert
        sp = self.offsetVertice(vertNum, vertNum-1, offset, inner=False)
        ep = self.offsetVertice(vertNum, vertNum, offset, inner=False)
        circ = Circle.fromCenterRadius(self.vertices[vertNum%len(self.vertices)], offset)
        cp = Point.fromEuclid(circ.projShape.cx, circ.projShape.cy)
        if sp.isIdeal() or cp.isIdeal() or ep.isIdeal():
            idealpts=[p for p in [sp,cp,ep] if p.isIdeal()]
            return idealpts[0]
        else:
            arc = Arc.fromPointsWithCenter(*sp,*ep, *cp, r=circ.projShape.r, cw= not self.isCCW())
            return Hypercycle(arc, segment=True).reversed()
    def neigbourhood(self, delta, edgeNum=0):
        k=edgeNum
        sCap = self.endCap(k, k-1, delta)
        v2 = self.offsetVertice(k, k-1, delta, inner=False)
        v3 = self.offsetVertice(k-1, k-1, delta, inner=False)  
        sOutLine = self.offsetEdge(k-1, delta, inner=False).trimmed(*v3, *v2).reversed()
        mCap = self.midCap(k-1, delta)
        v4 = self.offsetVertice(k-1, k+1, delta, inner=False)
        v5 = self.offsetVertice(k+1, k+1, delta, inner=False)
        eOutLine = self.offsetEdge(k+1, delta, inner=False).trimmed(*v5, *v4).reversed()
        eCap = self.endCap(k+1, k+1, delta)
        if isinstance(eCap, Hypercycle):
            eCap=eCap.reversed()
        v1 = self.offsetVertice(k, k-1, delta, inner=True)
        v6 = self.offsetVertice(k+1, k+1, delta, inner=True)
        temp7 = self.offsetVertice(k-1, k+1, delta, inner=True)
        temp8 = self.offsetVertice(k-1, k-1, delta, inner= True) 
        sInLine = self.offsetEdge(k-1, delta, inner=True).trimmed(*temp8, *v1)
        eInLine = self.offsetEdge(k+1, delta, inner=True).trimmed(*v6, *temp7)
        if len(capIntersections(sCap, eCap))==1:
            v1 = capIntersections(sCap, eCap)[0]
            sCap = sCap.trimmed(*v1, *v2)
            eCap = eCap.trimmed(*v5, *v1)
            vertices = [v1, v2, v3, v4, v5]
            edges = [sCap, sOutLine, mCap, eOutLine, eCap]
        elif len(capIntersections(sCap, eInLine))==1:
            v1 = capIntersections(sCap, eInLine)[0]
            eInLine = eInLine.trimmed(*v6, *v1)
            sCap = sCap.trimmed(*v1, *v2)
            vertices = [v1, v2, v3, v4, v5, v6]
            edges = [sCap, sOutLine, mCap, eOutLine, eCap, eInLine]
        elif len(capIntersections(eCap, sInLine))==1:
            v6 = capIntersections(eCap, sInLine)[0]
            sInLine = sInLine.trimmed(*v6, *v1)
            eCap = eCap.trimmed(*v5,*v6)
            vertices = [v1, v2, v3, v4, v5, v6]
            edges = [sCap, sOutLine, mCap, eOutLine, eCap, sInLine]
        else:
            v7 = self.offsetEdgeIntersectionPoint(k, delta)
            sInLine = sInLine.trimmed(*v7, *v1)
            eInLine = eInLine.trimmed(*v6, *v7)
            vertices = [v1, v2, v3, v4, v5, v6, v7]
            edges = [sCap, sOutLine, mCap, eOutLine, eCap, eInLine, sInLine]
        vertices = [v for v,e in zip(vertices, edges) if isinstance(e, Hypercycle)]
        edges = [e for e in edges if isinstance(e, Hypercycle)]
        return Polygon(edges, join=False, vertices=vertices)
    @classmethod
    def fromEdges(cls, edges, join=True):
        return cls(edges=edges, join=join)
    @classmethod
    def fromVertices(cls, vertices):
        return cls(vertices=vertices) 

