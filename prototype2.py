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
cubeQuads = ((0,3,2,1),(2,1,7,5),(0,1,7,4),(2,3,6,5),(3,0,4,6),(4,6,5,7))
colours = ((0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(0.5,0.5,0.5),(1,1,1))
#pygame
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
    x=0
    glBegin(GL_QUADS)
    for cubeQuad in cubeQuads:
        x+=1
        for cubeVertex in cubeQuad:
            glColor3fv(colours[x])
            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()

def main():
    pg.init()

    display = (1680, 1050)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    #glEnable(GL_CULL_FACE)
    #glCullFace(GL_FRONT)

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
        keys=pg.key.get_pressed()

        #Matrices are done in REVERSE
        if keys[K_w]:
            glRotatef(1, 0, 0, 1) # angle, x, y, z
        if keys[K_e]:
            glRotatef(-1, 0, 0, 1)
        if keys[K_s]:
            glRotatef(-1, 0, 1, 0)
        if keys[K_d]:
            glRotatef(1, 0, 1, 0)
        if keys[K_q]:
            glRotatef(-1, 1, 0, 0)
        if keys[K_a]:
            glRotatef(1, 1, 0, 0)
        #glPopMatrix()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glShadeModel(GL_SMOOTH)
        glDepthRange(0.0,1.0)
        
        solidCube()
        #wireCube()
        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10)

if __name__ == "__main__":
    main()