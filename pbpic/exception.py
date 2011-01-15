class PBPicException(Exception):
  pass

class FontNotFound(PBPicException):
  def __init__(self,fname):
    PBPicException.__init__(self,'Font %s not found.' % fname)

class FontUnrecognized(PBPicException):
  def __init__(self,fd):
    PBPicException.__init__(self,'Font %s not in a known format.' % fd)
