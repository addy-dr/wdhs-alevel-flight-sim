from PIL import Image
from random import *
import numpy as np
import math
import json

# Pygame
import pygame as pg
from pygame.locals import *

# OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# JIT (numba)
from numba import njit

from maths_module import Vector3, rotate

# Error and traceback handling
from crash_handler import generateLog
import traceback


print("Packages successfully loaded.")
#########

# Import data
heightmap = np.array(Image.open('heightmap.bmp'))
colourmap = np.array(Image.open('colourmap.bmp'))
watermask = np.array(Image.open('watermask.bmp'))
with open("NACA2412.json", "r+") as f:
    # Produced using the Xfoil program from .dat files freely available at
    # http://airfoiltools.com/airfoil/details?airfoil=naca2412-il
    naca2412_airfoil = json.load(f)[1]
# Map size
ZLENGTH = len(heightmap)
XLENGTH = len(heightmap[0])
RENDER_DISTANCE = 30

class Camera:
    up = Vector3([0, 1, 0]) # Global definition of 'up' independent of the camera
    # Note that with Vector3, we must define all our numbers to be an
    # ARRAY (not list) where each number is a 64 bit float

    def __init__(self, position, takenOff):
        self.__eulerAngles = Vector3([270,0,0])   # yaw, pitch, roll
        self.__eulerAngularVelocity = Vector3([0,0,0])  # yaw, pitch, roll
        self.__position = Vector3(position)    # x, y ,z
        self.__velocity = Vector3([0, 0, 0])
        self.__acceleration = Vector3([0,0,0])
        self.__front = Vector3([0,0,0])
        self.__right = Vector3([0,0,0])
        self.__up = Vector3([0, 1, 0])

        self.__angleofattack = 0
        self.__climbangle = 0
        self.__thrust = 0
        self.__throttlePercent = 0
        self.__POWER = 754.7 * 140 #in watts, based on horsepower measurement in document

        self.__MASS = 1100
        self.__WINGAREA = 17

        self.__takeOffFlag = takenOff

    def getPos(self):
        return self.__position

    def getXZ(self):
        "Relevant as determining the position of the plane on a 2d
        # coordinate map will only require XZ coordinates, Y is irrelevant"
        return [self.__position.val[0], self.__position.val[2]]

    def getDir (self):
        return self.__eulerAngles

    def update(self, keys, deltaTime):
        "Handles the lookat system and camera movement"

        direction = Vector3([0, 1, 0])

        # Camera direction

        if keys[K_w]:   # Yaw: rudder
            if self.__eulerAngularVelocity.val[0] < 30:
                self.__eulerAngularVelocity.addVal(np.array([0.005, 0, 0], dtype=np.float64))
            text(1650, 1020, (1, 0, 0), "RUDDER: LEFT")
        elif keys[K_s]:
            if self.__eulerAngularVelocity.val[0] > -30:
                self.__eulerAngularVelocity.addVal(np.array([-0.005, 0, 0], dtype=np.float64))
            text(1650, 1020, (1, 0, 0), "RUDDER: RIGHT")
        else:   # Rudder is neutral
            text(1650, 1020, (1, 0, 0), "RUDDER: NEUTRAL")
            if abs(self.__eulerAngularVelocity.val[0]) < 0.1:
                # Prevent jittery motion from overshooting equilibrium
               self.__eulerAngularVelocity.setAt(0,0) 
            elif self.__eulerAngularVelocity.val[0] < 0:
                self.__eulerAngularVelocity.addVal(np.array([0.02, 0, 0], dtype=np.float64))
            else:
                self.__eulerAngularVelocity.addVal(np.array([-0.02, 0, 0], dtype=np.float64))

        if keys[K_e]:   # Pitch: elevator
            if self.__eulerAngularVelocity.val[1] < 30:
                self.__eulerAngularVelocity.addVal(np.array([0, 0.005, 0], dtype=np.float64))
            text(1650, 990, (1, 0, 0), "ELEVATOR: UP")
        elif keys[K_d]:
            if self.__eulerAngularVelocity.val[1] > -30:
                self.__eulerAngularVelocity.addVal(np.array([0, -0.005, 0], dtype=np.float64))
            text(1650, 990, (1, 0, 0), "ELEVATOR: DOWN")
        else:   # Elevator is neutral
            text(1650, 990, (1, 0, 0), "ELEVATOR: NEUTRAL")
        
            if abs(self.__eulerAngularVelocity.val[1]) < 0.1:
                # Prevents de-acceleration of pitch from overshooting itself
                self.__eulerAngularVelocity.setAt(1,0)
            elif self.__eulerAngularVelocity.val[1] < 0:
                self.__eulerAngularVelocity.addVal(np.array([0, 0.02, 0], dtype=np.float64))
            else:
                self.__eulerAngularVelocity.addVal(np.array([0, -0.02, 0], dtype=np.float64))
        
        # Ailerons: If both active in opposite directions, rotate.
        if keys[K_a]:   # Clockwise
            text(1650, 960, (1, 0, 0), "LEFT AILERON: DOWN")
            if self.__eulerAngularVelocity.val[2] < 30:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, 0.0025], dtype=np.float64))
        elif keys[K_q]: # Counterclockwise
            text(1650, 960, (1, 0, 0), "LEFT AILERON: UP")
            if self.__eulerAngularVelocity.val[2] > -30:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, -0.0025], dtype=np.float64))
        else:   # No roll acceleration
            text(1650, 960, (1, 0, 0), "LEFT AILERON: NEUTRAL")
            if abs(self.__eulerAngularVelocity.val[2]) < 0.1:
                self.__eulerAngularVelocity.setAt(2,0)
            elif self.__eulerAngularVelocity.val[2] < 0:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, 0.002], dtype=np.float64))
            else:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, -0.002], dtype=np.float64))
        
        if keys[K_r]:   # Clockwise
            text(1650, 930, (1, 0, 0), "RIGHT AILERON: UP")
            if self.__eulerAngularVelocity.val[2] < 30:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, 0.0025], dtype=np.float64))
        elif keys[K_f]: # Counterclockwise
            text(1650, 930, (1, 0, 0), "RIGHT AILERON: DOWN")
            if self.__eulerAngularVelocity.val[2] > -30:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, -0.0025], dtype=np.float64))
        else:   # No roll acceleration
            text(1650, 930, (1, 0, 0), "RIGHT AILERON: NEUTRAL")
            if abs(self.__eulerAngularVelocity.val[2]) < 0.1:
                self.__eulerAngularVelocity.setAt(2,0)
            elif self.__eulerAngularVelocity.val[2] < 0:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, 0.002], dtype=np.float64))
            else:
                self.__eulerAngularVelocity.addVal(np.array([0, 0, -0.002], dtype=np.float64))
            

        self.__eulerAngles.addVal(self.__eulerAngularVelocity.val)  # yaw, pitch, roll
        if self.__eulerAngles.val[1] > 89:  # Keep pitch to 180 degree bounds
            self.__eulerAngles.setAt(1,89)
        if self.__eulerAngles.val[1] < -89:
            self.__eulerAngles.setAt(1,-89)
        self.__eulerAngles.setAt(0,self.__eulerAngles.val[0] % 360) # Keep yaw within the bounds

        # From drawing trigonemtric diagrams:
        direction.setVal([math.cos(math.radians(self.__eulerAngles.val[0]))
        * math.cos(math.radians(self.__eulerAngles.val[1])),
        math.sin(math.radians(self.__eulerAngles.val[1])),
        math.sin(math.radians(self.__eulerAngles.val[0]))
        * math.cos(math.radians(self.__eulerAngles.val[1]))])

        self.__front = direction.normalise()    # Get the front normalised vector
        self.__right = (Vector3.cross(Camera.up, self.__front)).normalise()
        self.__right = rotate(self.__right, self.__front, math.radians(self.__eulerAngles.val[2]))  # Rotate right around front by roll
        self.__up = Vector3.cross(self.__front, self.__right)

        # Thrust
        if keys[K_z]:
            self.__throttlePercent += 1
        if keys[K_x]:
            self.__throttlePercent -= 1

        if self.__throttlePercent > 100:
            self.__throttlePercent = 100
        if self.__throttlePercent < 0:
            self.__throttlePercent = 0

        # Based on formula P = Fv:
        try:
            self.__thrust = (self.__POWER / self.__velocity.magnitude()) * self.__throttlePercent/100
            if self.__thrust > 8000: # Set upper cap for thrust
                self.__thrust = 8000
        except ZeroDivisionError:
            if self.__throttlePercent > 0:
                self.__thrust = 20 # Small thrust so that we can actually get out of zero velocity
            else:
                self.__thrust = 0 # In case we are perfectly still

        self.__resolveForces(deltaTime)

        # Accelerate the velocity. Make sure the value on the axes doesnt surpass 40ms⁻1,
        # which is the hardcoded limit (prevents infinite velocity from acceleration in case of drag not working)
        for i in range(0,3):
            newVelocity = self.__velocity.val[i]+self.__acceleration.val[i]
            if i == 1 and not self.__takeOffFlag:   # Code triggered if you haven't taken off yet
                if self.__acceleration.val[i] <= 0.1: # Must start accelerating up to lift off
                    newVelocity = 0
                else:
                    self.__takeOffFlag = True
            if newVelocity > 40:
                self.__velocity.setAt(i,40)
            elif newVelocity < -40:
                self.__velocity.setAt(i,-40)
            else:
                self.__velocity.setAt(i,newVelocity)

        newPos = []
        for i in range(3):  # 3 values in a Vector3
            newPos.append(self.__position.val[i]+self.__velocity.val[i]*0.001*deltaTime) #moves the plane, reduces scale by 100x
        self.__position.setVal(newPos)

        glLoadIdentity()    # As per explanation in https://stackoverflow.com/questions/54316746/using-glulookat-causes-the-objects-to-spin
        gluLookAt(*self.__position.val, *Vector3.addVectors(self.__position, self.__front).val, *self.__up.val)

        text(0, 960, (1, 0, 0), "G-Force: "+str((self.__acceleration.magnitude()+9.81)/(9.81))) # g-force = (a+g)/g
        text(0, 990, (1, 0, 0), "Velocity: "+str(self.__velocity.magnitude()))
        text(0, 1020, (1, 0, 0), "Acceleration: "+str(self.__acceleration.magnitude()))
        text(0, 900, (1, 0, 0), "Throttle: "+str(round((self.__throttlePercent)))+'%')

    def __resolveForces(self, deltaTime):

        self.__angleofattack = math.degrees(math.asin(
            Vector3.subtractVectors(self.__front, self.__velocity.normalise()).normalise().val[1],
            ))  # Via trigonemtry. We normalise twice,
            # once to get rid of velocity magnitude, second time to simplifcy c=a/h calculation
        
        self.__climbangle = math.degrees(math.asin(
            self.__front.val[1],
            ))  # Via trigonemtry. 
        
        if abs(self.__angleofattack) > 14.5:
            c_l, c_d = naca2412_airfoil["14.75"]
        else:
            self.__angleofattack = 0.25 * round(self.__angleofattack*4) # Rounds to closest 0.25
            c_l, c_d = naca2412_airfoil[str(self.__angleofattack)]  # Get angle of attack coefficent values from database

        # 1.2 is the density of air. velocity must be in the direction of front
        lift = 0.5 * Vector3.dot(self.__velocity,self.__front)**2  * self.__WINGAREA * c_l * 1.2
        drag = 0.5 * Vector3.dot(self.__velocity,self.__up)**2  * self.__WINGAREA * c_d * 1.2

        if lift > 15000: # Set upper cap for lift in case of bug
            lift = 15000
        if drag > 15000: # Set upper cap for drag in case os
            drag = 15000

        self.__angleofattack = math.radians(self.__angleofattack)
        self.__climbangle = math.radians(self.__climbangle)

        vertical = (self.__thrust-drag) * abs(math.sin(self.__climbangle)) + lift * math.cos(self.__climbangle) - 9.81*self.__MASS
        horizontal = (self.__thrust-drag) * math.cos(self.__climbangle) - lift * math.sin(self.__climbangle) 


        if self.__velocity.val[0] * self.__acceleration.val[0] > 0 and horizontal < 0: 
            # Drag would cause acceleration instead of deceleration if this is true.
            horizontal = 0

        if self.__thrust < drag:    # Act against velocity to slow down plane.
        # If removed, causes infinite acceleration due to "drag" in the opposite way the plane is facing when 0 thrust
            self.__acceleration = Vector3([ # x y z
                (horizontal*self.__velocity.normalise().val[0])/self.__MASS,
                (vertical)/self.__MASS,
                (horizontal*self.__velocity.normalise().val[2])/self.__MASS
            ])
        else:
            self.__acceleration = Vector3([ # x y z
                (horizontal*self.__front.val[0])/self.__MASS,
                (vertical)/self.__MASS,
                (horizontal*self.__front.val[2])/self.__MASS
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
            text(800, 1000, (1, 0, 0), "CRASHED!")

def mapGen(heightmap, colourmap, watermask):
    # Create our matrix for both the surface and the colours
    vertList = []
    coloursList = [(0,0.3,0.8)] # Space 0 reserved for ocean tile colour
    for zcord in range(ZLENGTH):
        for xcord in range(XLENGTH):
            if watermask[zcord][xcord][0] != 0: # => water tile as defined in the mask
                vertList.append((xcord,0.3,zcord))  # So render as an ocean tile
                # Generic lowlying land colour. Already check in map generating function if a tile is at sea level,
                # so this is simply the colour for terrain sloping into sea level.
                coloursList.append((0.85+uniform(-0.05,0.05),
                                    0.95+uniform(-0.05,0.05),
                                    0.85+uniform(-0.05,0.05)))
                coloursList.append((0.85+uniform(-0.05,0.05),
                                    0.95+uniform(-0.05,0.05),
                                    0.85+uniform(-0.05,0.05)))  # We do this twice since each "pixel" corresponds to two polygons.
            else:
                vertList.append((xcord,heightmap[zcord][xcord]/75,zcord))
                # Convert from 0-255 RGB format to 0-1 RGB format. Random number adds colour variation for aesthetic purposes
                pixelColour = ((colourmap[zcord][xcord][0]/255)+uniform(-0.05,0.05),
                               (colourmap[zcord][xcord][1]/255)+uniform(-0.05,0.05),
                               (colourmap[zcord][xcord][2]/255)+uniform(-0.05,0.05))
                coloursList.append(pixelColour) # Define RGB values for all corresponding vertices
                # We do this twice since each "pixel" corresponds to two polygons.
                # We can afford to take more processing while loading the map at this stage.
                pixelColour = ((colourmap[zcord][xcord][0]/255)+uniform(-0.05,0.05),
                               (colourmap[zcord][xcord][1]/255)+uniform(-0.05,0.05),
                               (colourmap[zcord][xcord][2]/255)+uniform(-0.05,0.05))
                coloursList.append(pixelColour)
    return np.array(vertList), np.array(coloursList)

def triThreePoints(p1,p2,p3,c):
    glColor3fv(c)
    glVertex3fv(p1)
    glVertex3fv(p2)
    glVertex3fv(p3)

def renderTriangle(vertices):
    "Renders a mesh of triangles based on the coords inputted"
    # Format of each entry: vertex 1, vertex 2, vertex 3, colour
    glBegin(GL_TRIANGLES)
    while vertices != []:
        triThreePoints(*vertices.pop())
    glEnd()

# We need to import all of these variables because numba won't know about them
@njit
def genTerrain(mapMatrix, coloursList, camPositionx, camPositionz, yaw, pitch):
    verticelist, collisionCheckList = [], []
    # We define an inner function so we can calculate arctan.
    # This is since we can't import math or numpy into this njit func.
    # cant use recursion here as njit doesnt support it
    def arctan(x):
        i = 0
        while abs(x) > 0.1:
            x = x / (1 + (1 + x*x)**0.5)
            i += 1
        return (360/(2*3.1416)) * (x - (x**3)/3 + (x**5)/5 - (x**7)/7 + (x**9)/9 - (x**11)/11) * 2**i
    
    length = len(mapMatrix)
    try:
        for i in range(length):                   
            if ((camPositionx-mapMatrix[i][0])**2 + (camPositionz-mapMatrix[i][2])**2)**(1/2) > RENDER_DISTANCE:
                # Only renders triangles within the render distance
                pass
            elif i+XLENGTH+1 > length:  # This stops vertices at the edge from rendering triangles
            # this previously led to triangles being rendered across the entire map before fix
                pass
            elif i%XLENGTH == XLENGTH-1:    # Same as above but for other edge
                pass
            else:
                if ((camPositionx-mapMatrix[i][0])**2 + (camPositionz-mapMatrix[i][2])**2)**(1/2) < 1:  # Check for collision
                    collisionCheckList.append((mapMatrix[i+1],mapMatrix[i],mapMatrix[i+XLENGTH]))
                    collisionCheckList.append((mapMatrix[i+1]
                    mapMatrix[i+XLENGTH],mapMatrix[i+XLENGTH+1]))

                if (mapMatrix[i][0]-camPositionx) < 0:  # Calculate the bearing of the vertice from the x axis
                    bearing = 180 - abs(arctan((mapMatrix[i][2]-camPositionz)/(mapMatrix[i][0]-camPositionx)))
                else:
                    bearing = abs(arctan((mapMatrix[i][2]-camPositionz)/(mapMatrix[i][0]-camPositionx)))

                if (mapMatrix[i][2]-camPositionz) < 0:
                    bearing = 360-bearing

                # If the vertice is more than 100 degrees away from the yaw, do not render.
                # Also renders every tile if looking straight down, to preserve illusion
                if abs(bearing-yaw) > 100 and abs(bearing-yaw) < 280 and bearing>0 and pitch>-75:
                    pass

                else:
                    # The two triangles adjacent to any vertex
                    if mapMatrix[i][1] == mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == 0.3:
                        # This is only true if all three corners are at sea level
                        verticelist.append((mapMatrix[i+1],mapMatrix[i],
                        mapMatrix[i+XLENGTH],coloursList[0]))
                    else:
                        verticelist.append((mapMatrix[i+1],mapMatrix[i],
                        mapMatrix[i+XLENGTH],coloursList[2*i+1]))
                    if mapMatrix[i+1][1] == mapMatrix[i+XLENGTH][1] == mapMatrix[i+XLENGTH+1][1] == 0.3:
                        # This is only true if all three corners are at sea level
                        verticelist.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],
                        mapMatrix[i+XLENGTH+1],coloursList[0]))
                    else:
                        verticelist.append((mapMatrix[i+1],mapMatrix[i+XLENGTH],
                        mapMatrix[i+XLENGTH+1],coloursList[2*i+2]))
    except Exception:   # Invalid triangle, avoid crashing and dont render it instead
        pass
    return verticelist, collisionCheckList

# Define a text rendering framework:
def text(x, y, color, text):
    glColor3fv(color)
    glWindowPos2f(x, y)
    glutBitmapString(GLUT_BITMAP_HELVETICA_18, text.encode('ascii'))

def main(collectDataPermission):

    pg.init()
    pg.font.init()
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    # pg.mouse.set_visible(False)

    display = (1920, 1080)
    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    mainCam = Camera((231,0.8,450), False)   # Position
    glClearColor(25/255, 235/225, 235/225, 0)   # Sets the colour of the "sky"

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) # fov, aspect, zNear, zFar
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    print("Display initialised")    # for logging

    mapMatrix, coloursList = mapGen(heightmap, colourmap, watermask)
    print("Map Generated")    # for logging

    #culling settings
    glDepthMask(GL_TRUE)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    glDepthRange(0.0,1.0)

    ### RUN PROGRAM ###

    currTime=pg.time.get_ticks() # Initialise program clock
    
    while True: # Allows us to actually leave the program
        try:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
        
                if event.type == pg.KEYDOWN:
                    # Regenerate the map for debugging purposes
                    if event.key == pg.K_m:
                        mapMatrix, coloursList = mapGen(heightmap, colourmap, watermask)
                        pg.time.wait(1)

                    # Dedicated crash button
                    if event.key == pg.K_c:
                        raise Exception("user forced crash")

            # Clear buffer
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            try:
                timeTaken=1000/((pg.time.get_ticks()-currTime))
            except Exception: # Divide by zero sometimes happens when a frame is rendered instantly
                timeTaken = 1000 # Small value of t

            currTime=pg.time.get_ticks()

            # Update the camera with input from the user
            keys = pg.key.get_pressed()
            mainCam.update(keys, (1/timeTaken))

            text(0, 1050, (1, 0, 0), str(round(timeTaken,1))+' FPS')
            text(0, 930, (1, 0, 0), "Position: " + str(mainCam.getPos().val))

            # Generate the visible terrain
            verticelist, colCheck = genTerrain(mapMatrix, coloursList,
            *mainCam.getXZ(), mainCam.getDir().val[0], mainCam.getDir().val[1])

            renderTriangle(verticelist)
            checkforcollision(colCheck, mainCam)

            pg.display.flip() # Update window with active buffer contents
            pg.time.wait(10) # Prevents frames from being rendered instantly

        except Exception as err:
            print("An error has ocurred.")
            if collectDataPermission:
                generateLog(err, traceback.format_exc(),
                            [mainCam.getPos().val, mainCam.getDir().val,
                            timeTaken, currTime, verticelist, colCheck])
            pg.quit()
            quit()