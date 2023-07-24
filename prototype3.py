import pygame as pg
from pygame.locals import *
from random import *
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from numba import njit

print("Packages successfully loaded.")
#########

zlength = 50
xlength = 50

def mapGen():
    #Create our matrix for both the 20x20 surface and the colours
    vertList = []
    coloursList = []
    for zcord in range(-zlength//2,zlength//2):
        for xcord in range(-xlength//2,xlength//2):
            vertList.append((xcord/5,uniform(-1,-0.5),zcord/5)) #enables steps of 0.1m
            coloursList.append(((uniform(0.1,1)),(uniform(0.1,1)),(uniform(0.1,1)))) #define random RGB values for all corresponding vertices
            coloursList.append(((uniform(0.1,1)),(uniform(0.1,1)),(uniform(0.1,1)))) #every vertice has 2 triangles associated with it
    return np.array(vertList), np.array(coloursList)

def triangulate(p1,p2,p3,colour):
    #remember: counter clockwise rotation
    glBegin(GL_TRIANGLES)
    glColor3fv(colour)
    glVertex3fv(p1)
    glVertex3fv(p2)
    glVertex3fv(p3)
    glVertex3fv(p1)
    glEnd()

def genTerrain(mapMatrix, coloursList):
    try:
        for i in range(len(mapMatrix)):
            #This stops vertices at the edge from rendering triangles - this previously led to triangles being rendered across the entire map
            if i%xlength == xlength-1:
                pass
            else:
                #the two triangles adjacent to any vertex
                triangulate(mapMatrix[i+1],mapMatrix[i],mapMatrix[i+xlength],coloursList[2*i])
                triangulate(mapMatrix[i+1],mapMatrix[i+xlength],mapMatrix[i+xlength+1],coloursList[(2*i)-1])
    except IndexError: #invalid triangle, avoid crashing
        pass

#Define a text rendering framework:
def text(x, y, color, text):
    glColor3fv(color)
    glWindowPos2f(x, y)
    glutBitmapString(GLUT_BITMAP_HELVETICA_18, text.encode('ascii'))

def main():
    pg.init()
    pg.font.init()
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)

    my_font = pg.font.Font('freesansbold.ttf', 32)

    display = (1280, 720)

    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glTranslatef(0.0, 0.0, -5)

    mapMatrix, coloursList = mapGen()

    

    while True: #allows us to actually leave the program
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
    
            #regenrate the map
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    mapMatrix, coloursList = mapGen()
                    pg.time.wait(1)
        timeTaken=pg.time.get_ticks()
        keys=pg.key.get_pressed()

        #clear buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        if keys[K_w]:
            glTranslatef(0, 0, 0.2) # angle, x, y, z
        if keys[K_s]:
            glTranslatef(0, 0, -0.2)
        if keys[K_a]:
            glTranslatef(0.2, 0, 0) # angle, x, y, z
        if keys[K_d]:
            glTranslatef(-0.2, 0, -0)

        if keys[K_o]:
            glRotatef(1, 0, 0, 1) # angle, x, y, z
        if keys[K_l]:
            glRotatef(-1, 0, 0, 1)
        if keys[K_i]:
            glRotatef(-1, 0, 1, 0)
        if keys[K_k]:
            glRotatef(1, 0, 1, 0)
        if keys[K_u]:
            glRotatef(-1, 1, 0, 0)
        if keys[K_j]:
            glRotatef(1, 1, 0, 0)

        #culling
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glShadeModel(GL_SMOOTH)
        glDepthRange(0.0,1.0)

        genTerrain(mapMatrix, coloursList)
        timeTaken=1/((pg.time.get_ticks()-timeTaken)/1000)
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10) #wait a bit, avoids speed of simulation from being speed of execution of code

if __name__ == "__main__":
    main()
