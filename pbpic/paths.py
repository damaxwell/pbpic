from __future__ import division
from math import cos, sin, sqrt, pi
from geometry import Point, Vector, Polar
import random

def line(canvas,A,B):
  canvas.moveto(A);
  canvas.lineto(B);


def arc(canvas,center=(0,0),r=0,t0=0,t1=0.5,orientation=1):
  """Draws a circular arc to the path of canvas with center c and radius r from cf angle t0 to cf angle t1.
  If no currentpoint exists, an initial moveto is done to the start of the arc, otherwise a lineto is performed.
  """
  c=center
  if orientation == 1:
    s=1
    while t1<t0:
      t1+=1
  else:
    s=-1
    while t1>t0:
      t1-=1
    
  xc = c[0]; yc=c[1]
  x0 = xc+r*cos(2*pi*t0); y0 = yc+r*sin(2*pi*t0);
  if canvas.currentpointexists():
    canvas.lineto(x0,y0)
  else:
    canvas.moveto(x0,y0)
  tp = t0
  while True:
    tp += s*0.25
    if s*(t1-tp) < 0.1:
      tp = t1
    x1 = xc+r*cos(2*pi*tp); y1 = yc+r*sin(2*pi*tp);
    canvas.curveto(*_arcpath(canvas,c,r,x0,y0,x1,y1))
    if s*tp >= s*t1:
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

  return (x1,y1,x2,y2,x3,y3)

def circle(canvas,r=1):
  """Adds a closed circle to the path of canvas with center c and radius r. If a currentpoint exists, the box is centered at it, 
  otherwise the box is centered at the origin.
  """
  c = canvas.currentpoint()
  canvas.moveto(c[0]+r,c[1])
  arc(canvas,c,r,0,1)
  canvas.closepath()

def wedge(canvas,r=1,v1=[0,1],v2=[1,0],orientation=1):
  """Adds a wedge to path with radius r with one side parallel to v1 and another parallel to v2.  The curve of the wedge travels counterclockwise
  from v1 to v2"""
  
  p0 = canvas.currentpoint()
  canvas.moveto(p0)
  t1=Vector(v1[0],v1[1]).angle()
  t2=Vector(v2[0],v2[1]).angle()
  arc(canvas,p0,r,t1,t2,orientation=orientation)
  canvas.closepath()


def square(canvas,L=1):
  """Adds a square to the path with sidelength r.  If a currentpoint exists, the box is centered at it, 
  otherwise the box is centered at the origin.
  """
  c = canvas.currentpoint()
  r=L/2
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

def rect(canvas,w=1,h=1):
  """Adds a rectangle of width 'w' and height 'h' to the current path with its lower left corner at the current point (or at the
  origin if no currentpoint exists)"""
  c = canvas.currentpoint()
  canvas.moveto(c)
  canvas.rlineto(w,0)
  canvas.rlineto(0,h)
  canvas.rlineto(-w,0)
  canvas.closepath()
  
def hlines(canvas,w=1,dy=1,N=2):
  """Adds a sequence of N horizontal lines of width w spaced dy between to the current path, starting at the currentpoint."""
  c = canvas.currentpoint()

  x0=c.x; y0=c.y
  for k in range(N):
    canvas.moveto(x0,y0)
    canvas.rlineto(w,0)
    y0 += dy

def vlines(canvas,h=1,dx=1,M=2):
  """Adds a sequence of M vertical lines of height h spaced dx between to the current path starting at the currentpoint."""

  c = canvas.currentpoint()
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

def ex(canvas,L=1):
  canvas.rmoveto(L/2,L/2)
  canvas.rlineto(-L,-L)  
  canvas.rmoveto(0,L)
  canvas.rlineto(L,-L)

def polygon(canvas,*args):
  # If the argument is a single list of points, extract the list,
  # otherwise args will be a tuple of points.
  if len(args) == 1:
    args = args[0]
  canvas.moveto(args[0])
  for k in range(1,len(args)):
    canvas.lineto(args[k])
  canvas.closepath()

def n_gon(canvas,r=1,n=3,phase=0):
  phase = phase+.25
  canvas.moveto(Polar(r,phase))
  for k in range(1,n):
    canvas.lineto(Polar(r,phase+k/float(n)))
  canvas.closepath()
  
def grid(canvas,box=None,N=1,M=1):
  """Adds a grid of NxM (horzontal x vertical) cells filling the box bbox to the current path."""
  dx = box.width()/M
  dy = box.height()/N
  canvas.moveto(box.ll())
  hlines(canvas,box.width(),dy,N+1)
  canvas.moveto(box.ll())
  vlines(canvas,box.height(),dx,M+1)


def r(x0,x1):
  l = x1-x0
  center = (x0+x1)/2.
  return random.gauss(center,l/6.)

def potato(canvas,seed,nodes=False):
  random.seed(seed)
  c = canvas.currentpoint()

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
        canvas.build(box,1)

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
