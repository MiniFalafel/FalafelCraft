from OpenGL.GL import *

from PIL import Image

def load_image(filename):
    im = Image.open(filename).transpose(Image.FLIP_TOP_BOTTOM)
    return im

def get_texture_data(mode, im):
    data = None
    if mode == "RGB":
        data = im.tobytes("raw", "RGB")
    elif mode == "RGBA":
        data = im.tobytes("raw", "RGBA")
    else:
        print("ERROR::IMAGE_DATA_ERROR:\n     Image format not supported!")
        exit()
    return data

class Texture:
    def __init__(self, id):
        self.id = id

# Get texture function
def getTexture(file):
    textureID = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, textureID)
    # set filters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    #
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Get Image Data
    tex = load_image(file)
    mode = "".join(Image.Image.getbands(tex))
    if mode == "RGB":
        format = GL_RGB
    else:
        format = GL_RGBA
    data = get_texture_data(mode, tex)
    # Store the image data on the GPU
    glTexImage2D(GL_TEXTURE_2D, 0, format, tex.width, tex.height,
                 0, format, GL_UNSIGNED_BYTE, data)
    del data, tex

    rTex = Texture(textureID)
    return rTex
