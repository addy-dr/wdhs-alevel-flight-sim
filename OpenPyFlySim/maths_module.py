import numpy as np
from numba import float64
from numba.experimental import jitclass
import math

### THIS IS A MODULE MOSTLY CONSISTING OF CLASSES AND FUNCTIONS USED IN THE OTHER FILES

# Define __values to be a list of contiguous floats:
@jitclass([("__values", float64[::1])])
class Vector3():
    "Defines a class for 3d vectors"
    # Class methods don't work with JIT
    @staticmethod
    def addVectors(vectorA, vectorB):
        "Static method to add two vectors and return a third one"
        result = []
        for i in range(3):
            result.append(vectorA.val[i]+vectorB.val[i])
        # Returns a vector with the summed values as its instantiation inputs
        return Vector3(result)
    
    @staticmethod
    def subtractVectors(vectorA, vectorB):
        "Static method to sub two vectors and return a third one"
        result = []
        for i in range(3):
            result.append(vectorA.val[i]-vectorB.val[i])
        # Returns a vector with the summed values as its instantiation inputs
        return Vector3(result)
    
    @staticmethod
    def dot(vectorA, vectorB):
        "Static method to dot product two vectors"
        result = 0
        for i in range(3):
            result += (vectorA.val[i] * vectorB.val[i])
        return result
    
    @staticmethod
    def cross(vectorA, vectorB):
        "Static method to cross product two vectors"
        result = []
        for t in [(1,2),(2,0),(0,1)]:
            # Based on mathematical definition of cross product:
            result.append(vectorA.val[t[0]]*vectorB.val[t[1]]
            - vectorA.val[t[1]]*vectorB.val[t[0]])
        # Returns a vector with the cross product as its instantiation inputs
        return Vector3(result)
    
    def __init__(self, arg):
        #Note: In order to work with the vector3 function,
        # we must pass in a numpy array with a defined data type of float64 for all values.
        self.__values = np.array(arg, dtype=np.float64)

    @property   # Turns this into a getter method
    def val(self):
        "Return value"
        return self.__values

    def setVal(self, a):
        "Setter function to change the value of the vector"
        self.__values = np.array(a, dtype=np.float64)

    def addVal(self, a):
        "Add values to existing vals"
        for i in range(3):
            self.__values[i] += a[i]

    def multiply(self, a):
        result = []
        for i in range(3):
            result.append(self.__values[i]*a)
        return Vector3(result)
    
    def magnitude(self):
        "Returns magnitude"
        return (self.__values[0]**2 + self.__values[1]**2 +
        self.__values[2]**2)**(0.5)
    
    def setAt(self, n, val):
        "Sets the value of the varable at n to val"
        self.__values[n] = val
    
    def normalise(self):
        """Normalises vectors."""
        magnitude = self.magnitude()
        if magnitude == 0:
            return Vector3([0,0,0])
        else:
            return Vector3([
                self.val[0] / magnitude,
                self.val[1] / magnitude,
                self.val[2] / magnitude])

# vector3,vector3,float (radians)
def rotate(vector, axis, theta):
    "Rotates one vector around another using the Euler-Rodrigues formula"
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
    "Retrieves data from datafile.txt"
    with open("datafile.txt", "r") as f:
        lines = f.read().split("\n")
    
    for string in lines:
        try:
            # Plus one because of equals sign
            start = string.index(variable) + len(variable) + 1
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
            # Replace the old content with the new parameter:
            newline = string[:start]+str(content)
            replacedline = lines.index(string)
        except ValueError:
            pass
    newfile = ""
    for i in range(len(lines)):
        if i == replacedline:
            # Replace previous item on this line with the new modified one
            newfile+=(newline)
        else:
            newfile+=(lines[i])
        if i != len(lines)-1:
            #write a new line, except on last line
            newfile+='\n'

    with open("datafile.txt", "w") as f:
        f.write(newfile)