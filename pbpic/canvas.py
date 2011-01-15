from __future__ import division
from geometry import Path, AffineTransform, BBox
from gstate import GState
from color import GrayColor, RGBColor
import pbpfont
import sysfont
from metric import Point, Vector, PagePoint
from render_bbox import BBoxRenderer
import math
import os
import exception


class Canvas:
  def __init__(self, w=None, h=None, bbox=None):
    self.w=w
    self.h=h
    self.extents = bbox
    self.gstate = GState();
    self.gstack = []
    self.renderer = None
    self.points = {}
    
    
  def begin(self,renderer=None,w=None,h=None,bbox=None):
    self.renderer=renderer

    # Determine how the page size is being specified.
    if not bbox is None:
      self.extents = bbox
    elif (not w is None) and (not h is None):
      self.extents = BBox(0,0,w.ptValue,h.ptValue())
    elif self.extents is None:
      # Maybe we specified the extents via w/h earlier
      if (not self.w is None) and (not self.h is None):
        self.extents = BBox(0,0,self.w.ptValue(),self.h.ptValue())

    if self.renderer: self.renderer.begin(self.extents)

  def end(self):
    if self.renderer: self.renderer.end()

  def toOnePoint(self,*args):
    if len(args) == 2:
      x=args[0]; y=args[1]
    elif len(args) == 1:
      p = args[0]
      if isinstance(p,str):
        return self.pagemark(p)
      elif isinstance(p,PagePoint):
        return p
      x = p[0]; y = p[1]
    else:
      raise ValueError()
    return self.gstate.ctm.T(x,y)

  def pagemark(self,name):
    # Look first for a named point
    p = self.points.get(name,None)
    if not p is None:
      return p
    
    # Otherwise, it should be one of the following:
    dp = None
    if name == 'll':
      dp = self.extents.ll()
    elif name == 'lr':
      dp = self.extents.lr()
    elif name == 'ul':
      dp = self.extents.ul()
    elif name == 'ur':
      dp = self.extents.ur()
    elif name == 'center':
      dp = self.extents.center()
    if dp is None:
      raise KeyError(name)
    return PagePoint(dp)
      
  def mark(self,name=None,point=None,):
    if point is None:
      point = self.currentpoint()
    point = PagePoint(self.T(point))
    if not name is None:
      self.points[name] = point
    return point

  def ctm(self):
    return self.gstate.ctm.copy()

  def setlinewidth(self,w):
    self.gstate.setlinewidth(w)

  def setcolor(self,c):
    self.gstate.setcolor(c)

  def setrgbcolor(self,r,g,b):
    self.gstate.setcolor(RGBColor(r,g,b))
  
  def setgray(self,g):
    self.gstate.setcolor(GrayColor(g))

  def currentpoint(self):
    cp = self.gstate.path.cp
    if cp is None: return cp
    return cp.copy()

  def setphysicalfont(self,fontdescriptor):
    self.gstate.setphysicalfont(fontdescriptor)

  def findfont(self,name):
    # First check if this is the path to a font.
    if os.path.isfile(name):
      fd = pbpfont.FontDescriptor(name,0)
    # Otherwise see if the operating system knows a font by this name
    else:
      fd = sysfont.findfont(name)

    if not fd is None:
      ftype = fd.fontType()
      if ftype == 'TrueType':
        # FIXME: What if there is not a unicode charmap?
        return pbpfont.UnicodeTrueTypeFont(fd)
      elif ftype == 'Type1':
        return pbpfont.EncodedType1Font(fd)

    # TODO: At this stage we'd like to see if this is a tex font, and if so return a beast that emulates
    # using it.  For now, we bail.
    raise exception.FontNotFound(name)

  def setfont(self,font):
    if isinstance(font,str):
      font = self.findfont(font)
    self.gstate.setfont(font)

  def setfontsize(self,size):
    self.gstate.setfontsize(size)

  def show(self,s):
    self.gstate.font.showto(self,s)

  def charpath(self,c):
    return self.gstate.font.charpath(c)

  def stringwidth(self,s):    
    return self.gstate.ctm.Tvinv(self.gstate.fontsize*self.gstate.font.stringWidth(s))

  def path(self):
    return PathBuilder(self)

  def newpath(self):
    self.gstate.path.clear()

  def lineto(self,*args):
    p = self.toOnePoint(*args)
    self.gstate.path.lineto(p)

  def moveto(self,*args):
    p = self.toOnePoint(*args)
    self.gstate.path.moveto(p)

  def curveto(self,*args):
    if len(args) == 6:
      q = (self.pToPoint(args[0],args[1]),self.pToPoint(args[2],args[3]),self.pToPoint(args[4],args[5]))
    elif len(args) == 3:
      q = [ self.pToPoint(p) for p in args]      
    else:
      raise ValueError()
    self.gstate.path.curveto(q[1],q[2],q[3])

  def polygon(self,pts):
    if len(pts)>0:
      self.moveto(pts[0])
    for p in pts[1:]:
      self.lineto(p)
    self.closepath()

  def closepath(self):
    self.gstate.path.close()

  def stroke(self):
    self.kstroke()
    self.gstate.path.clear()

  def kstroke(self):
    if self.renderer:
      self.renderer.stroke(self.gstate.path,self.gstate)

    # pathbox=BBox()
    # cp = None
    # lastv = None
    # start = None
    # for (cmd,coords) in self.gstate.path:
    #   if cmd == Path.MOVETO:
    #     cp=coords
    #     start=cp
    #     lastv = None
    #   elif cmd == Path.LINETO:
    #     v = coords-cp
    #     if lastv is None:
    #       r=Vector(-v[1],v[0])
    #       
    #     
    #     lastv = coords-cp
    #     


  def addpath(self,p):
    p.drawto(self)
    
  def showglyphs(self,s):
    font = pbpfont.findfont(self.gstate.fontdescriptor)
    metrics = [ font.metricsForGlyph(c) for c in s ]

    if self.renderer:
      self.renderer.showglyphs(s,self.gstate,metrics)

    adv = Vector(0,0)
    for m in metrics:
      adv += m.advance
    adv = self.gstate.texttm().Tv(adv)
    self.gstate.advancetextpoint(adv)


  def scaleto(self,size):
    self.gstate.ctm.makeortho()
    self.gstate.ctm.dilate(size.ptValue())

  def scale(self,*args):
    if len(args) == 1:
      self.gstate.ctm.dilate(args[0])
    else:
      self.gstate.ctm.scale(args[0],args[1])
    
  def translate(self,*args):
    if len(args) == 2:
      x=args[0]; y=args[1]
    elif len(args) == 1:
      p = args[0]
      if isinstance(p,str):
        p = self.Tinv(self.pagemark(p))
      elif isinstance(p,PagePoint):
        p = self.Tinv(p)
      x=p[0]; y=p[1]
    self.gstate.ctm.translate(x,y)

  def rotate(self,theta):
    self.gstate.ctm.rotate(theta)

  def frotate(self,ftheta):
    self.rotate(2*math.pi*ftheta)

  def offset(self,v,len):
    if not isinstance(v,Vector):
      v=Vector(v)
    return v*(len.ptValue()/self.gstate.ctm.Tv(v).length())    

  def T(self,p):
    q = self.gstate.ctm.T(p)
    return q

  def Tinv(self,q):
    return self.gstate.ctm.Tinv(q)

  def place(self,i,at=None,origin=None):
    # If we have a named point, use it.  This will raise an exception if the point doesn't exist.
    if isinstance(origin,str):
      origin = i.pagemark(origin)
      print origin
    # Otherwise, try looking for a point named 'origin'. It's ok if there isn't one.
    elif origin is None:
      try:
        origin = i.pagemark(origin)
      except KeyError:
        pass

    with self.gsave():
      if not at is None:
        self.translate(at)
      self.gstate.ctm.makeortho()
      print self.gstate.ctm
      if not origin is None:
        print origin
        self.translate(-(origin[0]),-(origin[1]))
      i.drawto(self)

  def gsave(self):
    # self.gstate.copy()
    self.gstack.append(self.gstate.copy())
    return GRestorer(self)
  
  def grestore(self):
    self.gstack[-1].setpending(self.gstate)
    self.gstate = self.gstack.pop()
    pass

class PathBuilder:
  def __init__(self,canvas):
    self.canvas = canvas
    
  def __add__(self,p):
    self.canvas.moveto(p)
    return self

  def __sub__(self,p):
    if p == 0:
      self.canvas.closepath()
    else:
      self.canvas.lineto(p)
    return self


class GRestorer:
  def __init__(self,canvas):
    self.canvas = canvas
  def __enter__(self):
    pass
  def __exit__(self,exc_type, exc_value, traceback):
    self.canvas.grestore()
    return False




  # 
  # def Tv(self,h,v):
  #   return self.gstate.ctm.Tv(toOnePoint(*args))
  # 
  # def stroke(self):
  #   self.actions.append(Stroke(deepcopy(self.gstate.path)))
  #   self.gstate.path = Path()
  # 
  # def tmoveto(self,x,y):
  #   self.actions.append(TMoveto(*self.T(x,y)))
  # 
  # def setfont(self,font, size):
  #   self.gstate.font = font
  #   self.actions.append(SetFont(font,size))
  # 
  # def show(self,s):
  #   self.actions.append(Show(s))
  # 
  # def showglyph(self,glyphName,x,y):
  #   self.actions.append(ShowGlyph(glyphName,*self.T(x,y)))
  # 
