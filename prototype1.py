#thank you to https://en.wikibooks.org/wiki/OpenGL_Programming/Installation/Linux for helping me install OpenGL
# resources used:
# https://stackabuse.com/advanced-opengl-in-python-with-pygame-and-pyopengl/

# Init:
import pygame as pg
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

print("Packages successfully loaded.")

#Principles of rendering:
#Every object in OpenGL is a collection of points; lines that connect pairs of points; triangles composed of three points; quads composed of four points etc etc
cubeVertices = ((1,1,1),(1,1,-1),(1,-1,-1),(1,-1,1),(-1,1,1),(-1,-1,-1),(-1,-1,1),(-1,1,-1)) #Points of a 2x2x2 cube
#every edge is given a number, from 0 through to 7, based on its position in our array. To join them:
cubeEdges = ((0,1),(0,3),(0,4),(1,2),(1,7),(2,5),(2,3),(3,6),(4,6),(4,7),(5,6),(5,7))
#Finally, connect the vertices via their number to also make a cube.
#It helps to draw a diagram at this point. The page I'm following here has this diagram:
# https://stackabuse.s3.amazonaws.com/media/advanced-opengl-in-python-pygame-and-pyopengl-2.png
cubeQuads = ((0,3,6,4),(2,5,6,3),(1,2,5,7),(1,0,4,7),(7,4,6,5),(2,3,0,1))

# draw wire cube
def wireCube():
    glBegin(GL_LINES)  # begin drawing. GL_LINES tells us we'll be drawing lines
    for cubeEdge in cubeEdges:
        for cubeVertex in cubeEdge:
            glVertex3fv(cubeVertices[cubeVertex]) 
            """
            What does this command mean?
            glVertex: defines a vertex
            glVertex3: 3-coordinate vertex
            glVertex3f: of type GLfloat
            glVertex3fv: put inside a vector (tuple) as opposed to glVertex3fl which uses a list of arguments instead
            So, we are drawing out all our vertices one by one.
            """
    glEnd() #stop drawing

#following similar logic:
def solidCube():
    glBegin(GL_QUADS)
    for cubeQuad in cubeQuads:
        for cubeVertex in cubeQuad:
            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()

def main():
    pg.init()
    display = (1680, 1050)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    while True: #allows us to actually leave the program
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        # Transformation matrix is T1 before this block of code
        #use an inbuilt openGL stack, allowing us to render multiple things:
        #glPushMatrix()
        glTranslatef(0.01,0,0)
        glRotatef(1, 1, 1, 1)
        wireCube()
        #glPopMatrix()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #solidCube()
        wireCube()
        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10)

if __name__ == "__main__":
    main()