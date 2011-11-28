from pbpic import *
import math

def koch(c,n):
  if n == 0:
    with c.ctmsave():
      c.scale(1/3.)
      c.lineto(1,0)
      with c.ctmsave():
        c.translate(1,0)
        c.rotate(1/6.)
        c.lineto(1,0)
        c.translate(1,0)
        c.rotate(-1/3.)
        c.lineto(1,0)
      c.lineto(3,0)
  else:
    with c.ctmsave():
      c.scale(1/3.)
      c.build(koch,n-1)
      with c.ctmsave():
        c.translate(1,0)
        c.rotate(1/6.)
        c.build(koch,n-1)
        c.translate(1,0)
        c.rotate(-1/3.)
        c.build(koch,n-1)
      c.translate(2,0)
      c.build(koch,n-1)

pbpbegin(10*cm,10*cm,'pdf')
setlinewidth(0.05*pt)
scaleto(8*cm)
translate(loc.center)
s = 1
for l in range(6):
  scale(s)
  with ctmsave():
    translate(-0.5,0.5/math.tan(math.pi/3))
    moveto(0,0)
    for k in range(3):
      build(koch,5)
      translate(1,0)
      rotate(-1/3.)
    closepath()
    stroke()
  s *= 0.66
pbpend()
