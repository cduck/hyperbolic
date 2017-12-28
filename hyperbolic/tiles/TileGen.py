
from ..poincare import Transform
from . import Tile


class TileGen:
    def __init__(self, centerTile, cornerTile):
        self.centerTile = centerTile
        self.cornerTile = cornerTile
    @staticmethod
    def fromCenterTile(centerTile):
        transToOrigin = Transform.shiftOrigin(centerTile.vertices[0],
                                              centerTile.vertices[1])
        cornerTile = centerTile.makeTransformed(transToOrigin)
        return TileGen(centerTile, cornerTile)
    def centeredTileWithTransform(self, trans):
        return self.centerTile.makeTransformed(trans)
    def tileWithTransform(self, trans):
        return self.cornerTile.makeTransformed(trans)
    def centeredTile(self, rotateDeg=0):
        if rotateDeg != 0:
            trans = Transform.rotation(deg=rotateDeg)
            return self.centeredTileWithTransform(trans)
        else:
            return self.centerTile
    def cornerCenteredTile(self, rotateDeg=0):
        if rotateDeg != 0:
            trans = Transform.rotation(deg=rotateDeg)
            return self.tileWithTransform(trans)
        else:
            return self.cornerTile
    def placedAgainstTile(self, tile, side, touchingSide=0):
        return self.placedAgainstEdge(tile.sides[side], touchingSide=touchingSide)
    def placedAgainstEdge(self, edge, touchingSide=0):
        trans = Transform.translation(edge.p2, edge.p1)
        if touchingSide != 0:
            transToSide = Transform.shiftOrigin(
                self.cornerTile.vertices[touchingSide],
                self.cornerTile.vertices[(touchingSide+1)%len(self.cornerTile.vertices)])
            trans = Transform.merge(transToSide, trans)
        tile = self.tileWithTransform(trans)
        tile.touchingSide = touchingSide
        return tile
    def makeGenWithPermutedEdges(self, newBaseSideIndex):
        centerTile = self.centerTile.makePermuted(newBaseSideIndex)
        cornerTile = self.cornerTile.makePermuted(newBaseSideIndex)
        return TileGen(centerTile, cornerTile)
    @staticmethod
    def makeRegular(p, q=None, innerDeg=None, er=None, hr=None, skip=1):
        centerTile = Tile.makeRegular(p, q=q, innerDeg=innerDeg, er=er, hr=hr, skip=skip)
        return TileGen.fromCenterTile(centerTile)

