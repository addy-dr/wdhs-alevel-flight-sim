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

from numba import njit


print("Packages successfully loaded.")
#########

#import data
heightmap = np.array(Image.open('heightmap.bmp'))
colourmap = np.array(Image.open('colourmap.bmp'))
watermask = np.array(Image.open('watermask.bmp'))
with open("NACA2412.json", "r+") as f: #produced using the Xfoil program from .dat files freely available at http://airfoiltools.com/airfoil/details?airfoil=naca2412-il
    naca2412_airfoil = json.load(f)[1]
#map size
ZLENGTH = len(heightmap)
XLENGTH = len(heightmap[0])
RENDER_DISTANCE = 10

class Camera:
    up = (0,1,0) #global definition of up independent of the camera

    @njit
    def magnitude(vector): #used by several functions
        return (vector[0]**2 + vector[1]**2 + vector[2]**2)**(0.5)

    def __init__(self, position, speed):
        self.__eulerAngles = [0,0,0] #yaw, pitch, roll
        self.__position = position #x, y, z
        self.__velocity = (speed,0,speed)
        self.__acceleration = (0,0,0)
        self.__front = (0,0,0)
        self.__right = (0,0,0)
        self.__up = (0,1,0)
        self.__angleofattack = 0

    def getPos(self):
        return self.__position

    def getXZ(self): #relevant as determining the position of the plane on a 2d coordinate map will only require XZ coordinates, Y is irrelevant
        return [self.__position[0], self.__position[2]]

    def getDir (self):
        return self.__eulerAngles

    def update(self, keys, mouse, deltaTime):
        #Handles the lookat system and camera movement

        speed = ((self.__velocity[0]**2) * (self.__velocity[1]**2) * (self.__velocity[2]**2))**(0.5) #pythagorean theorem
        direction = [0,0,0]

        #camera direction
        self.__eulerAngles[0] += mouse[0]/4 #yaw
        self.__eulerAngles[1] -= mouse[1]/4 #pitch
        if self.__eulerAngles[1] > 89: #keep pitch to 180 degree bounds
            self.__eulerAngles[1] = 89
        if self.__eulerAngles[1] < -89:
            self.__eulerAngles[1] = -89
        self.__eulerAngles[0] = self.__eulerAngles[0] % 360 #keep yaw within the bounds

        #From drawing trigonemtric diagrams:
        direction[0] = math.cos(math.radians(self.__eulerAngles[0])) * math.cos(math.radians(self.__eulerAngles[1]))
        direction[1] = math.sin(math.radians(self.__eulerAngles[1]))
        direction[2] = math.sin(math.radians(self.__eulerAngles[0])) * math.cos(math.radians(self.__eulerAngles[1]))
        self.__front = normalise(*tuple(direction)) #get the front normalised vector
        self.__right = normalise(*np.cross(Camera.up, self.__front))
        self.__up = np.cross(self.__front, self.__right)

        if keys[K_q]: #thrust testing
            self.resolveForces(1, deltaTime)
            pg.time.wait(1)
        else:
            self.resolveForces(0, deltaTime)
            pg.time.wait(1)

        text(0, 600, (1, 0, 0), str(self.__acceleration))

        self.__velocity = operateTuple(self.__velocity, self.__acceleration)

        newPos = ()
        for i in range(len(self.__front)):
            newPos += ((self.__position[i]+self.__velocity[i]*deltaTime),)
        self.__position = newPos

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

        glLoadIdentity() #as per https://stackoverflow.com/questions/54316746/using-glulookat-causes-the-objects-to-spin
        gluLookAt(*self.__position, *operateTuple(self.__position, self.__front), *self.__up) #use stars to unpack

    def resolveForces(self, Thrust, deltaTime, Area = 16.2, mass = 1100):
        
        self.__angleofattack = math.degrees(math.asin(np.dot(self.__front[1],self.__velocity[1])/(Camera.magnitude(self.__front)*Camera.magnitude(self.__velocity)))) #by definition of dot product

        if abs(self.__angleofattack) > 14.75: #causes stalling
            c_d = 0
            c_l = 0
        else:
            self.__angleofattack = 0.25 * round(self.__angleofattack/0.25) #rounds to closest 0.25
            c_l, c_d = naca2412_airfoil[str(self.__angleofattack)] #get angle of attack coefficent values from database

            lift = 0.5 * Camera.magnitude(self.__velocity*200)**2  * Area * c_l
            drag = 0.5 * Camera.magnitude(self.__velocity*200)**2  * Area * c_d


            vertical = (Thrust-drag) * math.sin(self.__angleofattack) + lift * math.cos(self.__angleofattack) - 9.81*mass
            horizontal = (Thrust-drag) * math.cos(self.__angleofattack) - lift * math.sin(self.__angleofattack)
            print(c_d,c_l,lift,drag,vertical, horizontal, deltaTime,Camera.magnitude(self.__velocity)**2)

            self.__acceleration = ((0.001*horizontal*deltaTime*self.__front[0])/mass,(0.001*vertical*deltaTime)/mass,(0.001*horizontal*deltaTime*self.__front[2])/mass) # x y z

@njit #Normalises 3d vectors
def normalise(a,b,c,*d): #*d handles any other data passed into the function that is irrelevant
    magnitude = (a**2 + b**2 + c**2)**(0.5)
    if magnitude == 0:
        return (0,0,0)
    else:
        return (a/magnitude, b/magnitude, c/magnitude)

#Adds tuples with each other.
#doesnt work with njit unfortunately
def operateTuple(a,b):
    result = ()
    for i in range(len(a)):
        result += (a[i]+b[i],)
    return result

def checkforcollision(triangles, Camera):
    for triangle in triangles:
        p1 = triangle[0]
        p2 = triangle[1]
        p3 = triangle[2]
        normal = np.cross(p2-p1, p3-p1)
        if np.dot(normal, Camera.getPos()) <= np.dot(normal, p1):
            text(800, 800, (1, 0, 0), "CRASHED!")

def mapGen(heightmap, colourmap, watermask):
    #Create our matrix for both the surface and the colours
    vertList = []
    coloursList = [(0,0.3,0.8)] #space 0 reserved for ocean tile colour
    for zcord in range(ZLENGTH):
        for xcord in range(XLENGTH):
            if watermask[zcord][xcord][0] != 0: # => water tile as defined in the mask
                vertList.append((xcord/3,0.75,zcord/3)) #so render as an ocean tile
                coloursList.append((0.56+uniform(-0.05,0.05),0.72+uniform(-0.05,0.05),0.48+uniform(-0.05,0.05))) #generic lowlying land colour. Already check in map generating function if a tile is at sea level, so this is simply the colour for terrain sloping into sea level.
                coloursList.append((0.56+uniform(-0.05,0.05),0.72+uniform(-0.05,0.05),0.48+uniform(-0.05,0.05))) #We do this twice since each "pixel" corresponds to two polygons.
            else:
                vertList.append((xcord/3,heightmap[zcord][xcord]/150,zcord/3))
                pixelColour = ((colourmap[zcord][xcord][0]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][1]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][2]/255)+uniform(-0.05,0.05)) #Convert from 0-255 RGB format to 0-1 RGB format. Random number adds colour variation for aesthetic purposes
                coloursList.append(pixelColour) #define RGB values for all corresponding vertices
                #We do this twice since each "pixel" corresponds to two polygons. We can afford to take more processing while loading the map at this stage.
                pixelColour = ((colourmap[zcord][xcord][0]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][1]/255)+uniform(-0.05,0.05), (colourmap[zcord][xcord][2]/255)+uniform(-0.05,0.05))
                coloursList.append(pixelColour)
    return np.array(vertList), np.array(coloursList)

def triThreePoints(p1,p2,p3,c):
    glColor3fv(c)
    glVertex3fv(p1)
    glVertex3fv(p2)
    glVertex3fv(p3)

#renders a mesh of triangles based on the coords inputted
def renderTriangle(vertices):  #format of each entry: vertex 1, vertex 2, vertex 3, colour
    glBegin(GL_TRIANGLES)
    while vertices != []:
        #Implement parallelisation here
        triThreePoints(*vertices.pop()) #doing this allows up to parallelise since all threads use one stack
    glEnd()

#we need to import all of these variables because numba won't know about them
@njit
def genTerrain(mapMatrix, coloursList, camPositionx, camPositionz, yaw, pitch):
    verticelist, collisionCheckList = [], []
    #We define an inner function so we can calculate arctan.This is since we can't import math or numpy into this njit func.
    #To calculate arctan, we use taylor series. This only works for small input values (here <0.1), so we otherwise use a trig identity derived from the arctan addition formula (found on https://en.wikipedia.org/wiki/List_of_trigonometric_identities) which can be expressed as arctanx = 2 * arctan(x / (1 + sqrt(1 + x^2)))
    #We use a loop to reduce x until it is smaller than 0.1, and then multiply by 2 by how many times we reduced it, essentially causing a cascading effect to get arctan.
    #cant use recursion here as njit doesnt support it
    def arctan(x):
        i = 0
        while abs(x) > 0.1:
            x = x / (1 + (1 + x*x)**0.5)
            i += 1
        return (360/(2*3.1416)) * (x - (x**3)/3 + (x**5)/5 - (x**7)/7 + (x**9)/9 - (x**11)/11) * 2**i
    
    length = len(mapMatrix)
    try:
        for i in range(length):                   
            if ((camPositionx-mapMatrix[i][0])**2 + (camPositionz-mapMatrix[i][2])**2)**(1/2) > RENDER_DISTANCE: #only renders triangles within the render distance
                pass
            elif i+XLENGTH+1 > length: #This stops vertices at the edge from rendering triangles - this previously led to triangles being rendered across the entire map
                pass
            elif i%XLENGTH == XLENGTH-1: #same as above but for other edge
                pass
            else:
                if ((camPositionx-mapMatrix[i][0])**2 + (camPositionz-mapMatrix[i][2])**2)**(1/2) < 1: # check for collision
                    collisionCheckList.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH]))
                    collisionCheckList.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],mapMatrix[i+XLENGTH+1]))

                if (mapMatrix[i][0]-camPositionx) < 0: #Calculate the bearing of the vertice from the x axis
                    bearing = 180 - abs(arctan((mapMatrix[i][2]-camPositionz)/(mapMatrix[i][0]-camPositionx)))
                else:
                    bearing = abs(arctan((mapMatrix[i][2]-camPositionz)/(mapMatrix[i][0]-camPositionx)))

                if (mapMatrix[i][2]-camPositionz) < 0:
                    bearing = 360-bearing

                if abs(bearing-yaw) > 100 and abs(bearing-yaw) < 280 and bearing>0 and pitch>-75: #If the vertice is more than 100 ddegrees away from the yaw, do not render
                    pass

                else:
                    #the two triangles adjacent to any vertex
                    if mapMatrix[i][1] == mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == 0.75: #This is only true if all three corners are at sea level
                        verticelist.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH],coloursList[0]))
                    else:
                        verticelist.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH],coloursList[2*i+1]))
                    if mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == mapMatrix[i+XLENGTH+1][1] == 0.75: #This is only true if all three corners are at sea level
                        verticelist.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],mapMatrix[i+XLENGTH+1],coloursList[0]))
                    else:
                        verticelist.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],mapMatrix[i+XLENGTH+1],coloursList[2*i+2]))
    except Exception: #invalid triangle, avoid crashing and dont render it instead
        pass
    return verticelist, collisionCheckList

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

    display = (1920, 1080)
    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    mainCam = Camera((30,3,60), 0.1) #position, speed (speed is a placeholder variable)
    glClearColor(25/255, 235/225, 235/225, 0) #sets the colour of the "sky"

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    print("Display initialised")    #test

    mapMatrix, coloursList = mapGen(heightmap, colourmap, watermask)
    print("Map Generated")    #test

    genTerrain(mapMatrix, coloursList, *mainCam.getXZ(), mainCam.getDir()[0], mainCam.getDir()[1]) #this first render is for debugging purposes
    print("Map Rendered")    #test

    #culling settings
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
    
            if event.type == pg.KEYDOWN:
                #regenerate the map for debugging purposes
                if event.key == pg.K_r:
                    mapMatrix, coloursList = mapGen()
                    pg.time.wait(1)

                #dedicated crash button
                if event.key == pg.K_c:
                    raise Exception("developer forced crash")
                
        timeTaken=pg.time.get_ticks()

        #clear buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    

        #generate the visible terrain
        verticelist, colCheck = genTerrain(mapMatrix, coloursList, *mainCam.getXZ(), mainCam.getDir()[0], mainCam.getDir()[1])
        renderTriangle(verticelist)
        checkforcollision(colCheck, mainCam)

        try:
            timeTaken=1/((pg.time.get_ticks()-timeTaken)/1000)
        except Exception: #divide by zero sometimes happens when a frame is rendered instantly
            pass

        #update the camera with input from the user
        mouse = pg.mouse.get_rel()
        keys = pg.key.get_pressed()
        mainCam.update(keys, mouse, (1/timeTaken))
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')
        text(0, 750, (1, 0, 0), str(mainCam.getPos()))
        text(0, 800, (1, 0, 0), str(mainCam.getDir()))

        pg.display.flip() #update window with active buffer contents
        while pg.time.get_ticks() % 17 != 0: #caps program at 60fps so that speed of execution is not speed of simulation
            pass

if __name__ == "__main__":
    main()
