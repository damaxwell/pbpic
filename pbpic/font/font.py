from pbpic.geometry import Vector

class FontMetrics:
  def __init__(self,hadvance,vadvance,hsb,vsb):
    self.advance = Vector(hadvance,vadvance)
    self.sidebearing = Vector(hsb,vsb)

  def __repr__(self):
    return 'Metrics advance:%s sidebearing:%s' % (self.advance,self.sidebearing)