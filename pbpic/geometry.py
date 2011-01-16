from __future__ import division
from misc import toOnePoint, toThreePoints
from metric import Point, Vector
import math

class AffineTransform:
  def __init__(self, initial=None):
    if initial is None:
      self.a = 1
      self.b = 0
      self.c = 0
      self.d = 1
      self.tx = 0
      self.ty = 0
    else:
      self.a=initial[0]
      self.b=initial[1]
      self.c=initial[2]
      self.d=initial[3]
      self.tx=initial[4]
      self.ty=initial[5]

  def __repr__(self):
    return '[ %g %g; %g %g] + [%g %g]' %(self.a, self.b, self.c, self.d, self.tx, self.ty)

  def __eq__(self,rhs):
    if not isinstance(rhs,AffineTransform):
      return False
    return (self.a==rhs.a) and (self.b==rhs.b) and (self.c==rhs.c) and (self.d==rhs.d)

  def __neq__(self,rhs):
    return not self.__eq__(rhs)

  def copy(self):
    copy=AffineTransform()
    copy.__dict__.update(self.__dict__)
    return copy

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

    # This seems like a bad idea
    #   
    # if isinstance(p,BBox):
    #   tbox = BBox()
    #   tbox.include(self.T(p.ll()))
    #   tbox.include(self.T(p.lr()))
    #   tbox.include(self.T(p.ul()))
    #   tbox.include(self.T(p.ur()))
    #   return tbox      

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

  def Tv(self, V):
    h=V[0]; v=V[1]
    return Vector(self.a*h+self.c*v, self.b*h+self.d*v)

  def Tvinv(self,V):
    h=V[0]; v=V[1]
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
    ct = math.cos(theta)
    st = math.sin(theta)
    a=self.a; b=self.b; c=self.c; d=self.d
    self.a =  a*ct + c*st
    self.b =  b*ct + d*st
    self.c = -a*st + c*ct
    self.d = -b*st + d*ct

  def det(self):
    return self.a*self.d-self.b*self.c

  def makeortho(self):
    self.orthoFrameX(tm=self)

  def orthoFrameX(self,tm=None):
    if tm is None:
      tm = AffineTransform()
    vx = self.a; vy = self.b
    lenv = math.sqrt(vx*vx+vy*vy)
    if lenv==0:
      return tm
    vx /= lenv; vy /= lenv
    det = self.a*self.d-self.b*self.c
    if det>0: 
      det = 1; 
    else:
      det = -1
    tm.a=vx; tm.b=vy
    tm.c=-det*vy; tm.d = det*vx
    tm.tx = self.tx; tm.ty = self.ty
    return tm

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
    cpath.coords = [ p.copy() for p in self.coords ]
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
    self.coords.append(())

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
 
class BBox:
  def __init__(self,*args):
    self.xmin = None
    if len(args) == 0:
      return

    if len(args) == 1:
      bbox = bbox[0]
    else:
      bbox = args

    if len(bbox) != 4:
      raise ValueError('A BBox must be constructed with nothing, a list [x0,y0,x1,y1], or four floats.\n Received %s.' % args)
    # we have x0, y0, x1, y1
    self.include(bbox[0],bbox[1])
    self.include(bbox[2],bbox[3])

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
    
  def addmargin(self,left=None,right=None,top=None,bottom=None):
    if left:
      if left < 0: raise ValueError('Margins must be non-negative')
      self.xmin -= left
    if right:
      if right < 0: raise ValueError('Margins must be non-negative')
      self.xmax += right
    if bottom:
      if bottom < 0: raise ValueError('Margins must be non-negative')
      self.ymin -= bottom
    if top:
      if top < 0: raise ValueError('Margins must be non-negative')
      self.ymax += top

  def thicken(self,w):
    self.addmargin(w,w,w,w)

  def ll(self):
    return (self.xmin,self.ymin)

  def lr(self):
    return (self.xmax,self.ymin)

  def ul(self):
    return (self.xmin,self.ymax)

  def ur(self):
    return (self.xmax,self.ymax)

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
    cbox.xmax=self.xmax
    if not cbox.xmax is None:
      cbox.ymax = self.ymax
      cbox.xmin = self.xmin
      cbox.ymin = self.ymin
    return cbox

  def path(self):
    p=Path()
    p.moveto(self.xmin,self.ymin)
    p.lineto(self.xmax,self.ymin)
    p.lineto(self.xmax,self.ymax)
    p.lineto(self.xmin,self.ymax)
    p.closepath()
    return p