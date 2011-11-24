from pbpic import *
from pbpic import paths, graph, geometry
import math

W=2.5*inch; H=2.5*inch

x0=0; x1=2;
y0=-3; y1=-1;

pbpbegin(W,H,'pdf')

pagebox=extents()
pagebox.addmargin(left=-45,bottom=-45,top=-10,right=-10)

gbox=geometry.BBox([x0,y0,x1,y1])
window(pagebox,gbox)

addpath(graph.boxaxis,gbox)
stroke()
with gsave():
  addpath(gbox)
  clip()

  setlinewidth(0.5*pt)

  for y in [y0,y1]:
    with ctmsave():
      translate(x0,y)
      yscale=vector(10*pt,(0,1))[1]
      scale(1,yscale)
      for x in [0,1]:
        moveto(x,0)
        addpath(graph.xlogticks,n=10,minor=0.5)
      stroke()

  for x in [x0,x1]:
    with ctmsave():
      translate(x,y0)
      xscale=vector(10*pt,(1,0))[0]
      scale(xscale,1)
      for y in [0,1]:
        moveto(0,y)
        addpath(graph.ylogticks,n=10,minor=0.5)
      stroke()

for k in [0,1,2]:
  moveto(k,y0)
  rmoveto(0,-5*pt)
  placetex('$10^{%d}$' % k,'uc')

for k in [-3,-2,-1]:
  moveto(x0,k)
  rmoveto(-5*pt,0)
  placetex('$10^{%d}$' % k,'cr')
  
moveto((x0+x1)/2,y0)
rmoveto(0,-15*pt)
rmoveto(0,-4*pt)
placetex('iteration','uc')

translate(x0,(y0+y1)/2)
rotate(0.25)
moveto(0,0)
rmoveto(0,30*pt)
placetex('$L^2$ discrepancy','lc')


pbpend()
