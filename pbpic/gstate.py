from __future__ import division
from geometry import Point, Vector, Path, AffineTransform
from metric import pt, Length, Units
from color import GrayColor
import math
import copy

nodash = ([],0)

kLineCap = ['square', 'butt', 'round']
kFillRule = ['evenodd', 'winding']
kLineJoin = ['bevel','miter','round']

class GState:
  def __init__(self,init=True):
    if init: self.init()

  def init(self):
    self.path = Path()

    self.linewidth = 1*pt
    self.linecolor = GrayColor(1)
    self.linecap='square'
    self.linejoin='miter'
    self.miterlimit=10
    self.dash = nodash

    self.fillcolor = GrayColor(1)
    self.fillrule = 'evenodd'

    self.font = None
    self.fontsize = 12*pt
    self.fontcolor = GrayColor(1)
    self.writingvector = Vector(1,0)

    self.clippaths = []

    # Transformation from local to page coordinates
    self.ctm=AffineTransform()
    self.ctmstack = []

    # # Transformation from page to device coordinates
    # self.ptm=AffineTransform()

    # Transformation from line to page coordinates
    self.unitsize = Units()

    self.strokepending = { GState.updatelinewidth:True, GState.updatelinecolor:True, GState.updatelinecap:True, GState.updatelinejoin:True,
                              GState.updatemiterlimit:True, GState.updatedash:True}
    self.fillpending = { GState.updatefillcolor:True, GState.updatefillrule:True }
    self.fontpending = { GState.updatefontdescriptor:True, GState.updatefontcolor:True, GState.updatefontmatrix:True }

  def copystyle(self,other):
    other.setlinewidth(self.linewidth)
    other.setlinecolor(self.linecolor)
    other.setlinecap(self.linecap)
    other.setlinejoin(self.linejoin)
    other.setmiterlimit(self.miterlimit)
    other.setdash(self.dash)
    other.setfillcolor(self.fillcolor)
    other.setfillrule(self.fillrule)
    other.setfont(self.font)
    other.setwritingvector(self.writingvector)
    other.setfontsize(self.fontsize)
    other.setfontcolor(self.fontcolor)

  def copy(self):
    copy=GState(init=False)
    copy.__dict__.update(self.__dict__)
    copy.path=self.path.copy()
    copy.ctm=self.ctm.copy()
    copy.ctmstack=[c.copy() for c in self.ctmstack]
    copy.linewidth=self.linewidth.copy()
    copy.unitsize=self.unitsize.copy()
    copy.fontsize = self.fontsize.copy()
    copy.writingvector=self.writingvector.copy()
    copy.strokepending=self.strokepending.copy()
    copy.fillpending=self.fillpending.copy()
    copy.fontpending=self.fontpending.copy()
    copy.clippaths = [p.copy() for p in self.clippaths]
    return copy

  def ctmsave(self):
    self.ctmstack.append(self.ctm.copy())

  def ctmrestore(self):
    if len(self.ctmstack) > 0:
      self.ctm = self.ctmstack.pop()
  
  def _clearctmstack(self):
    self.ctmstack=[]
      
  def setlinewidth(self,w):
    if self.linewidth == w: return
    self.linewidth = w
    self.strokepending[GState.updatelinewidth] = True

  def setlinecolor(self,c):
    if self.linecolor == c: return
    self.linecolor=c
    self.strokepending[GState.updatelinecolor] = True

  def setlinecap(self,cap):
    if self.linecap == cap: return
    try:
      kLineCap.index(cap)
    except ValueError:
      raise ValueError("Bad linecap '%s': pick one of %s" %(cap,kLineCap) )
    self.linecap=cap
    self.strokepending[GState.updatelinecap] = True

  def setlinejoin(self,join):
    if self.linejoin == join: return
    try:
      kLineJoin.index(join)
    except ValueError:
      raise ValueError("Bad linejoin '%s': pick one of %s" %(join,kLineJoin) )
    self.linejoin = join
    self.strokepending[GState.updatelinejoin] = True

  def setmiterlimit(self,ml):
    if self.miterlimit == ml: return
    self.miterlimit = ml
    self.strokepending[GState.updatemiterlimit] = True

  def setdash(self,d):
    if self.dash == d: return
    self.dash = ([p for p in d[0]],d[1])
    self.strokepending[GState.updatedash] = True

  def setfillcolor(self,c):
    if self.fillcolor == c: return
    self.fillcolor=c
    self.fillpending[GState.updatefillcolor] = True

  def setfillrule(self,r):
    if self.fillrule == r: return
    try:
      kFillRule.index(r)
    except ValueError:
      raise ValueError("Bad fillrule '%s': pick one of %s" %(r,kFillRule) )
    self.fillrule=r
    self.fillpending[GState.updatefillrule] = True

  def setfontsize(self,fontsize):
    if fontsize == self.fontsize:
      return
    self.fontsize=fontsize.copy()

  def setwritingvector(self,wv):
    if wv == self.writingvector:
      return
    self.writingvector=wv.copy()

  def setfontcolor(self,fontcolor):
    if fontcolor == self.fontcolor:
      return
    self.fontcolor=fontcolor
    self.fontpending[GState.updatefontcolor] = True

  def setfont(self,font):
    if self.font == font:
      return
    self.font=font

  def fonttm(self):
    fontsize = self.unitsize.copy()
    fontsize.concat(self.fontsize.units())
    fontsize.dilate(self.fontsize.length())

    wv = self.ctm.Tv(self.writingvector).unitvector()
    cp = self.path.cp
    o = self.ctm.orientation()

    tm = fontsize.affineTransform(page_v=wv,local_v=[1,0],origin=cp,orientation=o)
    return tm


  def clip(self,path):
    self.clippaths.append(path.copy())

  def updatestroke(self,renderer):
    for fcn in self.strokepending.keys():
      fcn(self,renderer)
    self.strokepending.clear()
    
  def updatefill(self,renderer):
    for fcn in self.fillpending.keys():
      fcn(self,renderer)
    self.fillpending.clear()
    
  def updatefont(self,renderer):
    for fcn in self.fontpending.keys():
      fcn(self,renderer)
    self.fontpending.clear()

    
  def updatelinewidth(self,renderer):
    renderer.setlinewidth(self.linewidth)

  def updatelinecolor(self,renderer):
    renderer.setlinecolor(self.linecolor)
    
  def updatelinecap(self,renderer):
    renderer.setlinecap(self.linecap)

  def updatelinejoin(self,renderer):
    renderer.setlinejoin(self.linejoin)

  def updatemiterlimit(self,renderer):
    renderer.setmiterlimit(self.miterlimit)

  def updatedash(self,renderer):
    renderer.setdash(*self.dash)

  def updatefillcolor(self,renderer):
    renderer.setfillcolor(self.fillcolor)

  def updatefillrule(self,renderer):
    renderer.setfillrule(self.fillrule)

  def updatefontdescriptor(self,renderer):
    renderer.setfont(self.fontdescriptor)

  def updatefontcolor(self,renderer):
    renderer.setfontcolor(self.fontcolor)
    
  def updatefontmatrix(self,renderer):
    pass
    
    
  # def checkpending(self,name):
  #   if self.pendingdict.has_key(name):
  #     self.pendingdict.pop(name)
  #     return True
  #   return False
  # 
  # def updatestrokestate(self,renderer):
  #   
  #   if self.checkpending('linewidth'):
  #     renderer.setlinewidth(self.linewidth)
  #   if self.checkpending('linecolor'):
  #     renderer.setlinecolor(self.linecolor)
  #   if self.checkpending('linecap'):
  #     renderer.setlinecap(self.linecap)
  #   if self.checkpending('linejoin'):
  #     renderer.setlinejoin(self.linejoin)
  #   if self.checkpending('miterlimit'):
  #     renderer.setmiterlimit(self.miterlimit)
  #   if self.checkpending('dash'):
  #     renderer.setdash(*self.dash)
  # 
  # def updatefillstate(self,renderer):
  #   if self.checkpending('fillcolor'):
  #     renderer.setfillcolor(self.fillcolor)
  #   if self.checkpending('fillrule'):
  #     renderer.setfillrule(self.fillrule)
  # 
  # def updatetextstate(self,renderer):
  #   if self.checkpending('fontcolor'):
  #     renderer.setfontcolor(self.fontcolor)
  #   if self.checkpending('fontdescriptor'):
  #     renderer.setfont(self.fontdescriptor)
  #   if self.checkpending('fontangle') or self.checkpending('fonteffect') or self.checkpending('fontsize'):
  #     renderer.setfonttm(self.fonttm())
