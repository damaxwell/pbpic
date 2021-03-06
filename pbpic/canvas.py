from .geometry import Point, Vector, BBox, AffineTransform
from .metric import Length, PagePoint, PageVector, Units
from .mark import NamedMarks, BBoxMarks
from . import exception
from .gstate import GState
from .font import pbpfont, sysfont
import math

dx = Vector(1,0)
dy = Vector(0,1)

# The global canvas for drawing into
_canvas = None
# Global stack for canvasses to draw into.
_canvasstack = []
def pushcanvas(c):
  global _canvas, _canvasstack
  _canvasstack.append(_canvas)
  _canvas = c

def popcanvas():
  global _canvas, _canvasstack
  _canvas = _canvasstack.pop()

def getcanvas():
  global _canvas
  return _canvas

def nobuild(func):
  def nobuildfunc(self,*args,**kwargs):
    if self.building:
      raise exception.BuildTransgression()
    return func(self,*args,**kwargs)
  return nobuildfunc

class Canvas:
  def __init__(self, w=None, h=None, renderer=None):
    self.gstate = GState();
    self.gstack = []
    self.renderer = renderer
    
    self.building = False

    self._extents = None
    if (w is not None) or (h is not None):
      if (w is None):
        raise ValueError("Cannot set canvas size from just a height specifiation; a width is needed.")
      elif h is None:
        raise ValueError("Cannot set canvas size from just a width specifiation; a height is needed.")
      if not isinstance(w,Length):
        raise ValueError("Canvas width must be specified as a Length (e.g. 8.5*in)")
      if not isinstance(h,Length):
        raise ValueError("Canvas height must be specified as a Length (e.g. 11*in)")      

      self._extents=BBox((0,0),(w.apply(dx).length(),h.apply(dy).length()))

    self.marks = [ NamedMarks() ]

  def begin(self):
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

    if isinstance(w,Units):
      units = w
    else:
      # It should be a length
      units = w.units()
  
    pageUnits = self.gstate.unitsize.copy()
    pageUnits.concat(units)

    tm = pageUnits.affineTransform(page_v=page_dx,local_v=preserve,origin=origin,orientation=o)

    if isinstance(w,Length):
      tm.dilate(w.length())
    self.gstate.ctm = tm

  def window(self, oldRect,newRect):
    hf = oldRect.width()/newRect.width()
    vf = oldRect.height()/newRect.height()

    self.translate( oldRect.ll() )
    self.scale(hf,vf)
    self.translate(-newRect.ll())

  def ctmconcat(self,tm):
    self.gstate.ctm.concat(tm)

  def currentpoint(self):
    cp = self.gstate.path.cp
    if cp is None: 
      raise exception.NoCurrentPoint()
    return self.gstate.ctm.Tinv(cp)

  def currentpagepoint(self):
    cp = self.gstate.path.cp
    if cp is None: 
      raise exception.NoCurrentPoint()
    return cp.copy()

  def currentpointexists(self):
    return not self.gstate.path.cp is None

  def currentpath(self):
    path = self.gstate.path.copy()
    Tinv = self.gstate.ctm.inverse()
    path.apply(Tinv)
    return path

  def __enter__(self):
    pushcanvas(self)
  def __exit__(self,exc_type, exc_value, traceback):
    popcanvas()
    return False

  @nobuild
  def gsave(self):
    self.gstack.append(self.gstate.copy())
    self.gstate._clearctmstack() # Ensure that it is not possible to restore the ctm past a gsave.
    if not self.renderer is None:
      self.renderer.gsave()
    return GRestorer(self)

  @nobuild
  def grestore(self):

    if len(self.gstack) <=0:
      raise exception.StackUnderflow("Extra grestore")
    
    if self.gstack[-1] is None:
     raise exception.StackUnderflow("Extra grestore during a 'draw' operation.")

    self.gstate = self.gstack.pop()

    if not self.renderer is None:
      self.renderer.grestore()

  def ctmsave(self):
    self.gstate.ctmsave()
    return CTMRestorer(self)
  def ctmrestore(self):
    if len(self.gstate.ctmstack) <=0:
      raise exception.StackUnderflow("Extra ctmrestore")
    self.gstate.ctmrestore()

  @nobuild
  def setlinewidth(self,w):
    if not isinstance(w,Length):      
      lw = self.gstate.linewidth.copy()
      lw.setlength(float(w))
      w=lw
    self.gstate.setlinewidth(w.copy())
  def linewidth(self):
    return self.gstate.linewidth

  @nobuild
  def setlinecap(self,cap):
    self.gstate.setlinecap(cap)
  def linecap(self):
    return self.gstate.linecap

  @nobuild
  def setlinejoin(self,join):
    self.gstate.setlinejoin(join)
  def linejoin(self):
    return self.gstate.linejoin

  @nobuild
  def setmiterlimit(self,ml):
    self.gstate.setmiterlimit(ml)
  def miterlimit(self):
    return self.gstate.miterlimit

  @nobuild
  def setdash(self,*args):
    if len(args) == 2:
      dash = args[0]; phase = args[1]
    elif len(args) == 1:
      d=args[0][0]
      if isinstance(d,list) or isinstance(d,tuple):
        dash=args[0][0]; phase=args[0][1]
      else:
        dash = args[0]; phase = 0
    else:
      raise ValueError('setdash takes 1 or 2 arguments')
    self.gstate.setdash((dash,phase))
  def dash(self):
    return ([d for d in self.gstate.dash[0] ], self.gstate.dash[1])

  @nobuild
  def stroke(self,color=None):
    self.kstroke(color=color)
    self.newpath()

  @nobuild
  def kstroke(self,color=None):
    if self.renderer:
      if not color is None:
        oldcolor = self.gstate.linecolor
        self.gstate.setlinecolor(color)
        self.renderer.stroke(self.gstate.path,self.gstate)
        self.gstate.setlinecolor(oldcolor)
      else:
        self.renderer.stroke(self.gstate.path,self.gstate)

  @nobuild
  def fill(self,color=None):
    self.kfill(color=color)
    self.newpath()

  @nobuild
  def kfill(self,color=None):
    if self.renderer:
      if not color is None:
        oldcolor = self.gstate.fillcolor
        self.gstate.setfillcolor(color)
        self.renderer.fill(self.gstate.path,self.gstate)
        self.gstate.setfillcolor(oldcolor)
      else:
        self.renderer.fill(self.gstate.path,self.gstate)

  @nobuild
  def fillstroke(self,fillcolor=None,strokecolor=None):
    self.kfill(fillcolor)
    self.stroke(strokecolor)

  @nobuild
  def clip(self):
    if self.renderer:
      self.renderer.clip(self.gstate.path,self.gstate)
    self.gstate.clip(self.gstate.path)
    self.gstate.path.clear()

  def newpath(self):
    self.gstate.path.clear()

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

  def vcurveto(self,*args):
    if len(args) == 6:
      q = [self.pageVector(args[0],args[1]),self.pageVector(args[2],args[3]),self.pagePoint(args[4],args[5])]
    elif len(args) == 3:
      q = [ self.pageVector(args[0]), self.pageVector(args[1]), self.pagePoint(args[2]) ]      
    else:
      raise ValueError()
    self.gstate.path.curveto(self.currentpagepoint()+q[0],q[2]-q[1],q[2])



  def rmoveto(self,*args):
    v = self.pageVector(*args)
    self.gstate.path.rmoveto(v)

  def rlineto(self,*args):
    v = self.pageVector(*args)
    self.gstate.path.rlineto(v)

  def closepath(self):
    self.gstate.path.close()

  @nobuild
  def setfont(self,font):
    if isinstance(font,str):
      font = pbpfont.findfont(font)
    self.gstate.setfont(font)

  @nobuild
  def setfontsize(self,size):
    if not isinstance(size,Length):
      fs = self.gstate.fontsize.copy()
      fs.setlength(size)
      self.gstate.setfontsize(fs)
    else:
      self.gstate.setfontsize(size.copy())
  def fontsize(self):
    return self.gstate.fontsize.copy()

  @nobuild
  def setwritingvector(self,*args):
    v=self.vector(*args)
    self.gstate.setwritingvector(v.copy())
  def writingvector(self):
    return self.gstate.writingvector.copy()

  @nobuild
  def setfontcolor(self,fontcolor):
    self.gstate.setfontcolor(fontcolor)
  def fontcolor(self):
    return self.gstate.fontcolor
    

  @nobuild
  def write(self,s):
    if self.gstate.path.cp is None: 
      raise exception.NoCurrentPoint()
    if self.gstate.font is None:
      raise exception.NoFont("A font must be set before calling 'write'.")
    self.gstate.font.write(self,s)

  def charpath(self,c):
    if self.gstate.font is None:
      raise exception.NoFont("A font must be set before calling 'charpath'.")
    return self.gstate.font.charpath(c)

  def stringwidth(self,s):
    tm=self.gstate.fonttm()
    pageWidth = tm.Tv(self.gstate.font.stringWidth(s))
    userWidth = self.gstate.ctm.Tvinv(pageWidth)
    return userWidth
    # print self.gstate.fontsize
    # return self.gstate.ctm.Tvinv(self.gstate.fontsize*self.gstate.font.stringWidth(s))
#    raise NotImplementedError()

  @nobuild
  def showglyphs(self,s,fontdescriptor):
    print(fontdescriptor)
    font = sysfont.findcachedfont(fontdescriptor)
    metrics = [ font.metricsForGlyph(c) for c in s ]

    tm=self.gstate.fonttm()
    if self.renderer:
      self.renderer.showglyphs(s,fontdescriptor,tm,metrics,self.gstate)

    adv = Vector(0,0)
    for m in metrics:
      adv += m.advance
    adv = tm.Tv(adv)
    self.gstate.path.rmoveto(adv)

  def getmark(self,markname):
    for m in self.marks:
      p = m.getpoint(markname)
      if p is not None:
        return p
    raise KeyError(markname)

  def markpoint(self,*args):
    if len(args)==1:
      name=args[0]
      self.markpoint(name,self.currentpoint())
      return
    if len(args)%2 != 0:
      raise ValueError()
    if len(args)>2:
      for k in range(len(args)/2):
        self.markpoint(args[2*k],args[2*k+1])
    else:
      point=self.pagePoint(args[1]);name=args[0]; 
      self.marks[0].addpoint(name,point)

  def addmarks(self,marker,*args,**kwargs):
    if hasattr(marker,'markup'):
      marker.markup(self,*args,**kwargs)
    elif callable(marker):
      marker(*args,**kwargs)
    else:
      raise ValueError('Unable to add marks from %s' % marker)

  def extents(self):
    if self._extents is None:
      raise exception.NoExtents()
    e = BBox()
    e.include(self.gstate.ctm.Tinv(self._extents.ll())); e.include(self.gstate.ctm.Tinv(self._extents.lr()))
    e.include(self.gstate.ctm.Tinv(self._extents.ul())); e.include(self.gstate.ctm.Tinv(self._extents.ur()))
    return e

  def pageextents(self):
    if self._extents is None:
      raise exception.NoExtents()
    return self._extents.copy()

  # # FIXME: the page->device needs more thought
  # def pageconcat(self,tm):
  #   self.gstate.ptm.concat(tm)
  # 
  # 
  # FIXME: the page->device needs more thought
  @nobuild
  def sizeconcat(self,tm):
    self.gstate.unitsize.concat(tm)

  def pagePoint(self,*args):
    """Converts anything that might be interpreted as a point into a
    point expressed in page coordinates."""
    if len(args) == 1:
      p = args[0]
      if callable(p):
        p=p(self)
        assert(isinstance(p,PagePoint))
        return p
      elif isinstance(p,str):
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
      if callable(p):
        p=p(self)
        assert(isinstance(p,PageVector))
        return p
      elif isinstance(p,str):
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
        if isinstance(y,str) or isinstance(y,PageVector) or isinstance(y,Vector) or isinstance(y,tuple) or isinstance(y,list) or isinstance(y,Point) or isinstance(y,PagePoint):
          v = self.vector(y)
          pagev = self.gstate.ctm.Tv(v)
          pagev /= x.measure(pagev)
          return PageVector(pagev.x,pagev.y)
        if isinstance(x,Length):
          dx = self.gstate.ctm.Tv([1,0])
          xv = x.apply(dx)
        else:
          xv = self.gstate.ctm.Tv(x,0)
        if isinstance(y,Length):
          dy = self.gstate.ctm.Tv([0,1])
          yv = y.apply(dy)
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
      if callable(p):
        p=p(self)
        if isinstance(p,PagePoint):
          return self.point(p)
        assert(isinstance(p,Point))
        return p
      elif isinstance(p,str):
        pp = self.getmark(p)
        return self.gstate.ctm.Tinv(pp.x,pp.y)
      elif isinstance(p,PagePoint):
        return self.gstate.ctm.Tinv(p.x,p.y)
      elif isinstance(p,Point):
        return p
      elif len(p) == 2:
        return Point(p[0],p[1])
    elif len(args) == 2:
      return Point(args[0],args[1])
    raise ValueError("Unable to convert %s to a point." % args.__str__())


  def vector(self,*args):
    """Converts anything that might be interpreted as a vector into a
    vector expressed in working coordinates."""
    if len(args) == 1:
      p = args[0]
      if callable(p):
        p=p(self)
        if isinstance(p,PageVector):
          return self.vector(p)
        assert(isinstance(p,Vector))
        return p
      elif isinstance(p,str):
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
          if isinstance(y,str) or isinstance(y,PageVector)  or isinstance(y,Vector) or isinstance(y,tuple) or isinstance(y,list) or isinstance(y,Point) or isinstance(y,PagePoint):
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

  @nobuild
  def setlinecolor(self,c):
    self.gstate.setlinecolor(c)
  def linecolor(self):
    return self.gstate.linecolor

  @nobuild
  def setfillcolor(self,c):
    self.gstate.setfillcolor(c)
  def fillcolor(self):
    return self.gstate.fillcolor

  @nobuild
  def setfillrule(self,r):
    self.gstate.setfillrule(r)
  def fillrule(self):
    return self.gstate.fillrule

  def build(self,builder,*args,**kwargs):
    """Calls on :builder: to add to the current path.  This is done by calling
    :builder:'s :buildpath: attribute, if present, or simply calling :builder:
    otherwise. 
    
    No  drawing operations may be peformed (though this is not yet enforced).  
    Upon exit, the current path may be changed, but other aspects of the 
    graphics state should not be.""" 

    wasBuilding = self.building
    self.building = True
    try:
      at = kwargs.get('at')
      if at is not None:
        self.moveto(at)
        kwargs.pop('at')

      with self.ctmsave():
        if hasattr(builder,'buildpath'):
          builder.buildpath(self,*args,**kwargs)
        elif callable(builder):
          builder(self,*args,**kwargs)
        else:
          raise ValueError("Unable to build a path from %s" % builder)
    finally:
      self.building = wasBuilding

  # Higher level operations:
  def draw(self,p,*args,**kwargs):
    at = kwargs.get('at')
    if at is not None:
      self.moveto(at)
      kwargs.pop('at')
    self.gstack.append(None)
    try:
      if hasattr(p,'drawto'):
        p.drawto(self,*args,**kwargs)
      elif callable(p):
        p(self,*args,**kwargs)
      else:
        raise TypeError()
    finally:
      while self.gstack[-1] is not None:
        self.grestore()
      self.gstack.pop()
      # FIXME: Verify that the gstate was not altered?
      self.newpath()

  def path(self):
    return PathBuilder(self)

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
  def __enter__(self):
    pass
  def __exit__(self,exc_type, exc_value, traceback):
    self.canvas.ctmrestore()
    return False


class PathBuilder:
  def __init__(self,canvas):
    self.canvas = canvas

  def __add__(self,p):
    if isinstance(p,tuple) and len(p)>2:
      self.canvas.curveto(*p)
    else:
      self.canvas.moveto(p)
    return self

  def __sub__(self,p):
    if p == 0:
      self.canvas.closepath()
    elif (isinstance(p,tuple) or isinstance(p,list)) and len(p)==3:
      self.canvas.curveto(p[0],p[1],p[2])
    else:
      self.canvas.lineto(p)
    return self

