from __future__ import division
from style import updatefromstyle, Style
from geometry import Vector, Point
import misc 
import math
import types
import paths

def defaultStyle():
  return Style(tip=ArrowHead)

def stdarrowhead(canvas,W,H,wingangle,v):
  with canvas.ctmsave():
    canvas.translate(canvas.currentpoint())
    v=Vector(v[0],v[1]).unitvector()
    vp=Vector(v[1],-v[0])

    a =(W-1)/2/math.tan(2*math.pi*wingangle)

    canvas.moveto(0.5*vp) 
    canvas.lineto(W/2*vp-a*v )
    canvas.lineto(H*v)
    canvas.lineto(-W/2*vp-a*v )
    canvas.lineto(-0.5*vp)
    canvas.rlineto(-0.1*v)
    canvas.rlineto(vp)
    canvas.closepath()

def spreaderhead(canvas,width=3,length=1,v=[1,0]):
  with canvas.ctmsave():
    canvas.translate(canvas.currentpoint())
    v=Vector(v[0],v[1]).unitvector()
    vp=Vector(v[1],-v[0])
    
    canvas.moveto(0.5*vp)
    canvas.lineto(width/2*vp)
    canvas.rlineto(length*v)
    canvas.rlineto(-width*vp)
    canvas.rlineto(-length*v)
    canvas.lineto(-0.5*vp)
    canvas.rlineto(-0.1*v)
    canvas.rlineto(vp)
    canvas.closepath()

def tiltspreaderhead(canvas,width=4,length=1,theta=0.05,v=[1,0]):
  with canvas.ctmsave():
    canvas.translate(canvas.currentpoint())
    v=Vector(v[0],v[1]).unitvector()
    vp=Vector(v[1],-v[0])
    w =-math.sin(2*math.pi*theta)*vp+math.cos(2*math.pi*theta)*v
    wp=math.cos(2*math.pi*theta)*vp+math.sin(2*math.pi*theta)*v
    
    canvas.moveto(0,0)
    start = .5*vp+.5*math.tan(2*math.pi*theta)*v
    canvas.rmoveto(start)
    canvas.lineto(width/2*wp)
    canvas.rlineto(length*w)
    canvas.rlineto(-width*wp)
    canvas.rlineto(-length*w)
    canvas.lineto(-start)
    canvas.lineto(-.1*v-.5*vp)
    canvas.rlineto(vp)
    canvas.closepath()

class ArrowHead:

  @staticmethod
  def defaultStyle():
    return Style(width=5,length=5,wingangle=1/6)

  def __init__(self,**kwargs):
    updatefromstyle(self,('width','length','wingangle'),kwargs)

  def headlength(self):
    return self.length

  def drawto(self,canvas,v):
    with canvas.ctmsave():
      canvas.translate(canvas.currentpoint())
      vp = canvas.pageVector(v)
      canvas.scaleto(canvas.linewidth())
      vpp = canvas.vector(vp)
      canvas.build(stdarrowhead,self.width,self.length,self.wingangle,vpp,at=(0,0))
      canvas.fill(canvas.linecolor())

class SpreaderHead:

  @staticmethod
  def defaultStyle():
    return Style(width=5,length=1.5)

  def __init__(self,**kwargs):
    updatefromstyle(self,('width','length'),kwargs)

  def headlength(self):
    return self.length

  def drawto(self,canvas,v):
    with canvas.ctmsave():
      canvas.translate(canvas.currentpoint())
      vp = canvas.pageVector(v)
      canvas.scaleto(canvas.linewidth())
      vpp = canvas.vector(vp)
      canvas.build(spreaderhead,width=self.width,length=self.length,v=vpp,at=(0,0))
      canvas.fill(canvas.linecolor())

class TiltSpreaderHead:

  @staticmethod
  def defaultStyle():
    return Style(width=5,length=1,theta=.05)

  def __init__(self,**kwargs):
    updatefromstyle(self,('width','length','theta'),kwargs)

  def headlength(self):
    return self.length

  def drawto(self,canvas,v):
    with canvas.ctmsave():
      canvas.translate(canvas.currentpoint())
      vp = canvas.pageVector(v)
      canvas.scaleto(canvas.linewidth())
      vpp = canvas.vector(vp)
      canvas.build(tiltspreaderhead,width=self.width,length=self.length,theta=self.theta,v=vpp,at=(0,0))
      canvas.fill(canvas.linecolor())


class ArrowTo:

  def __init__(self,**kwargs):
    updatefromstyle(self,('tip',),kwargs)
    if type(self.tip) == types.ClassType:
      self.tip = self.tip()
    
  def drawto(self,canvas,to=(0,0)):
    p = canvas.point(to)
    v = p-canvas.currentpoint()
    dv = canvas.vector(canvas.linewidth()*self.tip.headlength(),-v)
    o = p+dv
    canvas.lineto(o)
    canvas.stroke()
    canvas.moveto(o)
    self.tip.drawto(canvas,v)

class ArrowFromTo:
  def __init__(self,**kwargs):
    updatefromstyle(self,('fromtip','totip','tip'),kwargs)
    if self.fromtip is None:
      self.fromtip = self.tip
    if self.totip is None:
      self.totip = self.tip

    if type(self.fromtip) == types.ClassType:
      self.fromtip = self.fromtip()
    if type(self.totip) == types.ClassType:
      self.totip = self.totip()

  def drawto(self,canvas,to=[1,0]):

    p1 = canvas.point(to)
    p0 = canvas.currentpoint()
    v = p1-p0
    dv = canvas.vector(canvas.linewidth()*self.fromtip.headlength(),v)
    q0 = p0 + dv
    dv = canvas.vector(canvas.linewidth()*self.totip.headlength(),v)
    q1 = p1 - dv

    canvas.moveto(q0)
    canvas.draw(self.fromtip,-v)
    canvas.moveto(q0); canvas.lineto(q1); canvas.stroke()
    canvas.moveto(q1)
    canvas.draw(self.totip,v)


class ArrowCurveTo(ArrowTo):
  def drawto(self,canvas,p1,p2,p3):
    p2=canvas.point(p2); p3=canvas.point(p3)
    v = p3-p2

    dv = canvas.vector(canvas.linewidth()*self.tip.headlength(),-v)
    q3 = p3+dv
    q2 = p2+dv

    canvas.curveto(p1,q2,q3)
    canvas.stroke()
    canvas.moveto(q3)
    canvas.draw(self.tip,v)


class ArrowCurveFromTo(ArrowFromTo):
  def drawto(self,canvas,p1,p2,p3):
    p1=canvas.point(p1); p2=canvas.point(p2); p3=canvas.point(p3)
    p0 = canvas.currentpoint()
    
    v = p0-p1
    dv = canvas.vector(canvas.linewidth()*self.fromtip.headlength(),-v)
    q0 = p0+dv
    q1 = p1+dv
    canvas.moveto(q0)
    canvas.draw(self.fromtip,v)
    
    v = p3-p2
    dv = canvas.vector(canvas.linewidth()*self.totip.headlength(),-v)
    q3 = p3+dv
    q2 = p2+dv
        
    canvas.path() + q0 - (q1,q2,q3); canvas.stroke()

    canvas.moveto(q3)
    canvas.draw(self.totip,v)

class ArcArrowTo(ArrowTo):

  def drawto(self,canvas,to=[1,0],s=.2):
    
    p0=canvas.currentpoint()
    p1=canvas.point(to)
    v=p1-p0
    a=p0+v/2
    vp = v.perp().unitvector()
    eps=0.001
    if abs(s)<eps:
      if s<0:
        s=-eps
      else:
        s=eps

    L=v.length()/2    
    H = L/2*s*(1/s/s)

    R = math.sqrt(H*H+L*L)

    c=a+vp*H

    w=p1-c
    wp=w.perp()
    dv=canvas.vector(canvas.linewidth()*self.tip.headlength(),wp)
    q1=p1+dv

    pp0=canvas.pagePoint(p0)

    with canvas.ctmsave():
      canvas.translate(q1)
      canvas.rotate((q1-c).angle())
      
      p0=canvas.point(pp0)

      L=-p0.x; H=p0.y
      m= (L*L-H*H)/(2*L)
      R=(L-m)
      
      c=canvas.point(-L+m,0)
      
      canvas.moveto(c)
      canvas.lineto(0,0)
      
      canvas.newpath()
      canvas.build(paths.arc,c,R,0,(p0-c).angle())
      canvas.stroke()
      
      canvas.moveto(0,0)
      canvas.draw(self.tip,[0,-1])

class SArrowTo(ArrowTo):
  
  def drawto(self,canvas,to=[1,0],sposition=0.5,flip=False):
    p3 = canvas.point(to)
    p0 = canvas.currentpoint()
    v = p3-p0
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

    dv = canvas.vector(canvas.linewidth()*self.tip.headlength(),l1*vp+h1*v)

    q1 = q3-(l2*vp+h2*v)*2*s2
    q3 = p3-dv
    q2 = q3-(l1*vp+h1*v)*2*s2
    
    canvas.curveto(q1,q2,q3)
    canvas.stroke()

    canvas.moveto(q3)
    canvas.draw(self.tip,dv)
