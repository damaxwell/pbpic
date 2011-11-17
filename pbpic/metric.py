from __future__ import division
import math
from geometry import AffineTransform, Point, Vector
"""
Physical space is a plane with unit length equal to 1 point.
"""

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
      return Length(Units(self.tm),s)    
    raise ValueError()

class ScaledCoordSystem(CoordSystem):
  def __init__(self,scale,name):
    tm = AffineTransform()
    tm.dilate(scale)
    CoordSystem.__init__(self,tm,name)

_pts_per_cm = 72./2.54
cm=ScaledCoordSystem(_pts_per_cm,"cm")
_pts_per_in = 72.
inch=ScaledCoordSystem(_pts_per_in,"inch")
pt=ScaledCoordSystem(1,"pt")


class Units:
  def __init__(self,*args):
    if len(args)==0:
      self.a=1;self.b=0;
      self.c=0;self.d=1;
    elif (len(args) == 1) and isinstance(args[0],AffineTransform):
      tm = args[0]
      self.a = tm.a
      self.b = tm.b
      self.c = tm.c
      self.d = tm.d
    elif len(args) == 4:
      self.a = float(args[0])
      self.b = float(args[1])
      self.c = float(args[2])
      self.d = float(args[3])
    else:
      raise ValueError()

  def __repr__(self):
    return 'Units [ %g %g; %g %g]' %(self.a, self.b, self.c, self.d)

  def __eq__(self,rhs):
    if not isinstance(rhs,Units):
      return False
    return (self.a==rhs.a) and (self.b==rhs.b) and (self.c==rhs.c) and (self.d==rhs.d)

  def copy(self):
    copy=Units()
    copy.__dict__.update(self.__dict__)
    return copy

  def orientation(self):
    if self.det() < 0:
      return -1
    return 1

  def dilate(self,r):
    self.scale(r,r)

  def scale(self, sx, sy):
    self.a = self.a*sx
    self.b = self.b*sx
    self.c = self.c*sy
    self.d = self.d*sy

  def shear(self,v,l):
    raise NotImplementedError()

  def rotate( self, theta):
    self.rrotate(2*math.pi*theta)

  def rrotate( self, theta):
    ct = math.cos(theta)
    st = math.sin(theta)
    a=self.a; b=self.b; c=self.c; d=self.d
    self.a =  a*ct + c*st
    self.b =  b*ct + d*st
    self.c = -a*st + c*ct
    self.d = -b*st + d*ct

  def det(self):
    return self.a*self.d-self.b*self.c

  def affineTransform(self,origin=[0,0],page_v=[1,0],local_v=[1,0],orientation=1):
    """Returns an affine transformation :T:such that distance '1' in its coordinates
    corresponds to distance '1' with respect to the Unit's.  There are many
    such transformations, but they are all related to each other by an isometry.  
    The particular transformation is specified by indicating
      
      T(0,0)=origin
      T(local_v) points along page_v
    
    along with the orientation (+/-1) of T.  The default is origin=(0,0), 
    page_v=[1,0], and local_v[1,0], so that the origin of T is the origin
    in page coordiantes, and the x-direction for T corresponds to the page's
    x-direction.  
    """
    tm = AffineTransform([self.a,self.b,self.c,self.d,origin[0],origin[1]])

    # This is a unit vector in Length coordinates.
    dx = self.Tvinv(page_v).unitvector()
    a=dx.x; b=dx.y
    if orientation*self.orientation() > 0:
      o=1
    else:
      o=-1
    # The map tm is is orthogonally related to 'units', takes [1,0]  to c*page_v, and takes (0,0) to page_origin.
    # tm = self.u.affineTransform(origin=page_origin)
    rot = AffineTransform([a,b,-o*b,o*a,0,0])
    tm.concat(rot)

    # For the common case [0,1]~length_v, we're done.
    if local_v[0]>0 and local_v[1]==0:
      return tm

    # rot is a rotation matrix that takes local_v to positive multiple of [1,0]
    ldx = local_v.unitvector()
    c=ldx.x; d=ldx.y
    rot = AffineTransform([c,-d,d,c,0,0])
    tm.concat(rot)

    return tm
  
  def measure(self,v):
    w=self.Tvinv(v)
    return math.sqrt(w[0]*w[0]+w[1]*w[1])

  def Tv(self, *args):
    if len(args) == 2:
      h = args[0]; v=args[1]
    elif len(args) == 1:
      p = args[0]
      h=p[0]; v=p[1]
  
    return Vector(self.a*h+self.c*v, self.b*h+self.d*v)

  def Tvinv(self,*args):
    if len(args) == 2:
      h = args[0]; v=args[1]
    elif len(args) == 1:
      p = args[0]
      h=p[0]; v=p[1]
  
    det = self.a*self.d-self.b*self.c
    return Vector((self.d*h-self.c*v)/det, (self.a*v-self.b*h)/det)


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
  Represents a distance with respect to some units (i.e with respect
  to a coordinate system).
  """
  def __init__(self,units,r):
    self.u=units
    self.r=r
  
  def __str__(self):
    return "Length %f with respect to units%s." % (self.r,str(self.u))

  def measure(self,v):
    """Given a vector :v: in page coordinates, returns its length relative
    to the Length's length.  I.e., if :v: had length 2 with respect
    to the Length's units, and the Length's length is 3, then :measure(v):
    returns 2/3."""
    return self.u.measure(v)/self.r

  def apply(self,v):
    """"Given a vector :v: in page coordinates, returns a vector pointing in 
    the same direction as :v:, but with the Length's length, as measured
    in the Length's units.
    """
    return v/self.measure(v)

  def topagecoords(self,page_v,length_v,page_origin,orientation):
    """Returns a ctm T that is related to this Length's ctm by an isometry and
    such that:
       T(length_v) is a non-negative multiple of page_v
       T(0)=page_origin
       The orientation of T is the given by :orientation:.
       
       There is exactly one such T.
    """

    tm = self.units().affineTransform(origin=page_origin,page_v=page_v,local_v=length_v,orientation=orientation)
    tm.dilate(self.r)
    return tm

  def __float__(self):
    return float(self.r)

  def length(self):
    """Returns the length associated with the Length."""
    return self.r
    
  def setlength(self,r):
    self.r = r

  def units(self):
    return self.u

  def setunits(self,units):
    if not isinstance(units,Units):
      raise ValueError()
    self.u=units.copy()

  def __eq__(self,other):
    if isinstance(other,Length):
      return (self.r == other.r) and (self.u == other.u)
    return False

  def __neq__(self,rhs):
    return not self.__eq__(rhs)

  def __mul__(self,s):
    return Length(self.u,self.r*s)

  def __rmul__(self,s):
    return Length(self.u,self.r*s)

  def __div__(self,s):
    return Length(self.u,self.r/s)

  def __rdiv__(self,s):
    return Length(self.u,self.r/s)

  def copy(self):
    return Length(self.u.copy(),self.r)
