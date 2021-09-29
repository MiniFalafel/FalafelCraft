# Imports
# Default
# Project Relative
#from threading import Lock, Thread
# Main
# Project Files
from player import *
from world import *
from mesh import *
from shader import *
from shader_data import *
from profiling import *
from window import *
from textures import *

from settings import MAX_INTERACTION_DIST, RAY_CAST_REFINES, STEPS_PER_RAY_UNIT
from settings import PLAYER_HEIGHT, DAY_MINUTES

import random

# Generate skybox mesh based on a size parameter
def genSkyboxMesh(skyboxWidth = 1):
    t = Timer("    genSkyboxMesh(int)")

    # Get coordinates of the two main corners
    x, y, z = (-skyboxWidth / 2, ) * 3
    X, Y, Z = ( skyboxWidth / 2, ) * 3
    # Get the positions of the vertices
    vertices = [
        x, y, z, 1.0, 0.0, 0.0,
        X, y, z, 1.0, 1.0, 0.0,
        X, Y, z, 1.0, 1.0, 1.0,
        x, Y, z, 1.0, 0.0, 1.0,
        X, y, Z, 1.0, 0.0, 0.0,
        x, y, Z, 1.0, 1.0, 0.0,
        x, Y, Z, 1.0, 1.0, 1.0,
        X, Y, Z, 1.0, 0.0, 1.0,
        x, y, Z, 1.0, 0.0, 0.0,
        x, y, z, 1.0, 1.0, 0.0,
        x, Y, z, 1.0, 1.0, 1.0,
        x, Y, Z, 1.0, 0.0, 1.0,
        X, y, z, 1.0, 0.0, 0.0,
        X, y, Z, 1.0, 1.0, 0.0,
        X, Y, Z, 1.0, 1.0, 1.0,
        X, Y, z, 1.0, 0.0, 1.0,
        x, Y, z, 1.0, 0.0, 0.0,
        X, Y, z, 1.0, 1.0, 0.0,
        X, Y, Z, 1.0, 1.0, 1.0,
        x, Y, Z, 1.0, 0.0, 1.0,
        x, y, Z, 1.0, 0.0, 0.0,
        X, y, Z, 1.0, 1.0, 0.0,
        X, y, z, 1.0, 1.0, 1.0,
        x, y, z, 1.0, 0.0, 1.0,
    ]
    # Return
    mesh = Mesh(vertices)
    return mesh

# Generate sun and moon for the sky vertices based on a size parameter
def genSunMoonMesh(sunMoonDist = 700, sunScale = 0.5, moonScale = 0.375):
    t = Timer("    genSunMoonMesh(int, float, float)")

    # Get coordinates of the two main corners
    x = -sunMoonDist / 2
    X =  sunMoonDist / 2
    # Get the positions of the vertices
    s, S = (sunScale * sunMoonDist) / 8, -(sunScale * sunMoonDist) / 8
    m, M = (moonScale * sunMoonDist) / 8, -(moonScale * sunMoonDist) / 8
    vertices = [
        x, s, S, 1.0, 0.0, 0.0,
        x, s, s, 1.0, 0.5, 0.0,
        x, S, s, 1.0, 0.5, 1.0,
        x, S, S, 1.0, 0.0, 1.0,
        X, m, m, 1.0, 0.5, 0.0,
        X, m, M, 1.0, 1.0, 0.0,
        X, M, M, 1.0, 1.0, 1.0,
        X, M, m, 1.0, 0.5, 1.0,
    ]
    # Return
    mesh = Mesh(vertices)
    return mesh

# Reticle
def genReticleMesh(size = 0.05):
    t = Timer("    genSunMoonMesh(int, float, float)")

    x = -size / 2
    X =  size / 2
    m =  size / 10

    vertices = [
        x, -m, 0, 1.0, 0.0, 0.0,
        X, -m, 0, 1.0, 0.0, 0.0,
        X, m, 0, 1.0, 0.0, 0.0,
        x, m, 0, 1.0, 0.0, 0.0,
        -m, x, 0, 1.0, 0.0, 0.0,
        m, x, 0, 1.0, 0.0, 0.0,
        m, X, 0, 1.0, 0.0, 0.0,
        -m, X, 0, 1.0, 0.0, 0.0,
    ]
    # Return
    mesh = Mesh(vertices)
    return mesh

class rayEnd:
    def __init__(self, found : bool, dirUsed : tuple, position : tuple, prevPosition : tuple):
        self.foundPos = found
        self.dir = dirUsed
        self.position = toBlockPos(position)
        self.previousBlock = toBlockPos(prevPosition)

def rayCast(startPos : glm.vec3, direction : glm.vec3, chunk : Chunk, findBreakPos = True):
    found = False

    dir = glm.normalize(direction)
    multiplier = 1.0 / STEPS_PER_RAY_UNIT

    r = rayEnd(False, dir, startPos, startPos)

    endPos = startPos.xyz
    refineStart = endPos

    for _ in range(MAX_INTERACTION_DIST * STEPS_PER_RAY_UNIT):
        endPos += multiplier * dir
        found = chunk.checkBlock(toBlockPos(endPos))

        if found:
            refineStart = endPos - multiplier * dir
            break

    # Make the steps smaller and go back a little to try and find a closer estimate for the position
    if found:
        multiplier /= 2
        refinePos = refineStart
        rFound = False
        prevPos = refineStart
        for _ in range(RAY_CAST_REFINES):
            refinePos += multiplier * dir
            rFound = chunk.checkBlock(toBlockPos(refinePos))

            if rFound:
                endPos.xyz = refinePos.xyz
                refinePos -= multiplier * dir
                multiplier /= 2
            else:
                prevPos = refinePos

        r = rayEnd(True, dir, endPos, prevPos)

    return r

# Window subclass
class GameWindow(Window):
    # Variables
    mouseLocked = False

    def __init__(self, *args, **kwargs):
        t = Timer("Window.__init__()")

        # Setup parent class constructor
        super().__init__(*args, **kwargs)

        # Schedule the update function
        self.addLoop(self.Update)

        # Game and world
        self.chunk = Chunk(0, 0, random.randint(0, 1000000))
        self.camera = Camera((0.0, MAX_HEIGHT + 4, 0.0), (0, 90, 0))
        self.player = Player(self.camera)
        self.time = 0

        # Block and debug shaders
        self.blockShader = ShaderProgram(vertexCode, blockFragmentCode)
        self.debugShader = ShaderProgram(debugVertexCode, debugFragmentCode)

        # Block usage slot
        self.blockUseIndex = 0

        # Skybox setup
        self.setupSkybox()
        # GUI
        self.setupGUI()

        # Textures
        self.setupTextures()

        self.getTimeInterval()

    # Parent class mouse input function override
    def setup2DProjection(self, width, height):
        if not self.width == 0 and not self.height == 0:
            aspectRatio = width / height
            self.OrthoProjectionMatrix = glm.ortho(-aspectRatio, aspectRatio, -1.0, 1.0)
            self.reticleShader.use()
            self.reticleShader.setMat4("projectionMatrix", self.OrthoProjectionMatrix)

    def setupSkybox(self):
        # Skybox, sun, and moon
        self.skyboxMesh = genSkyboxMesh(1)
        self.sunMoonMesh = genSunMoonMesh(1)
        # Sun and moon shaders
        self.skyShader = ShaderProgram(vertexCode, skyFragmentCode)
        self.sunMoonShader = ShaderProgram(vertexCode, sunMoonFragmentCode)

    def setupGUI(self):
        # Reticle stuff
        self.reticle = genReticleMesh()
        self.reticleShader = ShaderProgram(reticleVertexCode, reticleFragmentCode)
        self.setup2DProjection(self.width, self.height)

    def setupTextures(self):
        # Textures
        self.TEXTURE_ATLAS = getTexture('res/atlas.png')
        self.CELESTIAL_BODIES = getTexture("res/celestial_bodies.png")
        # Set their uniforms so later they only need to be bound
        # Texture atlas
        self.blockShader.use()
        self.sunMoonShader.setTexture2D("uTextureAtlas", self.TEXTURE_ATLAS.id, 0)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.TEXTURE_ATLAS.id)
        # Celestial bodies
        self.sunMoonShader.use()
        self.sunMoonShader.setTexture2D("uCelestialTexture", self.CELESTIAL_BODIES.id, 1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.CELESTIAL_BODIES.id)

    def onUserResize(self, width, height):
        self.setup2DProjection(width, height)

    def onUserMouseMovement(self, xpos, ypos, xoff, yoff):
        if self.mouseLocked:
            self.camera.processMouseMotion(xoff, yoff, 0.25)

    def onUserMouseScroll(self, xoffset, yoffset):
        self.blockUseIndex -= int(math.copysign(1, yoffset))
        self.blockUseIndex %= len(blockList)

    def onUserMousePress(self, button, mods):
        if button == GLFW_MOUSE_BUTTON_1:
            r = rayCast(self.camera.pos, self.camera.Front, self.chunk)
            if r.foundPos:
                self.chunk.addBlockToQueue(r.position, None)
        if button == GLFW_MOUSE_BUTTON_2:
            r = rayCast(self.camera.pos, self.camera.Front, self.chunk, False)
            if r.foundPos:
                self.chunk.addBlockToQueue(r.previousBlock, blockList[self.blockUseIndex])

    # Parent class keyboard input function overload
    def onUserKeyPress(self, key, mods):
        if key == GLFW_KEY_ESCAPE:
            self.mouseLocked = not self.mouseLocked
            self.setCursorDisabled(self.mouseLocked)
        # Pass the key input to the camera
        if self.mouseLocked:
            self.player.processKeyInput(key, mods, True) # Tells it that the keys are being pressed

    def onUserKeyRelease(self, key, mods):
        # Pass the key input to the camera
        self.player.processKeyInput(key, mods, False) # Tells it that the keys are being released

    def Update(self):
        t = Timer("    Window.Update()")

        dt = self.getTimeInterval()

        # Update chunk
        self.chunk.updateChunk(dt)

        self.player.updateAABS(dt)
        self.player.CollideWithChunk(self.chunk)
        self.player.updateCameraPosition()

        # Tell the chunk loader that it can now load a chunk
        #self.world.updateChunks(self.camera.pos)
        # Add to time variable
        self.time += dt / (60 * DAY_MINUTES)
        self.time = self.time % 360

        # Draw
        self.Draw(dt)

    def Draw(self, dt):
        t = Timer("    Window.Draw(float)")

        # Clear the screen
        glClearColor(1.0, 0.0, 1.0, 1.0)
        self.clear()

        ### Draw the skybox and moon/sun with no depth testing ###
        # Disable depth testing
        glDisable(GL_DEPTH_TEST)
        # Set uniforms
        self.skyShader.use() # Use it the sky shader, obviously
        self.camera.setUniformsSkybox(self.skyShader, self.width / self.height)
        # Sun height
        self.skyShader.setFloat("sunHeight", (math.sin(-self.time) + 1.0) / 2)
        # Model matrix
        model = glm.mat4(1.0)
        self.skyShader.setMat4("modelMatrix", model)
        # Draw the mesh
        self.skyboxMesh.Draw()

        # Draw the sun and moon
        # Set uniforms
        self.sunMoonShader.use() # Use it the sky shader, obviously
        # Sun and moon textures
        self.camera.setUniformsSkybox(self.sunMoonShader, self.width / self.height)
        # Model matrix
        model = glm.mat4(1.0)
        model = glm.rotate(model, -self.time, glm.vec3(0, 0, 1))
        self.sunMoonShader.setMat4("modelMatrix", model)
        # Draw the mesh
        self.sunMoonMesh.Draw()
        # Unuse the shader because we don't want to draw the world the same way
        self.skyShader.unUse()

        # World drawing
        glEnable(GL_DEPTH_TEST)
        # Use the shader
        self.blockShader.use()
        # Set uniforms
        # Camera
        self.camera.setUniforms(self.blockShader, self.width / self.height)
        self.blockShader.setFloat("uSunCos", (math.sin(-self.time) + 1.0) / 2)
        # Model Matrix
        model = glm.mat4(1.0)
        self.blockShader.setMat4("modelMatrix", model)
        # Draw the mesh
        self.chunk.Draw()

        """ Debug Boxes (for camera AABB stuff)
        # Debug Boxes/Lines
        self.debugShader.use()
        self.camera.setUniforms(self.debugShader, self.width / self.height)
        self.player.DrawDebug(self.debugShader)
        """


        # Reticle
        glDisable(GL_DEPTH_TEST)
        self.reticleShader.use()
        self.reticle.Draw()


if __name__ == '__main__':
    # Set config for antialiasing and more color depth
    window = GameWindow(1280, 720)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    window.gameLoop()
