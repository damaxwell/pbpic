from __future__ import division
from geometry import Path, AffineTransform, BBox
from gstate import GState
from color import GrayColor, RGBColor
import pbpfont
import sysfont
from metric import Point, Vector, PagePoint, MeasuredLength
from render_bbox import BBoxRenderer
import math
import os
import exception
from style import style
import truetype, type1

def isvectorlike(a):
  try:
    return len(a) == 2
  except:
    pass
  return False

class MarkedPoints:
  def __init__(self):
    self.points = {}
    self.ctm = None
  
  def __repr__(self):
    return 'MarkedPonts'
    # print 'Marked points: '
    # for (key,value) in self.points.items():
    #   print '  %s: %s' % (key,value)
    # print '/MarkedPoints'
  
  def __getitem__(self,markname):
    p = self.getpoint(markname)
    if p is None:
      raise KeyError(markname)
    return p
    
  def __getattr__(self,markname):
    p = self.getpoint(markname)
    if p is None:
      raise AttributeError()
    return p
  
  def getpoint(self,markname):
    p = self.points.get(markname)
    return self._transform(p)

  def _transform(self,p):
    if isinstance(p,PagePoint) and (not self.ctm is None):
      return PagePoint(self.ctm.T(p))
    return p
    
  def _addpoint(self,markname,p):
    #FIXME: Should we  check that we are only adding a PagePoint or a MarkedPoints?
    self.points[markname] = p

  def copy(self):
    cp = MarkedPoints()
    cp.points = self.points.copy()
    if not self.ctm is None:
      cp.ctm = self.ctm.copy()
    return cp

  def append(self,ctm):
    if self.ctm is None:
      self.ctm = ctm.copy()
    else:
      self.ctm.append(ctm)
    for p in self.points.values():
      if isinstance(p,MarkedPoints):
        p.append(ctm)



class BBoxMarkedPoints(MarkedPoints):
  def __init__(self,bbox):
    MarkedPoints.__init__(self)
    self._bbox = bbox
    self.bboxcallbacks = { 'll':BBox.ll, 'lr':BBox.lr, 'ul':BBox.ul, 'ur':BBox.ur, 'center':BBox.center,
                           'cl':BBox.cl, 'cr':BBox.cr, 'uc':BBox.uc, 'lc':BBox.lc }

  def setbbox(self,bbox):
    self._bbox = bbox
  
  def getpoint(self,markname):
    # First look up a point with that name
    p = MarkedPoints.getpoint(self,markname)
    if not p is None:
      return p

    # Now try special points
    cb = self.bboxcallbacks.get(markname)
    if not cb is None:
      if self._bbox is None:
        raise PBPicException('No bounding box available to computed named point %s' % markname) 
      return self._transform(PagePoint(cb(self._bbox)))
    
    raise KeyError(markname)

  def copy(self):
    cp = BBoxMarkedPoints(None)
    cp.points = self.points.copy()
    if not self.ctm is None:
      cp.ctm = self.ctm.copy()
    if not self._bbox is None:
      cp._bbox =  self._bbox.copy()
    return cp


class Canvas:
  def __init__(self, w=None, h=None, bbox=None,renderer=None):
    self._setextents(w,h,bbox)
    self.gstate = GState();
    self.gstack = []
    self.renderer = renderer
    self.lineStyleCmds = { 'width':self.setlinewidth, 'color':self.setlinecolor, 'cap':self.setlinecap, 
                           'join':self.setlinejoin, 'miterlimit':self.setmiterlimit, 'dash':self.setdash }

    self.fillStyleCmds = { 'color':self.setfillcolor, 'rule':self.setfillrule }

  def _setextents(self,w,h,bbox):
    if (not w is None) or (not h is None):
      if not bbox is None:
        raise ValueError("Cannot set canvas size from both a bounding box and a width/height specifiation.")
      else:
        if (w is None):
          raise ValueError("Cannot set canvas size from just a height specifiation; a width is needed.")
        elif h is None:
          raise ValueError("Cannot set canvas size from just a width specifiation; a height is needed.")
        if isinstance(w,MeasuredLength):
          w = w.ptValue()
        if isinstance(h,MeasuredLength):
          h = h.ptValue()
        bbox = BBox(0,0,w,h)
    self._extents = bbox

  def begin(self,w=None,h=None,bbox=None,renderer=None):
    if not renderer is None:
      self.renderer=renderer

    if (not w is None) or (not h is None) or (not bbox is None):
      self._setextents(w,h,bbox)

    self.markedpoints = BBoxMarkedPoints(self._extents)

    if self.renderer: self.renderer.begin(self._extents)
    self.gstate.copystyle(self)

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
    return self.gstate.ptm.T(self.gstate.ctm.T(x,y))

  def toOneVector(self,*args):
    if len(args) == 2:
        x = args[0]; y=args[1]
    else:
      x = args[0][0]; y=args[0][1]

    if isvectorlike(x):
      v = self.gstate.ctm.Tv(self.offset(args[0],args[1]))
    else:      
      if isinstance(x,MeasuredLength):
        v0 = self.gstate.ctm.Tv(self.offset(Vector(1,0),x))
      else:
        v0 = self.gstate.ctm.Tv((x,0))

      if isinstance(y,MeasuredLength):
        v1 = self.gstate.ctm.Tv(self.offset(Vector(0,1),y))
      else:
        v1 = self.gstate.ctm.Tv((0,y))        
      v = v0+v1

    return self.gstate.ptm.Tv(v)

  def pagemark(self,name):
    return self.markedpoints[name]
      
  def mark(self,name=None,point=None,):
    if point is None:
      point = self.currentpoint()
    if not isinstance(point,PagePoint):
      point = PagePoint(self.T(point))
    if not name is None:
      self.markedpoints._addpoint(name,point)
    return point

  def marks(self):
    return self.markedpoints

  def extents(self):
    e = BBox()
    e.include(self.Tinv(self._extents.ll())); e.include(self.Tinv(self._extents.lr()))
    e.include(self.Tinv(self._extents.ul())); e.include(self.Tinv(self._extents.ur()))
    return e

  def local(self,p):
    if isinstance(p,PagePoint):
      return self.Tinv(p)
    return p

  def ctm(self):
    return self.gstate.ctm.copy()
  def setctm(self,ctm):
    self.gstate.ctm = ctm.copy()

  def setlinewidth(self,w):
    self.gstate.setlinewidth(w)
  def linewidth(self):
    return self.gstate.linewidth

  def setlinecolor(self,c):
    self.gstate.setlinecolor(c)
  def linecolor(self):
    return self.gstate.linecolor
  
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

  def setfillcolor(self,c):
    self.gstate.setfillcolor(c)
  def fillcolor(self):
    return self.gstate.fillcolor

  def setfillrule(self,r):
    self.gstate.setfillrule(r)
  def fillrule(self):
    return self.gstate.fillrule

  def setdash(self,*args):
    if len(args) == 2:
      dash = args[0]; phase = args[1]
    elif len(args) == 1:
      dash = args[0][0]; phase = args[0][1]
    else:
      raise ValueError('setdash takes 1 or 2 arguments')
    self.gstate.setdash((dash,phase))

  def dash(self):
    return ([d for d in self.gstate.dash[0] ], self.gstate.dash[1])

  def currentpoint(self):
    cp = self.gstate.path.cp
    if cp is None: return cp
    return self.gstate.ctm.Tinv(self.gstate.ptm.Tinv(cp))

  def currentpointexists(self):
    return not self.gstate.path.cp is None

  def setphysicalfont(self,fontdescriptor):
    self.gstate.setphysicalfont(fontdescriptor)

  # Fixme: this never uses self, so it doesn't belong here
  def findfont(self,name):
    fd = sysfont.findfont(name)
    if fd is None:
      raise exception.FontNotFound(name)

    font=sysfont.findcachedfont(fd);
    if font is None:
      raise exception.FontNotFound(name)
      
    if isinstance(font,truetype.TrueTypeFont):
      return pbpfont.UnicodeTrueTypeFont(fd,font)
    
    if isinstance(font,type1.Type1Font):
      return pbpfont.EncodedType1Font(fd,font)

    # TODO: At this stage we'd like to see if this is a tex font, and if so return a beast that emulates
    # using it.  For now, we bail.
    raise exception.FontNotFound(name)

  def setfont(self,font):
    if isinstance(font,str):
      font = self.findfont(font)
    self.gstate.setfont(font)

  def setfontsize(self,size):
    self.gstate.setfontsize(size)

  def setfontangle(self,angle):
    self.gstate.setfontangle(angle)
    
  def setfonteffect(self,fonteffect):
    self.gstate.setfonteffect(fonteffect)
  
  def setfontcolor(self,fontcolor):
    self.gstate.setfontcolor(fontcolor)
  def fontcolor(self):
    return self.gstate.fontcolor

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

  def rlineto(self,*args):
    v = self.toOneVector(*args)
    self.gstate.path.rlineto(v)

  def moveto(self,*args):
    p = self.toOnePoint(*args)
    self.gstate.path.moveto(p)

  def rmoveto(self,*args):
    v = self.toOneVector(*args)
    self.gstate.path.rmoveto(v)

  def curveto(self,*args):
    if len(args) == 6:
      q = (self.toOnePoint(args[0],args[1]),self.toOnePoint(args[2],args[3]),self.toOnePoint(args[4],args[5]))
    elif len(args) == 3:
      q = [ self.toOnePoint(p) for p in args]      
    else:
      raise ValueError()
    self.gstate.path.curveto(q[0],q[1],q[2])

  def polygon(self,pts):
    if len(pts)>0:
      self.moveto(pts[0])
    for p in pts[1:]:
      self.lineto(p)
    self.closepath()

  def closepath(self):
    self.gstate.path.close()

  def stroke(self):
    if self.renderer:
      self.renderer.stroke(self.gstate.path,self.gstate)
    self.gstate.path.clear()

  def kstroke(self):
    if self.renderer:
      self.renderer.stroke(self.gstate.path,self.gstate)

  def fill(self):
    if self.renderer:
      self.renderer.fill(self.gstate.path,self.gstate)
    self.gstate.path.clear()

  def kfill(self):
    if self.renderer:
      self.renderer.fill(self.gstate.path,self.gstate)

  def clip(self):
    if self.renderer:
      self.renderer.clip(self.gstate.path,self.gstate)
    self.gstate.clip(self.gstate.path)
    self.gstate.path.clear()
    

  def applystyle(self,s=None):
    if s is None:
      s = style()
    try:
      linestyle = s['line']
      for (key,value) in linestyle.sdict.items():
        linecmd = self.lineStyleCmds.get(key)
        # FIXME: Warn if there is a meaningless line style?
        if not linecmd is None:
          linecmd(value)
    except exception.StylePropertyNotFound:
      pass
    try:
      fillstyle = s['fill']
      for (key,value) in fillstyle.sdict.items():
        cmd = self.fillStyleCmds.get(key)
        # FIXME: Warn if there is a meaningless line style?
        if not cmd is None:
          cmd(value)
    except exception.StylePropertyNotFound:
      pass

  def addpath(self,p,*args,**kwargs):
    if callable(p):
      p(self,*args,**kwargs)
    elif hasattr(p,'drawto'):
      p.drawto(self,*args,**kwargs)
    else:
      raise TypeError()
    
  def showglyphs(self,s):
    font = sysfont.findcachedfont(self.gstate.fontdescriptor)
    metrics = [ font.metricsForGlyph(c) for c in s ]

    if self.renderer:
      self.renderer.showglyphs(s,self.gstate,metrics)

    adv = Vector(0,0)
    for m in metrics:
      adv += m.advance
    adv = self.gstate.fonttm().Tv(adv)
    self.gstate.path.rmoveto(adv)

  def scaleto(self,size):
    if isinstance(size,MeasuredLength):
      self.gstate.ctm.makeortho()
      self.gstate.ctm.dilate(size.ptValue())
    else:
      self.gstate.ctm.dilate(size)

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
        q = self.pagemark(p)
        p = self.Tinv(q)
      elif isinstance(p,PagePoint):
        p = self.Tinv(p)
      x=p[0]; y=p[1]
    self.gstate.ctm.translate(x,y)

  def window(self,oldRect,newRect):
    hf = oldRect.width()/newRect.width()
    vf = oldRect.height()/newRect.height()

    self.translate( oldRect.ll() )
    self.scale(hf,vf)
    self.translate(-newRect.ll())
    

  def rotate(self,theta):
    self.gstate.ctm.rotate(theta)

  def frotate(self,ftheta):
    self.rotate(2*math.pi*ftheta)

  def pagetranslate(self,*args):
    if len(args) == 2:
      x=args[0]; y=args[1]
    elif len(args) == 1:
      p = args[0]
      x=p[0]; y=p[1]
    self.gstate.ptm.translate(x,y)

  def pagerotate(self,theta):
    self.gstate.ptm.rotate(theta)

  def pagescale(self,sx,sy):
    self.gstate.ptm.scale(sx,sy)

  def offset(self,v,len):
    if not isinstance(v,Vector):
      v=Vector(v)
    return v*(len.ptValue()/self.gstate.ctm.Tv(v).length())    

  def T(self,p):
    q = self.gstate.ctm.T(p)
    return self.gstate.ptm.T(q)

  def Tinv(self,q):
    p = self.gstate.ctm.Tinv(q)
    return self.gstate.ptm.Tinv(p)

  def Tv(self,v):
    return self.gstate.ptm.Tv(self.gstate.ctm.Tv(v))

  def Tvinv(self,w):
    return self.gstate.ptm.Tv(self.gstate.ctm.Tvinv(w))

  def draw(self,o,*args,**kwargs):
    self.place(o,*args,**kwargs)

  def place(self,o,*args,**kwargs):
    d = {}
    for key in [ 'at', 'offset', 'name']:
      value = None
      try:
        value = kwargs.pop(key)
      except KeyError:
        pass
      d[key] = value
    at = d['at']
    offset = d['offset']
    name = d['name']

    if not at is None:
      self.moveto(at)
    if not offset is None:
      self.rmoveto(offset)
    o.drawto(self,*args,**kwargs)
      
    if not name is None:
      mp = i.markedpoints.copy()
      mp.append(self.ctm())
      self.markedpoints._addpoint(name,mp)


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


class PathBuilder:
  def __init__(self,canvas):
    self.canvas = canvas
    
  def __add__(self,p):
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
