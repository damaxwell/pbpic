import cairo
from .geometry import BBox, Path, AffineTransform
from .font import sysfont
import math


class BBoxRenderer:
  def __init__(self):
    self._bbox = BBox()

  def begin(self,extents):
    pass

  def end(self):
    pass

  def bbox(self):
    return self._bbox.copy()

  def gsave(self):
    pass
  
  def grestore(self):
    pass

  def stroke(self,path,gstate):
    bbox = self._bbox
    for (cmd,coords) in path:
      if(cmd==Path.MOVETO): 
        bbox.include(coords)
      elif(cmd==Path.LINETO):
        bbox.include(coords)
      elif(cmd==Path.CURVETO):
        for c in coords: bbox.include(c)

  def fill(self,path,gstate):
    self.stroke(path,gstate)

  def clip(self,path,gstate):
    pass

  def showglyphs(self,s,fontdescriptor,tm,metrics,gstate):
    font = sysfont.findcachedfont(fontdescriptor)
    tm = tm.copy()

    bbox = self._bbox
    for k in xrange(len(s)):
      gpath = font.pathForGlyph(s[k])
      for (cmd,coords) in gpath:
        if(cmd==Path.MOVETO): 
          bbox.include(tm.T(coords))
        elif(cmd==Path.LINETO):
          bbox.include(tm.T(coords))
        elif(cmd==Path.CURVETO):
          for c in coords: bbox.include(tm.T(c))
      adv=metrics[k].advance
      tm.translate(adv[0],adv[1])
