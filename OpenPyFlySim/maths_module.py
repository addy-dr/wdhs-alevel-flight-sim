import numpy as np
from numba import float64
from numba.experimental import jitclass
import math

### THIS IS A MODULE MOSTLY CONSISTING OF CLASSES AND FUNCTIONS USED IN THE OTHER FILES

@jitclass([("__values", float64[::1])]) #define __values to be a list of contiguous floats
class Vector3(): #Define a class for 3d vectorss
    #class methods don't work with JIT
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

    def multiply(self, a):
        result = []
        for i in range(3):
            result.append(self.__values[i]*a)
        return Vector3(result)
    
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

#rotates one vector around another using the Euler-Rodrigues formula
def rotate(vector, axis, theta): #vector3,vector3,float (radians)
    a = math.cos(theta/2)
    omega = Vector3([
        math.sin(theta/2) * axis.val[0],
        math.sin(theta/2) * axis.val[1],
        math.sin(theta/2) * axis.val[2]
    ])
    return Vector3.addVectors(
        Vector3.addVectors(vector, Vector3.cross(omega,vector).multiply(2*a)),
        Vector3.cross(omega, Vector3.cross(omega,vector)).multiply(2)
    )

def getDatafileData(variable):
    "retrieves data from datafile.txt"
    with open("datafile.txt", "r") as f:
        lines = f.read().split("\n")
    
    for string in lines:
        try:
            start = string.index(variable) + len(variable) + 1 #plus one because of equals sign
            return string[start:]
        except ValueError:
            pass
    return ""

def writeDatafileData(variable, content):
    "writes data to datafile.txt"
    with open("datafile.txt", "r") as f:
        lines = f.read().split("\n")
    replacedline = 0
    for string in lines:
        try:
            start = string.index(variable) + len(variable) + 1
            newline = string[:start]+str(content) #replace the old content with the new parameter
            replacedline = lines.index(string)
        except ValueError:
            pass
    newfile = ""
    for i in range(len(lines)):
        if i == replacedline:
            newfile+=(newline+"\n") #replace previous item on this line with the new modified one
        else:
            newfile+=(lines[i]+"\n")

    with open("datafile.txt", "w") as f:
        f.write(newfile)
