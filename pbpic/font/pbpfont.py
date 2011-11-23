import truetype, type1, sysfont
from pbpic.geometry import Vector

class Font:

  # @property
  # def descriptor(self):
  #   return self._descriptor

  def write(self,canvas,s):
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

  def write(self,canvas,s):
    canvas.showglyphs(self.cmap.glyphsForString(s),self._descriptor)

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

  def write(self,canvas,s):
    canvas.showglyphs(self.t1font.glyphIndices(self.ev.glyphNamesForChars(s)),self._descriptor)

  def charpath(self,c):
    return self.t1font.pathForGlyphname(self.ev[ord(c)])
    
  def stringWidth(self,s):
    w=Vector(0,0)
    for c in s:
      w += self.t1font.metricsForGlyphname( self.ev[ord(c)]).advance
    return w


def findfont(name):
  """Returns a Font associated with :name:, which is either a path
  to a font or the name of a font to be found by the operating system.
  """
  
  # Convert the name to a font descriptor
  fd = sysfont.findfont(name)
  if fd is None:
    raise exception.FontNotFound(name)

  # Load the physical font associated with the descriptor
  font=sysfont.findcachedfont(fd);
  if font is None:
    raise exception.FontNotFound(name)

  # For true type, return a unicode encoded font
  if isinstance(font,truetype.TrueTypeFont):
    return UnicodeTrueTypeFont(fd,font)

  # For type 1, return a default encoded font
  if isinstance(font,type1.Type1Font):
    return EncodedType1Font(fd,font)

  # TODO: At this stage we'd like to see if this is a tex font, and if so return a beast that emulates
  # using it.  For now, we bail.
  raise exception.FontNotFound(name)

