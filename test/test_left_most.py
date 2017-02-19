from pyCross.base import Vector, Column, Element

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

c.parse()
print '----------------------------'
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
c.cells[6].id[0] = elements[3].id
c.cells[7].id[0] = elements[3].id
c.cells[17].color = 1

c.parse()
