import math, types
from .pbpstyle import updatefromstyle, Style
from .metric import pt

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


def defaultStyle():
  return Style(ticklength=2*pt)

class XTick:
  def __init__(self,**kwargs):
    updatefromstyle(self,('ticklength',),kwargs)
  def drawto(self,canvas):
    canvas.rmoveto(0,-self.ticklength/2)
    canvas.rlineto(0,self.ticklength)
    canvas.stroke()
class XUpTick(XTick):
  def drawto(self,canvas):
    canvas.rlineto(0,self.ticklength/2)
    canvas.stroke()
class XDownTick(XTick):
  def drawto(self,canvas):
    canvas.rlineto(0,-self.ticklength/2)
    canvas.stroke()

class XTicks:
  @staticmethod
  def defaultStyle():
    return Style(xtick=XTick())
  def __init__(self,**kwargs):
    updatefromstyle(self,('xtick',),kwargs)
    if type(self.xtick) == types.ClassType:
      self.xtick = self.xtick()  
  def drawto(self,canvas,x=[0,1],y=0):
    for xc in x:
      canvas.draw(self.xtick,at=(xc,y))

class YTick:
  def __init__(self,**kwargs):
    updatefromstyle(self,('ticklength',),kwargs)
  def drawto(self,canvas):
    canvas.rmoveto(-self.ticklength/2,0)
    canvas.rlineto(self.ticklength,0)
    canvas.stroke()

class YTicks:
  @staticmethod
  def defaultStyle():
    return Style(ytick=YTick())
  def __init__(self,**kwargs):
    updatefromstyle(self,('ytick',),kwargs)
    if type(self.ytick) == types.ClassType:
      self.ytick = self.ytick()  
  def drawto(self,canvas,y=[0,1],x=0):
    for yc in y:
      canvas.draw(self.ytick,at=(x,yc))
