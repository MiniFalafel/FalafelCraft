# Imports
from OpenGL.GL import *

# Profiling
from profiling import *

# Compile shader
def compileShader(shaderCode, shaderType):
    t = Timer("    ShaderProgram.compileShader(str, GLenum)")

    # Create the shader
    shader = glCreateShader(shaderType)
    # Set shader code from source
    glShaderSource(shader, shaderCode)
    # Compile the shader
    glCompileShader(shader)
    # Error check
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        typeStr = "VERTEX" if shaderType == GL_VERTEX_SHADER else "FRAGMENT"
        print("ERROR::%s_SHADER_COMPILE_ERROR: " %typeStr)
        print(glGetShaderInfoLog(shader))
    # Return
    return shader

# Cast matrix to array of GLfloats
def castMatrix(matrix):
    m = [y for x in matrix for y in x]
    r = (GLfloat * len(m))(*m)
    return r

class ShaderProgram:
    def __init__(self, vertexSource, fragmentSource):
        t = Timer("ShaderProgram.__init__()")

        # Compile the vertex and fragment shaders
        self.vertex = compileShader(vertexSource.encode(), GL_VERTEX_SHADER)
        self.fragment = compileShader(fragmentSource.encode(), GL_FRAGMENT_SHADER)
        # Setup the program
        CompleteShaderSetup = Timer("    ShaderProgram.__init__::Linking Shaders")
        self.ID = glCreateProgram()
        # Attach shaders
        glAttachShader(self.ID, self.vertex) # Vertex shader
        glAttachShader(self.ID, self.fragment) # Fragment shader
        # Link the program to finalize the setup
        glLinkProgram(self.ID)
        # Error check
        if (not glGetProgramiv(self.ID, GL_LINK_STATUS)):
            print("ERROR::PROGRAM_LINKING_ERROR: ")
            print(glGetProgramInfoLog(self.ID))
        del CompleteShaderSetup

    # Use/Unuse shader function
    def use(self):
        glUseProgram(self.ID)

    def unUse(self):
        glUseProgram(0)

    # Uniform setting (sends data to the shader each frame for render settings)
    # Scalars
    # Integer
    def setInt(self, name, value):
        location = glGetUniformLocation(self.ID, name.encode())
        glUniform1i(location, value)
    # Boolean
    def setBool(self, name, value):
        glUniform1i(glGetUniformLocation(self.ID, name.encode()), int(value))
    # Float
    def setFloat(self, name, value):
        glUniform1f(glGetUniformLocation(self.ID, name.encode()), value)
    # Vectors
    # 2 component vector
    def setVec2(self, name, vec):
        glUniform2f(glGetUniformLocation(self.ID, name.encode()), vec.x, vec.y)
    # 3 component vector
    def setVec3(self, name, vec):
        glUniform3f(glGetUniformLocation(self.ID, name.encode()), vec.x, vec.y, vec.z)
    # 4 component vector
    def setVec4(self, name, vec):
        glUniform4f(glGetUniformLocation(self.ID, name.encode()), vec.x, vec.y, vec.z, vec.w)
    # Matrices
    # 3x3 matrix
    def setMat3(self, name, mat):
        glUniformMatrix3fv(glGetUniformLocation(self.ID, name.encode()), 1, GL_FALSE, castMatrix(mat))
    # 4x4 matrix
    def setMat4(self, name, mat):
        glUniformMatrix4fv(glGetUniformLocation(self.ID, name.encode()), 1, GL_FALSE, castMatrix(mat))
    # Texture 2D
    def setTexture2D(self, name, texID, index):
        # Set active texture
        glActiveTexture(GL_TEXTURE0 + index)
        # Bind the texture
        glBindTexture(GL_TEXTURE_2D, texID)
        # Set the uniform
        self.setInt(name, index)
