class PBPicException(Exception):
  pass

class FontNotFound(PBPicException):
  def __init__(self,fname):
    PBPicException.__init__(self,'Font %s not found.' % fname)

class FontUnrecognized(PBPicException):
  def __init__(self,fd):
    PBPicException.__init__(self,'Font %s not in a known format.' % fd)

class StylePropertyNotFound(PBPicException):
  def __init__(self,styleName):
    PBPicException.__init__(self,'Style %s not found' % styleName)
    
class NoCurrentPoint(PBPicException):
  pass

class NoExtents(PBPicException):
  pass


class NoFont(PBPicException):
  pass