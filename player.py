# Imports
from camera import *
from AABB import *
from chunk import *
# Settings
from settings import PLAYER_COLLISION_HEIGHT, PLAYER_COLLISION_WIDTH, PLAYER_HEIGHT,\
    JUMP_POWER, MOVEMENT_SPEED, SPRINT_SPEED, COLLISION_DAMPING

import math

class Player:
    def __init__(self, camera = None):
        if camera is None:
            self.camera = Camera()
        else:
            self.camera = camera

        self.camHeight = PLAYER_HEIGHT

        self.collisionBox = AABB(self.camera.pos - glm.vec3(0.0, PLAYER_HEIGHT - PLAYER_COLLISION_HEIGHT / 2, 0.0), glm.vec3(PLAYER_COLLISION_WIDTH, PLAYER_COLLISION_HEIGHT, PLAYER_COLLISION_WIDTH), glm.vec3(1.0, 1.0, 0.0))

        self.physBox = AABB(self.camera.pos, glm.vec3(1.0), glm.vec3(1.0, 0.0, 0.0))
        self.physBox.active = True

        self.CurrentBlockBoxes = list()

    def CollideWithChunk(self, chunk):
        checkPositions = []
        for x in range(-1, math.ceil(self.collisionBox.dimensions.x + 1)):
            for z in range(-1, math.ceil(self.collisionBox.dimensions.z + 1)):
                for y in range(-1, math.ceil(self.collisionBox.dimensions.y + 1)):
                    checkPositions.append(toBlockPos(glm.vec3(x, y, z) + self.collisionBox.position))

        self.CurrentBlockBoxes = [AABB(p + glm.vec3(0.5), glm.vec3(1.0)) for p in checkPositions]
        # FOR DEBUGGING ONLY!!!
        #self.CurrentBlockBoxes = [AABB(p + glm.vec3(0.5), glm.vec3(1.0), glm.vec3(1.0, 0.0, 1.0)) for p in checkPositions]
        for box in self.CurrentBlockBoxes:
            if chunk.checkBlock(toBlockPos(box.position)):
                collData = self.collisionBox.GetCollisionData(box)
                if collData.colliding:
                    # Adjust collision box position
                    self.collisionBox.position += collData.correctionVector
                    # Replace camera position accordingly
                    self.updateCameraPosition()
                    # Update physics box
                    self.physBox.setPosition(self.camera.pos)
                    # Set the physics velocity for the collision
                    self.physBox.velocity[collData.collisionAxis] = 0.0
                    # This is temporary!!! (maybe. It's just not good practice)
                    if collData.collisionAxis != 1:
                        self.camera.sprint = False
        self.physBox.reloadDebugModelMatrix()
        self.collisionBox.reloadDebugModelMatrix()

    def processKeyInput(self, key, mods, state):
        self.camera.processKeyInput(key, mods, state)

    def updateCameraPhysics(self, dt):

        horizontalMotion = self.physBox.velocity * glm.vec3(COLLISION_DAMPING, 0.0, COLLISION_DAMPING)

        if self.camera.forward:
            m = SPRINT_SPEED if self.camera.sprint else 1.0
            horizontalMotion += glm.normalize(self.camera.Front * glm.vec3(1.0, 0.0, 1.0)) * m # Only horizontal movement
        else:
            self.camera.sprint = False
        if self.camera.backward:
            horizontalMotion -= glm.normalize(self.camera.Front * glm.vec3(1.0, 0.0, 1.0)) # Only horizontal movement
        if self.camera.left:
            horizontalMotion -= self.camera.Right
        if self.camera.right:
            horizontalMotion += self.camera.Right
        if glm.length(horizontalMotion) > 0:
            horizontalMotion = horizontalMotion * MOVEMENT_SPEED

        if self.camera.up:
            if self.physBox.velocity.y == 0:
                self.physBox.velocity.y = JUMP_POWER

        self.physBox.velocity.x = horizontalMotion.x
        self.physBox.velocity.z = horizontalMotion.z

        self.physBox.update(dt)

    def updateAABS(self, dt):
        # Update camera movement box vectors
        self.updateCameraPhysics(dt)

        # Set the bounding box position to be the camera position
        self.collisionBox.setPosition(self.physBox.position + self.physBox.dimensions / 2 - glm.vec3(0.0, PLAYER_HEIGHT
                                      - PLAYER_COLLISION_HEIGHT / 2, 0.0))
        self.collisionBox.update(dt)

    def updateCameraPosition(self):
        # Set the camera position to be the bounding box position
        self.camera.pos = self.collisionBox.position + (self.collisionBox.dimensions / 2)
        self.camera.pos.y = self.collisionBox.position.y + PLAYER_HEIGHT

    def DrawDebug(self, shader):
        self.collisionBox.DrawDebug(shader)
        self.physBox.DrawDebug(shader)

        for box in self.CurrentBlockBoxes:
            box.DrawDebug(shader)

