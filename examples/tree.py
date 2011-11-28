from pbpic import *
import trees

nodes = [ trees.Node("%d" % k) for k in range(10) ]  # Extra Node[0] will be ignored
root = nodes[9]
root.add(3,nodes[6],1,nodes[8])
nodes[6].add(1,nodes[1],1,nodes[2])
nodes[8].add(1,nodes[7],3,nodes[3])
nodes[7].add(2,nodes[4],2,nodes[5])

def labeledInterior(c,node):
  c.rmoveto(0,3*pt)
  c.draw(trees.labeledNode,node)

fancytreefig = trees.TreeFigure(leaf=trees.leafNode,interior=trees.interiorNode,root=trees.interiorNode)
basictreefig = trees.TreeFigure(leaf=trees.labeledNode,interior=labeledInterior)

W=10.;H=7.
pbpbegin(W*cm,H*cm,'pdf')
scaleto(1*cm)

with inset() as basictree:
  scaleto(1*cm)
  scale(1,0.5)
  draw(basictreefig,node=root,at=(0,0))
basictree.setextents(basictree.markedbox())
basictree.markpoint(loc.lc,'lc')

with inset() as fancytree:
  scaleto(1*cm)
  scale(1,0.5)
  draw(fancytreefig,node=root,at=(0,0))
fancytree.setextents(fancytree.markedbox())
fancytree.markpoint(loc.lc,'lc')

h=basictree.pageextents().height()
w1=basictree.pageextents().width()
w2=fancytree.pageextents().width()
dw=(getcanvas().pageextents().width()-w1-w2)/3

moveto(0,H/2)
scaleto(1*pt)
rmoveto(dw,0)
rmoveto(w1/2,0)
rmoveto(0,h/2)
p=currentpoint()
draw(basictree,marks='plain')

moveto(p)
rmoveto(w1/2+dw+w2/2,0)
draw(fancytree,marks='fancy')

moveto('plain.lc')
rmoveto(0,-10*pt)
drawtex('Plain',origin=loc.uc)

moveto('fancy.lc')
rmoveto(0,-10*pt)
drawtex('Fancy',origin=loc.uc)

pbpend()
