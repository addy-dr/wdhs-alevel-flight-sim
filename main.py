from PIL import Image
from random import *
import numpy as np
import math
import json 

#Pygame
import pygame as pg
from pygame.locals import *

#OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from numba import njit, jit


print("Packages successfully loaded.")
#########

#import data
heightmap = np.array(Image.open('heightmap.bmp'))
colourmap = np.array(Image.open('colourmap.bmp'))
watermask = np.array(Image.open('watermask.bmp'))
with open("NACA2412.json", "r+") as f:
    naca2412_airfoil = json.load(f)[1]
#map size
ZLENGTH = len(heightmap)
XLENGTH = len(heightmap[0])
RENDER_DISTANCE = 10

class Camera:

    up = (0,1,0) #global definition of up independent of the camera

    def __init__(self, position, speed):
        self.__eulerAngles = [0,0,0] #yaw, pitch, roll
        self.__position = position #x, y, z
        self.__velocity = (speed,speed,speed)
        self.__acceleration = (0,0,0)
        self.__front = (0,0,0)
        self.__right = (0,0,0)
        self.__up = (0,1,0)

    def getPos(self):
        return self.__position

    def getXZ(self): #relevant as determining the position of the plane on a 2d coordinate map will only require XZ coordinates, Y is irrelevant
        return [self.__position[0], self.__position[2]]

    def getDir (self):
        return self.__front

    def update(self, keys, mouse):
        #returns a camera position vector. Otherwise, handles the lookat system and camera movement

        speed = ((self.__velocity[0]**2) * (self.__velocity[1]**2) * (self.__velocity[2]**2))**(0.5) #pythagorean theorem
        direction = [0,0,0]

        #camera direction
        self.__eulerAngles[0] += mouse[0]/4 #yaw
        self.__eulerAngles[1] -= mouse[1]/4 #pitch
        if self.__eulerAngles[1] > 89: #keep pitch to 180 degree bounds
            self.__eulerAngles[1] = 89
        if self.__eulerAngles[1] < -89:
            self.__eulerAngles[1] = -89

        #From drawing trigonemtric diagrams:
        direction[0] = math.cos(math.radians(self.__eulerAngles[0])) * math.cos(math.radians(self.__eulerAngles[1]))
        direction[1] = math.sin(math.radians(self.__eulerAngles[1]))
        direction[2] = math.sin(math.radians(self.__eulerAngles[0])) * math.cos(math.radians(self.__eulerAngles[1]))
        self.__front = normalise(*tuple(direction)) #get the front normalised vector
        self.__right = normalise(*np.cross(Camera.up, self.__front))
        self.__up = np.cross(self.__front, self.__right)

        # Handle movement input
        if keys[K_w]:
            newPos = ()
            for i in range(len(self.__front)):
                newPos += ((self.__position[i]+self.__front[i]*speed),)
            self.__position = newPos
        if keys[K_s]:
            newPos = ()
            for i in range(len(self.__front)):
                newPos += ((self.__position[i]-self.__front[i]*speed),)
            self.__position = newPos
        if keys[K_a]:
            newPos = ()
            for i in range(len(self.__front)):
                newPos += ((self.__position[i]+self.__right[i]*speed),)
            self.__position = newPos
        if keys[K_d]:
            newPos = ()
            for i in range(len(self.__front)):
                newPos += ((self.__position[i]-self.__right[i]*speed),)
            self.__position = newPos

        #use stars to unpack
        glLoadIdentity() #as per https://stackoverflow.com/questions/54316746/using-glulookat-causes-the-objects-to-spin
        gluLookAt(*self.__position, *operateTuple(self.__position, self.__front, '+'), *self.__up)

    def resolveForces(self, Thrust, deltaTime, Area = 16.2, mass = 1100):
        pass


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

def mapGen(heightmap, colourmap, watermask):
    #Create our matrix for both the surface and the colours
    vertList = []
    coloursList = [(0,0.3,0.8)] #space 0 reserved for ocean tile colour
    for zcord in range(ZLENGTH):
        for xcord in range(XLENGTH):
            if watermask[zcord][xcord][0] != 0: # => water tile as defined in the mask
                vertList.append((xcord/3,0.75,zcord/3)) #so render as an ocean tile
                coloursList.append((0.56+uniform(-0.05,0.05),0.72+uniform(-0.05,0.05),0.48+uniform(-0.05,0.05))) #generic lowlying land colour. Already check in map generating function if a tile is at sea level, so this is simply the colour for terrain sloping into sea level.
                coloursList.append((0.56+uniform(-0.05,0.05),0.72+uniform(-0.05,0.05),0.48+uniform(-0.05,0.05))) #We do this twice since each "pixel" corresponds to two colours.
            else:
                vertList.append((xcord/3,heightmap[zcord][xcord]/150,zcord/3))
                pixelColour = ((colourmap[zcord][xcord][0]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][1]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][2]/255)+uniform(-0.05,0.05)) #Convert from 0-255 RGB format to 0-1 RGB format. Random number adds colour variation for aesthetic purposes
                coloursList.append(pixelColour) #define RGB values for all corresponding vertices

                pixelColour = ((colourmap[zcord][xcord][0]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][1]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][2]/255)+uniform(-0.05,0.05)) #We do this twice since each "pixel" corresponds to two colours.
                coloursList.append(pixelColour)
    return np.array(vertList), np.array(coloursList)

#renders a triangle based on the coords inputted
def renderTriangle(t1, t2, t3, c):  #triangle 1, triangle 2, triangle 3, ocean tile? (not relevant here), colour
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
            else:
                #the two triangles adjacent to any vertex
                print()
                if mapMatrix[i][1] == mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == 0.75: #This is only true if all three corners are at sea level
                    verticelist.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH],coloursList[0]))
                else:
                    verticelist.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH],coloursList[2*i+1]))
                if mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == mapMatrix[i+XLENGTH+1][1] == 0.75: #This is only true if all three corners are at sea level
                    verticelist.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],mapMatrix[i+XLENGTH+1],coloursList[0]))
                else:
                    verticelist.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],mapMatrix[i+XLENGTH+1],coloursList[2*i+2]))
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

    mainCam = Camera((30,3,60), 0.5) #position, speed (speed is a placeholder variable)

    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    print("Display initialised")    #test

    mapMatrix, coloursList = mapGen(heightmap, colourmap, watermask)
    print("Map Generated")    #test
    genTerrain(mapMatrix, coloursList, *mainCam.getXZ()) #this first render is for debugging purposes
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
        
        #update the camera with input from the user
        mouse = pg.mouse.get_rel()
        keys = pg.key.get_pressed()
        mainCam.update(keys, mouse)

        #generate terrain
        verticelist = genTerrain(mapMatrix, coloursList, *mainCam.getXZ())
        for coords in verticelist:
            renderTriangle(*coords)

        try:
            timeTaken=1/((pg.time.get_ticks()-timeTaken)/1000)
        except Exception: #divide by zero sometimes happens when a frame is rendered instantly
            pass
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')
        text(0, 800, (1, 0, 0), str(mainCam.getPos()))

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10) #wait a bit, avoids speed of simulation from being speed of execution of code

if __name__ == "__main__":
    main()
