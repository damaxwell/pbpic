from truetype import TrueTypeFont, TrueTypeCollection
from type1 import Type1Font

from metric import Vector



class FontDescriptor:
  def __init__(self,path,faceindex=0,fontType=None):
    self._path = path
    self._faceindex=faceindex
    self.type = fontType

  @property
  def path(self):
    return self._path

  @property
  def faceindex(self):
    return self._faceindex

  def __eq__(self,rhs):
    if not isinstance(rhs,FontDescriptor): return False
    if self.path != rhs.path:
      return False
    return self.faceindex == rhs.faceindex

  def __repr__(self):
    return 'FontDescriptor: %s (face %d)' % (self.path,self.faceindex)

  def __hash__(self):
    return hash(self.path) ^ hash(self.faceindex)




class Font:

  # @property
  # def descriptor(self):
  #   return self._descriptor

  def showto(self,canvas,s):
    raise NotImplementedError()
  def stringWidth(self,s):
    raise NotImplementedError()
  def charpath(self,c):
    raise NotImplementedError()

class UnicodeTrueTypeFont(Font):
  def __init__(self,descriptor,ttfont):
    self._descriptor=descriptor
    self.ttf = ttfont
    self.cmap=self.ttf.cmapForUnicode()

  def showto(self,canvas,s):
    canvas.setphysicalfont(self._descriptor)
    canvas.showglyphs(self.cmap.glyphsForString(s))

  def charpath(self,c):
    return self.ttf.pathForGlyph(self.cmap.glyphForChar(c))
  
  def stringWidth(self,s):
    w=Vector(0,0)
    for c in s:
      w += self.ttf.metricsForGlyph( self.cmap.glyphForChar(c) ).advance
    return w

class EncodedType1Font(Font):
  def __init__(self,descriptor,t1font,encoding=None):
    self._descriptor=descriptor
    self.t1font = t1font
    if encoding is None:
      self.ev = self.t1font.encoding()
    else:
      self.ev = encoding

  def __repr__(self):
    return "EncodedType1Font(%s,%s)" % (self._descriptor,self.ev)

  def showto(self,canvas,s):
    canvas.setphysicalfont(self._descriptor)
    canvas.showglyphs(self.t1font.glyphIndices(self.ev.glyphNamesForChars(s)))

  def charpath(self,c):
    return self.t1font.pathForGlyphname(self.ev[ord(c)])
    
  def stringWidth(self,s):
    w=Vector(0,0)
    for c in s:
      w += self.t1font.metricsForGlyphname( self.ev[ord(c)]).advance
    return w
