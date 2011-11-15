import pbpic as pbp
from pbpic import paths, color, cm, pt
from decorators import PngTest, TaciturnTest
import nose

@PngTest(w=6,h=3)
def TestStrokeColorGsave():
  """
  Test of recovery of linecolor after a gsave.
  """

  pbp.setlinewidth(1*pt)
  pbp.moveto(1.5,1.5)
  pbp.draw(paths.ex,1)
  pbp.setlinecolor(color.red)

  with pbp.gsave():
    pbp.translate(3,0)
    pbp.moveto(1.5,1.5)
    pbp.draw(paths.ex,1)
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
    pbp.draw(paths.circle)
    pbp.stroke()

  pbp.translate(3,0)

  pen.scale(0.5,1)
  pen.rotate(1./8)
  pbp.setlinewidth(pen)
  with pbp.ctmsave():
    pbp.translate(1.5,1.5)
    pbp.scale(1,0.5)
    pbp.moveto(0,0)
    pbp.draw(paths.circle)
    pbp.stroke()

@PngTest(5,5)
def TestStrokeWithAColor():
  """Test stroke(color)"""
  pbp.translate('center')
  pbp.setlinewidth(0.2*cm)
  pbp.draw(paths.circle,2,at=(0,0))
  pbp.stroke(color.red)


@PngTest(5,5)
def TestStrokeWidths():
  """Test setting various line widths as a width or a number.
  Also test that stroke(color) does not change the strokecolor.
  """
  pbp.translate('center')
  pbp.setlinewidth(1*cm)
  pbp.draw(paths.ex,at=(0,0))
  pbp.stroke()
  pbp.setlinewidth(0.5)
  pbp.draw(paths.ex,at=(0,0))
  pbp.stroke(color.blue)

  pbp.setlinewidth(4*pt)
  pbp.draw(paths.ex,at=(0,0))
  pbp.stroke(color.red)

  pbp.setlinewidth(1)
  pbp.draw(paths.ex,at=(0,0))
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
      print 'path'
      pbp.moveto(.4,-.5)
      pbp.lineto(-.4,-.5)
      pbp.translate(pbp.currentpoint())
      pbp.rotate(.25)
      pbp.lineto(.8,0)
    print 'setlinejoin'
    pbp.setlinejoin(c)
    print 'stroke'
    pbp.stroke()
    pbp.translate(4,0)

@nose.tools.raises(ValueError)
@TaciturnTest(10,10)
def TestBadLinejoin():
  pbp.setlinejoin('foo')


