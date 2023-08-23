import pygame as pg
from pygame.locals import *
from random import *
import numpy as np
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from numba import njit, jit

print("Packages successfully loaded.")
#########

#map size
ZLENGTH = 100
XLENGTH = 100
RENDER_DISTANCE = 4

@njit #Normalises 3d vectors
def normalise(a,b,c,*d):
    magnitude = (a**2 + b**2 + c**2)**(0.5)
    if magnitude == 0:
        return (0,0,0)
    else:
        return (a/magnitude, b/magnitude, c/magnitude)

#Subtracts and adds tuples from each other.
#doesnt work with njit unfortunately
def operateTuple(a,b,operand):
    result = ()
    for i in range(len(a)):
        result += (a[i]+b[i],)
    return result

@njit
def mapGen():
    #Create our matrix for both the 20x20 surface and the colours
    vertList = []
    coloursList = []
    for zcord in range(ZLENGTH):
        for xcord in range(-XLENGTH//2,XLENGTH//2):
            vertList.append((xcord/6,uniform(-1,-0.5),zcord/6)) #enables steps of 0.1m
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
def genTerrain(mapMatrix, coloursList, camPosition):
    verticelist = []
    length = len(mapMatrix)
    try:
        for i in range(length):
            #This stops vertices at the edge from rendering triangles - this previously led to triangles being rendered across the entire map
            if i%XLENGTH == XLENGTH-1:
                pass
            elif i+XLENGTH+1 > length: #ditto but for the other edge
                pass
            elif ((camPosition[0]-mapMatrix[i][0])**2 + (camPosition[2]-mapMatrix[i][2])**2)**(1/2) > RENDER_DISTANCE:
                pass
            #only draw less than the render distance
            #elif ((mapMatrix[i][0]+offsetx)**2 + (mapMatrix[i][2]+offsetz)**2)**0.5 > RENDER_DISTANCE:
                #pass
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
    #pg.mouse.set_visible(False)
    my_font = pg.font.Font('freesansbold.ttf', 32)

    display = (1920, 1080)
    offsetx = 0 #pos of camera from origin
    offsetz = 0
    speed=0.1

    pitch = 0
    yaw = 0
    roll = 0

    #setup camera
    camPosition = (0,0,0)
    up = (0,1,0)
    camUp = (0,1,0)
    camFront = (0,0,0)
    direction = [0,0,0]

    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    print("Display initialised")

    mapMatrix, coloursList = mapGen()
    print("Map Generated")
    triangulate(genTerrain(mapMatrix, coloursList, camPosition)) #this first render is for debugging purposes
    print("Map Rendered")

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
        
        #generate terrain
        triangulate(genTerrain(mapMatrix, coloursList, camPosition))

        #culling
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glShadeModel(GL_SMOOTH)
        glDepthRange(0.0,1.0)

        if keys[K_w]:
            deltaPos = ()
            for i in range(len(camFront)):
                deltaPos += ((camPosition[i]+camFront[i]*speed),)
            camPosition = deltaPos
        if keys[K_s]:
            deltaPos = ()
            for i in range(len(camFront)):
                deltaPos += ((camPosition[i]-camFront[i]*speed),)
            camPosition = deltaPos
        if keys[K_a]:
            deltaPos = ()
            for i in range(len(camFront)):
                deltaPos += ((camPosition[i]+camRight[i]*speed),)
            camPosition = deltaPos
        if keys[K_d]:
            deltaPos = ()
            for i in range(len(camFront)):
                deltaPos += ((camPosition[i]-camRight[i]*speed),)
            camPosition = deltaPos

        #camera direction
        mouse = pg.mouse.get_rel()
        yaw += mouse[0]/4
        pitch -= mouse[1]/4
        if pitch > 89:
            pitch = 89
        if pitch < -89:
            pitch = -89

        #From drawing trigonemtric diagrams:
        direction[0] = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
        direction[1] = math.sin(math.radians(pitch))
        direction[2] = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
        camFront = normalise(*tuple(direction)) #get the front normalised vector
        camRight = normalise(*np.cross(up, camFront))
        camUp = np.cross(camFront, camRight)

        #use stars to unpack
        glLoadIdentity() #as per https://stackoverflow.com/questions/54316746/using-glulookat-causes-the-objects-to-spin
        gluLookAt(*camPosition, *operateTuple(camPosition, camFront, '+'), *camUp)

        try:
            timeTaken=1/((pg.time.get_ticks()-timeTaken)/1000)
        except Exception: #divide by zero sometimes happens when a frame is rendered instantly
            pass
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10) #wait a bit, avoids speed of simulation from being speed of execution of code

if __name__ == "__main__":
    main()
