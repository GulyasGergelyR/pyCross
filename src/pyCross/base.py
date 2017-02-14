
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
    def __init__(self, **kwargs):
        super(Cell, self).__init__(**kwargs)


class Column(object):
    def __init__(self, **kwargs):
        self.length = kwargs.pop('length', DEF_SIZE)
        self.cells = [Cell() for _ in range(self.length)]


class Table2D(object):
    def __init__(self, **kwargs):
        self.size = kwargs.pop('size', DEF_SIZE)
        self.cells = [[Cell() for _ in range(self.size)] for _ in range(self.size)]


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
