
import math

from ..euclid import Arc
from .shapes import Point, Hypercycle, Circle, Polygon
from . import Transform

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
            ccw=math.degrees(p2.theta)%360<=180
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
        '''returns True when the delta-neigbourhood of any two sides of the triangle already cover the last one'''
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
            # May throw if bad geometry
            elif len(ip1) > 1 or len(ip2) > 1:
                raise ValueError('Intersection with edge {} is ambiguous'.format(i))
            else:
                p1, p2 = ip1[0], ip2[0]
                s1 = self.vertices[i]
                if edge.trimmed(*s1, *p1).isPointOnSegment(*p2):
                    continue
                else:
                    return False
        return True
    def approx(self):
        '''returns the smallest delta for which the triangle is delta-slim'''
        i=1
        k=0
        delta=1    
        while self.isDeltaslim(delta)==False:
            delta=delta*2
            k=k+1
        while i-k<45:
            if self.isDeltaslim(delta)==True:
                delta=delta-2**(k-i)
                i=i+1
            else:
                delta=delta+2**(k-i)
                i=i+1
        if self.isDeltaslim(delta)==False:
            delta=delta+2**(k-i+1)
        return delta
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
            if ((vertNum%len(self.vertices)==edgeNum%len(self.edges) and offset>=0) 
                or (vertNum%len(self.vertices)!=edgeNum%len(self.edges) and offset<=0)):
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
    @classmethod
    def fromEdges(cls, edges, join=True):
        return cls(edges=edges, join=join)
    @classmethod
    def fromVertices(cls, vertices):
        tri=cls(vertices=vertices)    
        return cls.fromEdges(tri.edges)

