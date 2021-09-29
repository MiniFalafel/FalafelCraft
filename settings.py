import glm
import math
# Chunk size and max height
CHUNK_SIZE = 16 # X by Y size of each chunk
MAX_HEIGHT = 128

# Vertex Data Config
FLOATS_PER_VERTEX = 6
FLOATS_PER_DEBUG_VERTEX = 6
VERTS_PER_BLOCK = 24 # TODO: Optimize so that we only need 8
INDICES_PER_FACE = 6

# Terrain Generation settings
CAVE_NOISE_THRESHOLD = -0.4
NOISE_OCTAVES = 8
WATER_LEVEL = 32 # the height that water generates at
MAX_GEN_HEIGHT = 64 # the height that water generates at

# Graphics
AO_CLIPPING_STRENGTH = 0.125

# Physics stuff
GRAVITY = glm.vec3(0.0, -19.62, 0.0) # This is 2 times the strength of real gravity, but it feels nicer.
COLLISION_DAMPING = 0.75 # Accounts for friction and collision velocity correction
PLAYER_COLLISION_WIDTH = 0.75
PLAYER_COLLISION_HEIGHT = 1.8
PLAYER_JUMP_HEIGHT = 1.3
JUMP_POWER = math.sqrt(PLAYER_JUMP_HEIGHT * -GRAVITY.y * 2) # dy - (1/2)(a*dt^2) = vi

# Game stuff
PLAYER_HEIGHT = 1.7 # Average height of a man in meters
MOVEMENT_SPEED = 1.0
SPRINT_SPEED = 1.5
DAY_MINUTES = 1
TICKS_PER_SECOND = 16
FoV = 90

# Ray casting and interaction stuff
MAX_INTERACTION_DIST = 32 # in blocks
STEPS_PER_RAY_UNIT = 8 # How many steps it'll take to move the space of a block
RAY_CAST_REFINES = 8 # DON'T PUT BELOW 4!!!
