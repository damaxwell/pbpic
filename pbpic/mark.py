from .geometry import BBox
from .metric import PagePoint

class Marks:
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
    raise NotImplementedError()
    
class NamedMarks(Marks):
  def __init__(self):
    self._points = {}

  def __iter__(self):
    for (k,v) in self._points.items():
      yield (k,v)
    
  def getpoint(self,markname):
    p = self._points.get(markname,None)
    return p
  
  def addpoint(self,markname,point):
    assert(isinstance(point,PagePoint))
    self._points[markname] = point

class SubNamedMarks(Marks):
  def __init__(self,marks,name):
    self.marks = marks
    self.name = name+'.'
  
  def getpoint(self,markname):
    if markname.find(self.name)==0:
      return self.marks.getpoint(markname[len(self.name):])

class BBoxMarks(Marks):
  def __init__(self,canvas):
    self.bboxcallbacks = { 'll':BBox.ll, 'lr':BBox.lr, 'ul':BBox.ul, 'ur':BBox.ur, 'center':BBox.center,
                           'cl':BBox.cl, 'cr':BBox.cr, 'uc':BBox.uc, 'lc':BBox.lc }
    self._canvas = canvas
    
  def getpoint(self,markname):
    cb = self.bboxcallbacks.get(markname)
    if not cb is None:
      if self._canvas._extents is None:
        raise exception.PBPicException('No bounding box available to computed named point "%s"' % markname) 
      return PagePoint(cb(self._canvas._extents))

    return None
