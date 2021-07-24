# Chunk size and max height
CHUNK_SIZE = 16 # X by Y size of each chunk
MAX_HEIGHT = 128

# Vertex Data Config
FLOATS_PER_VERTEX = 6
VERTS_PER_BLOCK = 24 # TODO: Optimize so that we only need 8
INDICES_PER_FACE = 6

# Terrain Generation settings
CAVE_NOISE_THRESHOLD = -0.4
NOISE_OCTAVES = 8
WATER_LEVEL = 32 # the height that water generates at
MAX_GEN_HEIGHT = 64 # the height that water generates at

# Graphics
AO_CLIPPING_STRENGTH = 0.125

# Game
PLAYER_HEIGHT = 1.7 # Average height of a man in meters
DAY_MINUTES = 0.1
TICKS_PER_SECOND = 120

# Ray casting and interaction stuff
MAX_INTERACTION_DIST = 32 # in blocks
STEPS_PER_RAY_UNIT = 8 # How many steps it'll take to move the space of a block
RAY_CAST_REFINES = 8 # DON'T PUT BELOW 4!!!
