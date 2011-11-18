import pbpic as pbp
from pbpic import paths, color, cm, pt
from decorators import PngTest, TaciturnTest
import nose, math

@PngTest(w=3,h=3)
def TestInsetRotate():
  pbp.translate(1,1)
  pbp.rotate(.125)
  pbp.path() + (0,0) - (1,1)
  pbp.setlinewidth(0.5*cm)
  pbp.stroke()

  with pbp.inset() as i:
    pbp.scaleto(1*cm)
    pbp.path() + (0,0) - (1,1)
    pbp.setlinewidth(0.25*cm)
    pbp.stroke(color.red)
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas())


@PngTest(w=3,h=3)
def TestInsetRotate2():
  pbp.translate("center")
  pbp.rotate(.125)
  pbp.path() + (-.5,-.5) - (.5,.5)
  pbp.setlinewidth(0.5*cm)
  pbp.stroke()

  with pbp.inset(1*cm,1*cm) as i:
    pbp.scaleto(1*cm)
    pbp.path() + (0,0) - (1,1)
    pbp.setlinewidth(0.25*cm)
    pbp.stroke(color.red)
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas(),origin="center")


@PngTest(w=8,h=4)
def TestInsetWrite():
  pbp.setfont("Courier New")
  pbp.moveto(2,2)
  pbp.write("Hello.")


  with pbp.inset(4*cm,4*cm) as i:
    pbp.moveto("center")
    pbp.write("Hello.")

  pbp.translate(3,0)
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas())


@PngTest(w=8,h=4)
def TestInsetWriteRotate():
  pbp.setfont("Courier New")
  with pbp.gsave():
    pbp.translate(2,2)
    pbp.rotate(1/8.)
    pbp.moveto(0,0)
    pbp.write("Hello.")


  with pbp.inset() as i:
    pbp.moveto(0,0)
    pbp.write("Hello.")

  pbp.translate(3,0)
  pbp.moveto(2,2)
  pbp.rotate(1/8.)
  i.drawto(pbp.getcanvas())

