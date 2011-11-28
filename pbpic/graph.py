import math

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

def boxaxis(canvas,gbox):
  canvas.build(gbox)

def xtick(canvas):
  canvas.rmoveto(0,-0.5)
  canvas.rlineto(0,1)

def ytick(canvas):
  canvas.rmoveto(-0.5,0)
  canvas.rlineto(1,0)

def xlogticks(canvas,n=10,base=10,minor=0.25):
  dx=float(base)/n
  x=1+dx
  p=canvas.currentpoint()
  x0 = p.x; y0 = p.y

  for k in range(n-2):
    logx = math.log(x,base)
    canvas.moveto(x0+logx,y0)
    canvas.rmoveto(0,-minor/2)
    canvas.rlineto(0,minor)
    x+=dx
  canvas.moveto(x0+1,y0-0.5)
  canvas.rlineto(0,1)

def ylogticks(canvas,n=10,base=10,minor=0.25):
  dy=float(base)/n
  y=1+dy
  p=canvas.currentpoint()
  x0 = p.x; y0 = p.y

  for k in range(n-2):
    logy = math.log(y,base)
    canvas.moveto(x0,y0+logy)
    canvas.rmoveto(-minor/2,0)
    canvas.rlineto(minor,0)
    y+=dy
  canvas.moveto(x0-0.5,y0+1)
  canvas.rlineto(1,0)
