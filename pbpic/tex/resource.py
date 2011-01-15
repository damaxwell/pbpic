try:
  import pykpse
  find=pykpse.find
  formats=pykpse
except:
  import kpsewhich
  find=kpsewhich.find
  formats = kpsewhich
import font
import devicefont
import pbpic.userprefs as userprefs

class _TexPathCache:
  def __init__(self):
    self.clear()

  def clear(self):
    self.vfPathCache={}
    self.tfmPathCache = {}
    self.pfbPathCache = {}
    self.encPathCache = {}
    self.mapPathCache = {}

class TexPathCache(userprefs.PersistantCache):

  def __init__(self):
    userprefs.PersistantCache.__init__(self,_TexPathCache,'texResource.cache')
    
pathCache = TexPathCache()

def resetTexCache():
  pathCache.clear()

class TexResourceNotFound(Exception):
  def __init__(self,msg):
    Exception.__init__(self,'Tex resource not found: %s' % msg)

def findVFPath(fn):
  fontPath = pathCache().vfPathCache.get(fn)
  if fontPath is None:
    fontPath = find(fn, formats.VF_TYPE)
    if fontPath is None:
      pathCache().vfPathCache[fn] = ''
      raise TexResourceNotFound('Virtual font %s' % fn)
    pathCache().vfPathCache[fn] = fontPath
  if len(fontPath) == 0:
    raise TexResourceNotFound('Virtual font %s' % fn)
  return fontPath

def findTFMPath(fn):
  fontPath = pathCache().tfmPathCache.get(fn)
  if fontPath is None:
    fontPath = find(fn, formats.TFM_TYPE)
    if fontPath is None:
      raise TexResourceNotFound('Tex font metrics %s' % fn)
    pathCache().tfmPathCache[fn] = fontPath
  return fontPath

def findPFBPath(fn):
  fontPath = pathCache().pfbPathCache.get(fn)
  if fontPath is None:
    fontPath = find(fn, formats.TYPE1_TYPE)
    if fontPath is None:
      raise TexResourceNotFound('PFB font %s' % fn)
    pathCache().pfbPathCache[fn] = fontPath
  return fontPath

def findEncodingPath(e):
  ePath = pathCache().encPathCache.get(e)
  if ePath is None:
    ePath = find(e, formats.ENC_TYPE)
    if ePath is None:
      raise TexResourceNotFound('Encoding %s' % e)
    pathCache().encPathCache[e] = ePath
  return ePath

def findMapFilePath(m):
  mPath = pathCache().mapPathCache.get(m)
  if mPath is None:
    mPath = find(m, formats.FONTMAP_TYPE)
    if mPath is None:
      raise TexResourceNotFound('Mapfile %s' % m)
    pathCache().mapPathCache[m] = mPath
  return mPath


vfDict = {}
def findVF(fontName):
  vf = vfDict.get(fontName)
  if vf is None:
    path = findVFPath(fontName)
    vf = font.VirtualFont(path)
    vfDict[fontName] = vf
  return vf

tfmDict = {}
def findTFM(fontName):
  tfm = tfmDict.get(fontName,None)
  if tfm is None:
    p = findTFMPath( fontName )
    tfm = font.TFM(p)
    tfmDict[fontName] = font.TFM(p)
  return tfm

mapFileDict = {}
def findMapFile(m):
  mf = mapFileDict.get(m,None)
  if mf is None:
    p = findMapFilePath( m )
    mf = devicefont.DviPdfMapFile( p )
    mapFileDict[m] = mf
  return mf

encDict = {}
def findEncoding(e):
  enc = encDict.get(e,None)
  if enc is None:
    p = findEncodingPath( e )
    enc = devicefont.encodingVectorFromFile(p)
    encDict[e] = enc
  return enc


# We don't have a findPFB service since the base pbpic system takes care of this.
