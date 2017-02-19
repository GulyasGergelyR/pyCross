# Default Size
DEF_SIZE = 20

dim_x_id = 1000
x_id = 10
dim_y_id = 2000
y_id = 10
dim_z_id = 3000
z_id = 10


class Cell(object):
    def __init__(self, **kwargs):
        self.p = kwargs.pop('p', [0, 0, 0])
        self.id = kwargs.pop('id', [-2, -2, -2])
        self.color = kwargs.pop('color', -1)


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
        return [cell.color for cell in self.cells]

    def left_most(self):
        self.vector.arrange()
        self.print_it()

    def print_it(self):
        print 'sub:  |{}|'.format(''.join(['X' if c == 0 else str(c) for c in self.colors]))


class Column(BaseColumn):
    def __init__(self, **kwargs):
        super(Column, self).__init__(**kwargs)
        self.left_clone = None
        self.right_clone = None

    def create_copy(self, rotate=False):
        cells = [Cell(color=cell.color, id=cell.id[:]) for cell in self.cells]
        if rotate:
            cells = cells[::-1]
        c = SubColumn(parent=self, cells=cells, vector=self.vector.create_copy(rotate), rotated=rotate)
        return c

    def parse(self):
        self.print_it()
        self.left_clone = self.create_copy()
        self.left_clone.left_most()
        self.right_clone = self.create_copy(rotate=True)
        self.right_clone.left_most()
        self.merge_copies()

    def merge_copies(self):
        # get merged table
        pass

    def get_result(self, copy):
        for element in copy.vector.elements:
            if element.found:
                e = self.vector.get(element)
                e.found = True
                e.pos = element.pos

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
        # TODO fix id hack
        return [cell.id[0] for cell in self.cells]

    def spacer(self, element):
        if self.color == element.color:
            return 1
        else:
            return 0

    def set_invalid(self, i=0, j=None, length=0):
        j = j if j is not None else i+length
        for k in range(i, j):
            self.tc[k] = 0

    def find_valid_pos(self, anchor=None, info='None'):
        print_output = False

        if print_output:
            print '[Info]: %s - id: ' % info, self.id
        # TODO remove usage of tc
        if len(self.tc) == 0:
            self.tc = [-1 for _ in range(self.column.length)]

        # We have already found this, go on
        if self.found:
            if anchor is not None:
                raise ValueError('Trying to move an already found element!')
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
                        for j in range(pos, anchor):
                            if self.colors[j] != -1 and self.colors[j] != 0:  # it is a color
                                self.left_element.find_valid_pos(anchor=j, info='Found anchors before fix color')
                                return
                    # There was no anchors
                    break

        # Choose first starting point
        if anchor is not None:
            pos = anchor - self.length + 1
            # If we loosed an anchor then rollback with it
            if self.first_anchor is not None and pos > self.first_anchor:
                old_anchor = self.first_anchor
                self.first_anchor = None
                self.left_element.find_valid_pos(anchor=old_anchor, info='Loosed an anchor while getting new')
                return
        elif self.left_element is None:
            pos = 0
        else:
            pos = self.left_element.end + self.spacer(self.left_element) + 1

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
                    if self.tc[pos + i] != self.color:
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
        self.elements[0].find_valid_pos()
