import pygame as pg
from pygame.locals import *
from random import *
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

print("Packages successfully loaded.")
#########

colours = [0.2, 0.4, 0.6, 0.8]

def mapGen():
    #Create our matrix
    tempList = []
    for zcord in range(-10,10):
        for xcord in range(-10,10):
            tempList.append((xcord/2,uniform(-1,-0.5),zcord/2)) #enables steps of 0.1m
    return np.array(tempList)

def triangulate(p1,p2,p3):
    #remember: counter clockwise rotation
    for x in range(100):
        glBegin(GL_TRIANGLES)
        glColor3f(choice(colours), choice(colours), choice(colours))
        glVertex3fv(p1)
        glVertex3fv(p2)
        glVertex3fv(p3)
        glVertex3fv(p1)
        glEnd()

def genTerrain(mapMatrix):
    try:
        for i in range(len(mapMatrix)):
            #This stops vertices at the edge from rendering triangles - this prebiously led to triangles being rendered across the entire map
            if i%20 == 19:
                pass
            else:
                triangulate(mapMatrix[i+1],mapMatrix[i],mapMatrix[i+20])
                triangulate(mapMatrix[i+1],mapMatrix[i+20],mapMatrix[i+21])
    except IndexError: #invalid triangle, avoid crashing
        pass


def main():
    pg.init()
    pg.font.init()

    my_font = pg.font.Font('freesansbold.ttf', 32)
    text_surface = my_font.render('TEST', False, (255, 255, 255))

    display = (1280, 720)

    pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glTranslatef(0.0, 0.0, -5)

    mapMatrix = mapGen()

    #screen.blit(text_surface, (0,0))

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

        genTerrain(mapMatrix)

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10) #wait a bit, avoids speed of simulation from being speed of execution of code

if __name__ == "__main__":
    main()
