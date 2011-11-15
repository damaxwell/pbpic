from __future__ import division
import math
from geometry import AffineTransform, Point, Vector
"""
Physical space is a plane with unit length equal to 1 point.
"""

_pts_per_cm = 72./2.54
_pts_per_in = 72.

class CoordSystem:
  def __init__(self,tm,name=""):
    self.tm =tm.copy()
    self.name=name
  def __rmul__(self,s):
    if isinstance(s,tuple):
      p=self.tm.T(s)
      return PagePoint(p)
    elif isinstance(s,list):
      p=self.tm.Tv(s)
      return PageVector(p[0],p[1])
    elif isinstance(s,Point):
      p=self.tm.T(s.x,s.y)
      return PagePoint(p)
    elif isinstance(s,Vector):
      v=self.tm.Tv(s.x,s.y)
      return PageVector(v)
    elif isinstance(s,float) or isinstance(s,int):
      return Length(self.tm.copy(),s)    
    raise ValueError()

class ScaledCoordSystem(CoordSystem):
  def __init__(self,scale,name):
    tm = AffineTransform()
    tm.dilate(scale)
    CoordSystem.__init__(self,tm,name)

cm=ScaledCoordSystem(_pts_per_cm,"cm")
inch=ScaledCoordSystem(_pts_per_in,"inch")
pt=ScaledCoordSystem(1,"pt")

class PagePoint:
  """
  Represents a point in page coordinates.
  """
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

  def __len__(self):
    return 2

  def __getitem__(self,i):
    if i==0:
      return self.x
    if i==1:
      return self.y
    raise IndexError()

  def copy(self):
    return PagePoint(self.x,self.y)

class PageVector:
  """
  Represents a vector in physical space.
  """
  def __init__(self, x=0,y=0):
    self.x=float(x)
    self.y=float(y)

  def __add__(self,l):
    if isinstance(l,PageVector):
      return PageVector(self.x+l.x,self.y+l.y)
    raise ValueError()

  def __sub__(self,l):
    if isinstance(l,PageVector):
      return PageVector(self.x-l.x,self.y-l.y)
    raise ValueError()

  def __repr__(self):
    return 'PageVector (%g,%g)' % (self.x,self.y)

  def __len__(self):
    return 2

  def __getitem__(self,i):
    if i==0:
      return self.x
    if i==1:
      return self.y
    raise IndexError()

  def __mul__(self,s):
    return PageVector(self.x*s,self.y*s)

  def __rmul__(self,s):
    return PageVector(self.x*s,self.y*s)

  def __div__(self,s):
    return PageVector(self.x/s,self.y/s)

  def __truediv__(self,s):
    return PageVector(self.x/s,self.y/s)

  def __neg__(self):
    return PageVector(-self.x,-self.y)

  def angle(self):
    return self.rangle()/(2*math.pi)

  def rangle(self):
    return math.atan2(self.y,self.x)

  def dangle(self):
    return self.angle()*360

  def length(self):
    return math.sqrt(self.x*self.x+self.y*self.y)

  def unitvector(self):
    l=self.length()
    return Vector(self.x/l,self.y/l)


class Length:
  """
  Represents a distance in a coordinate system.  Given a vector :v:
  in page coordinates, a Length is used to rescale the length of :v:
  so that it has the the specified Length in the Length's coordinate system.
  """
  def __init__(self,tm,x=0):
    self.tm=tm
    self.x=x
  
  def __str__(self):
    return "%f in coordinates %s" % (self.x,str(self.tm))

  def rescale(self,v):
    """"Given a vector :v: in page coordinates, returns a vector pointing in 
    the same direction as :v:, but with the length specified by the Length
    in its coordinate system.
    """
    return v/self.measure(v)

  def measure(self,v):
    """Given a vector :v: in page coordinates, returns its length relative
    to the Length."""
    return self.tm.Tvinv(v).length()/self.x

  def pagelength(self,v):
    """Given a vector :v: in page coordinates, returns the length in page
    coordinates of the vector parallel to :v: having length equal to the 
    Length in the Length's coordinate system."""
    return self.rescale(v).length()

  def topagecoords(self,page_v,length_v,page_origin,orientation):
    """Returns a ctm T that is related to this Length's ctm by an isometry and
    such that:
       T(length_v) is a non-negative multiple of page_v
       T(0)=page_origin
       The orientation of T is the given by :orientation:.
       
       There is exactly one such T.
    """

    # This is a unit vector in Length coordinates.
    dx = self.tm.Tvinv(page_v).unitvector()
    if orientation == self.tm.orientation():
      o=1
    else:
      o=-1
    dy = Vector(-o*dx.y,o*dx.x)
    
    tm = AffineTransform([dx.x,dx.y,dy.x,dy.y,page_origin.x,page_origin.y])

    rv = self.tm.copy()
    rv.concat(tm)

    return rv

  def __float__(self):
    return float(self.x)

  def length(self):
    """Returns the length associated with the Length."""
    return self.x
    
  def setlength(self,x):
    self.x = x

  def rotate(self,angle):
    self.tm.rotate(angle)

  def scale(self,sx,sy):
    self.tm.scale(sx,sy)

  def dilate(self,r):
    self.tm.dilate(r)

  def __eq__(self,other):
    if isinstance(other,Length):
      return (self.x == other.x) and (self.tm == other.tm)
    return False

  def __neq__(self,rhs):
    return not self.__eq__(rhs)

  def __mul__(self,s):
    return Length(self.tm,self.x*s)

  def __rmul__(self,s):
    return Length(self.tm,self.x*s)

  def __div__(self,s):
    return Length(self.tm,self.x/s)

  def __rdiv__(self,s):
    return Length(self.tm,self.x/s)

  def copy(self):
    return Length(self.tm.copy(),self.x)
