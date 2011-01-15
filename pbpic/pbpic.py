from __future__ import division

import canvas
import inspect
import os
import logging
from metric import pt, cm, inch, Polar, FPolar, DPolar, Vector
from color import RGBColor, GrayColor
import color
from inset import Inset

_canvas = None

template = 'def %s(*args,**kwargs): global _canvas; return _canvas.%s(*args,**kwargs)'
functions = [ 'setlinewidth', 'setcolor', 'setrgbcolor', 'setgray', 'path', 'newpath',
              'lineto', 'moveto', 'polygon', 'closepath', 'stroke', 
              'kstroke', 'scaleto', 'scale', 'translate', 'gsave', 'grestore', 'setphyscialfont', 
              'showglyphs', 'textpoint', 'settextpoint', 'rotate', 'frotate', 
              'setfont', 'findfont', 'show', 'stringwidth', 'offset', 'point',
              'place', 'bbox', 'addpath', 'charpath', 'ctm', 'mark', 'pagemark', 'placetex' ]
for f in functions:
  filled_template = template % (f,f)
  exec filled_template in globals()

_rendertypes={'pdf':('render_pdf','PDFRenderer')}

def getcanvas():
  global _canvas
  return _canvas

  
def begin(w=None,h=None,target=None):
  global _canvas
  global _rendertypes

  if not(_canvas is None):
    logging.warning('Overwriting current canvas with a begin(). Did you forget to finish()?')

  if target is None:
    _canvas = inset.Inset(w,h)
    return

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
# render_pdf.PDFRenderer(filename)      BUILD ONE
  else:
    # Assume we have a renderer
    renderer = target

  _canvas=canvas.Canvas(w,h)
  _canvas.begin(renderer)

def end():
  global _canvas
  _canvas.end()
  _canvas=None


def inset():
  return InsetGuard()

_canvasstack = []
def pushcanvas(c):
  global _canvas, _canvasstack
  _canvasstack.append(_canvas)
  _canvas = c

def popcanvas():
  global _canvas, _canvasstack
  _canvas = _canvasstack.pop()

class InsetGuard:
  def __enter__(self):
    global _canvas
    self.i = Inset()
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
    settextpoint(0,0)
    show(s)
  i.setextents(i.markedbox())
  return i

def placetex(self,text,*args,**kwargs):
  i = texinset(text)
  place(i,*args,**kwargs)
