from __future__ import division
from geometry import Path, AffineTransform
from metric import Point,pt,MeasuredLength
from color import GrayColor
import copy

class GState:
  def __init__(self,init=True):
    if init: self.init()

  def init(self):
    self.color = GrayColor(0)
    self.path = Path()
    self.linewidth = 1*pt

    self.fontdescriptor = None
    self.font = None
    self.fontsize = 12
  
    self.ctm=AffineTransform()
    self.pendingdict = {}

  def copystyle(self,other):
    other.setcolor(self.color)
    other.setlinewidth(self.linewidth)
    other.setphysicalfont(self.fontdescriptor)
    other.setfont(self.font)
    other.setfontsize(self.fontsize)

  def copy(self):
    copy=GState(init=False)
    copy.__dict__.update(self.__dict__)
    copy.path=self.path.copy()
    copy.ctm=self.ctm.copy()
    copy.pendingdict = self.pendingdict.copy()
    return copy
    
  def texttm(self):
    ttm = self.ctm.orthoFrameX()
    self.path.verify_cp()
    ttm.tx = self.path.cp.x
    ttm.ty = self.path.cp.y
    ttm.dilate(self.fontsize)
    return ttm

  def setlinewidth(self,w):
    if self.linewidth == w:
      return
    self.linewidth=w
    self.setpending('linewidth')

  def setcolor(self,c):
    if self.color == c:
      return
    self.color=c
    self.setpending('color')

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
      self.pendingdict.update(name.pendingdict)
    else:
      self.pendingdict[name] = True

  def checkpending(self,name):
    if self.pendingdict.has_key(name):
      self.pendingdict.pop(name)
      return True
    return False

  def updatepathstate(self,renderer):
    if self.checkpending('linewidth'):
      renderer.setlinewidth(self.linewidth)
    if self.checkpending('color'):
      self.color.renderto(renderer)
  
  def updatetextstate(self,renderer):
    if self.checkpending('color'):
      self.color.renderto(renderer)
    if self.checkpending('fontdescriptor'):
      renderer.setfont(self.fontdescriptor)
    if self.checkpending('fontsize'):
      renderer.setfontsize(self.fontsize)
