# A chunk holds block data for a section of the world
# Imports
from terrain_gen import *
from block import *
from mesh import *

from settings import CHUNK_SIZE, CAVE_NOISE_THRESHOLD, AO_CLIPPING_STRENGTH, WATER_LEVEL
from settings import TICKS_PER_SECOND

from collections import deque

# List nesting removal function
def removeNestings(l):
    return [item for sublist in l for item in sublist]

# Vector addition
def addVectors(vec1, vec2):
    return (vec1[0] + vec2[0], vec1[1] + vec2[1], vec1[2] + vec2[2])

# Translate face data
def translateFaceData(face: tuple, offset: tuple):
    r = list()
    for i in range(len(face) // 3):
        r.append(face[(i * 3)] + offset[0])
        r.append(face[(i * 3) + 1] + offset[1])
        r.append(face[(i * 3) + 2] + offset[2])
    return r

# Find the chunk that any position is in
def toChunkPos(pos: tuple):
    return (pos[0] // CHUNK_SIZE, pos[2] // CHUNK_SIZE)

# Test whether relative position is inside of a chunk
def isInsideChunk(pos):
    return any(pos) > 0 or any(pos) < CHUNK_SIZE

def vertexCountToBytesOffset(numVerts : int):
    return numVerts * 8 * sizeof(GLfloat)

def calcVertAO(side1, side2, corner):
    if (side1 and side2):
        return 3
    return side1 + side2 + corner

# Chunk class
class Chunk:

    # Constructor
    def __init__(self, x, y, seed): # The x and y specify which chunk it is, not the real position of it
        t = Timer("Chunk.__init__(x, y, seed)")

        # Set chunk position
        self.cPos = (x, y)
        # Set seed variable
        self.seed = seed
        # Blocks and mesh variables
        self.blocks = dict() # Has 3D coordinates for each key and a blockType for each value
        self.mesh = Mesh()
        # Setup chunk
        self.setupblocks()

        # block loading queue
        self.blockQueue = deque()

    def processQueueTick(self):
        # Get the start time
        startTime = time.perf_counter()
        # Run while the elapsed time doesn't exceed the length of a tick
        while self.blockQueue and (time.perf_counter() - startTime) < (1.0 / TICKS_PER_SECOND):
            blockArgs = self.blockQueue.popleft()
            self.setBlock(*blockArgs)

    def addBlockToQueue(self, pos, type):
        self.blockQueue.append((pos, type))

    # get lighting of vertices based on neighboring blocks(ambient occlusion)
    def calcAmbientOcclusion(self, pos: tuple, facing: int):
        # Get the position that the face is facing
        openPos = addVectors(pos, faceOffsets[facing])
        # Get neighboring blocks
        # Get the indices of the block faces around the face
        upFace, downFace, leftFace, rightFace = faceNeighbors[facing]
        # Get corner faces
        upperLeftCorner = addVectors(addVectors(openPos, faceOffsets[upFace]), faceOffsets[leftFace])
        lowerLeftCorner = addVectors(addVectors(openPos, faceOffsets[downFace]), faceOffsets[leftFace])
        upperRightCorner = addVectors(addVectors(openPos, faceOffsets[upFace]), faceOffsets[rightFace])
        lowerRightCorner = addVectors(addVectors(openPos, faceOffsets[downFace]), faceOffsets[rightFace])
        # Calculate the occlusion based on each neighboring block
        occlusion = list()
        # We're saving whether the occlusion exists for each side into variables
        # Main 4 sides
        blockClear = self.blocks[pos].getTexCoords() not in opaqueBlocks
        _u = self.checkBlockOpacity(addVectors(openPos, faceOffsets[upFace]), blockClear)
        _d = self.checkBlockOpacity(addVectors(openPos, faceOffsets[downFace]), blockClear)
        _l = self.checkBlockOpacity(addVectors(openPos, faceOffsets[leftFace]), blockClear)
        _r = self.checkBlockOpacity(addVectors(openPos, faceOffsets[rightFace]), blockClear)
        # Corners
        _ul = self.checkBlockOpacity(upperLeftCorner, blockClear)
        _dl = self.checkBlockOpacity(lowerLeftCorner, blockClear)
        _ur = self.checkBlockOpacity(upperRightCorner, blockClear)
        _dr = self.checkBlockOpacity(lowerRightCorner, blockClear)
        # Bottom left corner of the face
        occlusion.append(1.0 - (calcVertAO(_d, _l, _dl) * AO_CLIPPING_STRENGTH))
        # Bottom right corner
        occlusion.append(1.0 - (calcVertAO(_r, _d, _dr) * AO_CLIPPING_STRENGTH))
        # Upper right corner
        occlusion.append(1.0 - (calcVertAO(_u, _r, _ur) * AO_CLIPPING_STRENGTH))
        # Upper Left Corner
        occlusion.append(1.0 - (calcVertAO(_l, _u, _ul) * AO_CLIPPING_STRENGTH))
        # Return this nightmarish tedious work
        return occlusion

    # Setup block data for this chunk
    def setupblocks(self):
        t = Timer("    Chunk.setupBlocks()")

        # Generate height map
        heightMap = dict() # will have a tuple as a key with x, y values and a height value (utilizing python XD)
        # Loop through the x and z distances
        for cx in range(CHUNK_SIZE):
            for cz in range(CHUNK_SIZE): # Technically z because the y axis is the up/height direction
                # Get block coords
                _x, _y = cx + (CHUNK_SIZE * self.cPos[0]), cz + (CHUNK_SIZE * self.cPos[1])
                # The height map is a top down view of the heights on the map
                biomeVal = getBiomeNoise(_x, _y, self.seed)
                h = getHeightFromNoise(getFractalNoise(_x, _y, self.seed), biomeVal)
                heightMap[(cx, cz)] = int(round(h))
        # Fill the block data
        self.fillBlocks(heightMap)
        # Generate the mesh
        self.generateChunkMesh()

    def fillBlocks(self, heightMap):
        t = Timer("    Chunk.fillBlocks(dict)")
        for pos, height in heightMap.items():
            for y in range(height + 1):
                # Get actual block position (since it's in chunk space right now instead of world space)
                bX = self.cPos[0] * CHUNK_SIZE + pos[0]
                bZ = self.cPos[1] * CHUNK_SIZE + pos[1]
                if getCaveNoise(bX, y, bZ, self.seed) > CAVE_NOISE_THRESHOLD:
                    # Finally, get the block type based on its height
                    blockType = None
                    if y == height:
                        if y < WATER_LEVEL + 2:
                            blockType = SAND
                        else:
                            blockType = GRASS # Grass is only on the top level
                    elif height > y >= height - 3:
                        blockType = DIRT # Dirt is only present a couple of blocks below the grass
                    elif y < height - 3:
                        blockType = STONE # Stone fills the rest (currently)
                    self.blocks[(bX, y, bZ)] = Block(len(self.blocks.items()), blockType)

    # Check block position
    def checkBlock(self, pos: tuple):
        return pos in self.blocks.keys()
    # Check block opacity
    def checkBlockOpacity(self, pos: tuple, baseBlockIsClear = False):
        if baseBlockIsClear:
            try:
                return pos in self.blocks.keys()
            except:
                return False
        else:
            try:
                return self.blocks[pos].getTexCoords() in opaqueBlocks
            except:
                return False

    # Check which faces should be visible for a block
    def checkVisibleFaces(self, pos: tuple):
        # Loop through each neighboring position and check if there is a block
        return [not self.checkBlockOpacity(addVectors(pos, offset), self.blocks[pos].getTexCoords() not in opaqueBlocks) for offset in faceOffsets]

    def setBlock(self, pos, blockType):
        if blockType is None:
            try:
                del self.blocks[pos]
            except KeyError:
                pass
        else:
            self.blocks[pos] = Block(len(self.blocks.items()), blockType)
        self.reload()

    # Generate chunk mesh (we generate a new one so that we aren't rendering blocks that the player can't see)
    def generateChunkMesh(self):
        # Loop through blocks and check their surroundings
        vertices = list()
        for pos, block in self.blocks.items():
            # Data variables
            positions = list()
            colors = list()
            texcoords = list()
            # check neighbors and get visible faces
            faces = self.checkVisibleFaces(pos)
            # If any faces are visible, generate the faces and add them to the vertices and texcoords
            # Get the indices of the visible faces and use them to retrieve faces
            for i, v in enumerate(faces):
                if v:
                    positions = translateFaceData(blockFaces[i], pos) # Add vertices
                    # Lighting
                    colors = self.calcAmbientOcclusion(pos, i)
                    # Add the texcoords of the block
                    texcoords = block.getTexCoords()[i] # The block data is saved as a set of texture coordinates
                    verts = [positions[i * 3:i * 3 + 3] + [colors[i],] + texcoords[i * 2:i * 2 + 2] for i in range(len(colors))]
                    vertices += removeNestings(verts)
            # Finally, add them to the chunk mesh :)
            #self.mesh.addData(positions, colors, texcoords)
            #p += positions; c += colors; t += texcoords
        self.mesh.addData(vertices)
        del v

    # Reload chunk
    def reload(self):
        # Clear the mesh's contents
        del self.mesh
        self.mesh = Mesh()
        # Re-generate the mesh
        self.generateChunkMesh()

    # Update
    def updateChunk(self, dt):
        # We don't need delta time yet, but I'm adding it in case we need it later
        self.processQueueTick()

    # Draw function
    def Draw(self):
        self.mesh.Draw()
