from pbpic import *

def staff(c,dx,dy):
  y=0;
  for k in range(5):
    c.moveto(0,y); c.rlineto(dx,0)
    y-=dy

pbpbegin(8.5*inch,11*inch,'pdf')

with inset() as i:
  v=vector(6.5*inch,.3*cm)
  dx=v[0];dy=v[1]

  for k in range(8):
    build(staff,v[0],v[1])
    stroke()
    translate(0,-5*dy)
    translate(0,-5*dy)
  i.setextents(i.markedbox())
with ctmsave():
  translate(loc.center)
  moveto(0,0); 
  draw(i,loc.center)

moveto(0,0)
scaleto(1*inch)
setfont("Times Roman")
setfontsize(6*pt)
moveto(1,0.5)
write("Banjo!")

# scaleto(1*inch)
# translate(0,11)
# translate(1,-1)
  
pbpend()