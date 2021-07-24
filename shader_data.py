# Literally just shader strings so that the main file isn't so cluttered

vertexCode = """#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in float aBrightness;
layout(location = 2) in vec2 aTexCoords;

// Uniforms
uniform mat4 modelMatrix;
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;

// Output
out vec3 FragPos;
out float Brightness;
out vec2 TexCoords;

void main()
{
    // FragPos
    FragPos = vec3(modelMatrix * vec4(aPos, 1.0));
    Brightness = aBrightness;
    // TexCoords
    TexCoords = aTexCoords.xy;
    gl_Position = projectionMatrix * viewMatrix * vec4(FragPos, 1.0);
}
"""

################################
# Skybox shader                #
################################
skyFragmentCode = """#version 330 core
out vec4 FragColor;

// Vertex Shader Output
in vec3 FragPos;

// Uniforms
uniform float sunHeight;

void main()
{
    // Declare result
    vec3 result = vec3(0.0);
    // Get the gradient factor based on y component of the fragment position
    float mixFactor = (normalize(FragPos).y + 1.0) / 2; // We do this to transform it to positive space between 0 and 1 (from -1 to 1)
    mixFactor = 1.0 - mixFactor; // Just flip the mix factor
    // Set result color
    vec3 topColor = vec3(0.3, 0.6, 0.9); // Sky blue
    vec3 bottomColor = vec3(0.6, 0.3, 0.3); // A nice darkish pink
    // Move the mix factor to bring the horizon haze up when the sun is low
    float offset = (abs(sunHeight) - 0.6) / 2;
    result = mix(topColor, bottomColor, max(min((mixFactor + offset) * 1.5, 1.0), 0.0));
    // Multiply the result by some float based on the height of the sun to make it darker
    result *= 1.0 - (sunHeight / 2);
    //result = pow(result, vec3(1.0 / 1.5));
    FragColor = vec4(result, 1.0);
}
"""

######################################
# Sun and Moon drawing shader        #
######################################
sunMoonFragmentCode = """#version 330 core
out vec4 FragColor;

// Vertex Shader Output
in vec3 FragPos;
in vec2 TexCoords;
in float Color;

// Uniforms
uniform sampler2D uCelestialTexture;

void main()
{
    // Declare result
    vec3 result = texture(uCelestialTexture, TexCoords).rgb;
    result = pow(result, vec3(1.0 / 2.2));
    FragColor = vec4(result, 1.0);
}
"""

#############################
# Block Shader              #
#############################
blockFragmentCode = """#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec2 TexCoords;
in float Brightness;

uniform sampler2D uTextureAtlas;
uniform float uSunCos;

uniform float uMinLighting = 0.4;

void main()
{
    vec4 result = texture(uTextureAtlas, TexCoords);
    result.xyz *= Brightness;
    result.xyz *= (1 - pow(uSunCos, 2)) * (1.0 - uMinLighting) + uMinLighting;
    // Return
    FragColor = result;
}
"""

#############################
# Reticle Shader            #
#############################
reticleVertexCode = """#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 2) in vec2 aTexCoords;

// Uniforms
uniform mat4 projectionMatrix;

// Output
out vec2 TexCoords;

void main()
{
    // TexCoords
    TexCoords = aTexCoords.xy;
    gl_Position = projectionMatrix * vec4(aPos, 1.0);
}
"""
reticleFragmentCode = """#version 330 core
out vec4 FragColor;

void main() {
    FragColor = vec4(0.8, 0.8, 0.8, 1.0);
}
"""