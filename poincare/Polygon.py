
from .shapes import Point, Line


class Polygon:
    def __init__(self, edges=None, join=False, vertices=None):
        ''' Assumes edges are hyperbolic lines or hypercycles of intersecting
            lines '''
        if vertices is None:
            vertices = [None]*len(edges)
            for i in range(len(edges)):
                e1, e2 = edges[i-1], edges[i]
                if isinstance(e1, Point):
                    vertices[i] = e1
                    continue
                if isinstance(e2, Point):
                    vertices[i] = e2
                    continue
                pts = e1.intersectionsWithHcycle(e2)
                if len(pts) <= 0:
                    raise ValueError('Polygon edges do not intersect')
                elif len(pts) > 1:
                    raise ValueError('Polygon edge join is ambiguous')
                vertices[i] = pts[0]
        if edges is None:
            edges = [None]*len(vertices)
            for i in range(len(vertices)):
                startP, endP = vertices[i], vertices[(i+1)%len(vertices)]
                edges[i] = Line.fromPoints(*startP, *endP, segment=True)
                #edges[i] = edges[i].trimmed(*startP, *endP, chooseShorter=True)
        if join:
            edges = list(edges)
            for i, edge in enumerate(edges):
                startP, endP = vertices[i], vertices[(i+1)%len(edges)]
                if isinstance(edge, Point):
                    edges[i] = edge
                    continue
                edges[i] = edge.trimmed(*startP, *endP, chooseShorter=True)
        self.edges = tuple(edges)
        self.vertices = tuple(vertices)
    @staticmethod
    def fromEdges(edges, join=False):
        return Polygon(edges=edges, join=join)
    @staticmethod
    def fromVertices(vertices):
        return Polygon(vertices=vertices)
    def toDrawables(self, elements, hwidth=None, **kwargs):
        if hwidth is None:
            path = elements.Path(**kwargs)
            self.drawToPath(path, includeM=True, includeL=False, **kwargs)
            path.Z()
            return (path,)
        else:
            try:
                hwidth1, hwidth2 = hwidth
            except TypeError:
                hwidth = float(hwidth)
                hwidth1, hwidth2 = hwidth/2, -hwidth/2
            path = elements.Path(**kwargs)
            outerEdges = [  # Maybe outer, maybe inner
                edge.makeOffset(hwidth1)
                for edge in self.edges
                if not isinstance(edge, Point)
            ]
            innerEdges = [  # Maybe outer, maybe inner
                edge.makeOffset(hwidth2)
                for edge in reversed(self.edges)
                if not isinstance(edge, Point)
            ]
            outerPoly = Polygon(outerEdges, join=True)
            innerPoly = Polygon(innerEdges, join=True)
            outerPoly.drawToPath(path, includeM=True, includeL=False, **kwargs)
            innerPoly.drawToPath(path, includeM=False, includeL=True, **kwargs)
            path.Z()
            return (path,)
    def drawToPath(self, path, includeM=True, includeL=False, **kwargs):
        for i, edge in enumerate(self.edges):
            if isinstance(edge, Point):
                continue
            edge.drawToPath(path, includeM=includeM and i==0,
                            includeL=includeL and i==0)

