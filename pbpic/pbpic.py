from __future__ import division

import canvas
import inspect
import os
import logging
from metric import pt, cm, inch, Polar, FPolar, DPolar, Point, Vector
from color import RGBColor, GrayColor
import color
from inset import Inset
from geometry import AffineTransform, BBox
from style import Style, style, setstyle, stylesave, stylerestore
import texinset
from math import pi


_canvas = None
_finalcanvas = None

template = 'def %s(*args,**kwargs): global _canvas; return _canvas.%s(*args,**kwargs)'
functions = [ 'setlinewidth', 'setlinecolor', 'setlinecap', 'setlinejoin', 'setmiterlimit', 'setdash',
              'setfillcolor', 'setfillrule',
              'setfontangle', 'setfontcolor', 'setfonteffect',
              'setcolor', 'setrgbcolor', 'setgray', 'path', 'newpath',
              'lineto', 'moveto', 'rmoveto', 'rlineto', 'curveto', 'polygon', 'closepath', 'stroke', 'kstroke', 
              'fill', 'kfill', 'clip', 'scaleto', 'scale', 'window', 'translate', 'ctmsave', 'gsave', 'grestore', 'setphyscialfont', 
              'showglyphs', 'rotate', 'frotate', 
              'pagetranslate', 'pagerotate', 'pagescale',
              'setfont', 'setfontsize', 'findfont', 'show', 'stringwidth', 'offset', 'point',
              'draw', 'place', 'bbox', 'addpath', 'charpath', 'ctm', 'mark', 'pagemark', 'local', 'marks', 'applystyle', 'currentpoint', 'extents' ]
for f in functions:
  filled_template = template % (f,f)
  exec filled_template in globals()

_rendertypes={'pdf':('render_pdf','PDFRenderer'), 'eps':('render_eps','EPSRenderer')}

def getcanvas():
  global _canvas
  return _canvas

  
def pbpbegin(w=None,h=None,target=None,bbox=None):
  global _canvas,_finalcanvas
  global _rendertypes

  if not(_canvas is None):
    logging.warning('Overwriting current canvas with a pbpbegin(). Did you forget to pbpend()?')

  renderer = None
  if isinstance(target,str):
    rendertype = _rendertypes.get(target,None)
    if not rendertype is None:
      frm = inspect.stack()[1]
      filename = inspect.getmodule(frm[0]).__file__
      filename = os.path.splitext(filename)[0] + "." + target
    else:
      # We have a filename.  Determine the renderer from its extension.
      filename = target
      ext = os.path.splitext(filename)[1][1:]
      rendertype = _rendertypes.get(ext,None)

    if rendertype is None:
      print 'Unable to determine a renderer for %s. Drawing to an Inset instead.' % target
      _canvas = Inset(w,h)
      return
    else:
      command = 'import %s;renderer=%s.%s("%s")' % (rendertype[0],rendertype[0],rendertype[1],filename)      
      exec command
  else:
    # Assume we have a renderer
    renderer = target

  if renderer is None:
    _canvas = Inset(w,h,bbox)
  elif (w is None) and (h is None) and (bbox is None):
    _canvas = Inset()
    _finalcanvas=canvas.Canvas(renderer=renderer)
  else:
    _canvas=canvas.Canvas(w=w,h=h,bbox=bbox,renderer=renderer)

  _canvas.begin()
  
  # If default styles have been set, we apply them at the start of the page.  Maybe this is a bad idea.
  applystyle()



def pbpend():
  global _canvas, _finalcanvas
  
  # FIXME: check that we have popped everything off of the canvas stack?
  _canvas.end()

  rv = _canvas
  if not _finalcanvas is None:
    # The top canvas should be an inset.  Determine its bounding box, set the boundingbox of the cavnas, and do a simple draw.
    bbox = _canvas._extents
    if bbox is None:
      bbox=_canvas.markedbox()
    _finalcanvas.begin(bbox=bbox)
    _finalcanvas.draw(_canvas)
    _finalcanvas.end()
    rv = _finalcanvas
    
  _canvas=None
  _finalcanvas=None
  return rv

begin=pbpbegin
end=pbpend

def inset(*args,**kwargs):
  return InsetGuard(*args,**kwargs)

_canvasstack = []
_canvas = None
def pushcanvas(c):
  global _canvas, _canvasstack
  _canvasstack.append(_canvas)
  _canvas = c

def popcanvas():
  global _canvas, _canvasstack
  _canvas = _canvasstack.pop()

class InsetGuard:
  def __enter__(self,*args,**kwargs):
    global _canvas
    self.i = Inset(*args,**kwargs)
    self.i.begin()
    _canvas.gstate.copystyle(self.i)
    pushcanvas(self.i)
    return self.i
    
  def __exit__(self,*args):
    self.i.end()
    popcanvas()
    return False

def text(s):
  with inset() as i:
    moveto(0,0)
    show(s)
  i.setextents(i.markedbox())
  return i

def placetex(text,*args,**kwargs):
  i = texinset.texinset(text)
  place(i,*args,**kwargs)
