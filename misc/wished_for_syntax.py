from pbpic import *
from math import *
from future import division

defaultStyle = Style(linewidth=2*pt, linecap=0, miterlimit=1, texenv='Minion'})

begin()
setstyle(defaultStyle)
scaleto(1*cm)

n=6
bdypts = [ FPolar(r,k/n) for k in range(n) ]
ipts = [ FPolar(4,k/3+0.5) for k in range(3) ]

polygon(bdypts)
polygon(ipts)
stroke()

adj = [ [0,2], [0,3], [0,4], [1,4], [1,5], [1,0], [2,0], [2,1], [2,2] ]
newpath()
for a in adj:
  path() + bdypts[a[1]] - ipts[a[0]]
close()

stroke()

# labels=[ 'a', 'b', 'c', 'a', 'b', 'c']
# t = 1/12
# for l in labels:
#   v = FPolar(r,t)
#   dv = offset(v,5*pt)
#   place(text(l),v+dv)
#   t += 1/6

end()
