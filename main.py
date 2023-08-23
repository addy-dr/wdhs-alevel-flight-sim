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

#Principles of rendering:
#Every object in OpenGL is a collection of points; lines that connect pairs of points; triangles composed of three points; quads composed of four points etc etc
cubeVertices = ((1,1,1),(1,1,-1),(1,-1,-1),(1,-1,1),(-1,1,1),(-1,-1,-1),(-1,-1,1),(-1,1,-1)) #Points of a 2x2x2 cube
#every edge is given a number, from 0 through to 7, based on its position in our array. To join them:
cubeEdges = ((0,1),(0,3),(0,4),(1,2),(1,7),(2,5),(2,3),(3,6),(4,6),(4,7),(5,6),(5,7))
#Finally, connect the vertices via their number to also make a cube.
#It helps to draw a diagram at this point. The page I'm following here has this diagram:
# https://stackabuse.s3.amazonaws.com/media/advanced-opengl-in-python-pygame-and-pyopengl-2.png
cubeQuads = ((0,3,6,4),(2,5,6,3),(1,2,5,7),(1,0,4,7),(7,4,6,5),(2,3,0,1))

# draw wire cube
def wireCube():
    glBegin(GL_LINES)  # begin drawing. GL_LINES tells us we'll be drawing lines
    for cubeEdge in cubeEdges:
        for cubeVertex in cubeEdge:
            glVertex3fv(cubeVertices[cubeVertex]) 
            """
            What does this command mean?
            glVertex: defines a vertex
            glVertex3: 3-coordinate vertex
            glVertex3f: of type GLfloat
            glVertex3fv: put inside a vector (tuple) as opposed to glVertex3fl which uses a list of arguments instead
            So, we are drawing out all our vertices one by one.
            """
    glEnd() #stop drawing

#map size
ZLENGTH = 300
XLENGTH = 300
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
    try:
        if operand=='-':
            for i in range(len(a)):
                result += (a[i]-b[i],)
        elif operand=='+':
            for i in range(len(a)):
                result += (a[i]+b[i],)
        else:
            result = a
    except Exception:
        raise Exception("Tuples in function \"subTuple\" of different lengths")
    return result

@njit
def mapGen():
    #Create our matrix for both the 20x20 surface and the colours
    vertList = []
    coloursList = []
    for zcord in range(-ZLENGTH//2,ZLENGTH//2):
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
    offsetx = 0 #pos of camera from origin
    offsetz = 0
    speed=0.1

    pitch = -90
    yaw = 0
    roll = 0

    #setup camera
    camPosition = (0,0,0)
    up = (0,1,0)
    camUp = (0,1,0)
    camFront = (0,0,-4)
    direction = [0,0,0]


    screen = pg.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(60, (display[0]/display[1]), 0.1, 50.0) #fov, aspect, zNear, zFar

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
            glTranslatef(0, 0, speed)
            offsetz += speed
            #camPosition += speed * camFront
        if keys[K_s]:
            glTranslatef(0, 0, -speed)
            offsetz -= speed
            #camPosition -= speed * camFront
        if keys[K_a]:
            glTranslatef(0.1, 0, 0)
            offsetx+=0.1
        if keys[K_d]:
            glTranslatef(-0.1, 0, -0)
            offsetx-=0.1

        #camera direction
        mouse = pg.mouse.get_rel()
        yaw += mouse[0]
        pitch += mouse[1]
        if pitch > 89:
            pitch = 89
        if pitch < -89:
            pitch = -89

        #From drawing trigonemtric diagrams:
        direction[0] = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
        direction[1] = math.sin(math.radians(pitch))
        direction[2] = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
        camFront = normalise(*tuple(direction)) #get the front normalised vector
        camRight = np.cross(up, camFront)
        camUp = np.cross(camFront, camRight)

        #use stars to unpack
        print(operateTuple(camPosition,camFront,'+'))
        gluLookAt(*camPosition, *(operateTuple(camPosition,(0,0,1),'+')), *camUp)
        print(yaw,pitch,roll)
        
        #culling
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glShadeModel(GL_SMOOTH)
        glDepthRange(0.0,1.0)

        #generate terrain
        wireCube()
        triangulate(genTerrain(mapMatrix, coloursList, offsetx, offsetz))
        timeTaken=1/((pg.time.get_ticks()-timeTaken)/1000)
        text(0, 700, (1, 0, 0), str(round(timeTaken,1))+' FPS')

        pg.display.flip() #update window with active buffer contents
        pg.time.wait(10) #wait a bit, avoids speed of simulation from being speed of execution of code

if __name__ == "__main__":
    main()
