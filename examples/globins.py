from pbpic import *
from trees import Node, treeinset

x=.5;w=.4
a=Node();a.add(2,Node(r"theta"),1,Node(r"alpha"))
b=Node();b.add(x,a,1+x,Node("zeta"))
c=Node();c.add(.7,Node("epsilon"),.5,Node("gamma"))
d=Node();d.add(.3,Node("beta"),.3,Node("delta"))
e=Node();e.add(1,c,.5,d)
r=Node();r.add(w,b,1+x+w,e)

pbpbegin(15*cm,10*cm,'pdf')
scaleto(1*cm)
translate(loc.center)
moveto(0,0)

tree=treeinset(r,1*cm)
tree.mark('ll',loc.ll,'lr',loc.lr);
tree.addmarks(getcanvas(),'tree',origin=loc.center)

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
rmoveto(0,-3*pt)
myo=texinset("myoglobin")
myo.drawto(getcanvas(),origin=loc.uc,marks='myo')

moveto(0,0)
tree.drawto(getcanvas(),origin=loc.center)

tree_left=point('tree.ll').x;tree_right=point('tree.lr').x
moveto((tree_left+tree_right)/2,point('myo.origin').y)
rmoveto(0,-6*pt)
p=currentpoint()
hemo = texinset(r'h\ae moglobins')
hemo.mark('cl',loc.cl,'cr',loc.cr)
hemo.drawto(getcanvas(),origin=loc.uc,marks='hemo')
moveto('hemo.cl')
rmoveto(-3*pt,0)
lineto(tree_left,currentpoint().y)
stroke()

moveto('hemo.cr')
rmoveto(3*pt,0)
lineto(tree_right,currentpoint().y)
stroke()

pbpend()