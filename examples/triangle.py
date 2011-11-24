from pbpic import *
from pbpic.geometry import Point

# texStyle = Style('tex',preamble=r'\documentclass[10pt]{article}\usepackage{MinionPro}\pagestyle{empty}\begin{document}')
# # texStyle = Style('tex',preamble=r'\documentclass[10pt]{article}\pagestyle{empty}\begin{document}')
# setstyle(texStyle)

# Vertices of the triangle
v = [ Point(-2,1), Point(2,-0.5), Point(0,1.5) ]

# Vertex labels
labels=[r'$\alpha$',r'$\beta$',r'$\gamma$']

# Vectors pointing along each edge
w = [ (v[k%3]-v[(k-1)%3]).unitvector() for k in range(4) ]

# Radius of the yellow wedges.
arc_r = 0.4 

pbpbegin(5*cm,5*cm,'pdf')
scaleto(1*cm)
translate(loc.center)

# Add the triangle
draw(paths.polygon,v)
stroke()

# Add each of the circular wedges
setfillcolor(color.yellow)
for k in range(3):
  moveto(v[k])
  draw(paths.wedge,arc_r,w[k],w[k+1])
fillstroke()

# Add the vertex labels
locs=[loc.lc,loc.border((w[1]+w[2])/2),loc.ll]
for k in range(3):
  moveto(v[k])           # Move to the vertex.
  wmid = (w[k]+w[k+1])/2 # Points straight into the yellow wedge.
  rmoveto(-3*pt,wmid)  # Offset away from the yellow wedge by 3 pts.
  placetex(labels[k],origin=locs[k])

# Add the exploding circle
translate(-1,-1)
for k in range(3):
  wmid = ((w[k]+w[k+1])/2).unitvector()
  
  moveto(0,0)
  rmoveto(2*pt,wmid)
  tip = currentpoint()
  draw(paths.wedge,arc_r,w[k],w[k+1])
  fillstroke()  # Fill color of yellow still used.

  moveto(tip+arc_r*wmid) # At middle of outer boundary of exploded wedge.
  rmoveto(3*pt,wmid)     # And a little more
  placetex(labels[k],origin=loc.border(-wmid))

pbpend()
