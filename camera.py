# Imports
# Default
import math
# GLFW key codes and gl stuff
from glfw.GLFW import *
# OpenGL Mathematics
import glm

# Profiling
from profiling import *

from settings import FoV

# World up direction
WORLDUP = glm.vec3(0, 1, 0) # Positive y is the up direction/

# Camera class
class Camera(object):
    # Maximum and minimum pitch values for camera rotation
    maxY = 89
    minY = -89
    # Field of view
    FOV = FoV # Default value
    # Camera speed
    camSpeed = 3.5 # Default

    # Movement variables (true means moving in that direction and false means not moving)
    forward = False; backward = False
    right = False; left = False
    up = False; down = False
    sprint = False; crouch = False

    # Constructor
    def __init__(self, pos=(0, 0, 0), rot=(0, 0, 0), FOV = 70.0):
        t = Timer("Camera.__init__(vec3, vec3, float, float)")

        # Set position and rotation
        self.pos = glm.vec3(pos)
        self.rot = glm.vec3(rot)
        # Make directional vectors and set them up
        self.Front, self.Right, self.Up = glm.vec3(0.0)
        self.updateVectors()
        # Set FOV
        self.FOV = FOV

    def addToPos(self, deltaVec):
        self.pos += deltaVec

    # Update camera vectors
    def updateVectors(self):
        t = Timer("    Camera.updateVectors()")

        # Get the front vector
        front = glm.vec3()
        front.x = math.sin(glm.radians(self.rot.y + 180)) * math.cos(glm.radians(self.rot.x))
        front.y = math.sin(glm.radians(self.rot.x))
        front.z = math.cos(glm.radians(self.rot.y + 180)) * math.cos(glm.radians(self.rot.x))
        self.Front = glm.normalize(front)
        # Get the right vector
        self.Right = glm.normalize(glm.cross(self.Front, WORLDUP))
        # Get the up vector (the top of the camera, like the top of someone's head)
        self.Up = glm.normalize(glm.cross(self.Right, self.Front))

    # Mouse input function
    def processMouseMotion(self, dx, dy, sensitivity = 0.25):
        t = Timer("    Camera.processMouseMotion(float, float, float)")

        self.rot.x += dy * sensitivity; self.rot.y -= dx * sensitivity
        if self.rot.x > self.maxY: self.rot.x = self.maxY
        elif self.rot.x < self.minY: self.rot.x = self.minY
        # Update direction vectors with the new rotation
        self.updateVectors()

    # Keyboard input function
    def processKeyInput(self, KEY, MODS, keyPressed = True):
        t = Timer("    Camera.processKeyInput(int, int, bool)")
        # Set the movement booleans for the update function
        # Cardinal
        if KEY == GLFW_KEY_W: self.forward = keyPressed
        if KEY == GLFW_KEY_A: self.left = keyPressed
        if KEY == GLFW_KEY_S: self.backward = keyPressed
        if KEY == GLFW_KEY_D: self.right = keyPressed
        # Up and down
        if KEY == GLFW_KEY_SPACE: self.up = keyPressed
        if KEY == GLFW_KEY_LEFT_CONTROL: self.down = keyPressed
        # Sprint and crouch mods
        if MODS == GLFW_MOD_SHIFT: self.sprint = keyPressed
        if MODS == GLFW_MOD_CONTROL: self.crouch = keyPressed

    # Matrix stuff
    # Get view matrix (for shaders)
    def getViewMatrix(self):
        return glm.lookAt(self.pos, self.pos + self.Front, self.Up)

    # A view matrix getter that gets a view matrix that is not translated, but only rotated
    def getViewMatrixRotated(self):
        return glm.lookAt(glm.vec3(0), self.Front, self.Up)

    # Get projection matrix
    def getProjectionMatrix(self, aspectRatio):
        return glm.perspective(self.FOV, aspectRatio, 0.1, 1000)

    # Uniform Setting
    def setUniforms(self, shader, aspectRatio: float):
        t = Timer("    Camera.setUniforms(ShaderProgram, float)")

        # Use the shader
        shader.use()
        # Set the view matrix
        shader.setMat4("viewMatrix", self.getViewMatrix())
        # Set the projection matrix
        shader.setMat4("projectionMatrix", self.getProjectionMatrix(aspectRatio))

    # Set skybox uniforms
    def setUniformsSkybox(self, shader, aspectRatio: float):
        t = Timer("    Camera.SetUniformsSkybox(ShaderProgram, float)")

        # Use the shader
        shader.use()
        # Set the view matrix
        shader.setMat4("viewMatrix", self.getViewMatrixRotated())
        # Set the projection matrix
        shader.setMat4("projectionMatrix", self.getProjectionMatrix(aspectRatio))
