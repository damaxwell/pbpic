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

style.setstyle(ArrowHead,width=3,length=3,wingangle=1/6.)
arrow=ArrowTo()
fancytreefig = trees.TreeFigure(leaf=trees.leafNode,interior=trees.interiorNode,root=trees.interiorNode)

pbpbegin(15*cm,10*cm,'pdf')
style.setstyle(pbptex,preamble = r'\documentclass[12pt]{article}\usepackage[lf]{MinionPro}\pagestyle{empty}\begin{document}')


with inset() as bigtree:
  scaleto(1*cm)
  moveto(0,0)
  with inset() as tree:
    scaleto(1*cm)
    markpoint((0,0),'root')
    draw(fancytreefig,r,at='root')
  tree.setextents(tree.markedbox())
  tree.markpoint(loc.ll,'ll',loc.lr,'lr');
  addmarks(tree,'tree')

  myo_tip = point('tree.ll')-vector(1.3,1)
  root=point('tree.root')
  top=root+vector(0,1)
  dy=(top.y-myo_tip.y)/3
  moveto(root)
  lineto(top)
  lineto(myo_tip.x,top.y)
  rlineto(0,-dy)
  p=currentpoint()
  stroke()
  
  with gsave():
    setlinecap('butt')
    setdash([3,4],1)
    moveto(p); rlineto(0,-dy)
    p=currentpoint()
    stroke()
  
  moveto(p); lineto(myo_tip)
  stroke()
  
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
  hemo.markpoint(loc.cl,'cl',loc.cr,'cr')
  hemo.drawto(getcanvas(),origin=loc.uc,marks='hemo')
  moveto('hemo.cl')
  rmoveto(-3*pt,0)
  draw(arrow,to=(tree_left,currentpoint().y))
  
  moveto('hemo.cr')
  rmoveto(3*pt,0)
  draw(arrow,to=(tree_right,currentpoint().y))
bigtree.setextents(bigtree.markedbox())

draw(bigtree,at=loc.center,origin=loc.center)

pbpend()