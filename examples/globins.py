from pbpic import *
from trees import Node
import trees
from pbpic.arrow import ArrowTo, ArrowHead

x=.5;w=.4
a=Node();a.add(2,Node(r"theta"),1,Node(r"alpha"))
b=Node();b.add(x,a,1+x,Node("zeta"))
c=Node();c.add(.7,Node("epsilon"),.5,Node("gamma"))
d=Node();d.add(.3,Node("beta"),.3,Node("delta"))
e=Node();e.add(1,c,.5,d)
r=Node();r.add(w,b,1+x+w,e)

style.setstyle(arrow,tip=arrow.ArrowHead(width=5,length=5,wingangle=1/6.))
arrowto=arrow.ArrowTo()
tiltspreader=arrow.ArrowTo(tip=arrow.TiltSpreaderHead(theta=.1,width=10,length=1))

fancytreefig = trees.TreeFigure(leaf=trees.leafNode,interior=trees.interiorNode,root=trees.interiorNode)

pbpbegin(15*cm,10*cm,'pdf')
style.setstyle(pbptex,preamble = r'\documentclass[12pt]{article}\usepackage[lf]{MinionPro}\pagestyle{empty}\begin{document}')


with inset() as bigtree:
  scaleto(1*cm)
  moveto(0,0)
  with inset() as tree:
    scaleto(1*cm)
    markpoint('root',(0,0))
    draw(fancytreefig,r,at='root')
  tree.setextents(tree.markedbox())
  tree.markpoint('ll',loc.ll,'lr',loc.lr);
  addmarks(tree,'tree')

  myo_tip = point('tree.ll')-vector(1.3,1)
  root=point('tree.root')
  top=root+vector(0,1)
  dy=(top.y-myo_tip.y)/2
  moveto(root)
  lineto(top)
  lineto(myo_tip.x,top.y)
  p=currentpoint()
  stroke()

  moveto(p)
  rmoveto(0,-dy)
  rmoveto(0,2*pt)
  draw(tiltspreader,at=p,to=currentpoint())

  moveto(myo_tip)
  rmoveto(0,dy)
  rmoveto(0,-2*pt)
  draw(tiltspreader,at=myo_tip,to=currentpoint())
    
  moveto(myo_tip)
  draw(trees.leafNode,Node("myoglobin"))
  
  moveto('tree.root')
  tree.drawto(getcanvas())
  
  moveto('tree.root')
  draw(trees.interiorNode,r)
  
  tree_left=point('tree.ll').x;tree_right=point('tree.lr').x
  moveto((tree_left+tree_right)/2,point('leaf_myoglobin.origin').y)
  rmoveto(0,-6*pt)
  p=currentpoint()
  hemo = texinset(r'h\ae moglobins')
  hemo.markpoint('cl',loc.cl,'cr',loc.cr)
  hemo.drawto(getcanvas(),origin=loc.uc,marks='hemo')
  moveto('hemo.cl')
  rmoveto(-3*pt,0)
  draw(arrowto,to=(tree_left,currentpoint().y))
  
  moveto('hemo.cr')
  rmoveto(3*pt,0)
  draw(arrowto,to=(tree_right,currentpoint().y))
bigtree.setextents(bigtree.markedbox())

draw(bigtree,at=loc.center,origin=loc.center)

pbpend()