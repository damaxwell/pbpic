import pbpic as pbp
from pbpic import pt, cm, loc
from pbpic.test.decorators import TaciturnTest
import nose

@nose.tools.raises(pbp.exception.StackUnderflow)
@TaciturnTest(5,5)
def TestDrawGstateUnderflow():
  def drawer(c):
    with c.gsave():
      c.lineto(1,1)
      c.stroke()
    c.grestore()

  pbp.moveto(pbp.loc.center)
  pbp.draw(drawer)

@TaciturnTest(5,5)
def TestDrawGstateNoUnderflow():
  def drawer(c):
    with c.gsave():
      c.lineto(1,1)
      c.stroke()

  pbp.moveto(pbp.loc.center)
  pbp.draw(drawer)
