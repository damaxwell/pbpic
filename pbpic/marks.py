from style import Style, updatefromstyle
from metric import pt
import paths

class Dot:

  @staticmethod
  def defaultStyle():
    return Style('mark',size=1*pt)

  def __init__(self,**kwargs):
    updatefromstyle(self,('size',),'mark',kwargs)

  def drawto(self,canvas):
    with canvas.ctmsave():
      canvas.translate(canvas.currentpoint())
      canvas.scaleto(0.5*self.size)
      canvas.addpath(paths.circle,1)
      canvas.fill()
