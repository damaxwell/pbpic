import pbpic as pbp
from pbpic import loc, paths, color, cm, pt, geometry
from pbpic.test.decorators import PngTest, TaciturnTest
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
  print i
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas())


@PngTest(w=3,h=3)
def TestInsetRotate2():
  pbp.translate(loc.center)
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
  i.drawto(pbp.getcanvas(),origin=loc.center)


@PngTest(w=8,h=4)
def TestInsetWrite():
  pbp.setfont("Courier New")
  pbp.moveto(2,2)
  pbp.write("Hello.")


  with pbp.inset(4*cm,4*cm) as i:
    pbp.moveto(loc.center)
    pbp.write("Hello.")

  print i
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

@PngTest(8,4)
def TestInsetInInset():
  with pbp.ctmsave():
    pbp.scaleto(1*cm)
    pbp.draw(paths.grid,box=pbp.extents(),N=4,M=8,at=(0,0))
    pbp.stroke(color.GrayColor(0.2))

  with pbp.inset(1*cm,1*cm) as i1:
    pbp.scaleto(1*cm)
    pbp.draw(pbp.extents())
    with pbp.gsave():
      pbp.stroke()
    pbp.clip()
    pbp.translate(loc.center)
    pbp.rotate(1/8.)
    w=.25; h=.33
    pbp.moveto(-w/2,-h/2)
    pbp.draw(paths.rect,w,h)
    pbp.fillstroke(fillcolor=color.blue)

  pbp.scaleto(1*cm)
  pbp.translate(2,2)
  pbp.moveto(0,0)
  i1.drawto(pbp.getcanvas(),origin=loc.center)
  
  pbp.translate(4,0)  
  with pbp.inset(2*cm,2*cm) as i2:
    pbp.moveto(loc.center)
    with pbp.ctmsave():
      pbp.rotate(1/8.)
      i1.drawto(i2,origin=loc.center)
    pbp.draw(pbp.extents())
    pbp.stroke()

  pbp.moveto(0,0)
  i2.drawto(pbp.getcanvas(),origin=loc.center)

@PngTest(6,3)
def TestInsetLinewidth():
  pbp.scaleto(1*cm)
  with pbp.inset(1*cm,1*cm) as i:
    pbp.scaleto(1*cm)
    linewidth=4*pt
    linewidth.units().scale(0.5,1)
    print linewidth
    pbp.setlinewidth(linewidth)
    pbp.draw(paths.rect,w=1,h=1,at=(0,0))
    pbp.stroke()
  pbp.translate(1.5,1.5)
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas(),origin=loc.center)

  pbp.translate(3,0)
  pbp.rotate(1/8.)
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas(),origin=loc.center)


@PngTest(6,3)
def TestInsetFontsize():
  pbp.scaleto(1*cm)
  with pbp.inset(1*cm,1*cm) as i:
    pbp.scaleto(1*cm)
    fontsize=24*pt
    fontsize.units().scale(0.5,1)
    pbp.setfontsize(fontsize)
    pbp.moveto(loc.center)
    pbp.setfont("Courier New")
    pbp.write("Hi.")
  pbp.translate(1.5,1.5)
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas(),origin=loc.center)

  pbp.translate(3,0)
  pbp.rotate(1/8.)
  pbp.moveto(0,0)
  i.drawto(pbp.getcanvas(),origin=loc.center)
  

@PngTest(16,8)
def TestInsetBorderSquare():
  v = [ [geometry.Vector(0.3,1), geometry.Vector(-0.3,1),geometry.Vector(0.3,-1),geometry.Vector(-0.3,-1)],
        [geometry.Vector(1,.3), geometry.Vector(1,-0.3),geometry.Vector(-1,0.3),geometry.Vector(-1,-0.3)] ]
  pbp.scaleto(1*cm)
  pbp.moveto(4,0)
  pbp.draw(paths.vlines,8,4,3)
  pbp.moveto(0,4)
  pbp.draw(paths.hlines,16,4,1)
  pbp.stroke()

  pbp.translate(2,2)
  
  for k in range(2):
    for l in range(4):
      w=v[k][l]
      with pbp.ctmsave():
        pbp.translate(l*4,k*4)
        
        with pbp.ctmsave():
          pbp.scaleto(1*pt)
          pbp.draw(paths.circle,3,at=(0,0))
          pbp.fill(color.red)

        with pbp.inset(1*cm,1*cm) as i:    
          pbp.scaleto(1*cm)
          pbp.moveto(loc.ll)
          pbp.draw(paths.rect,1,1)
          with pbp.gsave():
            pbp.clip()
            pbp.moveto(loc.center)
            pbp.draw(paths.ex)
            pbp.stroke()

            pbp.setlinewidth(1.5)
            pbp.moveto(loc.center)
            pbp.lineto(loc.border(w)(i))
            pbp.stroke()

          pbp.stroke() # Outer square border

        pbp.moveto(0,0)
        i.drawto(pbp.getcanvas(),origin=loc.border(w))

        with pbp.gsave():
          pbp.scaleto(1*cm)
          pbp.moveto(0,0)
          pbp.setlinewidth(0.5)
          if k==0:
            pbp.rlineto(-w/abs(w.y)*0.5)
          else:
            pbp.rlineto(-w/abs(w.x)*0.5)          
          pbp.stroke(color.yellow)

