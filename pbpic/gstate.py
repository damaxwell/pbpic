from __future__ import division
from geometry import Path, AffineTransform
from metric import Point,pt,MeasuredLength
from color import GrayColor
import copy

nodash = ([],0)

class GState:
  def __init__(self,init=True):
    if init: self.init()

  def init(self):
    self.color = GrayColor(1)
    self.path = Path()

    self.linewidth = 1*pt
    self.linecolor = GrayColor(1)
    self.linecap='square'
    self.linejoin='butt'
    self.miterlimit=1
    self.dash = nodash

    self.fillcolor = GrayColor(1)
    self.fillrule = 'evenodd'

    self.fontdescriptor = None
    self.font = None
    self.fontsize = 12

    self.ctm=AffineTransform()
    self.pendingdict = {}
    self.useddict = {}

  def copystyle(self,other):
    other.setcolor(self.color)
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

  def copy(self):
    copy=GState(init=False)
    copy.__dict__.update(self.__dict__)
    copy.path=self.path.copy()
    copy.ctm=self.ctm.copy()
    copy.pendingdict = self.pendingdict.copy()
    copy.useddict = self.useddict.copy()
    return copy
    
  def texttm(self):
    ttm = self.ctm.orthoFrameX()
    self.path.verify_cp()
    ttm.tx = self.path.cp.x
    ttm.ty = self.path.cp.y
    ttm.dilate(self.fontsize)
    return ttm

  def setlinewidth(self,w):
    if self.linewidth == w: return
    self.linewidth=w
    self.setpending('linewidth')

  def setlinecolor(self,c):
    if self.linecolor == c: return
    self.linecolor=c
    self.setpending('linecolor')

  def setlinecap(self,cap):
    if self.linecap == cap: return
    self.linecap=cap
    self.setpending('linecap')

  def setlinejoin(self,join):
    if self.linejoin == join: return
    self.linejoin = join
    self.setpending('linejoin')

  def setmiterlimit(self,ml):
    if self.miterlimit == ml: return
    self.miterlimit = ml
    self.setpending('miterlimit')

  def setdash(self,d):
    if self.dash == d: return
    self.dash = ([p for p in d[0]],d[1])
    self.setpending('dash')

  def setfillcolor(self,c):
    if self.fillcolor == c: return
    self.fillcolor=c
    self.setpending('fillcolor')

  def setfillrule(self,r):
    if self.fillrule == r: return
    self.fillrule=r
    self.setpending('fillrule')
    
  def setphysicalfont(self,fontdescriptor):
    if self.fontdescriptor == fontdescriptor:
      return
    self.fontdescriptor=fontdescriptor
    self.setpending('fontdescriptor')

  def setfontsize(self,fontsize):
    if isinstance(fontsize,MeasuredLength):
      fontsize=fontsize.value()
    if fontsize == self.fontsize:
      return
    self.fontsize=fontsize
    self.setpending('fontsize')

  def setfont(self,font):
    if self.font == font:
      return
    self.font=font

  def setpending(self, name):
    if isinstance(name,GState):
      self.pendingdict.update(name.useddict)
      self.useddict.update(name.useddict)
    else:
      self.pendingdict[name] = True
      self.useddict[name] = True

  def setused(self,name):
    if isinstance(name,GState):
      self.useddict.update(name.useddict)
    else:
      self.useddict[name] = True

  def checkpending(self,name):
    if self.pendingdict.has_key(name):
      self.pendingdict.pop(name)
      return True
    return False

  def updatestrokestate(self,renderer):
    if self.checkpending('linewidth'):
      renderer.setlinewidth(self.linewidth)
    if self.checkpending('linecolor'):
      renderer.setlinecolor(self.linecolor)
    if self.checkpending('linecap'):
      renderer.setlinecap(self.linecap)
    if self.checkpending('linejoin'):
      renderer.setlinejoin(self.linejoin)
    if self.checkpending('miterlimit'):
      renderer.setmiterlimit(self.miterlimit)
    if self.checkpending('dash'):
      renderer.setdash(*self.dash)

  def updatefillstate(self,renderer):
    if self.checkpending('fillcolor'):
      renderer.setfillcolor(self.fillcolor)
    if self.checkpending('fillrule'):
      renderer.setfillrule(self.fillrule)
      
  def updatetextstate(self,renderer):
    if self.checkpending('color'):
      self.color.renderto(renderer)
    if self.checkpending('fontdescriptor'):
      renderer.setfont(self.fontdescriptor)
    if self.checkpending('fontsize'):
      renderer.setfontsize(self.fontsize)
