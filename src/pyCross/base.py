import numpy as np

# Default Size
DEF_SIZE = 10
# First ID
current_id = 10


def get_next_id():
    global current_id
    current_id += 1
    return current_id


class Base(object):
    def __init__(self, **kwargs):
        self.color = kwargs.pop('color', -1)
        self.id = kwargs.pop('id', -1)


class Cell(Base):
    def __init__(self, x, y, **kwargs):
        super(Cell, self).__init__(**kwargs)
        self.x = x
        self.y = y


class Column(object):
    def __init__(self, **kwargs):
        self.length = kwargs.pop('length', DEF_SIZE)
        self.cells = kwargs.pop('cells', [])


class Table2D(object):
    def __init__(self, **kwargs):
        self.size = kwargs.pop('size', DEF_SIZE)
        self.cells = np.array([[Cell(j, i) for j in range(self.size)] for i in range(self.size)])

    def get(self, x=None, y=None):
        if x is not None and y is not None:
            return self.cells[y][x]
        if x is not None:
            return self.cells[:][x]
        if y is not None:
            return self.cells[y][:]
        raise ValueError('Did not specify what to get from column!')


class Element(Base):
    def __init__(self, **kwargs):
        kwargs['id'] = kwargs.pop('id', get_next_id())
        super(Element, self).__init__(**kwargs)
        self.length = kwargs.pop('length', 1)


class Vector(object):
    def __init__(self, **kwargs):
        self.elements = kwargs.pop('elements', [])

    def add(self, element):
        self.elements += [element]

    def get(self, element):
        for e in self.elements:
            if element.id == e.id:
                return self.elements
        return None


class Map2D(object):
    def __init__(self, **kwargs):
        self.size = kwargs.pop('size', DEF_SIZE)
        self.X = [Vector() for _ in self.size]
        self.Y = [Vector() for _ in self.size]

        self.table_2d = None

    def assign_table_2d(self, table_2d):
        self.table_2d = table_2d
        self._parse_table()

    def _parse_table(self):
        pass
