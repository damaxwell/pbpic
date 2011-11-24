from pbpic import *
from pbpic.metric import PageVector

class Node:
  def __init__(self,name=None):
    self.name = name
    self.left = None
    self.right = None

  def addLeft(self,dist,node):
    self.left = Edge(dist,node)

  def addRight(self,dist,node):
    self.right = Edge(dist,node)

  def add(self,distL,nodeL,distR,nodeR):
    self.addLeft(distL,nodeL)
    self.addRight(distR,nodeR)

  def isLeaf(self):
    return self.left is None

class Edge:
  def __init__(self,dist,node):
    self.dist = dist
    self.node = node

nodes = [ Node("%d" % k) for k in range(10) ]  # Extra Node[0] will be ignored
root = nodes[9]
root.add(3,nodes[6],1,nodes[8])
nodes[6].add(1,nodes[1],1,nodes[2])
nodes[8].add(1,nodes[7],3,nodes[3])
nodes[7].add(2,nodes[4],2,nodes[5])

def leafinset(node,tscale):
  with inset() as i:
    moveto(0,0)
    rmoveto(0,-6*pt)
    if node.name is not None:
      placetex(node.name,origin=loc.uc)
    i.setextents(i.markedbox())
  return i

def treeinset(node,tscale,root=True):
  if isinstance(node,Edge):
    node = node.node
  if node.isLeaf():
    return leafinset(node,tscale)
  with inset() as i:
    scaleto(tscale)

    # Build the children insets
    left_inset  = treeinset(node.left,tscale,root=False)
    right_inset = treeinset(node.right,tscale,root=False)

    # Determine the width between children trees
    left_w  = PageVector(left_inset.pageExtents().width(),0)
    right_w = PageVector(right_inset.pageExtents().width(),0)
    gap = pageVector(.5,0)    
    dx = left_w/2+right_w/2+gap

    moveto(0,0); rmoveto(-dx/2); rmoveto(0,-node.left.dist)
    left_tip=currentpoint()
    moveto(0,0); rmoveto(dx/2); rmoveto(0,-node.right.dist)
    right_tip=currentpoint()
    
    # Draw the tree branches
    moveto(left_tip)
    rlineto(0,node.left.dist)
    rlineto(dx)
    lineto(right_tip)
    stroke()
    
    # Draw the left child
    moveto(left_tip)
    left_inset.drawto(getcanvas())
    moveto(left_tip)
    with ctmsave():
      scaleto(1*pt)
      draw(paths.square,2*3)
      kfill(color.red);stroke()

    # Draw the right child
    moveto(right_tip)
    right_inset.drawto(getcanvas())
    moveto(right_tip)
    with ctmsave():
      scaleto(1*pt)
      draw(paths.circle,3)
      kfill(color.red);stroke()

    if root:
      # path() + (0,0) - (0,1); stroke()
      mark('root',(0,0))
      with ctmsave():
        scaleto(1*pt)
        draw(paths.n_gon,r=3.5,n=5)
        kfill(color.red);stroke()

    if node.name is not None:
      moveto(0,0)
      rmoveto(0,-6*pt)    
      placetex(node.name,origin=loc.uc)
    
    i.setextents(i.markedbox())
  return i
