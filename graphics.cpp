#include <pybind11/pybind11.h>
#include <GL/glew.h>

void initializeOpenGL() {
    // Initialize OpenGL here
    // Set up shaders, buffers, etc.
}

void renderTriangle(float t1[3], float t2[3], float t3[3], float c[3]) {
    //glBegin(GL_TRIANGLES);
    //glColor3fv(c);
    //glVertex3fv(t1);
    //glVertex3fv(t2);
    //glVertex3fv(t3);
    //glEnd();
}

int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(graphics, m) {
    m.doc() = "Renders the environment and world of the flight simulator";

    m.def("initializeOpenGL", &initializeOpenGL, "Initialises opengl");
    m.def("renderTriangle", &renderTriangle, "Renders the individual triangles of the terrain");
    m.def("add", &add, "adds");
}
