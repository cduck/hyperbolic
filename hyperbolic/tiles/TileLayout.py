
class TileLayout:
    ''' Override this class and implement the calc* methods to create a custom
        layout. '''
    def __init__(self, genList=None):
        self.genList = [] if genList is None else genList
    def addGenerator(self, tileGen, sideCodes, decorator=None):
        self.genList.append([tileGen, sideCodes, decorator])
    def setDecorator(self, decorator, genIndex):
        self.genList[genIndex][2] = decorator
    def tilePlane(self, startTile, depth=2):
        tiles = [startTile]
        boundary = list(startTile.sides)
        for j in range(depth):
            boundary2 = []
            i = 0
            while i < len(boundary):
                tile = self.placeTile(boundary[i])
                tiles.append(tile)
                sides = tile.permutedSides()
                o = 1
                p = len(sides)
                if i == 0:
                    if sides[o] == boundary[-1]:
                        o += 1
                        boundary.pop()
                else:
                    if sides[o] == boundary2[-1]:
                        o += 1
                        boundary2.pop()
                    if sides[p-1] == boundary[(i + 1) % len(boundary)]:
                        p -= 1
                        i += 1
                    if sides[p-1] == boundary2[0]:
                        p -= 1
                        boundary2.pop(0)
                boundary2.extend(sides[o:p])
                i += 1
            boundary = boundary2
        return tiles
    def placeTile(self, edge):
        ''' Returns a tile placed against edge according to the
            placement rules '''
        code = edge.code
        genIndex = self.calcGenIndex(code)
        tileGen, defaultCodes, decorator = self.genList[genIndex][0:3]
        touchSideIndex = self.calcTileTouchSide(code, genIndex)
        sideCodes = self.calcSideCodes(code, genIndex, touchSideIndex, defaultCodes)
        tile = tileGen.placedAgainstEdge(edge, touchingSide=touchSideIndex)
        tile.setSideCodes(sideCodes)
        tile.decorator = decorator
        return tile
    def startTile(self, code=0, genIndex=None, sideCodes=None, rotateDeg=0, centerCorner=False):
        if genIndex is None:
            genIndex = self.calcGenIndex(code)
        tileGen, defaultCodes, decorator = self.genList[genIndex][0:3]
        if sideCodes is None:
            touchSideIndex = self.calcTileTouchSide(code, genIndex)
            sideCodes = self.calcSideCodes(code, genIndex, touchSideIndex, defaultCodes)
        if centerCorner:
            tile = tileGen.cornerCenteredTile(rotateDeg=rotateDeg)
        else:
            tile = tileGen.centeredTile(rotateDeg=rotateDeg)
        tile.setSideCodes(sideCodes)
        tile.decorator = decorator
        return tile
    def defaultStartTile(self, rotateDeg=0, centerCorner=False):
        return self.startTile(rotateDeg=rotateDeg, centerCorner=centerCorner)
    def calcGenIndex(self, code):
        ''' Override in subclass to control which type of tile to place '''
        return code
    def calcTileTouchSide(self, code, genIndex):
        ''' Override in subclass to control tile orientation '''
        return 0
    def calcSideCodes(self, code, genIndex, touchSide, defaultCodes):
        ''' Override in subclass to control tile side codes '''
        return defaultCodes

