import _sysfont_mac
import truetype

def find_font(name):
  fontData = _sysfont_mac.find_font(name)
  if fontData is None:
    return (None,None,None,None);
  if fontData[3]:
    return (fontData[0],fontData[1],fontData[2],'RES')
  return (fontData[0],fontData[1],fontData[2],None)

def load_raw(fd):
  if fd.type == 'RES':
    font_data = _sysfont_mac.load_resource_font(fd.path,fd.faceindex);
    ttf = truetype.TrueTypeFont.fromData(font_data)
    return font_data
  return None

def load(fd):
  if fd.type == 'RES':
    font_data = _sysfont_mac.load_resource_font(fd.path,fd.faceindex);
    if font_data is None:
      return None
    ttf = truetype.TrueTypeFont.fromData(font_data)
    return ttf
  return None


def font_type(path):
  if _sysfont_mac.is_resource_font(path):
    return 'RES'
  return None
