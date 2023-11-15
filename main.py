from PIL import Image
from random import *
import numpy as np
import math

import pygame as pg
from pygame.locals import *

import threading

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from numba import njit, jit


print("Packages successfully loaded.")
#########

#import heightmap
heightmap = np.array(Image.open('heightmap.bmp'))
colourmap = np.array(Image.open('colourmap.bmp'))
#map size
ZLENGTH = len(heightmap)
XLENGTH = len(heightmap[0])
RENDER_DISTANCE = 10


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

def mapGen(heightmap, colourmap):
    #Create our matrix for both the 20x20 surface and the colours
    vertList = []
    coloursList = []
    for zcord in range(ZLENGTH):
        for xcord in range(XLENGTH):
            vertList.append((xcord/6,heightmap[zcord][xcord]/150,zcord/6))
            pixelColour = (colourmap[zcord][xcord][0]/255, colourmap[zcord][xcord][1]/255, colourmap[zcord][xcord][2]/255) #Convert from 0-255 RGB format to 0-1 RGB format
            coloursList.append(pixelColour) #define RGB values for all corresponding vertices
            coloursList.append(pixelColour) #every vertice has 2 triangles associated with it
    return np.array(vertList), np.array(coloursList)

#renders a triangle based on the coords inputted
def renderTriangle(t1, t2, t3, c):  #triangle 1, triangle 2, triangle 3, colour
    glBegin(GL_TRIANGLES)
    glColor3fv(c)
    glVertex3fv(t1)
    glVertex3fv(t2)
    glVertex3fv(t3)
    glVertex3fv(c)
    glEnd()

#we need to import all of these variables because numba won't know about them
@njit
def genTerrain(mapMatrix, coloursList, camPositionx, camPositionz):
    verticelist = []
    length = len(mapMatrix)
    try:
        for i in range(length):
            #This stops vertices at the edge from rendering triangles - this previously led to triangles being rendered across the entire map
            if i%XLENGTH == XLENGTH-1:
                pass
            elif i+XLENGTH+1 > length: #ditto but for the other edge
                pass
            elif ((camPositionx-mapMatrix[i][0])**2 + (camPositionz-mapMatrix[i][2])**2)**(1/2) > RENDER_DISTANCE:
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

def cameraSystem(camPosition, up, speed, yaw, pitch, roll):
    #returns a camera position vector. Otherwise, handles the lookat system and camera movement

    direction = [0,0,0]
    keys=pg.key.get_pressed()

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

    # Handle movement input
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

    #use stars to unpack
    glLoadIdentity() #as per https://stackoverflow.com/questions/54316746/using-glulookat-causes-the-objects-to-spin
    gluLookAt(*camPosition, *operateTuple(camPosition, camFront, '+'), *camUp)

    return camPosition, [yaw, pitch, roll]

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
    speed = 0.1

    #setup camera
    eulerAngles = [0,0,0]
    camPosition = (0,0,0)
    up = (0,1,0)

    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    print("Display initialised")    #test

    mapMatrix, coloursList = mapGen(heightmap, colourmap)
    print("Map Generated")    #test
    genTerrain(mapMatrix, coloursList, camPosition[0], camPosition[2]) #this first render is for debugging purposes
    print("Map Rendered")    #test

    #culling
    glDepthMask(GL_TRUE)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    glShadeModel(GL_SMOOTH)
    glDepthRange(0.0,1.0)

    ### RUN PROGRAM ###
    
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

        #clear buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        #Camera
        camPosition, eulerAngles = cameraSystem(camPosition, up, speed, *eulerAngles)

        #generate terrain
        verticelist = genTerrain(mapMatrix, coloursList, camPosition[0], camPosition[2])
        for coords in verticelist:
            renderTriangle(*coords)

        try:
            timeTaken=1/((pg.time.get_ticks()-timeTaken)/1000)
        except Exception: #divide by zero sometimes happens when a frame is rendered instantly
            pass
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10) #wait a bit, avoids speed of simulation from being speed of execution of code

if __name__ == "__main__":
    main()
