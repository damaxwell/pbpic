from __future__ import division
from pbpic import *
from pbpic.geometry import Polar
from pbpic.paths import polygon

w=10*cm; h=10*cm
pbpbegin(w,h,'pdf')
translate('center')

# applystyle(thickLine)
scaleto(1*cm)

r=3
# Exterior hexagon vertices
bdypts = [ Polar(r,k/6) for k in range(6) ]
# Interior triangle vertices, rotated 1/2 turn
ipts = [ Polar(r/1.5,k/3+0.5) for k in range(3) ]

# Draw inner triangle
setlinecolor(color.red)
draw(polygon,ipts)
stroke()

# Draw connecting segments
setlinecolor(color.blue)
adj = [ [0,2], [0,3], [0,4], [1,4], [1,5], [1,0], [2,0], [2,1], [2,2] ]
for a in adj:
  path() + bdypts[a[1]] - ipts[a[0]]
stroke()

# Draw outer vertices
setlinecolor(color.red)
draw(polygon,bdypts)
stroke()

setlinecolor(color.black)
labels=[ '$a$', '$b$', '$c$', '$a$', '$b$', '$c$']
t = 0
for l in labels:
  v = (Polar(r,t)+Polar(r,t+1/6))/2 # Midpoint of edge
  dv = vector(15*pt,v)              # Additional 15pt away from center
  moveto(v+dv)
  drawtex(l,origin='center')
  t += 1/6

pbpend()
