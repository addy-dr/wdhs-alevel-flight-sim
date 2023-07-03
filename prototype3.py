import pygame as pg
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

mapMatrix = []

cubeVertices = ((1,1,1),(1,1,-1),(1,-1,-1),(1,-1,1),(-1,1,1),(-1,-1,-1),(-1,-1,1),(-1,1,-1)) #Points of a 2x2x2 cube
#every edge is given a number, from 0 through to 7, based on its position in our array. To join them:
cubeEdges = ((0,1),(0,3),(0,4),(1,2),(1,7),(2,5),(2,3),(3,6),(4,6),(4,7),(5,6),(5,7))

print("Packages successfully loaded.")

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


def terrain():
    #remember: counter clockwise rotation
    glBegin(GL_TRIANGLES)
    glColor3f(1, 1, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(1, 0, 0)
    glVertex3f(1, 1, 0)
    glVertex3f(0, 0, 0)
    glEnd()

def main():
    pg.init()

    display = (1680, 1050)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    #now, generatoe the map
    for xcord in range(100):
        for ycord in range(100):
            mapMatrix.append([xcord,ycord,-1])

    while True: #allows us to actually leave the program
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        #clear buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        #culling
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glShadeModel(GL_SMOOTH)
        glDepthRange(0.0,1.0)
        
        wireCube()
        terrain()
        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10)

if __name__ == "__main__":
    main()