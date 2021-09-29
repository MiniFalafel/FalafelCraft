from OpenGL.GL import *
from glfw.GLFW import *
import time

class Window:
    def __init__(self, width=800, height=600, caption="Game Window", contextVersionMajor=3, contextVersionMinor=3,
                 resizable=True, vsync=True, samples=None):
        # Initialize GLFW and set window hints
        glfwInit()
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, contextVersionMajor)
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, contextVersionMinor)
        if resizable:
            glfwWindowHint(GLFW_RESIZABLE, GL_TRUE)
        else:
            glfwWindowHint(GLFW_RESIZABLE, GL_FALSE)

        if samples is not None:
            glfwWindowHint(GLFW_SAMPLES, samples)

        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

        # Test if window was successfully created
        self.window = glfwCreateWindow(width, height, caption, None, None)
        if self.window is None:
            print("Failed to create GLFW window")
            glfwTerminate()

        # Set context as current
        glfwMakeContextCurrent(self.window)

        # Set vsync as context is required first
        if vsync:
            glfwSwapInterval(1)
        else:
            glfwSwapInterval(0)

        # Set the viewport
        glViewport(0, 0, width, height)

        # Input variables
        self.lastPressedKey = None
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.firstMouseMovement = True

        # Set callbacks
        glfwSetFramebufferSizeCallback(self.window, self.framebuffer_size_callback)
        glfwSetKeyCallback(self.window, self.key_callback)
        glfwSetCursorPosCallback(self.window, self.cursor_position_callback)
        glfwSetMouseButtonCallback(self.window, self.mouse_button_callback)
        glfwSetScrollCallback(self.window, self.mouse_scroll_callback)

        # Time variables
        self.elapsedTime = 0
        self.firstTimeInterval = True

        # Setup loop functions
        self.loopFunctions = []

        # Width and height
        self.width = width; self.height = height

    # Input functions
    def framebuffer_size_callback(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width; self.height = height
        self.onUserResize(width, height)

    def onUserResize(self, width, height):
        """ For override """

    def key_callback(self, window, key, scancode, action, mods):
        if action == GLFW_PRESS or action == GLFW_REPEAT:
            self.onUserKeyPress(key, mods)
        else:
            self.onUserKeyRelease(key, mods)
        self.lastPressedKey = key

    def onUserKeyPress(self, key, mods):
        """ For override """

    def onUserKeyRelease(self, key, mods):
        """ For override """

    def cursor_position_callback(self, window, xpos, ypos):
        if self.firstMouseMovement:
            self.lastMouseX = xpos
            self.lastMouseY = ypos
            self.firstMouseMovement = False
        else:
            xoffset, yoffset = xpos - self.lastMouseX, self.lastMouseY - ypos
            self.onUserMouseMovement(xpos, ypos, xoffset, yoffset)
            self.lastMouseX = xpos
            self.lastMouseY = ypos

    def onUserMouseMovement(self, xpos, ypos, xoffset, yoffset):
        """ For override """

    def mouse_button_callback(self, window, button, action, mods):
        if action == GLFW_PRESS:
            self.onUserMousePress(button, mods)
        else:
            self.onUserMouseRelease(button, mods)

    def onUserMousePress(self, button, mods):
        """ For override """

    def onUserMouseRelease(self, button, mods):
        """ For override """

    def mouse_scroll_callback(self, window, xoffset, yoffset):
        self.onUserMouseScroll(xoffset, yoffset)

    def onUserMouseScroll(self, xoffset, yoffset):
        """ For override """

    # Cursor States
    def setCursorHidden(self, b):
        """ A notable difference between the cursor states hidden and disabled are what they do:
            A hidden state simply hides the cursor when it hovers over the window while a disabled
            state hides the cursor as well as prevents it from moving from the center.
        """
        if b:
            glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_HIDDEN)
        else:
            glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_NORMAL)

    def setCursorDisabled(self, b):
        """ A notable difference between the cursor states hidden and disabled are what they do:
            A hidden state simply hides the cursor when it hovers over the window while a disabled
            state hides the cursor as well as prevents it from moving from the center.
        """
        if b:
            glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)
        else:
            glfwSetInputMode(self.window, GLFW_CURSOR, GLFW_CURSOR_NORMAL)

    # Time functions
    def getTimeInterval(self):
        if not self.firstTimeInterval:
            t = time.perf_counter()
            r = t - self.elapsedTime
            self.elapsedTime = t
        else:
            r = 0
            self.firstTimeInterval = False
        return r

    # Render loop functions
    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    def addLoop(self, function):
        self.loopFunctions.append(function)

    def gameLoop(self):
        while not glfwWindowShouldClose(self.window):
            # Poll events
            glfwPollEvents()
            # Run given functions
            for i in range(len(self.loopFunctions)):
                self.loopFunctions[i]()

            # Swap buffers
            glfwSwapBuffers(self.window)

        # Terminate after exiting loop
        glfwTerminate()

