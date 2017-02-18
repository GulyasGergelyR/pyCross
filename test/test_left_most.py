from pyCross.base import Vector, Column, Element

elements = [
    Element(color=1, length=1),
    Element(color=2, length=2),
    Element(color=1, length=3),
    Element(color=1, length=4),
]
v = Vector(elements=elements)
c = Column(vector=v)
c.cells[1].color = 0
c.cells[4].color = 0

c.parse()
