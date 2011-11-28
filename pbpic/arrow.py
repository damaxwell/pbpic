from __future__ import division
from style import updatefromstyle, Style
from geometry import Vector, Point
from marks import Mark
import misc 
import math


def stdarrowhead(canvas,W,H,theta,origin,v):
  with canvas.ctmsave():
    canvas.translate(origin)
    v=Vector(v[0],v[1]).unitvector()
    vp=Vector(v[1],-v[0])

    a =(W-1)/2/math.tan(2*math.pi*theta)

    canvas.moveto(0.5*vp) 
    canvas.lineto(W/2*vp-a*v )
    canvas.lineto(H*v)
    canvas.lineto(-W/2*vp-a*v )
    canvas.lineto(-0.5*vp)
    canvas.rlineto(-0.1*v)
    canvas.rlineto(vp)
    canvas.closepath()

class ArrowHead(Mark):

  @staticmethod
  def defaultStyle():
    return Style(width=3,length=3,wingangle=1/6)

  def __init__(self,**kwargs):
    updatefromstyle(self,('width','length','wingangle'),'arrow',kwargs)

  def drawto(self,canvas,v):
    with canvas.ctmsave():
      canvas.translate(canvas.currentpoint())
      vp = canvas.pageVector(v)
      canvas.scaleto(canvas.linewidth())
      vpp = canvas.vector(vp)
      canvas.build(stdarrowhead,self.width,self.length,self.wingangle,(0,0),vpp)
      fc = canvas.fillcolor()
      canvas.setfillcolor(canvas.linecolor())
      canvas.fill()
      canvas.setfillcolor(fc)

class ArrowTo(Mark):
  def __init__(self,**kwargs):
    self.head = ArrowHead(**kwargs)
  def drawto(self,canvas,to=(0,0)):
    p = canvas.point(to)
    v = p-canvas.currentpoint()
    dv = canvas.vector(canvas.linewidth()*self.head.length,-v)
    o = p+dv
    canvas.lineto(o)
    canvas.stroke()
    canvas.moveto(o)
    self.head.drawto(canvas,v)

class ArrowFromTo(Mark):
  def __init__(self,**kwargs):
    self.head = ArrowHead(**kwargs)
  def drawto(self,canvas,*args):
    p1 = canvas.point(*args)
    p0 = canvas.currentpoint()
    v = p1-p0
    dv = canvas.rescale(v,canvas.linewidth()*self.head.length)
    q0 = p0 + dv
    q1 = p1 - dv

    canvas.moveto(q0)
    canvas.place(self.head,-v)
    canvas.moveto(q0); canvas.lineto(q1); canvas.stroke()
    canvas.moveto(q1)
    canvas.place(self.head,v)

class ArrowCurveTo(Mark):
  def __init__(self,**kwargs):
    self.head = ArrowHead(**kwargs)
  def drawto(self,canvas,p1,p2,p3):
    p2=canvas.point(p2); p3=canvas.point(p3)
    v = p3-p2

    dv = canvas.rescale(-v,canvas.linewidth()*self.head.length)
    q3 = p3+dv
    q2 = p2+dv

    curveto(p1,q2,q3)
    stroke()
    canvas.moveto(q3)
    canvas.place(self.head,v)

class ArrowCurveFromTo(Mark):
  def __init__(self,**kwargs):
    self.head = ArrowHead(**kwargs)
  def drawto(self,canvas,p1,p2,p3):
    p1=canvas.point(p1); p2=canvas.point(p2); p3=canvas.point(p3)
    p0 = canvas.currentpoint()
    
    v = p0-p1
    dv = canvas.rescale(-v,canvas.linewidth()*self.head.length)
    q0 = p0+dv
    q1 = p1+dv
    canvas.moveto(q0)
    canvas.place(self.head,v)
    
    v = p3-p2
    dv = canvas.rescale(-v,canvas.linewidth()*self.head.length)
    q3 = p3+dv
    q2 = p2+dv
        
    canvas.path() + q0 - (q1,q2,q3); stroke()

    canvas.moveto(q3)
    canvas.place(self.head,v)

class SArrowTo(Mark):
  def __init__(self,**kwargs):
    self.head = ArrowHead(**kwargs)
  
  def drawto(self,canvas,tip,sposition=0.5,flip=False):
    p3 = canvas.point(tip)
    p0 = canvas.currentpoint()
    v = (p3-p0)
    vp = Vector(v[1],-v[0])
    if flip:
      vp = -1*vp

    l1=.1
    l2=.15
    h1 = .5
    h2 = 0.2
    s1 = min(0.5,sposition)
    s2 = min(0.5,1-sposition)


    q0 = p0
    q1 = q0+2*s1*(l1*vp+h1*v)
    q3 = p0+sposition*v
    q2 = q3+2*s1*(l2*vp+h2*v)
    
    canvas.moveto(q0); canvas.curveto(q1,q2,q3)

    dv = canvas.rescale(l1*vp+h1*v,canvas.linewidth()*self.head.length)

    q1 = q3-(l2*vp+h2*v)*2*s2
    q3 = p3-dv
    q2 = q3-(l1*vp+h1*v)*2*s2
    
    canvas.curveto(q1,q2,q3)
    canvas.stroke()

    canvas.moveto(q3)
    canvas.place(self.head,dv)
