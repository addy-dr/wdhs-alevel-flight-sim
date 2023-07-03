import pygame as pg
from pygame.locals import *
from random import *

from OpenGL.GL import *
from OpenGL.GLU import *

mapMatrix = []

print("Packages successfully loaded.")


def terrain():
    #remember: counter clockwise rotation
    for x in range(10000):
        try:
            glBegin(GL_TRIANGLES)
            glColor3f(randint(0,1), randint(0,1), 1)
            glVertex3fv(mapMatrix[x+1])
            glVertex3fv(mapMatrix[x])
            glVertex3fv(mapMatrix[x+100])
            glVertex3fv(mapMatrix[x+1])
            glEnd()
        except IndexError: #at the edge
            glEnd()
            pass

def main():
    pg.init()

    display = (1680, 1050)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    #now, generatoe the map
    for xcord in range(-50,50):
        for zcord in range(-50,50):
            mapMatrix.append((xcord,-0.5,zcord))

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

        terrain()
        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10)

if __name__ == "__main__":
    main()