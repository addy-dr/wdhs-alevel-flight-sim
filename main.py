import pygame as pg
from pygame.locals import *
from random import *
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from numba import njit, jit

print("Packages successfully loaded.")
#########

#map size
ZLENGTH = 200
XLENGTH = 200
RENDER_DISTANCE = 3

@njit
def mapGen():
    #Create our matrix for both the 20x20 surface and the colours
    vertList = []
    coloursList = []
    for zcord in range(-ZLENGTH//2,ZLENGTH//2):
        for xcord in range(-XLENGTH//2,XLENGTH//2):
            vertList.append((xcord/5,uniform(-1,-0.5),zcord/5)) #enables steps of 0.1m
            coloursList.append(((uniform(0.1,1)),(uniform(0.1,1)),(uniform(0.1,1)))) #define random RGB values for all corresponding vertices
            coloursList.append(((uniform(0.1,1)),(uniform(0.1,1)),(uniform(0.1,1)))) #every vertice has 2 triangles associated with it
    return np.array(vertList), np.array(coloursList)

def triangulate(verticelist):
    #remember: counter clockwise rotation
    for coordtuple in verticelist:
        glBegin(GL_TRIANGLES)
        glColor3fv(coordtuple[3])
        glVertex3fv(coordtuple[0])
        glVertex3fv(coordtuple[1])
        glVertex3fv(coordtuple[2])
        glVertex3fv(coordtuple[0])
        glEnd()

#we need to import all of these variables because numba won't know about them
@njit
def genTerrain(mapMatrix, coloursList, offsetx, offsetz):
    verticelist = []
    try:
        for i in range(len(mapMatrix)):
            #This stops vertices at the edge from rendering triangles - this previously led to triangles being rendered across the entire map
            if i%XLENGTH == XLENGTH-1:
                pass
            #only draw less than the render distance
            elif ((mapMatrix[i][0]+offsetx)**2 + (mapMatrix[i][2]+offsetz)**2)**0.5 > RENDER_DISTANCE:
                pass
            else:
                #the two triangles adjacent to any vertex
                verticelist.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH],coloursList[2*i]))
                verticelist.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],mapMatrix[i+XLENGTH+1],coloursList[(2*i)-1]))
    except Exception: #invalid triangle, avoid crashing
        pass
    return verticelist

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
    offsetx = 0
    offsetz = 0

    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glTranslatef(0.0, 0.0, -3.5)

    mapMatrix, coloursList = mapGen()

    #Run program:

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
            glTranslatef(0, 0, 0.1)
            offsetz+=0.1
        if keys[K_s]:
            glTranslatef(0, 0, -0.1)
            offsetz-=0.1
        if keys[K_a]:
            glTranslatef(0.1, 0, 0)
            offsetx+=0.1
        if keys[K_d]:
            glTranslatef(-0.1, 0, -0)
            offsetx-=0.1

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

        triangulate(genTerrain(mapMatrix, coloursList, offsetx, offsetz))
        timeTaken=1/((pg.time.get_ticks()-timeTaken)/1000)
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10) #wait a bit, avoids speed of simulation from being speed of execution of code

if __name__ == "__main__":
    main()
