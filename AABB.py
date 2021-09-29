# Imports
# Math
import glm
# Settings
from settings import GRAVITY, TICKS_PER_SECOND

from mesh import DebugMesh

class CollisionData:
    def __init__(self, colliding : bool, axialOverlap1 : glm.vec3, axialOverlap2 : glm.vec3):
        self.colliding = colliding
        self.overlap1 = axialOverlap1
        self.overlap2 = axialOverlap2

        self.correctionVector = glm.vec3(0.0)
        self.collisionAxis = None
        self.CalculateCorrectionVector()

    def CalculateCorrectionVector(self):
        absOverlaps1 = [abs(o) for o in self.overlap1]
        absOverlaps2 = [abs(o) for o in self.overlap2]

        minOverlap1 = min(absOverlaps1)
        minOverlap2 = min(absOverlaps2)

        overallMin = min([minOverlap1, minOverlap2])

        o1min = overallMin == minOverlap1

        overlapIndex = absOverlaps1.index(overallMin) if o1min else absOverlaps2.index(overallMin)
        self.collisionAxis = overlapIndex

        collisionDelta = 0.001

        correctionAmount = self.overlap1[overlapIndex] + collisionDelta if o1min else -(self.overlap2[overlapIndex] + collisionDelta)
        self.correctionVector[overlapIndex] = correctionAmount
        
class AABB:
    def __init__(self, center, dimensions = glm.vec3(1.0), debugBoxColor = None, positionCentered = True):
        self.dimensions = glm.vec3(dimensions)

        if positionCentered:
            self.position = glm.vec3(center) - self.dimensions / 2
        else:
            self.position = glm.vec3(center)

        if debugBoxColor is not None:
            self.SetupDebugBox(debugBoxColor)

        # physics stuff
        self.active = False
        self.acceleration = GRAVITY
        self.velocity = glm.vec3(0.0)

    def SetupDebugBox(self, color : glm.vec3):
        x, y, z = glm.vec3(0.0)
        X, Y, Z = self.dimensions

        vertices = [
            # A list of all possible vertices
            x, y, z, color.x, color.y, color.z,
            X, y, z, color.x, color.y, color.z,
            X, Y, z, color.x, color.y, color.z,
            x, Y, z, color.x, color.y, color.z,

            x, y, Z, color.x, color.y, color.z,
            X, y, Z, color.x, color.y, color.z,
            X, Y, Z, color.x, color.y, color.z,
            x, Y, Z, color.x, color.y, color.z,
        ]
        indices = [
            # Front side
            0, 1, 1, 2, 2, 3, 3, 0,
            # Back side
            4, 5, 5, 6, 6, 7, 7, 4,
            # Left side
            4, 0, 0, 3, 3, 7, 7, 4,
            # Right side
            1, 5, 5, 6, 6, 2, 2, 1,
            # Top side
            3, 2, 2, 6, 6, 7, 7, 3,
            # Bottom side
            0, 1, 1, 5, 5, 4, 4, 0,
        ]

        self.debugMesh = DebugMesh(vertices, indices)
        self.debugBoxModelMat = glm.translate(glm.mat4(1.0), self.position)

    def setPosition(self, position):
        self.position = position - (self.dimensions / 2)

    def addToPosition(self, offset):
        self.position += offset

    def GetCollisionData(self, box):
        ox1 = box.dimensions.x - self.position.x + box.position.x
        oy1 = box.dimensions.y - self.position.y + box.position.y
        oz1 = box.dimensions.z - self.position.z + box.position.z

        ox2 = self.dimensions.x - box.position.x + self.position.x
        oy2 = self.dimensions.y - box.position.y + self.position.y
        oz2 = self.dimensions.z - box.position.z + self.position.z

        colliding = ox1 > 0 and oy1 > 0 and oz1 > 0 and ox2 > 0 and oy2 > 0 and oz2 > 0

        return CollisionData(colliding, glm.vec3(ox1, oy1, oz1), glm.vec3(ox2, oy2, oz2))

    def update(self, dt):
        # TODO: Fix this so that it processes physics anyway (should resolve with Mesh.addData() being fixed)
        if dt < 1 / TICKS_PER_SECOND and self.active:
            # Accelerate velocity for gravity
            self.velocity += self.acceleration * dt

            # Add velocity to position
            self.position += self.velocity * dt

            self.reloadDebugModelMatrix()

    def reloadDebugModelMatrix(self):
        try:
            self.debugBoxModelMat = glm.translate(glm.mat4(1.0), self.position)
        except AttributeError:
            pass
            
    def collideWithActive(self, box):
        """
        For collisions with other moving objects like entities that will react to the collision as well.
        """
        collisionData = self.GetCollisionData(box)

    def collideWithPassive(self, box):
        """
        For collisions with stationary objects like blocks that will NOT react to the collision.
        i.e. only this AABB will collide and react.
        """
    def DrawDebug(self, shader):
        try:
            shader.use()
            shader.setMat4("modelMatrix", self.debugBoxModelMat)
            self.debugMesh.Draw()
        except AttributeError:
            pass
