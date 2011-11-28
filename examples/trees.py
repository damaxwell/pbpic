import pbpic as pbp
from pbpic import pt, texinset, loc, paths, color
from pbpic.metric import PageVector, PagePoint

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

def basecenter(canvas):
  y=canvas.pagePoint('origin').y
  x=canvas.extents().center().x
  return PagePoint(x,y)

def leafNode(canvas,node):
  with canvas.ctmsave():
    canvas.scaleto(1*pt)
    p=canvas.currentpoint()
    canvas.build(paths.circle,3)
    canvas.fillstroke(fillcolor=color.red)
    if node.name is not None:
      canvas.moveto(p)
      canvas.draw(labeledNode,node)

def labeledNode(canvas,node):
  if node.name is not None:
    canvas.rmoveto(0,-14*pt)
    label=texinset(node.name)
    canvas.draw(label,origin=basecenter,marks="leaf_"+node.name)

def interiorNode(canvas,node):
  with canvas.ctmsave():
    canvas.scaleto(1*pt)
    canvas.build(paths.square,2*3)
    canvas.fillstroke(fillcolor=color.red)

class TreeFigure:
  def __init__(self,leaf=None,interior=None,root=None):
    self.leafNode = leaf
    self.interiorNode = interior
    self.root = root
    self.branchgap=0.5

  def drawto(self,canvas,node=None,isRoot=True):
    if node.isLeaf():
      if self.leafNode is not None:
        canvas.draw(self.leafNode,node)
      return

    # Make insets for the left and right branches
    left_branch = pbp.Inset(init=canvas)
    left_branch.draw(self,node.left.node,at=(0,0),isRoot=False)
    left_branch.setextents(left_branch.markedbox())

    right_branch = pbp.Inset(init=canvas)
    right_branch.draw(self,node.right.node,at=(0,0),isRoot=False)
    right_branch.setextents(right_branch.markedbox())

    # Determine the width between children trees in page coordinates
    # This is a little awkward.  Calling pageVector(left_branch.pageExtents().width()) would
    # do the wrong thing.  How to explian this?
    left_w  = pbp.metric.PageVector(left_branch.pageextents().width(),0)
    right_w = pbp.metric.PageVector(right_branch.pageextents().width(),0)
    gap = canvas.pageVector(self.branchgap,0)    
    dx = left_w/2+right_w/2+gap

    c = canvas
    base=c.currentpoint()

    c.moveto(base); c.rmoveto(-dx/2); c.rmoveto(0,-node.left.dist)
    left_tip=c.currentpoint()

    c.moveto(base); c.rmoveto(dx/2); c.rmoveto(0,-node.right.dist)
    right_tip=c.currentpoint()

    # Draw the tree branches
    c.moveto(left_tip)
    c.rlineto(0,node.left.dist)
    c.rlineto(dx)
    c.lineto(right_tip)
    c.stroke()
    
    c.moveto(left_tip)
    c.draw(left_branch)
    
    c.moveto(right_tip)
    c.draw(right_branch)

    if isRoot:
      if self.root is not None:
        c.moveto(base)
        c.draw(self.root,node)
    elif self.interiorNode is not None:
      c.moveto(base)
      c.draw(self.interiorNode,node)
