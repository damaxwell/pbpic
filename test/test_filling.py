import pbpic as pbp
from pbpic import paths, color, cm, pt, loc
from pbpic.test.decorators import PngTest, TaciturnTest
import nose

@PngTest(10,5)
def TestFillWithAColor():
  """Test fill(color)"""
  pbp.translate(2.5,2.5)
  pbp.setlinewidth(0.2*cm)
  pbp.draw(paths.circle,2,at=(0,0))
  pbp.kfill(color.red)
  pbp.stroke()

  pbp.translate(5,0)
  pbp.draw(paths.circle,2,at=(0,0))
  pbp.fillstroke(fillcolor=color.red)

@PngTest(2,2)
def TestFillColorGSave():
  """Test stroke(color)"""
  pbp.scaleto(1*cm)
  pbp.translate(loc.center)
  pbp.setlinewidth(0.2*cm)
  pbp.draw(paths.circle,0.5,at=(0,0))
  with pbp.gsave():
    pbp.draw(paths.circle,0.8,at=(0,0))
    pbp.setfillcolor(color.green)
    pbp.fill()
  pbp.fill()

def pent(c,r=1):
  with c.ctmsave():
    c.translate(c.currentpoint())
    c.rotate(1./4)
    p=c.point(r,0)
    c.moveto(p)
    for k in range(4):
      c.rotate(2./5)
      c.lineto(p)
    c.closepath()

@PngTest(4,2)
def TestFillRule():
  r = 0.9
  pbp.translate(1,1)
  pbp.draw(pent,r=r,at=(0,0))
  pbp.setfillrule('evenodd')
  pbp.fill(color.blue)

  pbp.translate(2,0)
  pbp.draw(pent,r=r,at=(0,0))
  pbp.setfillrule('winding')
  pbp.fill(color.green)

@PngTest(4,2)
def TestFillRuleGsave():
  r = 0.9
  pbp.translate(1,1)
  pbp.setfillrule('evenodd')
  with pbp.gsave():
    pbp.draw(pent,r=r,at=(0,0))
    pbp.setfillrule('winding')
    pbp.fill(color.blue)

  pbp.translate(2,0)
  pbp.draw(pent,r=r,at=(0,0))
  pbp.fill(color.green)

@PngTest(4,2)
def TestFillRuleInit():
  r = 0.9
  pbp.translate(1,1)
  pbp.draw(pent,r=r,at=(0,0))
  pbp.fill(color.blue)

  pbp.translate(2,0)
  pbp.setfillrule('evenodd')
  pbp.draw(pent,r=r,at=(0,0))
  pbp.fill(color.green)

@nose.tools.raises(ValueError)
@TaciturnTest(10,10)
def TestBadFillRule():
  pbp.setfillrule('eveneven')

@PngTest(4,4)
def TestClip():
  pbp.translate(loc.center)

  pbp.setlinewidth(3*pt)
  pbp.draw(paths.circle,1.5,at=(0,0))
  pbp.stroke(color.red)

  pbp.draw(paths.circle,1.5,at=(0,0))
  pbp.clip()
  pbp.draw(paths.square,L=2,at=(1,1))
  pbp.fill(color.blue)

  pbp.setlinewidth(3.1*pt)
  pbp.draw(paths.circle,1.5,at=(0,0))
  pbp.stroke()
