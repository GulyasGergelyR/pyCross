import random

import numpy as np

# Default Size
DEF_SIZE = 20

dim_x_id = 1000
x_id = 10
dim_y_id = 2000
y_id = 10
dim_z_id = 3000
z_id = 10


def set_def_size(size):
    global DEF_SIZE
    DEF_SIZE = size


def get_def_size():
    return DEF_SIZE


class Cell(object):
    def __init__(self, **kwargs):
        self.p = kwargs.pop('p', [0, 0, 0])
        self.id = kwargs.pop('id', [-2, -2, -2])
        self.color = kwargs.pop('color', -1)


class BaseColumn(object):
    def __init__(self, direction, **kwargs):
        self.dir = direction
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
    def __init__(self, direction, **kwargs):
        super(SubColumn, self).__init__(direction, **kwargs)
        self.parent = kwargs.pop('parent', None)
        self.rotated = kwargs.pop('rotated', False)

    @property
    def colors(self):
        t = [0 for _ in range(self.length)]
        for element in self.vector.elements:
            for i in range(element.length):
                if self.rotated:
                    t[self.length - element.pos - i - 1] = element.color
                else:
                    t[element.pos + i] = element.color
        return t

    @property
    def ids(self):
        cells = self.cells[::-1] if self.rotated else self.cells
        return [cell.id[self.dir] for cell in cells]

    def left_most(self, print_output=True):
        self.vector.arrange()
        if print_output:
            self.print_it()

    def print_it(self):
        print 'sub:  |{}|'.format(''.join(['X' if c == 0 else str(c) for c in self.colors]))


class Column(BaseColumn):
    def __init__(self, direction, **kwargs):
        super(Column, self).__init__(direction, **kwargs)
        self.left_clone = None
        self.right_clone = None

    def create_copy(self, rotate=False):
        cells = [Cell(color=cell.color, id=cell.id[:]) for cell in self.cells]
        if rotate:
            cells = cells[::-1]
        c = SubColumn(direction=self.dir, parent=self, cells=cells, vector=self.vector.create_copy(rotate),
                      rotated=rotate)
        return c

    def parse(self, print_output=True):
        if print_output:
            self.print_it()

        self.left_clone = self.create_copy()
        self.left_clone.left_most()
        self.right_clone = self.create_copy(rotate=True)
        self.right_clone.left_most()
        self.merge_copies()

        if print_output:
            self.print_it()

    def merge_copies(self):
        # create temporary id tuple
        left_ids = [-2 for _ in range(DEF_SIZE)]
        for element in self.left_clone.vector.elements:
            for c in range(element.length):
                left_ids[element.pos + c] = element.id
        print 'sub:  |{}|'.format(','.join([str(c) for c in left_ids]))
        right_ids = [-2 for _ in range(DEF_SIZE)]
        for element in self.right_clone.vector.elements:
            for c in range(element.length):
                right_ids[DEF_SIZE - element.pos - c - 1] = element.id
        print 'sub:  |{}|'.format(','.join([str(c) for c in right_ids]))

        # check in merged values
        for element in self.left_clone.vector.elements:
            every = True
            for c in range(element.length):
                if left_ids[element.pos + c] == right_ids[element.pos + c]:
                    self.cells[element.pos + c].id[self.dir] = element.id
                    self.cells[element.pos + c].color = element.color
                else:
                    every = False
            if every:
                self.vector.get(element).found = True
                self.vector.get(element).pos = element.pos

        # check in valid 'X's
        current = -2  # no id
        for i in range(self.length):
            # if current == 0:
            #     current = self.left_clone.ids[i]
            # if i > 0 and self.right_clone.colors[i] == 0 and self.left_clone.colors[i] == 0\
            #         and self.right_clone.colors[i-1] == current:
            #     current = 0
            # # we can add this X as permanent
            # if current == 0 and self.right_clone.colors[i] == 0 and self.left_clone.colors[i] == 0:
            #     self.cells[i].color = 0
            if left_ids[i] != -2:
                current = left_ids[i]
            if i > 0 and self.right_clone.colors[i] == 0 and self.left_clone.colors[i] == 0 \
                    and right_ids[i-1] == current:
                current = -2
            if current == -2 and self.right_clone.colors[i] == 0 and self.left_clone.colors[i] == 0:
                self.cells[i].color = 0

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


class Table2D(object):
    def __init__(self, v_vectors=None, h_vectors=None):
        self.cells = np.array([[Cell(p=[i, j, 0]) for i in range(DEF_SIZE)] for j in range(DEF_SIZE)])
        self.vertical_vectors = v_vectors if v_vectors is not None else [Vector() for _ in range(DEF_SIZE)]
        self.horizontal_vectors = h_vectors if h_vectors is not None else [Vector() for _ in range(DEF_SIZE)]

    def solve_one(self):
        v, h = self.cells.shape
        for c_i in range(v):
            column = Column(direction=0, vector=self.vertical_vectors[c_i], cells=self.cells[c_i, :])
            print '%s, %s' % (c_i, len(column.vector.elements))
            column.parse()

        for c_i in range(h):
            column = Column(direction=1, vector=self.horizontal_vectors[c_i], cells=self.cells[:, c_i])
            print '%s, %s' % (c_i, len(column.vector.elements))
            column.parse()


class Element(object):
    element_id = 10

    @staticmethod
    def get_id():
        Element.element_id += 1
        return Element.element_id

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

        self.id = kwargs.pop('id', None)
        if self.id is None:
            self.id = Element.get_id()

        self.color = kwargs.pop('color', 1)
        self.length = kwargs.pop('length', 1)

        self.found = kwargs.pop('found', False)
        self.pos = kwargs.pop('pos', 0) if self.found else 0
        self.rotated = kwargs.pop('rotated', False)
        if self.rotated:
            self.pos = kwargs.pop('col_length', DEF_SIZE) - self.end - 1

        self.tc = []

        self.left_element = None
        self.right_element = None

        self.first_anchor = None

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
        return [cell.id[self.column.dir] for cell in self.cells]

    def spacer(self, element):
        if self.color == element.color:
            return 1
        else:
            return 0

    def set_invalid(self, i=0, j=None, length=0):
        j = j if j is not None else i+length
        for k in range(i, j):
            self.tc[k] = 0

    def find_valid_pos(self, anchor=None, info='None', print_output=True):

        if print_output:
            print '[Info]: %s - id: ' % info, self.id
        # TODO remove usage of tc
        if len(self.tc) == 0:
            self.tc = [-1 for _ in range(self.column.length)]

        # We have already found this, go on
        if self.found:
            if anchor is not None:
                raise ValueError('Trying to move an already found element!')
            if self.right_element is not None:
                self.right_element.find_valid_pos(info='Moving onto next element, after fix element')
            return

        # There is an anchor point
        if anchor is not None:
            # check what is the color of the anchor point
            if self.colors[anchor] != self.color:
                self.first_anchor = None
                self.left_element.find_valid_pos(anchor=anchor, info='Not the right color, keep rolling back')
                return
        else:
            # Search for partially found elements:
            for i, element_id in enumerate(self.ids if self.rotated else self.ids[::-1]):
                if element_id == self.id:
                    anchor = i if self.rotated else self.column.length - i - 1
                    if print_output:
                        print "[Info]: Created anchor based on fix color"
                    # Check if is there any anchors between, if so then rollback with left element
                    if self.left_element is not None:
                        pos = self.left_element.end + self.spacer(self.left_element) + 1
                        for j in range(pos, anchor - self.length + 1):
                            if self.colors[j] != -1 and self.colors[j] != 0:  # it is a color
                                self.left_element.find_valid_pos(anchor=j, info='Found anchors before fix color')
                                return
                    # There was no anchors
                    break

        # Choose first starting point
        if self.left_element is None:
            pos = 0
        else:
            pos = self.left_element.end + self.spacer(self.left_element) + 1

        if anchor is not None:
            new_pos = anchor - self.length + 1
            # there might be an element what we have already found
            if new_pos > pos:
                pos = new_pos
            # might become negative
            if pos < 0:
                pos = 0
            # If we loosed an anchor then rollback with it
            if self.first_anchor is not None and pos > self.first_anchor:
                old_anchor = self.first_anchor
                self.first_anchor = None
                self.left_element.find_valid_pos(anchor=old_anchor, info='Loosed an anchor while getting new')
                return

        # Find invalid positions
        # pos is the first valid cell after the prev element (without main constraints)
        self.set_invalid(j=pos)
        # left: [XXXXXXX111-----]
        # self: [XXXXXXXXXXX11--] length: 2, color: 1
        for i, c in enumerate(self.colors[pos:]):
            if c != -1:
                self.tc[i+pos] = c
        # main: [--2-1XX--333---]
        # left: [X22------------] length: 2, color: 2
        #           |----------|  iterate here
        # self: [XXX-1XX--333---] color: 1
        # Find valid positions
        valid = False
        pattern = [self.color for _ in range(self.length)]
        if self.right_element is not None:
            if self.color == self.right_element.color:
                pattern += [0]
        while not valid:
            for i, c in enumerate(pattern):
                if self.tc[pos + i] != -1 and self.tc[pos + i] != c:
                    # If it is another color then we rollback
                    if self.tc[pos + i] != self.color and self.tc[pos+i] != 0:
                        self.first_anchor = None
                        self.left_element.find_valid_pos(anchor=pos + i, info='Found another color in pattern')
                        return
                    # If it is just because of an 'X', then try to move forward
                    pos += 1
                    # If we loosed an anchor then rollback
                    if self.first_anchor is not None and pos > self.first_anchor:
                        old_anchor = self.first_anchor
                        self.first_anchor = None
                        self.left_element.find_valid_pos(anchor=old_anchor, info='Loosed an anchor while moving')
                        return

                    # set prev points to invalid
                    self.set_invalid(j=pos)
                    break
                elif self.tc[pos + i] == c and c != 0:
                    if self.first_anchor is None:
                        self.first_anchor = pos + i  # we save only the first one
            else:
                valid = True
        if valid:
            self.pos = pos
            if print_output:
                print 'pos: %s' % pos
            if self.right_element is not None:
                if self.right_element.found:
                    if print_output:
                        print "[Info] Found Element %s" % self.id
                    for i in range(pos + len(pattern), self.right_element.pos):
                        if self.tc[i] != -1 and self.tc[i] != 0:  # it is a color
                            self.find_valid_pos(anchor=i, info='Found anchors before fix element')
                            return
                    self.right_element.find_valid_pos(info='Moving onto next element')
                    return
                else:
                    self.right_element.find_valid_pos(info='Moving onto next element')
                    return
            else:
                # look for anchors
                for i in range(pos + len(pattern), self.column.length):
                    if self.tc[i] != -1 and self.tc[i] != 0:
                        self.find_valid_pos(anchor=i, info='Found anchors before end')
                        return
                if print_output:
                    print '[Info]: Should stop now!'


class Vector(object):
    def __init__(self, **kwargs):
        self.elements = kwargs.pop('elements', [])
        self.column = None
        for element in self.elements:
            element.vector = self

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

    def create_copy(self, rotate=False):
        elements = [Element(id=e.id, color=e.color,
                            length=e.length, found=e.found, pos=e.pos, rotated=rotate, col_length=self.column.length)
                    for e in self.elements]
        if rotate:
            elements = elements[::-1]
        e = Vector(elements=elements)
        return e

    def arrange(self):
        if len(self.elements) > 0:
            self.elements[0].find_valid_pos()


class Source(object):
    def __init__(self):
        self.cells = np.array([[Cell(p=[i, j, 0]) for i in range(DEF_SIZE)] for j in range(DEF_SIZE)])
        self.vertical_vectors = []
        self.horizontal_vectors = []

    def print_it(self):
        for row in self.cells:
            print '|{}|'.format(''.join([str(cell.color) if cell.color > 0 else '-' for cell in row]))

        print 'Vertical vectors'
        for vi, vector in enumerate(self.vertical_vectors):
            for element in vector.elements:
                print '{}. length: {} color: {}'.format(vi, element.length, element.color)
        print 'Horizontal vectors'
        for vi, vector in enumerate(self.horizontal_vectors):
            for element in vector.elements:
                print '{}. length: {} color: {}'.format(vi, element.length, element.color)

    def randomize(self):
        for _ in range(DEF_SIZE*10):
            desired_length = random.randint(1, DEF_SIZE/3)
            position = random.randint(0, DEF_SIZE-1)
            column = random.randint(0, DEF_SIZE-1)
            color = random.randint(1, 5)
            direction = random.randint(0, 1)

            for index in range(desired_length):
                if position + index >= DEF_SIZE:
                    break
                if direction == 0:  # vertical
                    self.cells[column, position + index].color = color
                else:
                    self.cells[position + index, column].color = color

    def analyze(self):
        v, h = self.cells.shape
        # vertical analyze
        for c_i in range(v):
            self.vertical_vectors += [self._analyze_column(self.cells[c_i, :])]

        for c_i in range(v):
            self.horizontal_vectors += [self._analyze_column(self.cells[:, c_i])]

    @staticmethod
    def _analyze_column(cell_column):
        elements = []
        current_color = 0
        current_length = 0
        for c in cell_column:
            if c.color != current_color:
                if current_length > 0:
                    elements += [Element(color=current_color, length=current_length)]
                current_length = 0
                current_color = c.color
            if current_color > 0:
                current_color = c.color
                current_length += 1

        if current_length > 0:
            elements += [Element(color=current_color, length=current_length)]
        return Vector(elements=elements)
