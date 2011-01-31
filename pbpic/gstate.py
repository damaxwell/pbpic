from __future__ import division
from geometry import Path, AffineTransform
from metric import Point,pt,MeasuredLength
from color import GrayColor
import math
import copy

nodash = ([],0)

class GState:
  def __init__(self,init=True):
    if init: self.init()

  def init(self):
    self.path = Path()

    self.linewidth = 1*pt
    self.linecolor = GrayColor(1)
    self.linecap='square'
    self.linejoin='miter'
    self.miterlimit=1
    self.dash = nodash

    self.fillcolor = GrayColor(1)
    self.fillrule = 'evenodd'

    self.fontdescriptor = None
    self.font = None
    self.fontsize = 12
    self.fonteffect = AffineTransform()
    self.fontangle = 0
    self.fontcolor = GrayColor(1)

    # Transformation from local to page coordinates
    self.ctm=AffineTransform()

    # Transformation from page to device coordinates
    self.ptm=AffineTransform()

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
    other.setphysicalfont(self.fontdescriptor)
    other.setfont(self.font)
    other.setfontsize(self.fontsize)
    other.setfontangle(self.fontangle)
    other.setfonteffect(self.fonteffect)
    other.setfontcolor(self.fontcolor)

  def copy(self):
    copy=GState(init=False)
    copy.__dict__.update(self.__dict__)
    copy.path=self.path.copy()
    copy.ctm=self.ctm.copy()
    copy.ptm=self.ptm.copy()
    copy.fonteffect=self.fonteffect.copy()
    copy.strokepending=self.strokepending.copy()
    copy.fillpending=self.fillpending.copy()
    copy.fontpending=self.fontpending.copy()
    return copy
    
  def fonttm(self,reflectY=False):
    ttm = AffineTransform()
    ttm.tx=self.path.cp.x
    ttm.ty=self.path.cp.y
    ttm.rotate(self.fontangle*2*math.pi)
    ttm.dilate(self.fontsize)
    ttm.concat(self.fonteffect)
    if reflectY:
      ttm.scale(1,-1)
    return ttm

  def setlinewidth(self,w):
    if self.linewidth == w: return
    self.linewidth=w
    self.strokepending[GState.updatelinewidth] = True

  def setlinecolor(self,c):
    if self.linecolor == c: return
    self.linecolor=c
    self.strokepending[GState.updatelinecolor] = True

  def setlinecap(self,cap):
    if self.linecap == cap: return
    self.linecap=cap
    self.strokepending[GState.updatelinecap] = True

  def setlinejoin(self,join):
    if self.linejoin == join: return
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
    self.fillrule=r
    self.fillpending[GState.updatefillrule] = True
    
  def setphysicalfont(self,fontdescriptor):
    if self.fontdescriptor == fontdescriptor:
      return
    self.fontdescriptor=fontdescriptor
    self.fontpending[GState.updatefontdescriptor] = True

  def setfontsize(self,fontsize):
    if isinstance(fontsize,MeasuredLength):
      fontsize=fontsize.ptValue()
    if fontsize == self.fontsize:
      return
    self.fontsize=fontsize
    self.fontpending[GState.updatefontmatrix] = True

  def setfontangle(self,fontangle):
    if fontangle == self.fontangle:
      return
    self.fontangle=fontangle
    self.fontpending[GState.updatefontmatrix] = True

  def setfonteffect(self,fonteffect):
    if fonteffect == self.fonteffect:
      return
    self.fonteffect=fonteffect
    self.fontpending[GState.updatefontmatrix] = True

  def setfontcolor(self,fontcolor):
    if fontcolor == self.fontcolor:
      return
    self.fontcolor=fontcolor
    self.fontpending[GState.updatefontcolor] = True

  def setfont(self,font):
    if self.font == font:
      return
    self.font=font

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
