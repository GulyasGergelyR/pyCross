# Default Size
DEF_SIZE = 20
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


class BaseColumn(object):
    def __init__(self, **kwargs):
        self.cells = kwargs.pop('cells', None)
        if self.cells is None:
            self.length = kwargs.pop('length', DEF_SIZE)
            self.cells = [Cell() for _ in range(self.length)]
        else:
            self.length = len(self.cells)

        self.vector = kwargs.pop('vector', None)

        if self.vector is not None:
            self.vector.column = self


class SubColumn(BaseColumn):
    def __init__(self, **kwargs):
        super(SubColumn, self).__init__(**kwargs)
        self.parent = kwargs.pop('parent', None)

    def left_most(self):
        for element in self.vector.elements:
            element.find_valid_pos()
        self.print_it()

    def print_it(self):
        t = ['X' for _ in range(self.length)]
        for element in self.vector.elements:
            for i in range(element.length):
                t[element.pos+i] = str(element.color)
        print 'sub:  |{}|'.format(''.join(t))


class Column(BaseColumn):
    def __init__(self, **kwargs):
        super(Column, self).__init__(**kwargs)
        self.left_clone = None
        self.right_clone = None

    def create_copy(self):
        cells = [Cell(color=cell.color) for cell in self.cells]
        c = SubColumn(parent=self, cells=cells, vector=self.vector.create_copy())
        return c

    def parse(self):
        self.print_it()
        self.left_clone = self.create_copy()
        self.left_clone.left_most()

    def print_it(self):
        t = ['-' for _ in range(self.length)]
        for i, cell in enumerate(self.cells):
            if cell.color == -1:
                pass
            elif cell.color == 0:
                t[i] = 'X'
            else:
                t[i] = str(cell.color)
        print 'main: |{}|'.format(''.join(t))


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

        self.pos = kwargs.pop('pos', 0)
        self.found = kwargs.pop('found', False)

        self.tc = []

        self.left_element = None
        self.right_element = None

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
        return self.left_element

    def get_right(self):
        return self.right_element

    def set_invalid(self, i=0, j=None, length=0):
        j = j if j is not None else i+length
        for k in range(i, j):
            self.tc[k] = 0

    def find_valid_pos(self, anchor=None):
        if len(self.tc) == 0:
            self.tc = [-1 for _ in range(self.column.length)]

        # Find invalid positions
        left = self.get_left()
        if left is None:
            left_pos = 0
        else:
            left_pos = left.end + self.spacer(left) + 1
        # left_pos is the first valid cell after the prev element (without main constraints)
        self.set_invalid(j=left_pos)
        # left: [XXXXXXX111-----]
        # self: [XXXXXXXXXXX11--] length: 2, color: 1
        for i, c in enumerate(self.colors[left_pos:]):
            if c != -1:
                self.tc[i+left_pos] = c

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

        for i in range(len(self.elements)-1):
            self.elements[i].right_element = self.elements[i+1]
            self.elements[i+1].left_element = self.elements[i]

    def add(self, element):
        self.elements[-1].right_element = element
        element.left_element = self.elements[-1]
        self.elements += [element]
        element.vector = self

    def get(self, element, offset=0):
        for i, e in enumerate(self.elements):
            if element.id == e.id:
                if len(self.elements) > i+offset >= 0:
                    return self.elements[i+offset]
                else:
                    return None
        raise ValueError("There is no such element with id: '{}'".format(element.id))

    def create_copy(self):
        elements = [Element(vector=self, id=e.id, color=e.color,
                            length=e.length, found=e.found, pos=e.pos) for e in self.elements]
        e = Vector(elements=elements)
        return e
