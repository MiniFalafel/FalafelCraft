# Imports
# Project Files
from chunk import *
from profiling import *

# Chunk generation distance
CHUNK_DIST = 2  # Because it's a nice number

# Convert a position to its position relative to its chunk
def getRelativeChunkPos(pos):
    # Get the chunk that the block is in
    chunkPos = toChunkPos(pos)
    # Calculate deltas
    realX, realZ = chunkPos[0] * CHUNK_SIZE, chunkPos[1] * CHUNK_SIZE
    # Subtract the deltas
    r = [pos[0], pos[1], pos[2]]
    # Return
    return tuple(r)


# World Class Thing
class World:
    # Variables
    # Chunks
    chunks = dict()

    # Initializer
    def __init__(self, seed):
        t = Timer("World.__init__(seed)")

        # Setup the fractal noise for the heightmap
        self.seed = seed
        # load center chunk
        #self.loadChunk(0, 0)
        self.toLoad = list()

    # Load chunk
    def loadChunk(self, chunkX, chunkY):
        t = Timer("World.loadChunk(int, int)")

        # Only load it if the chunk doesn't already exist
        if not (chunkX, chunkY) in self.chunks.keys():
            # Load the chunk
            self.chunks[(chunkX, chunkY)] = Chunk(chunkX, chunkY, self.seed)

    # Chunk updating
    def updateChunks(self, playerPos):
        t = Timer("World.updateChunks(vec3)")

        # Get a list of the chunks that need to be loaded
        cRange = range(-CHUNK_DIST // 2, CHUNK_DIST // 2)
        pChunkPos = toChunkPos(playerPos)
        # We already have index checking in the load function, so we don't need to exclude loaded chunks here
        self.toLoad = [(x + pChunkPos[0], z + pChunkPos[1])
                       for x in cRange for z in cRange
                       if ((x, z) not in self.chunks.keys())]
        # Start working on loading them
        if len(self.toLoad) > 0:
            print("%s Chunks left to load!" % str(len(self.toLoad)))
            self.loadChunk(*self.toLoad[0])

    # Draw
    def Draw(self):
        t = Timer("World.Draw()")

        # Draw only the visible/fully loaded chunks
        for key in self.chunks.keys():
            self.chunks[key].Draw()
