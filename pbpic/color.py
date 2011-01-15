class GrayColor:
  def __init__(self,g):
    self.g = g
    
  def renderto(self,r):
    r.setgray(self.g)
    
class RGBColor:
  def __init__(self,r,g,b):
    self.r=r
    self.g=g
    self.b=b
  
  def renderto(self,r):
    r.setrgbcolor(self.r,self.g,self.b)

red = RGBColor(1,0,0)
green = RGBColor(0,1,0)
blue = RGBColor(0,0,1)
black = GrayColor(1)