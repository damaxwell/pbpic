from pbpic import *
import trees

nodes = [ trees.Node("%d" % k) for k in range(10) ]  # Extra Node[0] will be ignored
root = nodes[9]
root.add(3,nodes[6],1,nodes[8])
nodes[6].add(1,nodes[1],1,nodes[2])
nodes[8].add(1,nodes[7],3,nodes[3])
nodes[7].add(2,nodes[4],2,nodes[5])


pbpbegin(10*cm,10*cm,'pdf')
translate(loc.center)

moveto(0,0)
i = trees.treeinset(root,0.5*cm)
i.drawto(getcanvas(),origin=loc.center)

pbpend()
