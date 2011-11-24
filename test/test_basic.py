import pbpic as pbp
from pbpic import pt, cm, loc
from math import pi, sqrt
import cairo, os
from decorators import TaciturnTest

eps = 1e-6

def checksame(a,b):
  assert( (a-b).length()<eps )

@TaciturnTest(10,10)
def TestPointAndPagePoint():
  pbp.translate(5,5)

  # Page point converted to working coords
  p = pbp.pagePoint(1,3)
  checksame(pbp.point(p),pbp.point(1,3))

  # Page point defined in one coord system, expressed in another.
  with pbp.ctmsave():
    pbp.rotate(1./8)
    q = pbp.pagePoint(1,0)
  checksame( pbp.point(q), pbp.point(1/sqrt(2),1/sqrt(2)) ) 
  
  v = pbp.point(1.3,.9)
  with pbp.ctmsave():
    pbp.rotate(0.21)
    pbp.translate(1.1,0)
    pbp.scale(.1,.9)
    vv = pbp.point(v)
    assert(vv==v)

    e = pbp.point(pbp.pagePoint([0,0]))
    f = pbp.point([0,0])
    checksame(e,f)
    
    # Verify the center is the same as a point or page point, and
    # that they are the center.
    c = pbp.pagePoint(loc.center)
    d = pbp.point(loc.center)

    checksame(pbp.point(c), d)

@TaciturnTest(10,10)
def TestVectorAndPageVector():
  pbp.translate(5,5)

  with pbp.ctmsave():
    pbp.rotate(0.21)
    pbp.translate(1.1,0)
    pbp.scale(.1,.9)
  
    vl=[5,3]
    v=pbp.pageVector(vl)
    checksame(pbp.vector(v),pbp.vector(vl))

    vl=(2,9)
    v=pbp.pageVector(vl)
    checksame(pbp.vector(v),pbp.vector(vl))
    
    v=pbp.pageVector(-3*pt,0)
    w=pbp.vector(-3*pt,0)
    checksame(pbp.vector(v),w)

    v=pbp.pageVector(3*cm,4*pt)
    w=pbp.vector(3*cm,4*pt)
    checksame(pbp.vector(v),w)

    v=pbp.pageVector(3*cm,4)
    w=pbp.vector(3*cm,4)
    checksame(pbp.vector(v),w)
    
    v=pbp.vector(3*cm,[1,0])
    w=pbp.vector(3*cm,0)
    checksame(pbp.vector(v),w)

    v=pbp.pageVector(3*cm,[1,0])
    w=pbp.pageVector(3*cm,0)
    checksame(v,w)
    
  pbp.scaleto(1*cm)
  assert(abs(pbp.vector(v).length()-3)<eps)
  assert(abs(pbp.vector(w).length()-3)<eps)
