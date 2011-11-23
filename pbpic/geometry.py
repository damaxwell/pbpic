from __future__ import division
import math

# TODO: make Point immutable
class Point:
  def __init__(self, x=0,y=0):
    self.x=x
    self.y=y

  def __add__(self,l):
    return Point(self.x+l[0],self.y+l[1])

  def __len__(self):
    return 2

  def __sub__(self,l):
    return Vector(self.x-l[0],self.y-l[1])

  def __neg__(self):
    return Point(-self.x,-self.y)

  def __mul__(self,s):
    return Point(self.x*s,self.y*s)

  def __rmul__(self,s):
    return Point(self.x*s,self.y*s)

  def __div__(self,s):
    return Point(self.x/s,self.y/s)

  def __truediv__(self,s):
    return Point(self.x/s,self.y/s)

  
  
  def __repr__(self):
    return 'Point (%g,%g)' % (self.x,self.y)
  
  def __getitem__(self,i):
    if i==0:
      return self.x
    if i==1:
      return self.y
    raise IndexError()
    
  def copy(self):
    return Point(self.x,self.y)

class Vector:
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
    return Vector(self.x+l.x,self.y+l.y)
  
  def __sub__(self,l):
    return Vector(self.x-l.x,self.y-l.y)
  
  def __repr__(self):
    return 'Vector (%g,%g)' % (self.x,self.y)

  def __len__(self):
    return 2
  
  def __getitem__(self,i):
    if i==0:
      return self.x
    if i==1:
      return self.y
    raise IndexError()

  def __mul__(self,s):
    return Vector(self.x*s,self.y*s)

  def __rmul__(self,s):
    return Vector(self.x*s,self.y*s)

  def __div__(self,s):
    return Vector(self.x/s,self.y/s)

  def __truediv__(self,s):
    return Vector(self.x/s,self.y/s)

  def __neg__(self):
    return Vector(-self.x,-self.y)

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
    return Vector(self.x/l,self.y/l)

  def copy(self):
    return Vector(self.x,self.y)

  def dot(self,other):
    return self.x*other.x+self.y*other.y

class Polar(Vector):
  def __init__(self,r,theta):
    Vector.__init__(self,r*math.cos(2*math.pi*theta),r*math.sin(2*math.pi*theta))

class RPolar(Vector):
  def __init__(self,r,theta):
    Vector.__init__(self,r*math.cos(theta),r*math.sin(theta))

class DPolar(Vector):
  def __init__(self,r,dtheta):
    Vector.__init__(self,r*math.cos(2*math.pi*dtheta/360.),r*math.sin(2*math.pi*dtheta/360.))

def pToPoint(p):
  if isinstance(p,Point):# or isinstance(p,PagePoint):
    return p
  return Point(p[0],p[1])

def toOnePoint(*args):
  if len(args) == 2:
    return Point(args[0],args[1])
  if len(args) != 1:
    raise ValueError()
  return pToPoint(args[0])

def toThreePoints(*args):
  if len(args) == 6:
    return (Point(args[0],args[1]),Point(args[2],args[3]),Point(args[4],args[5]))
  if len(args) != 3:
    raise ValueError()
  return [ pToPoint(p) for p in args]


class AffineTransform:
  def __init__(self,*args):
    if len(args) == 0:
      self.a = 1
      self.b = 0
      self.c = 0
      self.d = 1
      self.tx = 0
      self.ty = 0
    elif len(args) == 1 and isinstance(args[0],list):
      initial = args[0]
      self.a=initial[0]
      self.b=initial[1]
      self.c=initial[2]
      self.d=initial[3]
      self.tx=initial[4]
      self.ty=initial[5]
    elif len(args) == 1 and isinstance(args[0],AffineTransform):
      tm = args[0]
      self.a=tm.a
      self.b=tm.b
      self.c=tm.c
      self.d=tm.d
      self.tx=tm.tx
      self.ty=tm.ty
    elif len(args) == 6:
      self.a=float(args[0])
      self.b=float(args[1])
      self.c=float(args[2])
      self.d=float(args[3])
      self.tx=float(args[4])
      self.ty=float(args[5])

  def __repr__(self):
    return '[ %g %g; %g %g] + [%g %g]' %(self.a, self.b, self.c, self.d, self.tx, self.ty)

  def __eq__(self,rhs):
    if not isinstance(rhs,AffineTransform):
      return False
    return (self.a==rhs.a) and (self.b==rhs.b) and (self.c==rhs.c) and (self.d==rhs.d) and (self.tx==rhs.tx) and (self.ty==rhs.ty)

  def __neq__(self,rhs):
    return not self.__eq__(rhs)

  def copy(self):
    copy=AffineTransform()
    copy.__dict__.update(self.__dict__)
    return copy

  def orientation(self):
    if self.det() < 0:
      return -1
    return 1

  def inverse(self):
    inv = AffineTransform()
    det = self.det()
    inv.a = self.d/det
    inv.b = -self.b/det
    inv.c = -self.c/det
    inv.d = self.a/det
    inv.tx = -(inv.a*self.tx+inv.c*self.ty)
    inv.ty = -(inv.b*self.tx+inv.d*self.ty)
    return inv
    
  def concat(self,tm):
    a = self.a*tm.a+self.c*tm.b
    b = self.b*tm.a+self.d*tm.b
    c = self.a*tm.c+self.c*tm.d
    d = self.b*tm.c+self.d*tm.d
    self.tx = self.a*tm.tx+self.c*tm.ty+self.tx
    self.ty = self.b*tm.tx+self.d*tm.ty+self.ty
    self.a = a; self.b=b; self.c=c; self.d=d

  def T(self, *args):
    if len(args) == 2:
      x = args[0]; y=args[1]
    elif len(args) == 1:
      p = args[0]
      x=p[0]; y=p[1]
    else:
      raise ValueError()

    return Point(self.a*x+self.c*y+self.tx, self.b*x+self.d*y+self.ty)


  def Tinv(self,*args):
    if len(args) == 2:
      xx = args[0]; yy=args[1]
    elif len(args) == 1:
      p = args[0]
      xx=p[0]; yy=p[1]
    else:
      raise ValueError()
    x=xx-self.tx; y=yy-self.ty
    det = self.a*self.d-self.b*self.c
    return Point((self.d*x-self.c*y)/det,(self.a*y-self.b*x)/det)

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

  def dilate(self,r):
    self.scale(r,r)

  def scale(self, sx, sy):
    self.a = self.a*sx
    self.b = self.b*sx
    self.c = self.c*sy
    self.d = self.d*sy

  def translate(self, tx, ty):
    self.tx = self.a*tx+self.c*ty+self.tx
    self.ty = self.b*tx+self.d*ty+self.ty

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

  def origin(self):
    return Point(self.tx,self.ty)

  def det(self):
    return self.a*self.d-self.b*self.c

  def setdiag(self,*args):
    if len(args) == 1:
      self.a = bbox[0]
      self.d = bbox[0]
    else:
      self.a = bbox[0]
      self.d = bbox[1]
    self.b=0; self.c=0

  def asTuple(self):
    return ( self.a, self.b, self.c, self.d, self.tx, self.ty)

class Path:
  MOVETO = 0
  LINETO = 1
  CURVETO = 2
  CLOSEPATH = 3
  
  def __init__(self):
    self.commands = []
    self.coords = []
    self.cp = None

  def copy(self):
    cpath = Path()
    cpath.commands = [ c for c in self.commands ]
    cpath.coords = [ p for p in self.coords ]
    if self.cp:
      cpath.cp = self.cp.copy()
    return cpath

  def __repr__(self):
    s = "Path:"
    cmd = ['M','L','C','CP']
    for k in range(len(self.commands)):
      s = s + ' ' + cmd[self.commands[k]] + ' ' + str(self.coords[k]) + '\n'
    return s

  def __iter__(self):
    for k in range(len(self.commands)):
      yield self.commands[k],self.coords[k]

  def __add__(self,p):
    if p == 0:
      self.closepath()
    else:
      self.moveto(p)
    return self

  def __sub__(self,p):
    self.lineto(p)
    return self

  def clear(self):
    self.commands = []
    self.coords=[]
    self.cp = None

  def setcurrentpoint(self,*args):
    p = toOnePoint(*args)
    self.cp = p

  def advancecurrentpoint(self,v):
    self.cp += v

  def moveto(self, *args):
    p = toOnePoint(*args)
    self.cp = p
    if (len(self.commands) > 0) and (self.commands[-1] == self.MOVETO):
      self.coords[-1] = p
    else:
      self.commands.append(self.MOVETO)
      self.coords.append(self.cp)
    
  def lineto(self, *args):
    self.verify_cp()
    p = toOnePoint(*args)
    self.commands.append(self.LINETO)
    self.cp = p
    self.coords.append(self.cp)

  def curveto(self, *args):
    self.verify_cp()
    (p1,p2,p3) = toThreePoints(*args)
    self.commands.append(self.CURVETO)
    self.cp = p3
    self.coords.append([ p1, p2, p3 ] )

  def rmoveto(self,*args):
    self.verify_cp()
    p = toOnePoint(*args)
    self.moveto(p[0]+self.cp[0],p[1]+self.cp[1])

  def rlineto(self,*args):
    self.verify_cp()
    p = toOnePoint(*args)
    self.lineto(p[0]+self.cp[0],p[1]+self.cp[1])

  def rcurveto(self,*args):
    self.verify_cp()
    (p1,p2,p3) = toThreePoints(*args)
    self.curveto(p1[0]+self.cp[0],p1[1]+self.cp[1],p2[0]+self.cp[0],p2[1]+self.cp[1],p3[0]+self.cp[0],p3[1]+self.cp[1])

  def close(self):
    self.closepath()

  def closepath(self):
    self.verify_cp()
    self.commands.append(self.CLOSEPATH)
    self.coords.append([])

  def append(self,p):
    self.commands.extend(p.commands)
    self.coords.extend(p.coords)
    self.cp = p.cp
  
  def verify_cp(self):
    if(self.cp==None):
      raise RuntimeError("No current point")
  
  def currentpoint(self):
    return self.cp.copy()

  def drawto(self,r):
    for (cmd,coords) in self:
      if(cmd==self.MOVETO):
        r.moveto(coords)
      elif(cmd==self.LINETO):
        r.lineto(coords)
      elif(cmd==self.CLOSEPATH):
        r.closepath()
      elif(cmd==self.CURVETO):
        r.curveto(*coords)

  def bbox(self):
    self.verify_cp()
    box = BBox()
    for (cmd,coords) in self:
      if(cmd==self.MOVETO): 
        box.include(coords)
      elif(cmd==self.LINETO):
        box.include(coords)
      elif(cmd==self.CURVETO):
        for c in coords: box.include(c)
    return box

  def apply(self,a):
    for k in range(len(self.coords)):
      coords = self.coords[k]
      if isinstance(coords,list):
        self.coords[k]=(a.T(c) for c in coords)
      else:
        self.coords[k] = a.T(coords)
 
class BBox:
  def __init__(self,*args):
    self.xmin = None

    if len(args) == 0:
      # empty box
      return

    for p in args:
      self.include(p)

  def __repr__(self):
    if self.xmin is None:
      return 'Empty BBox'
    return 'BBox((%g,%g),(%g,%g))' % (self.xmin,self.ymin,self.xmax,self.ymax)
  
  def include(self,*args):
    p=toOnePoint(*args)
    if self.xmin is None:
      self.xmin = p[0]; self.xmax = self.xmin;
      self.ymin = p[1]; self.ymax = self.ymin;
    else:
      if self.xmin > p[0]: self.xmin = p[0]
      if self.xmax < p[0]: self.xmax = p[0]
      if self.ymin > p[1]: self.ymin = p[1]
      if self.ymax < p[1]: self.ymax = p[1]

  def join(self,box):
    if box.xmin is None:
      return
    if self.xmin is None:
      self.xmin=box.xmin
      self.xmax=box.xmax
      self.ymin=box.ymin
      self.ymax=box.ymax
    if self.xmin>box.xmin: self.xmin = box.xmin
    if self.xmax<box.xmax: self.xmax = box.xmax
    if self.ymin>box.ymin: self.ymin = box.ymin
    if self.ymax<box.ymax: self.ymax = box.ymax

  def shrink(self,left=None,right=None,top=None,bottom=None):
    if left:
      self.xmin += left
      if self.xmin > self.xmax: self.xmin=self.xmax
    if right:
      self.xmax -= right
      if self.xmin > self.xmax: self.xmin=self.xmax
    if top:
      self.ymax -= top
      if self.ymin > self.ymax: self.ymin=self.ymax
    if bottom:
      self.ymin += bottom
      if self.ymin > self.ymax: self.ymin=self.ymax
    
    
  def addmargin(self,left=None,right=None,top=None,bottom=None):
    if left:
      # if left < 0: raise ValueError('Margins must be non-negative')
      self.xmin -= left
    if right:
      # if right < 0: raise ValueError('Margins must be non-negative')
      self.xmax += right
    if bottom:
      # if bottom < 0: raise ValueError('Margins must be non-negative')
      self.ymin -= bottom
    if top:
      # if top < 0: raise ValueError('Margins must be non-negative')
      self.ymax += top

  def isEmpty(self):
    return self.xmin is None

  def thicken(self,w):
    self.addmargin(w,w,w,w)

  def ll(self):
    return Point(self.xmin,self.ymin)

  def lr(self):
    return Point(self.xmax,self.ymin)

  def ul(self):
    return Point(self.xmin,self.ymax)

  def ur(self):
    return Point(self.xmax,self.ymax)

  def cl(self):
    return Point(self.xmin,(self.ymin+self.ymax)/2)

  def cr(self):
    return Point(self.xmax,(self.ymin+self.ymax)/2)

  def uc(self):
    return Point((self.xmin+self.xmax)/2,self.ymax)

  def lc(self):
    return Point((self.xmin+self.xmax)/2,self.ymin)

  def width(self):
    return self.xmax-self.xmin

  def height(self):
    return self.ymax-self.ymin

  def size(self):
    return Vector(self.xmax-self.xmin,self.ymax-self.ymin)

  def center(self):
    return Point((self.xmax+self.xmin)/2.,(self.ymin+self.ymax)/2.)

  def copy(self):
    cbox = BBox()
    if self.xmin is None:
      return cbox
    cbox.xmax=self.xmax
    cbox.ymax = self.ymax
    cbox.xmin = self.xmin
    cbox.ymin = self.ymin
    return cbox

  def drawto(self,canvas):
    canvas.path() + (self.xmin,self.ymin) - (self.xmax,self.ymin) \
                    - (self.xmax,self.ymax) - (self.xmin,self.ymax)
    canvas.closepath()

  def path(self):
    p=Path()
    p.moveto(self.xmin,self.ymin)
    p.lineto(self.xmax,self.ymin)
    p.lineto(self.xmax,self.ymax)
    p.lineto(self.xmin,self.ymax)
    p.closepath()
    return p