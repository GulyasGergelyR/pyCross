from __builtin__ import staticmethod

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

ESCAPE = '\033'
SIZE = 0.3
window = 0
X_AXIS = 0

tex = None


class Element2D(object):
    def __init__(self, x=0, y=0, color=(1.0, 1.0, 1.0,)):
        self.color = color
        self.x = x
        self.y = y

    def draw(self):
        glBegin(GL_QUADS)
        glColor3f(*self.color)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x, self.y + SIZE)
        glVertex2f(self.x + SIZE, self.y + SIZE)
        glVertex2f(self.x + SIZE, self.y)
        glEnd()


class Number(object):
    def __init__(self):
        pass


class Renderer(object):
    def __init__(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(200, 200)

        self.window = glutCreateWindow('pyCross')

        glutDisplayFunc(self._draw_gl_scene)
        glutIdleFunc(self._draw_gl_scene)

        glutKeyboardFunc(self._key_pressed)
        self._init_gl(640, 480)
        glutMainLoop()

        self.texture = None

    def _key_pressed(*args):
        if args[0] == ESCAPE:
            sys.exit()

    def _draw_2d_grid(self):
        pass

    def _draw_2d_numbers(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, 0)
        glTexCoord2f(0, 1)
        glVertex3f(0, 1, 0)
        glTexCoord2f(1, 1)
        glVertex3f(1, 1, 0)
        glTexCoord2f(1, 0)
        glVertex3f(1, 0, 0)
        glEnd()

    def _draw_2d_elements(self):
        pass

    def _draw_gl_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glAlphaFunc(GL_GREATER, 0)

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -6.0)
        self._draw_2d_grid()
        self._draw_2d_numbers()
        self._draw_2d_elements()
        glutSwapBuffers()

    def _init_gl(self, width, height):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_TEXTURE_2D)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_ALPHA_TEST)

        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        self.texture = self._load_texture("..\\..\\res\\pycross_one.png")

    @staticmethod
    def _load_texture(filename):
        texture = glGenTextures(1)
        im = Image.open(filename)
        try:
            ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBA", 0, -1)
        except SystemError:
            ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBX", 0, -1)

        glBindTexture(GL_TEXTURE_2D, texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        return texture

if __name__ == "__main__":
    renderer = Renderer()
