from pyCross.base import Vector, Column, Element, set_def_size

set_def_size(25)

print "[Test-1]: simple left right"
elements = [
    Element(color=1, length=1),
    Element(color=1, length=1),
    Element(color=2, length=3),
    Element(color=1, length=4),
]
v = Vector(elements=elements)
c = Column(vector=v)
c.cells[4].color = 1
c.cells[7].color = 1
c.cells[17].color = 1

c.parse(print_output=True)
print '----------------------------'
print "[Test-2]: with fix element"
elements = [
    Element(color=1, length=1),
    Element(color=1, length=1),
    Element(color=1, length=2, pos=6, found=True),
    Element(color=2, length=3),
    Element(color=1, length=4),
]
v = Vector(elements=elements)
c = Column(vector=v)
c.cells[4].color = 1
c.cells[6].color = 1
c.cells[7].color = 1
c.cells[6].id[0] = elements[2].id
c.cells[7].id[0] = elements[2].id
c.cells[17].color = 1

c.parse()
print '----------------------------'
print "[Test-3]: with fix color"
elements = [
    Element(color=1, length=1),
    Element(color=1, length=2),
    Element(color=2, length=3),
    Element(color=1, length=4),
]
v = Vector(elements=elements)
c = Column(vector=v)
c.cells[4].color = 1
c.cells[7].color = 1
c.cells[12].color = elements[2].color
c.cells[12].id[0] = elements[2].id
c.cells[17].color = 1

c.parse()
print '----------------------------'
print "[Test-3.1]: run again"
c.parse()
print '----------------------------'
print "[Test-3.2]: run again with new color"
c.cells[14].color = elements[2].color
c.cells[14].id[0] = elements[2].id
c.parse()
print '----------------------------'
