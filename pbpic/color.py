class GrayColor:
  def __init__(self,g):
    self.g = g
    
  def renderto(self,r):
    r.setgray(self.g)

  def tex(self,name):
    return '\definecolor{%s}{rgb}{%g,%g,%g}' % (name,1-self.g,1-self.g,1-self.g)


  def __repr__(self):
    return 'GrayColor(%g)' % self.g
    
class RGBColor:
  def __init__(self,r,g,b,scale=1.):
    scale = float(scale)
    self.r=r/scale
    self.g=g/scale
    self.b=b/scale
  
  def renderto(self,r):
    r.setrgbcolor(self.r,self.g,self.b)

  def tex(self,name):
    return '\definecolor{%s}{rgb}{%g,%g,%g}' % (self.r,self.g,self.b)

  def __repr__(self):
    return 'RGBColor(%g,%g,%g)' % (self.r,self.g,self.b)

red = RGBColor(1,0,0)
green = RGBColor(0,1,0)
blue = RGBColor(0,0,1)
cyan = RGBColor(0,1,1)
magenta = RGBColor(1,0,1)
yellow = RGBColor(1,1,0)
black = GrayColor(1)
white = GrayColor(0)

periwinkle=RGBColor(69,66,142,scale=256)
burgundy=RGBColor(171,32,119,scale=256)
lime=RGBColor(33,177,50,scale=256)
