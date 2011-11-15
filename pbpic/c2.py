from geometry import Point, Vector, BBox
from metric import Length, PagePoint, PageVector
from mark import NamedMarks, BBoxMarks
from exception import NoCurrentPoint
from gstate import GState
import math

dx = Vector(1,0)
dy = Vector(0,1)

class Canvas2:
  def __init__(self, w=None, h=None, renderer=None):
    self._setextents(w,h,bbox)
    self.gstate = GState();
    self.gstack = []
    self.renderer = renderer
    self.marks = [ NamedMarks(), BBoxMarks(self)]
    self.units = AffineTransform()

  def _setextents(self,w,h):
    if (w is None):
      raise ValueError("Cannot set canvas size from just a height specifiation; a width is needed.")
    elif h is None:
      raise ValueError("Cannot set canvas size from just a width specifiation; a height is needed.")
    if isinstance(w,Length):
      w = w.pagelength(dx)
    if isinstance(h,Length):
      h = h.pagelength(dy)
    self._extents = BBox( (0,0), (w,h) )

  def begin(self,w=None,h=None,renderer=None):
    if not renderer is None:
      self.renderer=renderer

    if (w is not None) or (h is not None):
      self._setextents(w,h)

    if self.renderer: self.renderer.begin(self._extents)

  def end(self):
    if self.renderer: self.renderer.end()

  def scale(self,*args):
    if len(args) == 1:
      self.gstate.ctm.dilate(args[0])
    else:
      self.gstate.ctm.scale(args[0],args[1])

  def translate(self,*args):
    p=self.point(*args)
    self.gstate.ctm.translate(p.x,p.y)

  def rotate(self,ftheta):
    self.gstate.ctm.rotate(ftheta)

  def rrotate(self,theta):
    self.gstate.ctm.rrotate(theta)

  def drotate(self,dtheta):
    self.gstate.ctm.rrotate(2*math.pi*dtheta/360.)

  def scaleto(self,w,preserve=dx):
    page_dx = self.gstate.ctm.Tv(preserve)
    o = self.gstate.ctm.orientation()
    origin=self.gstate.ctm.origin()
    self.setctm(w.topagecoords(page_dx,preserve,origin,o))

  def ctm(self):
    return self.gstate.ctm.copy()
  def setctm(self,ctm):
    self.gstate.ctm = ctm.copy()

  def currentpoint(self):
    cp = self.gstate.path.cp
    if cp is None: 
      raise NoCurrentPoint()
    return self.gstate.ctm.Tinv(self.gstate.ptm.Tinv(cp))

  def currentpointexists(self):
    return not self.gstate.path.cp is None

  def gsave(self):
    self.gstack.append(self.gstate.copy())
    if not self.renderer is None:
      self.renderer.gsave()

    return GRestorer(self)

  def grestore(self):
    self.gstate = self.gstack.pop()

    if not self.renderer is None:
      self.renderer.grestore()

  def ctmsave(self):
    return CTMRestorer(self)

  def setlinewidth(self,w):
    if not isinstance(w,Length):      
      lw = self.gstate.linewidth.copy()
      lw.setlength(w)
      w=lw
    self.gstate.setlinewidth(w.copy())

  def linewidth(self):
    return self.gstate.linewidth

  def setlinecap(self,cap):
    self.gstate.setlinecap(cap)
  def linecap(self):
    return self.gstate.linecap

  def setlinejoin(self,join):
    self.gstate.setlinejoin(join)
  def linejoin(self):
    return self.gstate.linejoin

  def setmiterlimit(self,ml):
    self.gstate.setmiterlimit(ml)
  def miterlimit(self):
    return self.gstate.miterlimit

  def stroke(self,color=None):
    self.kstroke(color=color)
    self.gstate.path.clear()

  def kstroke(self,color=None):
    if self.renderer:
      if not color is None:
        oldcolor = self.gstate.linecolor
        self.gstate.setlinecolor(color)
        self.renderer.stroke(self.gstate.path,self.gstate)
        self.gstate.setlinecolor(oldcolor)
      else:
        self.renderer.stroke(self.gstate.path,self.gstate)

  def fill(self,color=None):
    self.kfill(color=color)
    self.gstate.path.clear()

  def kfill(self,color=None):
    if self.renderer:
      if not color is None:
        oldcolor = self.gstate.fillcolor
        self.gstate.setfillcolor(color)
        self.renderer.fill(self.gstate.path,self.gstate)
        self.gstate.setfillcolor(oldcolor)
      else:
        self.renderer.fill(self.gstate.path,self.gstate)

  def fillstroke(self,fillcolor=None,strokecolor=None):
    self.kfill(fillcolor)
    self.stroke(strokecolor)

  def moveto(self,*args):
    p = self.pagePoint(*args)
    self.gstate.path.moveto(p)

  def lineto(self,*args):
    p = self.pagePoint(*args)
    self.gstate.path.lineto(p)

  def curveto(self,*args):
    if len(args) == 6:
      q = (self.pagePoint(args[0],args[1]),self.pagePoint(args[2],args[3]),self.pagePoint(args[4],args[5]))
    elif len(args) == 3:
      q = [ self.pagePoint(p) for p in args]      
    else:
      raise ValueError()
    self.gstate.path.curveto(q[0],q[1],q[2])

  def rmoveto(self,*args):
    v = self.pageVector(*args)
    self.gstate.path.rmoveto(v)

  def rlineto(self,*args):
    v = self.pageVector(*args)
    self.gstate.path.rlineto(v)

  def closepath(self):
    self.gstate.path.close()

  def getmark(self,markname):
    for m in self.marks:
      p = m.getpoint(markname)
      if p is not None:
        return p
    raise KeyError(markname)

  def pagePoint(self,*args):
    """Converts anything that might be interpreted as a point into a
    point expressed in page coordinates."""
    if len(args) == 1:
      p = args[0]
      if isinstance(p,str):
        return self.getmark(p)
      elif isinstance(p,PagePoint):
        return p
      elif len(p) == 2:
        x = p[0]; y = p[1]
      else:
        raise ValueError()
    elif len(args) == 2:
      x=args[0]; y=args[1]
    else:
      raise ValueError()
    return PagePoint(self.gstate.ctm.T(x,y))

  def pageVector(self,*args):
    """Converts anything that might be interpreted as a vector into a
    vector expressed in page coordinates."""
    if len(args) == 1:
      p = args[0]
      if isinstance(p,str):
        raise NotImplementedError()
      elif isinstance(p,PageVector):
        return p
      elif len(p) == 2:
        x = p[0]; y = p[1]
      else:
        raise ValueError()
    elif len(args) == 2:
      x=args[0]; y=args[1]
      if isinstance(x,Length) or isinstance(y,Length):
        if isinstance(y,str) or isinstance(y,PageVector) or isinstance(y,tuple) or isinstance(y,list):
          v = self.vector(y)
          pagev = self.gstate.ctm.Tv(v)
          pagev /= x.measure(pagev)
          return PageVector(pagev.x,pagev.y)
        if isinstance(x,Length):
          dx = self.gstate.ctm.Tv([1,0])
          xv = x.rescale(dx)
        else:
          xv = self.gstate.ctm.Tv(x,0)
        if isinstance(y,Length):
          dy = self.gstate.ctm.Tv([0,1])
          yv = y.rescale(dy)
        else:
          yv = self.gstate.ctm.Tv(0,y)
        v = xv+yv
        return PageVector(v.x,v.y)
      else:
        x=args[0]; y=args[1]
    else:
      raise ValueError()
    v = self.gstate.ctm.Tv(x,y)
    return PageVector(v.x, v.y)


  def point(self,*args):
    """Converts anything that might be interpreted as a point into a
    point expressed in working coordinates."""
    pp = None
    if len(args) == 1:
      p = args[0]
      if isinstance(p,str):
        pp = self.getmark(p)
        return self.gstate.ctm.Tinv(pp.x,pp.y)
      elif isinstance(p,PagePoint):
        return self.gstate.ctm.Tinv(p.x,p.y)
      elif isinstance(p,Point):
        return p
      elif len(p) == 2:
        return Point(p[0],p[1])
      else:
        raise ValueError()
      return Point(self.gstate.ctm.T(x,y))
    elif len(args) == 2:
      return Point(args[0],args[1])
    raise ValueError()


  def vector(self,*args):
    """Converts anything that might be interpreted as a vector into a
    vector expressed in working coordinates."""
    if len(args) == 1:
      p = args[0]
      if isinstance(p,str):
        raise NotImplementedError()
      elif isinstance(p,PageVector):
        return self.gstate.ctm.Tvinv(p.x,p.y)
      elif len(p) == 2:
        return Vector(p[0],p[1])
      else:
        raise ValueError()
    elif len(args) == 2:
      x = args[0]; y=args[1]
      if isinstance(x,Length) or isinstance(y,Length):
        if isinstance(x,Length):
          if isinstance(y,str) or isinstance(y,PageVector) or isinstance(y,tuple) or isinstance(y,list):
            v = self.vector(y)
            pagev = self.gstate.ctm.Tv(v)
            v /= x.measure(pagev)
            return v
          dx = self.gstate.ctm.Tv([1,0])
          l = x.measure(dx)
          xv = Vector(1./l,0)
        else:
          xv = Vector(x,0)
        if isinstance(y,Length):
          dy = self.gstate.ctm.Tv([0,1])
          l = y.measure(dy)
          yv = Vector(0,1./l)
        else:
          yv = Vector(0,y)
        return xv+yv
      else:
        x=args[0]; y=args[1]
    else:
      raise ValueError()
    return Vector(x,y)

  def setlinecolor(self,c):
    self.gstate.setlinecolor(c)
  def linecolor(self):
    return self.gstate.linecolor

  def setfillcolor(self,c):
    self.gstate.setfillcolor(c)
  def fillcolor(self):
    return self.gstate.fillcolor

  def setfillrule(self,r):
    self.gstate.setfillrule(r)
  def fillrule(self):
    return self.gstate.fillrule


  # Higher level operations:
  def draw(self,p,*args,**kwargs):
    at = kwargs.get('at')
    if at is not None:
      self.moveto(at)
      kwargs.pop('at')
    if callable(p):
      p(self,*args,**kwargs)
    elif hasattr(p,'drawto'):
      p.drawto(self,*args,**kwargs)
    else:
      raise TypeError()

class GRestorer:
  def __init__(self,canvas):
    self.canvas = canvas
  def __enter__(self):
    pass
  def __exit__(self,exc_type, exc_value, traceback):
    self.canvas.grestore()
    return False

class CTMRestorer:
  def __init__(self,canvas):
    self.canvas = canvas
    self.ctm = canvas.ctm()
  def __enter__(self):
    pass
  def __exit__(self,exc_type, exc_value, traceback):
    self.canvas.setctm(self.ctm)
    return False

