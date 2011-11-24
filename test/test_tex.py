import pbpic as pbp
from pbpic import paths, color, cm, pt, loc
from pbpic.test.decorators import PngTest, TaciturnTest
import nose, math

@PngTest(w=3,h=3)
def TestTexHello():
  pbp.translate(loc.center)
  with pbp.ctmsave():
    pbp.scaleto(1*pt)
    pbp.draw(pbp.paths.circle,1.,at=(0,0))
  pbp.fill(color.red)
  pbp.moveto(0,0)
  pbp.placetex("Hello")
  pbp.pbpend()
