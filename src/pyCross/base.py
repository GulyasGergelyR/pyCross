import numpy as np

# Default Size
DEF_SIZE = 10
# First ID
element_id = 10

dim_x_id = 1000
x_id = 10
dim_y_id = 2000
y_id = 10
dim_z_id = 3000
z_id = 10


def get_id():
    global element_id
    element_id += 1
    return element_id


class Cell(object):
    def __init__(self, **kwargs):
        self.p = kwargs.pop('p', [0, 0, 0])
        self.id = kwargs.pop('id', [-1, -1, -1])
        self.color = -1


class Column(object):
    def __init__(self, **kwargs):
        self.cells = kwargs.pop('cells', [])
        self.length = len(self.cells)
        self.vector = kwargs.pop('vector', None)
        if self.vector is not None:
            self.vector.column = self

        self.parent = kwargs.pop('parent', None)

        self.left_clone = Column(parent=self)
        self.right_clone = Column(parent=self)


class Element(object):
    def __init__(self, **kwargs):
        """

        :param kwargs:
         vector: Vector element which stores the elements of a specified column
         id: Unique id for an element
         color: color id
         length: length of the element
         pos: position in the column
         found: boolean - If this is true, then this element cannot be moved
         tc: test column
        """
        self.vector = kwargs.pop('vector', None)

        self.id = kwargs.pop('id', get_id())
        self.color = kwargs.pop('color', 1)
        self.length = kwargs.pop('length', 1)

        self.pos = kwargs.pop('pos', None)
        self.found = kwargs.pop('found', False)

        self.tc = kwargs.pop('tc', [-1 for _ in range(self.column)])

    @property
    def end(self):
        return self.pos + self.length - 1

    @property
    def column(self):
        return self.vector.column

    @property
    def cells(self):
        return self.column.cells

    @property
    def colors(self):
        return [cell.color for cell in self.cells]

    @property
    def ids(self):
        return [cell.color for cell in self.cells]

    def spacer(self, element):
        if self.color == element.color:
            return 1
        else:
            return 0

    def get_left(self):
        return self.vector.get(self, -1)

    def get_right(self):
        return self.vector.get(self, +1)

    def set_invalid(self, i=0, j=None, length=0):
        j = j if j is not None else i+length
        for k in range(i, j):
            self.tc[k] = 0

    def find_valid_pos(self, anchor=None):
        # Find invalid positions
        left = self.get_left()
        if left is None:
            left_pos = 0
        else:
            left_pos = left.end + self.spacer(left)
        # left_pos is the first valid cell after the prev element (without main constraints)
        self.set_invalid(j=left_pos)
        # left: [XXXXXXX111-----]
        # self: [XXXXXXXXXXX11--] length: 2, color: 1
        for i, c in enumerate(self.colors[left_pos:]):
                self.tc[i] = c

            # main: [--2-1XX--333---]
            # left: [X22------------] length: 2, color: 2
            #           |----------|  iterate here
            # self: [XXX-1XX--333---] color: 1

        # Find valid positions
        valid = False
        if anchor is not None:
            # anchor is the end point
            pos = anchor - self.length + 1
        else:
            pos = left_pos
        right = self.get_right()
        pattern = [self.color for _ in range(self.length)]
        if right is not None:
            if self.color == right.color:
                pattern += [0]
        while not valid:
            for i, c in enumerate(pattern):
                if self.tc[pos + i] != -1 and self.tc[pos + i] != c:
                    # we failed at the ith element
                    # we start again at pos + i + 1
                    pos += i + 1
                    # set prev points to invalid
                    self.set_invalid(j=pos)
                    break
            else:
                valid = True

        if valid:
            self.pos = pos


class Vector(object):
    def __init__(self, **kwargs):
        self.elements = kwargs.pop('elements', [])
        self.column = None

    def add(self, element):
        self.elements += [element]
        element.vector = self

    def get(self, element, offset=0):
        for i, e in enumerate(self.elements):
            if element.id == e.id:
                if len(self.elements) > i+offset >= 0:
                    return e[i+offset]
                else:
                    return None
        raise ValueError("There is no such element with id: '{}'".format(element.id))
