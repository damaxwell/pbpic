import cairo
from geometry import BBox, Path, AffineTransform
import sysfont
import math


class BBoxRenderer:
  def __init__(self,ctm=None):
    self._bbox = BBox()
    if ctm is None:
      ctm = AffineTransform()
    self.ctm = ctm

  def begin(self,extents):
    pass

  def end(self):
    pass

  def bbox(self):
    return self._bbox.copy()
    
  def stroke(self,path,gstate):
    bbox = self._bbox
    ctm = self.ctm
    for (cmd,coords) in path:
      if(cmd==Path.MOVETO): 
        bbox.include(ctm.T(coords))
      elif(cmd==Path.LINETO):
        bbox.include(ctm.T(coords))
      elif(cmd==Path.CURVETO):
        for c in coords: bbox.include(ctm.T(c))

    # pathbox = path.bbox(self.Tinv)
    # pathbox.thicken(gstate.linewidth.ptValue()/2)
    # self._bbox.join(pathbox)

  def fill(self,path,gstate):
    self.stroke(path,gstate)

  def showglyphs(self,s,gstate,metrics):
    font = sysfont.findcachedfont(gstate.fontdescriptor)

    ttm = gstate.texttm()
    ctm = self.ctm

    for k in xrange(len(s)):
      gpath = font.pathForGlyph(s[k])
      gbox=BBox()
      for (cmd,coords) in gpath:
        if(cmd==Path.MOVETO): 
          gbox.include(ctm.T(ttm.T(coords)))
        elif(cmd==Path.LINETO):
          gbox.include(ctm.T(ttm.T(coords)))
        elif(cmd==Path.CURVETO):
          for c in coords: gbox.include(ctm.T(ttm.T(c)))
      self._bbox.join(gbox)
      adv=metrics[k].advance
      ttm.translate(adv[0],adv[1])
