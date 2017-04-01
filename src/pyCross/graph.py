from __builtin__ import staticmethod

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
from pyCross.base import Table2D, set_def_size, Source, get_def_size

ESCAPE = '\x1b'
SPACE = ' '
SIZE = 0.3
TEXT_SIZE = 0.3

colors = {0: (1, 1, 1,), 1: (1.0, 0.0, 0.0,), 2: (0.0, 1.0, 0.0,), 3: (0.0, 0.0, 1.0,),
          4: (0.0, 0.5, 1.0,), 5: (0.5, 0.0, 1.0,)}


class Element2D(object):
    def __init__(self, x=0, y=0, color=(1.0, 1.0, 1.0,), texture=None):
        self.color = color
        self.x = x - get_def_size() / 2.0
        self.y = -y + get_def_size() / 2.0
        self.texture = texture

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glColor3f(*self.color)
        glTexCoord2f(0, 0)
        glVertex3f(self.x * SIZE, self.y * SIZE, 0)
        glTexCoord2f(0, 1)
        glVertex3f(self.x * SIZE, self.y * SIZE + SIZE, 0)
        glTexCoord2f(1, 1)
        glVertex3f(self.x * SIZE + SIZE, self.y * SIZE + SIZE, 0)
        glTexCoord2f(1, 0)
        glVertex3f(self.x * SIZE + SIZE, self.y * SIZE, 0)
        glEnd()


class Number(object):
    def __init__(self, number=0, x=0, y=0, color=(1.0, 1.0, 1.0,), texture=None):
        self.color = color
        self.x = x - get_def_size() / 2.0
        self.y = -y + get_def_size() / 2.0
        self.texture = texture
        self.number = number

    def draw(self):
        text_dist = 0.3
        temp = self.number
        n = 0
        while temp >= 10:
            temp /= 10
            n += 1

        temp = self.number
        for ni in range(n+1):
            tempi = temp/(10**(n-ni))
            x_offset = -text_dist/2.0*(n % 2)*0
            self._draw(x=self.x+x_offset + (ni-n/2.0)*text_dist, number=tempi)
            temp -= tempi*(10**(n-ni))

    def _draw(self, x, number):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glColor3f(*self.color)
        glTexCoord2f(number/10.0, 0)
        glVertex3f(x * TEXT_SIZE, self.y * TEXT_SIZE, 0)
        glTexCoord2f(number/10.0, 1)
        glVertex3f(x * TEXT_SIZE, self.y * TEXT_SIZE + TEXT_SIZE, 0)
        glTexCoord2f(number/10.0+0.1, 1)
        glVertex3f(x * TEXT_SIZE + TEXT_SIZE, self.y * TEXT_SIZE + TEXT_SIZE, 0)
        glTexCoord2f(number/10.0+0.1, 0)
        glVertex3f(x * TEXT_SIZE + TEXT_SIZE, self.y * TEXT_SIZE, 0)
        glEnd()


class Game(object):
    def __init__(self):
        global SIZE, colors
        set_def_size(100)
        source = Source()
        # source.randomize()
        # source.analyze()
        source.read_from_file('c:\\Greg\\Drive\\Dev\\python\\pyCross\\test\\picma.txt')
        source.print_it()

        colors = source.colors

        self.table2d = Table2D()
        self.table2d.horizontal_vectors = source.vertical_vectors
        self.table2d.vertical_vectors = source.horizontal_vectors
        Renderer(self)


class Renderer(object):
    def __init__(self, game):
        self.game = game
        self.texture = dict()
        self._translate = [0, 0, -10]
        self._last_pos = [0, 0]
        self._motion_start = [0, 0]
        self._track_motion = False

        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(1024, 768)
        glutInitWindowPosition(200, 200)

        self.window = glutCreateWindow('pyCross')

        glutDisplayFunc(self._draw_gl_scene)
        glutIdleFunc(self._draw_gl_scene)

        glutKeyboardFunc(self._key_pressed)
        glutMouseFunc(self._mouse_event)
        glutMotionFunc(self._mouse_motion)
        self._init_gl(1024, 768)
        glutMainLoop()

    def _mouse_motion(self, x, y):
        motion = [x, y]
        if self._track_motion:
            self._translate[0:2] = [self._last_pos[i] +
                                    (motion[i]-self._motion_start[i])/1000.0*(-self._translate[2])*(-1)**i
                                    for i in range(2)]

    def _mouse_event(self, button, state, x, y):
        if button == 3:
            self._translate[2] -= 0.5
        elif button == 4:
            self._translate[2] += 0.5

        if self._translate[2] > -6:
            self._translate[2] = -6

        if button == 0:
            if state == 0:
                self._track_motion = True
                self._motion_start = [x, y]
                self._last_pos[:] = self._translate[0:2]
            if state == 1:
                self._track_motion = False

    def _key_pressed(self, *args):
        if args[0] == ESCAPE:
            sys.exit()
        if args[0] == SPACE:
            self.game.table2d.solve_one()

    def _draw_2d_grid(self):
        pass

    def _draw_2d_numbers(self):
        for vi, v in enumerate(self.game.table2d.horizontal_vectors):
            for ei, e in enumerate(v.elements):
                number = Number(e.length, vi, -len(v.elements)+ei, colors[e.color], self.texture['nums'])
                number.draw()
        for vi, v in enumerate(self.game.table2d.vertical_vectors):
            for ei, e in enumerate(v.elements):
                number = Number(e.length, -len(v.elements)+ei, vi, colors[e.color], self.texture['nums'])
                number.draw()

    def _draw_2d_elements(self):
        for y, row in enumerate(self.game.table2d.cells):
            for x, cell in enumerate(row):
                if cell.color in colors.keys():
                    element2d = Element2D(x=x, y=y, color=colors[cell.color],
                                          texture=self.texture['cell'] if cell.color != 0 else self.texture['x'])
                    element2d.draw()

    def _draw_gl_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glAlphaFunc(GL_GREATER, 0)

        glLoadIdentity()
        glTranslatef(*self._translate)

        self._draw_2d_grid()
        self._draw_2d_numbers()
        self._draw_2d_elements()
        glutSwapBuffers()

    def _init_gl(self, width, height):
        glClearColor(0.2, 0.2, 0.2, 0.0)
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
        self.texture['nums'] = self._load_texture("..\\..\\res\\pycross_nums.png")
        self.texture['cell'] = self._load_texture("..\\..\\res\\pycross_cell.png")
        self.texture['x'] = self._load_texture("..\\..\\res\\pycross_x.png")

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
