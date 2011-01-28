import pbpfont
import os.path
import truetype, type1
import exception

try:
  import sysfont_mac
  sysfont_platform = sysfont_mac
except:
  class sysfont_none:
    @staticmethod
    def find_font(fontname): return (None,None,None,None)
    @staticmethod
    def load(fontname): return None
    @staticmethod
    def font_type(fontpath): return fontTypeFromExtension(fontpath)
    
  sysfont_platform = sysfont_none
import pbpfont
import truetype

def findfont(name):
  # First check if this is the path to a font.
  fontPath = None
  psName = None
  fontType = None
  index = -1

  if os.path.isfile(name):
    fontPath = name
  # Otherwise see if the operating system knows a font by this name
  else:
    (fontPath,psName,index,fontType) = sysfont_platform.find_font(name)

  if fontPath is None:
    raise exception.FontNotFound(name)

  if fontType is None:
    fontType = sysfont_platform.font_type(fontPath)
    if fontType is None:
      raise exception.FontUnrecognized(fontPath)
    if fontType == 'TTC':
      if not psName is None:
        with open(fontPath,'rb') as f:
          ttc = truetype.TrueTypeCollection(f)
          index = ttc.indexForPSName(psName)

  if index <0: index = 0

  return pbpfont.FontDescriptor(fontPath,index,fontType)


def fontTypeFromExtension(path):
  import os.path
  ext = os.path.splitext(path)[1].lower()
  
  if ext == '.ttf':
    return 'TrueType'
  elif ext == '.ttc':
    return 'TTC'
  elif ext == '.pfb':
    return 'Type1'

  return None

def load(font_descriptor):
  font = None
  font = sysfont_platform.load(font_descriptor);
  
  if not font is None:
    return font
  
  path = font_descriptor.path
  ftype = fontTypeFromExtension(path)
  
  if ftype == 'TrueType':
    return truetype.TrueTypeFont.fromPath(path)
  elif ftype == 'Type1':
    return type1.Type1Font.fromPath(path)
  elif ftype == 'TTC':
    with open(path,'rb') as f:
      ttc = truetype.TrueTypeCollection(f)
      offset = ttc.offsetForFontIndex(font_descriptor.faceindex)
    return truetype.TrueTypeFont(open(path,'rb'),offsetTableStart=offset)

  raise Exception('Unknown font type for file %s',self.path)


class PhysicalFontCache:
  def __init__(self):
    self.cache={}

  def findfont(self,fontdescriptor):
    font = self.cache.get(fontdescriptor,None)
    if font is None:
      font = load(fontdescriptor)
      self.cache[fontdescriptor] = font
    return font

_globalFontCache = PhysicalFontCache()
def findcachedfont(fontdescriptor):
  return _globalFontCache.findfont(fontdescriptor)

if __name__ == '__main__':
  import sys
  fd = findfont(sys.argv[1])
  f = load(fd)
  print f