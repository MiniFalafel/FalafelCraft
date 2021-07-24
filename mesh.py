# Imports
from OpenGL.GL import *
from profiling import *

from settings import CHUNK_SIZE, MAX_HEIGHT, FLOATS_PER_VERTEX, VERTS_PER_BLOCK, INDICES_PER_FACE
# Temp settings
facesPerBlock = 6

from ctypes import sizeof, c_void_p

def toGLfloats(array : list):
    return (GLfloat * len(array))(*array)
def toGLuints(array : list):
    return (GLuint * len(array))(*array)

# List nesting removal function
def removeNestings(l):
    return [item for sublist in l for item in sublist]

def genIndices(NumVertices : int):

    # Loop Through starter vertices
    indices = []
    for i in range(NumVertices // 4):
        i0 = i * 4
        indices += [i0 + j for j in range(3)]
        indices.append(i0 + 2)
        indices.append(i0 + 3)
        indices.append(i0)

    return indices

class MeshError(Exception):
    pass

class Mesh:
    def __init__(self, vertices = None):
        t = Timer("Mesh.__init__(list, list)")

        if vertices is None:
            vertices = list()

        if not len(vertices) % FLOATS_PER_VERTEX == 0:
            raise MeshError("Make sure there are 6 floats contained in each vertex:\n"
                            "    3 for position.xyz,\n"
                            "    1 for brightness,\n"
                            "    and 2 for texture coordinates xy/st/uv."
            )

        indices = genIndices(len(vertices) // FLOATS_PER_VERTEX)
        self.drawLength = len(indices)

        # Declare VAO and VBO
        self.VAO = GLuint(0); self.VBO = GLuint(0); self.EBO = GLuint(0)

        self.vertexSize = FLOATS_PER_VERTEX * sizeof(GLfloat)
        self.EndIndex = sizeof(GLfloat) * len(vertices)

        self.setupMesh(vertices, indices)

    def setupMesh(self, vertexData, indices):
        t = Timer("    Mesh.setupMesh()")

        glGenVertexArrays(1, self.VAO)
        glGenBuffers(1, self.VBO)
        glGenBuffers(1, self.EBO)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        VBOAllocSpace = len(vertexData)
        VBOData = toGLfloats(vertexData)
        if VBOAllocSpace == 0:
            VBOAllocSpace = CHUNK_SIZE * CHUNK_SIZE * MAX_HEIGHT * FLOATS_PER_VERTEX * VERTS_PER_BLOCK # The maximum number of vertex floats for a chunk
            VBOData = None # Just allocates the space with no data

        glBufferData(GL_ARRAY_BUFFER, VBOAllocSpace * sizeof(GLfloat), VBOData, GL_DYNAMIC_DRAW)

        vertSize = FLOATS_PER_VERTEX * sizeof(GLfloat)

        # Position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertSize, c_void_p(0))
        glEnableVertexAttribArray(0)

        # Colors
        glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, vertSize, c_void_p(3 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)

        # TexCoords
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, vertSize, c_void_p(4 * sizeof(GLfloat)))
        glEnableVertexAttribArray(2)

        # Element Buffer Object
        EBOAllocSpace = len(indices)
        EBOData = toGLuints(indices)
        if EBOAllocSpace == 0:
            EBOAllocSpace = CHUNK_SIZE * CHUNK_SIZE * MAX_HEIGHT * INDICES_PER_FACE * facesPerBlock # The max number of indices for a chunk
            EBOData = None

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, EBOAllocSpace * sizeof(GLuint), EBOData, GL_STATIC_DRAW)

        # Unbind
        glBindVertexArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def orphan(self):
        glBindVertexArray(self.VAO)
        # Vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        VBOAllocSpace = CHUNK_SIZE * CHUNK_SIZE * MAX_HEIGHT * FLOATS_PER_VERTEX * VERTS_PER_BLOCK  # The maximum number of vertex floats for a chunk
        glBufferData(GL_ARRAY_BUFFER, VBOAllocSpace * sizeof(GLfloat), None, GL_DYNAMIC_DRAW)

        # Index buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)

        EBOAllocSpace = CHUNK_SIZE * CHUNK_SIZE * MAX_HEIGHT * INDICES_PER_FACE * facesPerBlock  # The max number of indices for a chunk
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, EBOAllocSpace * sizeof(GLuint), None, GL_DYNAMIC_DRAW)

        # Reset draw Length
        self.drawLength = 0
        self.EndIndex = 0

    def addData(self, vertices):
        t = Timer("    Mesh.addData(list)")

        glBindVertexArray(self.VAO)

        # Vertex Buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        # Submit
        glBufferSubData(GL_ARRAY_BUFFER, self.EndIndex * sizeof(GLfloat), len(vertices) * sizeof(GLfloat), toGLfloats(vertices))
        self.EndIndex += len(vertices)

        # Index Buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        # Submit Data
        indices = genIndices(len(vertices) // FLOATS_PER_VERTEX)
        glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, self.drawLength * sizeof(GLuint), len(indices) * sizeof(GLuint), toGLuints(indices))

        self.drawLength += len(indices)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def Draw(self):
        t = Timer("    Mesh.Draw()")

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glDrawElements(GL_TRIANGLES, self.drawLength, GL_UNSIGNED_INT, None)
