
from .shapes import Point


class Polygon:
    def __init__(self, edges, join=False):
        ''' Assumes edges are hyperbolic lines or hypercycles of intersecting
            lines '''
        if join:
            edges = list(edges)
            edgeStarts = [None]*len(edges)
            for i in range(len(edges)):
                e1, e2 = edges[i-1], edges[i]
                if isinstance(e1, Point):
                    edgeStarts[i] = e1
                    continue
                if isinstance(e2, Point):
                    edgeStarts[i] = e2
                    continue
                pts = e1.intersectionsWithHcycle(e2)
                if len(pts) <= 0:
                    raise ValueError('Polygon edges do not intersect')
                elif len(pts) > 1:
                    raise ValueError('Polygon edge join is ambiguous')
                edgeStarts[i] = pts[0]
            for i, edge in enumerate(edges):
                startP, endP = edgeStarts[i], edgeStarts[(i+1)%len(edges)]
                if isinstance(edge, Point):
                    edges[i] = edge
                    continue
                edges[i] = edge.trimmed(*startP, *endP, chooseShorter=True)
        self.edges = tuple(edges)
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

