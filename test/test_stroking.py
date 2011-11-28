import pbpic as pbp
from pbpic import paths, color, cm, pt, loc
from pbpic.test.decorators import PngTest, TaciturnTest
import nose, math

@PngTest(w=6,h=3)
def TestStrokeColorGsave():
  """
  Test of recovery of linecolor after a gsave.
  """

  pbp.setlinewidth(1*pt)
  pbp.moveto(1.5,1.5)
  pbp.build(paths.ex,1)
  pbp.setlinecolor(color.red)

  with pbp.gsave():
    pbp.translate(3,0)
    pbp.moveto(1.5,1.5)
    pbp.build(paths.ex,1)
    pbp.setlinecolor(color.blue)
    with pbp.gsave():
      pbp.setlinecolor(color.green)
    pbp.stroke()

  pbp.stroke()

@PngTest(6,3)
def TestLineWidthRotate():
  """Test setting a rotated linewidth"""
  pen = 3*pt
  pbp.setlinewidth(pen)
  with pbp.ctmsave():
    pbp.translate(1.5,1.5)
    pbp.scale(1,0.5)
    pbp.moveto(0,0)
    pbp.build(paths.circle)
    pbp.stroke()

  pbp.translate(3,0)

  pen.units().scale(0.5,1)
  pen.units().rotate(1./8)
  pbp.setlinewidth(pen)
  with pbp.ctmsave():
    pbp.translate(1.5,1.5)
    pbp.scale(1,0.5)
    pbp.moveto(0,0)
    pbp.build(paths.circle)
    pbp.stroke()

@PngTest(5,5)
def TestStrokeWithAColor():
  """Test stroke(color)"""
  pbp.translate(loc.center)
  pbp.setlinewidth(0.2*cm)
  pbp.build(paths.circle,2,at=(0,0))
  pbp.stroke(color.red)


@PngTest(5,5)
def TestStrokeWidths():
  """Test setting various line widths as a width or a number.
  Also test that stroke(color) does not change the strokecolor.
  """
  pbp.translate(loc.center)
  pbp.setlinewidth(1*cm)
  pbp.build(paths.ex,at=(0,0))
  pbp.stroke()
  pbp.setlinewidth(0.5)
  pbp.build(paths.ex,at=(0,0))
  pbp.stroke(color.blue)

  pbp.setlinewidth(4*pt)
  pbp.build(paths.ex,at=(0,0))
  pbp.stroke(color.red)

  pbp.setlinewidth(1)
  pbp.build(paths.ex,at=(0,0))
  pbp.stroke()

@nose.tools.raises(ValueError)
@TaciturnTest(10,10)
def TestBadLinecap():
  pbp.setlinecap('foo')


@PngTest(6,4)
def TestLineCap():
  pbp.setlinewidth(12*pt)
  pbp.translate(3,1)
  for c in pbp.gstate.kLineCap:
    pbp.setlinecap(c)
    pbp.moveto(-2,0)
    pbp.rlineto(4,0)
    pbp.stroke()
    pbp.translate(0,1)

@PngTest(12,4)
def TestLineJoin():
  pbp.setlinewidth(8*pt)
  pbp.translate(2,2)
  pbp.setmiterlimit(10)
  r=.8
  for c in pbp.gstate.kLineJoin:
    with pbp.ctmsave():
      pbp.moveto(.4,-.5)
      pbp.lineto(-.4,-.5)
      pbp.translate(pbp.currentpoint())
      pbp.rotate(.25)
      pbp.lineto(.8,0)
    pbp.setlinejoin(c)
    pbp.stroke()
    pbp.translate(4,0)

@nose.tools.raises(ValueError)
@TaciturnTest(10,10)
def TestBadLinejoin():
  pbp.setlinejoin('foo')


@PngTest(6,3)
def TestMiterLimit():
  """The PostScript language reference manual says that if the 
  miterlimit is 10, then miters will be cut of at about 11 degrees.
  Tests making miters at 10 and 12 degrees to verify this."""
  theta = [ 10, 12]
  w = 1.;
  pbp.translate(1.5,1.5)
  pbp.translate(-w/2,0)
  pbp.setlinewidth(2*pt)
  pbp.setlinejoin('miter')
  pbp.setmiterlimit(10)
  for t in theta:
    pbp.moveto(w,0)
    pbp.lineto(0,0)
    with pbp.ctmsave():
      pbp.drotate(t)
      pbp.lineto(w,0)
    pbp.stroke()
    pbp.translate(3,0)

@nose.tools.raises(pbp.exception.BuildTransgression)
@TaciturnTest(1,1)
def TestNoBuild():
  def badbuilder(canvas):
    canvas.rlineto(1,1)
    canvas.stroke()
  pbp.moveto(0,0)
  pbp.build(badbuilder)
