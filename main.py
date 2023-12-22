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

#JIT (numba)
from numba import njit, float64
from numba.experimental import jitclass


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
RENDER_DISTANCE = 30

@jitclass([("__values", float64[::1])]) #define __values to be a list of contiguous floats
class Vector3(): #Define a class for 3d vectorss

    #class methods would work better here but theyre not compatible with jit
    @staticmethod #static method to add two vectors and return a third one
    def addVectors(vectorA, vectorB):
        result = []
        for i in range(3):
            result.append(vectorA.val[i]+vectorB.val[i])
        return Vector3(result) #returns a vector with the summed values as its instantiation inputs
    
    @staticmethod #static method to sub two vectors and return a third one
    def subtractVectors(vectorA, vectorB):
        result = []
        for i in range(3):
            result.append(vectorA.val[i]-vectorB.val[i])
        return Vector3(result) #returns a vector with the summed values as its instantiation inputs
    
    @staticmethod #static method to dot product two vectors
    def dot(vectorA, vectorB):
        result = 0
        for i in range(3):
            result += (vectorA.val[i] * vectorB.val[i])
        return result
    
    @staticmethod #static method to cross product two vectors
    def cross(vectorA, vectorB):
        result = []
        for t in [(1,2),(2,0),(0,1)]: #based on mathematical definition of cross product
            result.append(vectorA.val[t[0]]*vectorB.val[t[1]] - vectorA.val[t[1]]*vectorB.val[t[0]])
        return Vector3(result) #returns a vector with the cross product as its instantiation inputs
    
    def __init__(self, arg):
        #Note: In order to work with the vector3 function, we must pass in a numpy array with a defined data type of float64 for all values.
        self.__values = np.array(arg, dtype=np.float64)

    @property #decorator marks this as being a property. This is just a getter function so this is appropriate
    def val(self): #return value
        return self.__values
    
    #setter function to change the value of the vector
    def setVal(self, a):
        self.__values = np.array(a, dtype=np.float64)

    #add values to existing vals
    def addVal(self, a):
        for i in range(3):
            self.__values[i] += a[i]
    
    def magnitude(self): #returns magnitude
        return (self.__values[0]**2 + self.__values[1]**2 + self.__values[2]**2)**(0.5)
    
    def setAt(self, n, val): #sets the value of the varable at n to val
        self.__values[n] = val
    
    def normalise(self): #normalises vectors. Since we can't import our zero vector into here since it uses a numpy definition, we need to set a fallback whenever we call this function instead.
        magnitude = self.magnitude()
        if magnitude == 0:
            return Vector3([0,0,0])
        else:
            return Vector3([
                self.val[0] / magnitude,
                self.val[1] / magnitude,
                self.val[2] / magnitude])

class Camera:
    up = Vector3([0, 1, 0]) #global definition of up independent of the camera
    #note that with Vector3, we must define all our numbers to be an ARRAY (not list) where each number is a 64 bit float

    def __init__(self, position):
        self.__eulerAngles = Vector3([0,0,0]) #yaw, pitch, roll
        self.__position = Vector3(position)    #x, y ,z
        self.__velocity = Vector3([0, 0, 0])
        self.__acceleration = Vector3([0,0,0])
        self.__front = Vector3([0,0,0])
        self.__right = Vector3([0,0,0])
        self.__up = Vector3([0, 1, 0])
        self.__angleofattack = 0

        self.__mass = 1100
        self.__wingArea = 17

    def getPos(self):
        return self.__position

    def getXZ(self): #relevant as determining the position of the plane on a 2d coordinate map will only require XZ coordinates, Y is irrelevant
        return [self.__position.val[0], self.__position.val[2]]

    def getDir (self):
        return self.__eulerAngles

    def update(self, keys, mouse, deltaTime):
        #Handles the lookat system and camera movement

        speed = 0.2
        direction = Vector3([0, 1, 0])

        #camera direction
        self.__eulerAngles.addVal(np.array([mouse[0]/4, -mouse[1]/4, 0], dtype=np.float64)) #yaw, pitch, roll
        if self.__eulerAngles.val[1] > 89: #keep pitch to 180 degree bounds
            self.__eulerAngles.setAt(1,89)
        if self.__eulerAngles.val[1] < -89:
            self.__eulerAngles.setAt(1,-89)
        self.__eulerAngles.setAt(0,self.__eulerAngles.val[0] % 360) #keep yaw within the bounds

        #From drawing trigonemtric diagrams:
        direction.setVal([math.cos(math.radians(self.__eulerAngles.val[0])) * math.cos(math.radians(self.__eulerAngles.val[1])),
        math.sin(math.radians(self.__eulerAngles.val[1])),
        math.sin(math.radians(self.__eulerAngles.val[0])) * math.cos(math.radians(self.__eulerAngles.val[1]))])
        self.__front = direction.normalise() #get the front normalised vector
        self.__right = (Vector3.cross(Camera.up, self.__front)).normalise()
        self.__up = Vector3.cross(self.__front, self.__right)



        if keys[K_q]: #thrust testing
            self.__resolveForces(1000, deltaTime)
        else:
            self.__resolveForces(0, deltaTime)

        text(0, 600, (1, 0, 0), "G-Force: "+str((self.__acceleration.magnitude())/(self.__mass*9.81)))
        text(0, 560, (1, 0, 0), "Velocity: "+str(self.__velocity.val))
        text(0, 520, (1, 0, 0), "Acceleration: "+str(self.__acceleration.val))
        text(0, 480, (1, 0, 0), "Front: "+str(self.__front.val))

        self.__velocity = Vector3.addVectors(self.__velocity, self.__acceleration)
        
        if self.__velocity.magnitude() > 65:
            Vector3.subtractVectors(self.__velocity, self.__acceleration)

        newPos = []
        for i in range(3): #3 values in a Vector3
            newPos.append(self.__position.val[i]+self.__velocity.val[i]*0.001*deltaTime) #moves the plane, reduces scale by 10000x
        self.__position.setVal(newPos)

        # Handle movement input
        if keys[K_w]:
            newPos = []
            for i in range(3):
                newPos.append(self.__position.val[i]+self.__front.val[i]*speed)
            self.__position.setVal(newPos)
        if keys[K_s]:
            newPos = []
            for i in range(3):
                newPos.append(self.__position.val[i]-self.__front.val[i]*speed)
            self.__position.setVal(newPos)
        if keys[K_a]:
            newPos = []
            for i in range(3):
                newPos.append(self.__position.val[i]+self.__right.val[i]*speed)
            self.__position.setVal(newPos)
        if keys[K_d]:
            newPos = []
            for i in range(3):
                newPos.append(self.__position.val[i]-self.__right.val[i]*speed)
            self.__position.setVal(newPos)

        glLoadIdentity() #as per explanation in https://stackoverflow.com/questions/54316746/using-glulookat-causes-the-objects-to-spin
        gluLookAt(*self.__position.val, *Vector3.addVectors(self.__position, self.__front).val, *self.__up.val) #use stars to unpack

    def __resolveForces(self, thrust, deltaTime):

        self.__angleofattack = math.degrees(math.asin(
            Vector3.subtractVectors(self.__front, self.__velocity.normalise()).normalise().val[1],
            )) #via trigonemtry. We normalise twice, once to get rid of velocity magnitude, second time to simplifcy c=a/h calculation

        text(0, 440, (1, 0, 0), "Angle of Attack: "+str(self.__angleofattack))
        
        if abs(self.__angleofattack) > 14.75: #causes stalling
            c_l, c_d = naca2412_airfoil["14.75"]
        else:
            self.__angleofattack = 0.25 * round(self.__angleofattack*4) #rounds to closest 0.25
            c_l, c_d = naca2412_airfoil[str(self.__angleofattack)] #get angle of attack coefficent values from database

        lift = 0.5 * self.__velocity.magnitude()**2  * self.__wingArea * c_l * 1.2 #1.2 is the density of air
        drag = 0.5 * self.__velocity.magnitude()**2  * self.__wingArea * c_d * 1.2

        if lift > 10000: #set upper cap for lift in case of bug
            lift = 50000
        if drag > 10000: #set upper cap for drag in case os
            drag = 50000

        self.__angleofattack = math.radians(self.__angleofattack)

        vertical = (thrust-drag) * abs(math.sin(self.__angleofattack)) + lift * math.cos(self.__angleofattack) - 9.81*self.__mass
        horizontal = (thrust-drag) * math.cos(self.__angleofattack) - lift * abs(math.sin(self.__angleofattack))

        text(0, 400, (1, 0, 0), "Vertical: "+str(vertical))
        text(0, 360, (1, 0, 0), "Horizontal: "+str(horizontal))
        text(0, 320, (1, 0, 0), "Lift: "+str(lift))
        text(0, 280, (1, 0, 0), "Drag: "+str(drag))

        if thrust < drag: #act against velocity to slow down plane.
            self.__acceleration = Vector3([ # x y z
                (horizontal*deltaTime*self.__velocity.normalise().val[0])/self.__mass,
                (vertical*deltaTime)/self.__mass,
                (horizontal*deltaTime*self.__velocity.normalise().val[2])/self.__mass
            ])
        else:
            self.__acceleration = Vector3([ # x y z
                (horizontal*deltaTime*self.__front.val[0])/self.__mass,
                (vertical*deltaTime)/self.__mass,
                (horizontal*deltaTime*self.__front.val[2])/self.__mass
            ])

        return 1



def checkforcollision(triangles, Camera):
    for triangle in triangles:
        p1 = Vector3(list(triangle[0]))
        p2 = Vector3(list(triangle[1]))
        p3 = Vector3(list(triangle[2]))
        normal = Vector3.cross(Vector3.subtractVectors(p2,p1),
                               Vector3.subtractVectors(p3,p1))
        if Vector3.dot(normal, Camera.getPos()) <= Vector3.dot(normal, p1):
            text(800, 800, (1, 0, 0), "CRASHED!")

def mapGen(heightmap, colourmap, watermask):
    #Create our matrix for both the surface and the colours
    vertList = []
    coloursList = [(0,0.3,0.8)] #space 0 reserved for ocean tile colour
    for zcord in range(ZLENGTH):
        for xcord in range(XLENGTH):
            if watermask[zcord][xcord][0] != 0: # => water tile as defined in the mask
                vertList.append((xcord,0.3,zcord)) #so render as an ocean tile
                coloursList.append((0.85+uniform(-0.05,0.05),0.95+uniform(-0.05,0.05),0.85+uniform(-0.05,0.05))) #generic lowlying land colour. Already check in map generating function if a tile is at sea level, so this is simply the colour for terrain sloping into sea level.
                coloursList.append((0.85+uniform(-0.05,0.05),0.95+uniform(-0.05,0.05),0.85+uniform(-0.05,0.05))) #We do this twice since each "pixel" corresponds to two polygons.
            else:
                vertList.append((xcord,heightmap[zcord][xcord]/75,zcord))
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

                if abs(bearing-yaw) > 100 and abs(bearing-yaw) < 280 and bearing>0 and pitch>-75: #If the vertice is more than 100 degrees away from the yaw, do not render. Also renders every tile if looking straight down, to preserve illusion
                    pass

                else:
                    #the two triangles adjacent to any vertex
                    if mapMatrix[i][1] == mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == 0.3: #This is only true if all three corners are at sea level
                        verticelist.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH],coloursList[0]))
                    else:
                        verticelist.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH],coloursList[2*i+1]))
                    if mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == mapMatrix[i+XLENGTH+1][1] == 0.3: #This is only true if all three corners are at sea level
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

    mainCam = Camera((250,4,250)) #position
    glClearColor(25/255, 235/225, 235/225, 0) #sets the colour of the "sky"

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    print("Display initialised")    #test

    mapMatrix, coloursList = mapGen(heightmap, colourmap, watermask)
    print("Map Generated")    #test

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

    currTime=pg.time.get_ticks() # initialise program clock
    
    while True: #allows us to actually leave the program
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
    
            if event.type == pg.KEYDOWN:
                #regenerate the map for debugging purposes
                if event.key == pg.K_r:
                    mapMatrix, coloursList = mapGen(heightmap, colourmap, watermask)
                    pg.time.wait(1)

                #dedicated crash button
                if event.key == pg.K_c:
                    raise Exception("developer forced crash")

        #clear buffer
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        try:
            timeTaken=1000/((pg.time.get_ticks()-currTime))
        except Exception: #divide by zero sometimes happens when a frame is rendered instantly
            timeTaken = 1000 # small value of t

        currTime=pg.time.get_ticks()

        #update the camera with input from the user
        mouse = pg.mouse.get_rel()
        keys = pg.key.get_pressed()
        mainCam.update(keys, mouse, (1/timeTaken))
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')
        text(0, 750, (1, 0, 0), str(mainCam.getPos().val))
        text(0, 800, (1, 0, 0), str(mainCam.getDir().val))

        #generate the visible terrain
        verticelist, colCheck = genTerrain(mapMatrix, coloursList, *mainCam.getXZ(), mainCam.getDir().val[0], mainCam.getDir().val[1])
        renderTriangle(verticelist)
        checkforcollision(colCheck, mainCam)

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(2)
        
if __name__ == "__main__":
    main()
