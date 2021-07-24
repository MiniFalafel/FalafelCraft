# A block will store its index and can use it to find where it is in a chunk's vertex buffer data

# Get texture coordinates from texture atlas position
def genTexCoord(x, y, atlasWidth = 4, atlasHeight = 4):
    # Get the constants for x and y coordinate conversion
    kX = 1.0 / atlasWidth
    kY = 1.0 / atlasHeight
    # Apply constants
    o = [x * kX, y * kY]
    coords = [o[0], o[1], o[0] + kX, o[1], o[0] + kX, o[1] + kY, o[0], o[1] + kY]
    return coords

def genTexCoords(blockTop, blockSide, blockBottom, atlasWidth = 4, atlasHeight = 4): # I saw someone else do something similar project and thought it was neat
    # Get all texcoords
    top = genTexCoord(*blockTop, atlasWidth, atlasHeight)
    bottom = genTexCoord(*blockBottom, atlasWidth, atlasHeight)
    sides = [genTexCoord(*blockSide, atlasWidth, atlasHeight)] * 4 # We have four sides so we do it four times
    # Add them all together and return
    return [top, bottom, *sides]

# The amount of textures on the texture atlas for width and height
AW = 4
AH = 4

# Block types
# The tuples are the positions in a 4x4 grid of the textures for top sides and bottom of the block
GLASS   = genTexCoords((3, 0), (3, 0), (3, 0), AW, AH) # Glass
WOOD    = genTexCoords((1, 2), (0, 2), (1, 2), AW, AH) # Wood
PLANKS  = genTexCoords((2, 2), (2, 2), (2, 2), AW, AH) # Planks
STONE   = genTexCoords((0, 0), (0, 0), (0, 0), AW, AH) # Stone
SAND    = genTexCoords((1, 0), (1, 0), (1, 0), AW, AH) # Sand
DIRT    = genTexCoords((0, 1), (0, 1), (0, 1), AW, AH) # Dirt
GRASS   = genTexCoords((2, 1), (1, 1), (0, 1), AW, AH) # Grass
WATER   = genTexCoords((2, 0), (2, 0), (2, 0), AW, AH) # Water
# Usable and opaque blocks
opaqueBlocks = [WOOD, PLANKS, STONE, SAND, DIRT, GRASS]
blockList = [WATER, GLASS, WOOD, PLANKS, STONE, SAND, DIRT, GRASS]

# Define block face types
# Up
blockFaceUp = (0, 1, 1,   1, 1, 1,   1, 1, 0,   0, 1, 0) # The vertices of a face should be defined counter clockwise
# Down
blockFaceDown = (0, 0, 0,   1, 0, 0,   1, 0, 1,   0, 0, 1)
# West (same as left)
blockFaceWest = (0, 0, 0,   0, 0, 1,   0, 1, 1,   0, 1, 0)
# East (same as right)
blockFaceEast = (1, 0, 1,   1, 0, 0,   1, 1, 0,   1, 1, 1)
# North (same as forward)
blockFaceNorth = (1, 0, 0,   0, 0, 0,   0, 1, 0,   1, 1, 0)
# South (same as backward)
blockFaceSouth = (0, 0, 1,   1, 0, 1,   1, 1, 1,   0, 1, 1)
# Put them in an array for easy access
# Same order as the return of the Chunk.checkVisibleFaces() function
blockFaces = [blockFaceUp, blockFaceDown, blockFaceWest, blockFaceEast, blockFaceNorth, blockFaceSouth]

# Face offsets
up =   (0,  1, 0)
down = (0, -1, 0)
# Left and right neighbors
left =  (-1, 0, 0)
right = ( 1, 0, 0)
# Backward and forward neighbors
forward =  (0, 0, -1)
backward = (0, 0,  1)  # the negative z direction is forward
# Put them in an array
faceOffsets = [up, down, left, right, forward, backward]

# Indices of face offsets
faceNeighbors = [
    [4, 5, 2, 3],
    [5, 4, 2, 3],
    [0, 1, 4, 5],
    [0, 1, 5, 4],
    [0, 1, 3, 2],
    [0, 1, 2, 3]
]

def toBlockPos(pos : tuple):
    return tuple([pos[0] // 1, pos[1] // 1, pos[2] // 1])

class Block:
    def __init__(self, blockIndex : int, atlasLookupCoordinates : list):
        self.index = blockIndex
        self.TexCoords = atlasLookupCoordinates

    def getIndex(self):
        return self.index

    def getTexCoords(self):
        return self.TexCoords

