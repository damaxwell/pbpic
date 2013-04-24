from pbpic import *
from math import floor, sin, cos, tan, pi
import math
R=2

def Exp(s):
  return geometry.Point( math.cos(2*math.pi*s), math.sin(2*math.pi*s) )

def hypline(canvas,s0,s1):
  ds = s1-s0
  s = ds-math.floor(ds)
  sigma = 1
  if s>0.5:
    s=1-s
    sigma=-1

  eps = 1e-4
  s=min(.5-eps,s)
  s=max(eps,s)

  r=math.tan(s*math.pi)
  P0 = Exp(s0); P1 = Exp(s1); 
  C = P0-r*sigma*geometry.Vector(P0.y,-P0.x)

  t0 = (P0-C).angle()
  t1 = (P1-C).angle()

  # Correct start and end angles for 
  if sigma<0 and t0>t1:
    t0-=1
  if sigma>0 and t0<t1:
    t0+=1

  canvas.build(paths.arc,center=C,r=r,t0=t0,t1=t1,orientation=-1)

pbpbegin(7*cm,6*cm,'pdf')
scaleto(R*cm)
translate(loc.center)
moveto(0,0)
build(paths.circle,r=1)
stroke()

s = [.1, .37, .7]
moveto(Exp(s[0]))
for i in range(3):
  s0 = s[i]; s1 = s[(i+1)%3]
  build(hypline,s0,s1)
with gsave():
  fill(color.yellow)
stroke()

label = ['$A$', '$B$', '$C$']
for i in range(3):
  P = Exp(s[i])
  moveto(P); rmoveto(4*pt,P)
  drawtex(label[i],origin=loc.border(-P))

pbpend()
