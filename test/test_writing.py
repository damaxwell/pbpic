import pbpic as pbp
from pbpic import paths, color, cm, pt
from decorators import PngTest, TaciturnTest

@PngTest(3,3)
def TestWrite():
  pbp.moveto("center")
  pbp.setfont("Courier New")
  pbp.write("Abc")
  pbp.moveto("center")
  pbp.setwritingvector([0,1])
  pbp.write("Abc")


@PngTest(2,2)
def TestFontSize():
  fontsize=20
  pbp.moveto("center")
  pbp.rmoveto(-.9,0)
  pbp.setfont("Courier New")
  pbp.setfontsize(fontsize*pt)
  pbp.write("ABC")

  pbp.setlinewidth(1*pt)
  pbp.moveto("center")
  pbp.rmoveto(-.9,0)
  pbp.scaleto(1*pt)
  pbp.draw(paths.rect,fontsize,fontsize)
  pbp.stroke()

@PngTest(2,2)
def TestFontSquash():
  fontsize=12*pt
  fontsize.units().scale(1.,0.5)
  pbp.setwritingvector([1,1])
  pbp.moveto("center")
  pbp.setfont("Courier New")
  pbp.setfontsize(fontsize)
  pbp.write("ABC")
  pbp.moveto("center")
  pbp.rmoveto(0,-12*pt)
  pbp.setwritingvector([1,0])
  pbp.write("ABC")
  
@PngTest(2,2)
def TestFontColor():
  pbp.moveto("center")
  pbp.setfont("Courier New")
  pbp.setfontcolor(color.red)
  pbp.write("Q")

@PngTest(3,3)
def TestWritingVector():
  pbp.moveto("center")
  pbp.setfont("Optima Regular")
  pbp.setwritingvector([1,1])
  pbp.write("David")
  pbp.moveto("center")
  pbp.rmoveto(0,-12*pt)
  pbp.setwritingvector([1,0])
  pbp.write("David")
  


@PngTest(2,2)
def TestFontRotate():
  pbp.moveto("center")
  with pbp.gsave():
    pbp.scaleto(1*pt)
    pbp.draw(paths.circle,.5)
    pbp.fill()

  pbp.setfont("Courier New")
  right = pbp.pageVector([1,0])
  pbp.rotate(1./7)
  pbp.write("Q")
  with pbp.gsave():
    pbp.scaleto(1*pt)
    pbp.draw(paths.circle,.5)
    pbp.fill()
  pbp.setwritingvector(right)
  pbp.write("Q")
  with pbp.gsave():
    pbp.scaleto(1*pt)
    pbp.draw(paths.circle,.5)
    pbp.fill()
  pbp.setwritingvector([0,-1])
  pbp.write("Q")

