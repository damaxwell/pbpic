from truetype import TrueTypeFont
from type1 import Type1Font

from metric import Vector

class FontDescriptor:
  def __init__(self,path,faceindex=0):
    self._path = path
    self._faceindex=faceindex

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

  def fontType(self):
    if self.path.lower().endswith('.ttf'):
      return 'TrueType'
    elif self.path.lower().endswith('.pfb'):
      return 'Type1'

    # FIXME: Try harder. Look at headers.
    return None

  def load(self):
    ftype = self.fontType()

    if ftype == 'TrueType':
      return TrueTypeFont.fromPath(self.path)
    elif ftype == 'Type1':
      return Type1Font.fromPath(self.path)
      
    raise Exception('Unknown font type for file %s',self.path)


class PhysicalFontCache:
  def __init__(self):
    self.cache={}

  def findfont(self,fontdescriptor):
    font = self.cache.get(fontdescriptor,None)
    if font is None:
      font = fontdescriptor.load()
      self.cache[fontdescriptor] = font
    return font

_globalFontCache = PhysicalFontCache()
def findfont(fontdescriptor):
  return _globalFontCache.findfont(fontdescriptor)

class Font:
  def __init__(self,descriptor):
    self._descriptor = descriptor

  @property
  def descriptor(self):
    return self._descriptor

  def showto(self,canvas,s):
    raise NotImplementedError()
  def stringWidth(self,s):
    raise NotImplementedError()
  def charpath(self,c):
    raise NotImplementedError()

class UnicodeTrueTypeFont(Font):
  def __init__(self,descriptor):
    Font.__init__(self,descriptor)
    self.ttf = findfont(descriptor)
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
  def __init__(self,descriptor,encoding=None):
    Font.__init__(self,descriptor)
    self.t1font = findfont(descriptor)
    if encoding is None:
      self.ev = self.t1font.encoding()
    else:
      self.ev = encoding

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
