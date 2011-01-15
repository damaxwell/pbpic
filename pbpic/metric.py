from __future__ import division
import math

"""
Physical space is a plane with unit length equal to 1 point.
"""

_pts_per_cm = 72./2.54
_pts_per_in = 72.

class Length:
  """
  Represents a distance in physical space.
  """
  def __init__(self,x=0):
    self.x=x

  def __add__(self,l):
    return Length(self.x+l.x)

  def __mul__(self,s):
    return Length(self.x*s)

  def __rmul__(self,s):
    return Length(self.x*s)
    
  def value(self):
    return self.x

class MeasuredLength:
  def __init__(self,l,scale,name):
    self.x=l
    self.scale=scale
    self.name=name

  def __add__(self,l):
    return MeasuredLength(self.x+l.x,self.scale,self.name)

  def __neg__(self):
    return MeasuredLength(-self.x,self.scale,self.name)

  def __mul__(self,s):
    return MeasuredLength(self.x*s,self.scale,self.name)

  def __rmul__(self,s):
    return MeasuredLength(self.x*s,self.scale,self.name)

  def value(self):
    return self.x/self.scale

  def ptValue(self):
    return self.x

  def __repr__(self):
    return '%g %s' %(self.value(),self.name)

class Cm(MeasuredLength):
  def __init__(self,x=0):
    MeasuredLength.__init__(self,x*_pts_per_cm,_pts_per_cm,'cm')

class Inch(MeasuredLength):
  def __init__(self,x=0):
    MeasuredLength.__init__(self,x*_pts_per_in,_pts_per_in,'in')

class AdobePoint(MeasuredLength):
  def __init__(self,x=0):
    MeasuredLength.__init__(self,x,1.,'pt')

class Point:
  def __init__(self, x=0,y=0):
    self.x=x
    self.y=y

  def __add__(self,l):
    return Point(self.x+l.x,self.y+l.y)
  
  def __repr__(self):
    return 'Point (%g,%g)' % (self.x,self.y)
  
  def __getitem__(self,i):
    if i==0:
      return self.x
    if i==1:
      return self.y
    raise IndexError()


class PagePoint:
  def __init__(self,*args):
    if len(args) == 1:
      x=args[0][0]; y=args[0][1]
    elif len(args) == 2:
      x=args[0]; y=args[1]
    else:
      raise ValueError()
    self.x=x
    self.y=y

  def __repr__(self):
    return 'PagePoint (%g,%g)' % (self.x,self.y)

  def __getitem__(self,i):
    if i==0:
      return self.x
    if i==1:
      return self.y
    raise IndexError()


class Segment:
  """
  Represents a vector in physical space.
  """
  def __init__(self, x=0,y=0):
    self.x=x
    self.y=y

  def value(self):
    return [self.x,self.y]
    
  def length(self):
    return Length(math.sqrt(self.x*self.x+self.y*self.y))
  
  def __add__(self,l):
    return Segment(self.x+l.x,self.y+l.y)
  
  def __repr__(self):
    return 'Segment (%g,%g)' % (self.x,self.y)
  
  def __getitem__(self,i):
    if i==0:
      return self.x
    if i==1:
      return self.y
    raise IndexError()

  def __mul__(self,s):
    return Segment(self.x*s,self.y*s)

  def __rmul__(self,s):
    return Segment(self.x*s,self.y*s)

  def __div__(self,s):
    return Segment(self.x/s,self.y/s)

  def __truediv__(self,s):
    return Segment(self.x/s,self.y/s)

  def __neg__(self):
    return Segment(-self.x,-self.y)

  def angle(self):
    return math.atan2(self.y,self.x)
    
  def fangle(self):
    return self.angle()/(2*math.pi)
  
  def dangle(self):
    return self.fangle()*360

  def length(self):
    return math.sqrt(self.x*self.x+self.y*self.y)

  def unitvector(self):
    l=self.length()
    return Segment(self.x/l,self.y/l)

Vector = Segment
    
class MeasuredSegment:
  def __init__(self,x,y,scale,name):
    self.x=x
    self.y=y
    self.scale=scale
    self.name=name

  def __add__(self,l):
    return MeasuredSegment(self.x+l.x,self.y+l.y,self.scale,self.name)

  def __neg__(self):
    return MeasuredSegment(-self.x,-self.y,self.scale,self.name)

  def __mul__(self,s):
    return MeasuredSegment(self.x*s,self.y*s,self.scale,self.name)

  def __rmul__(self,s):
    return MeasuredSegment(self.x*s,self.y*s,self.scale,self.name)

  def value(self):
    return [self.x/self.scale,self.y/self.scale]

  def __repr__(self):
    v=self.value()
    return '[%g,%g] %s' %(v[0],v[1],self.name)

class CmSegment(MeasuredSegment):
  def __init__(self,x=0,y=0):
    MeasuredSegment.__init__(self,x*_pts_per_cm,y*_pts_per_cm,_pts_per_cm,'cm')

class InchSegment(MeasuredSegment):
  def __init__(self,x=0,y=0):
    MeasuredSegment.__init__(self,x*_pts_per_in,y*_pts_per_in,_pts_per_in,'in')

class AdobePointSegment(MeasuredSegment):
  def __init__(self,x=0,y=0):
    MeasuredSegment.__init__(self,x,y,1.,'pt')

class CmFactory:
  def __rmul__(self,s):
    if isinstance(s,tuple) or isinstance(s,list):
      return CmSegment(*s)
    return Cm(s)
cm=CmFactory()

class InchFactory:
  def __rmul__(self,s):
    if isinstance(s,tuple) or isinstance(s,list):
      return InchSegment(*s)
    return Inch(s)
inch=InchFactory()

class AdobePointFactory:
  def __rmul__(self,s):
    if isinstance(s,tuple) or isinstance(s,list):
      return AdobePointSegment(*s)
    return AdobePoint(s)
pt=AdobePointFactory()


class Polar(Segment):
  def __init__(self,r,theta):
    Segment.__init__(self,r*math.cos(theta),r*math.sin(theta))

class FPolar(Segment):
  def __init__(self,r,ftheta):
    Segment.__init__(self,r*math.cos(2*math.pi*ftheta),r*math.sin(2*math.pi*ftheta))

class DPolar(Segment):
  def __init__(self,r,dtheta):
    Segment.__init__(self,r*math.cos(2*math.pi*dtheta/360.),r*math.sin(2*math.pi*dtheta/360.))
