from __future__ import division
from math import cos, sin, sqrt, pi
from metric import Point, Vector
import random

def arc(canvas,c,r,t0,t1):
  """Draws a circular arc to the path of canvas with center c and radius r from cf angle t0 to cf angle t1.  If t0 is larger than t1,
  then t1 is increased by the least integer that makes it bigger than t1.  If no currentpoint exists, an initial moveto is done
  to the start of the arc, otherwise a lineto is performed.
  """
  while t1<t0:
    t1+=1
  xc = c[0]; yc=c[1]
  x0 = xc+r*cos(2*pi*t0); y0 = yc+r*sin(2*pi*t0);
  if canvas.currentpointexists():
    canvas.lineto(x0,y0)
  else:
    canvas.moveto(x0,y0)
  tp = t0
  while True:
    tp += 0.25
    if tp > t1-0.1:
      tp = t1
    x1 = xc+r*cos(2*pi*tp); y1 = yc+r*sin(2*pi*tp);
    _arcpath(canvas,c,r,x0,y0,x1,y1)
    if tp >= t1:
      break
    x0 = x1; y0 = y1

def _arcpath(canvas,c,r,x0,y0,x3,y3):
  xc = c[0]; yc=c[1]
  xa = x0-xc; ya = y0-yc
  xb = x3-xc; yb = y3-yc
  
  q1 = r*r
  q2 = q1+xa*xb+ya*yb
  k = 4/3*(sqrt(2*q1*q2)-q2 )/(xa*yb-xb*ya)
  
  x1 = x0 - k*ya; y1 = y0 + k*xa
  x2 = x3 + k*yb; y2 = y3 - k*xb

  canvas.curveto(x1,y1,x2,y2,x3,y3)

def circle(canvas,r):
  """Adds a closed circle to the path of canvas with center c and radius r. If a currentpoint exists, the box is centered at it, 
  otherwise the box is centered at the origin.
  """
  if canvas.currentpointexists():
    c = canvas.currentpoint()
  else:
    c = Point(0,0)  
  canvas.moveto(c[0]+r,c[1])
  arc(canvas,c,r,0,1)
  canvas.closepath()

def wedge(canvas,r,v1,v2):
  """Adds a wedge to path with radius r with one side parallel to v1 and another parallel to v2.  The curve of the wedge travels counterclockwise
  from v1 to v2"""
  if canvas.currentpointexists():
    p0 = canvas.currentpoint()
  else:
    p0 = Point(0,0)  
  canvas.moveto(p0)
  t1=Vector(v1[0],v1[1]).fangle()
  t2=Vector(v2[0],v2[1]).fangle()
  arc(canvas,p0,r,t1,t2)
  canvas.closepath()


def box(canvas,r):
  """Adds a box to the path with sidelength 2*r.  If a currentpoint exists, the box is centered at it, 
  otherwise the box is centered at the origin.
  """    
  if canvas.currentpointexists():
    c = canvas.currentpoint()
  else:
    c = Point(0,0)  
  canvas.path() + (c.x+r,c.y-r) - (c.x+r,c.y+r) - (c.x-r,c.y+r) - (c.x-r,c.y-r) - 0


def graph(canvas,f,x0,x1,N=200):
  dx = float(x1-x0)/N
  x=x0
  y0 = f(x0)
  if canvas.currentpointexists():
    canvas.lineto(x,y0)
  else:
    canvas.moveto(x,y0)
  for k in range(N):
    x+=dx
    canvas.lineto(x,f(x))

def rect(canvas,w,h):
  """Adds a rectangle of width 'w' and height 'h' to the current path with its lower left corner at the current point (or at the
  origin if no currentpoint exists)"""
  if not canvas.currentpointexists():
    canvas.moveto(0,0)
  canvas.rlineto(w,0)
  canvas.rlineto(0,h)
  canvas.rlineto(-w,0)

def hlines(canvas,w,dy,N):
  """Adds a sequence of N horizontal lines of width w spaced dy between to the current path, starting at the currentpoint."""
  if canvas.currentpointexists():
    c = canvas.currentpoint()
  else:
    c=Point(0,0)

  x0=c.x; y0=c.y
  for k in range(N):
    canvas.moveto(x0,y0)
    canvas.rlineto(w,0)
    y0 += dy

def vlines(canvas,h,dx,M):
  """Adds a sequence of M vertical lines of height h spaced dx between to the current path starting at the currentpoint."""
  if canvas.currentpointexists():
    c = canvas.currentpoint()
  else:
    c=Point(0,0)

  x0=c.x; y0=c.y
  for k in range(M):
    canvas.moveto(x0,y0)
    canvas.rlineto(0,h)
    x0 += dx

def polylines(canvas,*args):
  if len(args) == 2:
    x=args[0]
    y=args[1]
  else:
    x=args[0][:,0]
    y=args[0][:,1]
  
  canvas.moveto(x[0],y[0])
  for k in range(1,len(x)):
    canvas.lineto(x[k],y[k])

def grid(canvas,bbox,N,M):
  """Adds a grid of NxM (horzontal x vertical) cells filling the box bbox to the current path."""
  dx = bbox.width()/N
  dy = bbox.height()/M
  canvas.moveto(bbox.ll())
  hlines(canvas,bbox.width(),dy,M+1)
  canvas.moveto(bbox.ll())
  vlines(canvas,bbox.height(),dx,N+1)


def r(x0,x1):
  l = x1-x0
  center = (x0+x1)/2.
  return random.gauss(center,l/6.)

def potato(canvas,seed,nodes=False):
  random.seed(seed)
  if canvas.currentpointexists():
    c = canvas.currentpoint()
  else:
    c=Point(0,0)
  W= 1.5
  H =1
  p0 = c+0.5*Vector(r(-1,1),-H)
  p1 = c+0.5*Vector(W,r(-1,1)*H)
  p20 = c+0.5*Vector(r(1/3.,1)*W,r(0.8,1)*H)
  p21 = c+0.5*Vector(r(-1/3.,1/3.)*W,r(0,1)*H)
  p22 = c+0.5*Vector(r(-1,-1/3.)*W,H)
  p3 = c+0.5*Vector(-W,r(-1,1)*H)
  left = Vector(-1,0)
  right = Vector(1,0)
  up = Vector(0,1)
  down = Vector(0,-1)

  blob(canvas,p0,right,p1,up,p20,left,p21,left,p22,left,p3,down)

  if nodes:
    pts = [ p0, p1, p20, p21, p22, p3]
    from metric import pt
    for p in pts:
      canvas.moveto(p)
      with canvas.ctmsave():
        canvas.scaleto(1*pt)
        canvas.addpath(box,1)

def blob(canvas,*args):
  data = [ (args[2*k],args[2*k+1]) for k in range(int(len(args)/2)) ]
  p0 = Vector(data[0][0][0],data[0][0][1])
  v0 = data[0][1].unitvector()

  canvas.moveto(p0)
  for d in data[1:]:
    p1 = Vector(d[0][0],d[0][1])
    r=(p0-p1).length()/2.5

    v1 = d[1].unitvector()
    q0 = p0+r*v0
    q1 = p1-r*v1
    canvas.curveto(q0,q1,p1)
    p0=p1; v0=v1;

  p1 = Vector(data[0][0][0],data[0][0][1])
  r=(p0-p1).length()/2.5
  v1 = data[0][1].unitvector()
  q0 = p0+r*v0
  q1 = p1-r*v1
  canvas.curveto(q0,q1,p1)
  canvas.closepath()
