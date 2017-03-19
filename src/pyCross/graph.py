from __builtin__ import staticmethod

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
from pyCross.base import Table2D, set_def_size, Source, get_def_size

ESCAPE = '\x1b'
SPACE = ' '
SIZE = 0.07

window = 0
X_AXIS = 0

tex = None

colors = {0: (0.1, 0.1, 0.1,), 1: (1.0, 0.0, 0.0,), 2: (0.0, 1.0, 0.0,), 3: (0.0, 0.0, 1.0,),
          4: (0.0, 0.5, 1.0,), 5: (0.5, 0.0, 1.0,)}


class Element2D(object):
    def __init__(self, x=0, y=0, color=(1.0, 1.0, 1.0,)):
        self.color = color
        self.x = x - get_def_size() / 2.0
        self.y = -y + get_def_size() / 2.0

    def draw(self):
        glEnable(GL_COLOR_MATERIAL)
        glBegin(GL_QUADS)
        glColor3f(*self.color)
        glVertex3f(self.x*SIZE, self.y*SIZE, 0)
        glVertex3f(self.x*SIZE, self.y*SIZE + SIZE, 0)
        glVertex3f(self.x*SIZE + SIZE, self.y*SIZE + SIZE, 0)
        glVertex3f(self.x*SIZE + SIZE, self.y*SIZE, 0)
        glEnd()


class Number(object):
    def __init__(self):
        pass


class Game(object):
    def __init__(self):
        set_def_size(50)
        source = Source()
        source.randomize()

        source.analyze()
        source.print_it()

        self.table2d = Table2D()
        self.table2d.horizontal_vectors = source.horizontal_vectors
        self.table2d.vertical_vectors = source.vertical_vectors
        Renderer(self)


class Renderer(object):
    def __init__(self, game):
        self.game = game
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

    def _key_pressed(self, *args):
        if args[0] == ESCAPE:
            sys.exit()
        if args[0] == SPACE:
            self.game.table2d.solve_one()

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
        for y, row in enumerate(self.game.table2d.cells):
            for x, cell in enumerate(row):
                if cell.color in colors.keys():
                    element2d = Element2D(x=x, y=y, color=colors[cell.color])
                    element2d.draw()

    def _draw_gl_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # glAlphaFunc(GL_GREATER, 0)

        glLoadIdentity()
        glTranslatef(0.0, 0.0, -6.0)

        self._draw_2d_grid()
        # self._draw_2d_numbers()
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
    Game()
