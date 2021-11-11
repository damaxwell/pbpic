from . import canvas
from .inset import Inset
import inspect, os
from .pbptex import texinset
import logging


# In the event that the extents of _canvas are not known when
# it is created, _canvas will be an Inset.  At the end,
# we then draw it into the _finalcanvas, which knows about the
# actual renderer to be used.
_finalcanvas = None

template = 'def %s(*args,**kwargs): return canvas._canvas.%s(*args,**kwargs)'
functions = [ 'scale', 'scaleto', 'translate', 'rotate', 'rrotate', 'drotate', 'ctmconcat',  'window', # methods that affect the CTM
              'setlinewidth', 'linewidth', 'setlinecolor', 'linecolor',  # methods that affect the line state 
              'setlinecap', 'linecap', 'setlinejoin', 'linejoin', 'setdash', 'dash',
              'setmiterlimit', 'miterlimit',
              'setfillcolor', 'fillcolor', 'setfillrule', 'fillrule',    # methods that affect fill state
              'gsave', 'grestore', 'ctmsave', 'ctmrestore',              # methods that affect save/restore
              'stroke', 'kstroke', 'fill', 'kfill', 'fillstroke',        # methods that stroke or fill
              'clip',                                                    # clipping path
              'currentpointexists', 'currentpoint', 'currentpath',      # current point/path
              'newpath', 'moveto', 'lineto', 'closepath',                # path construction
              'curveto', 'vcurveto',
              'rmoveto', 'rlineto',
              'write', 'setfont', 
              'setfontsize', 'fontsize', 'setwritingvector', 'writingvector',
              'setfontcolor', 'fontcolor',
              'charpath','stringwidth',             # font
              'build', 'draw', 'path',                                                   # high level path
              'point', 'vector', 'pagePoint', 'pageVector',             # point/vector transformations
              'extents', 'markpoint', 'getmark', 'addmarks' ]                                               # introspection

for f in functions:
  filled_template = template % (f,f)
  exec(filled_template, globals())

_rendertypes={'pdf':('render_cairo','PDFRenderer'), 'png':('render_cairo','PNGRenderer')}

def setrenderer(ext,render_desc):
  """Sets the renderer to be used for files with extension :ext:.  The :render_desc:
  should be the class of the renderer to use."""
  # We also allow a tuple of strings ("module","class") so that we can have provide
  # default renderers based on cairo, but not insist that cairo be installed.
  # By describing the default renderer using strings, we will not 
  # load cairo as a part of starting up pbpic.
  _rendertypes[ext]=render_desc

def getrenderer(ext):
  return _rendertypes[ext]


def pbpbegin(w=None,h=None,target=None):
  global _finalcanvas
  global _rendertypes
  
  c=canvas.getcanvas()
  if not(c is None):
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
      print('Unable to determine a renderer for %s. Drawing to an Inset instead.' % target)
      canvas.pushcanvas(Inset(w,h))
      return
    else:
      # The rendertype with either be a class for the renderer, or a tuple (modulename,classname)
      # of strings describing the renderer's class.
      if isinstance(rendertype,tuple):
        namespace = {}
        command = 'from .%s import %s as RendererClass' % (rendertype[0],rendertype[1])
        exec( command,None,namespace)
        RendererClass = namespace["RendererClass"]
      else:
        RendererClass=rendertype
      renderer=RendererClass(filename)
  else:
    # Assume we have a renderer
    # FIXME: check that the target is indeed a renderer?
    renderer = target

  if renderer is None:
    canvas.pushcanvas(Inset(w,h))
  elif (w is None) or (h is None):
    canvas.pushcanvas( Inset(w,h) )
    _finalcanvas=canvas.Canvas(renderer=renderer)
  else:
    canvas.pushcanvas( canvas.Canvas(w=w,h=h,renderer=renderer) )

  canvas.getcanvas().begin()

def pbpend():
  global _finalcanvas

  c=canvas.getcanvas()
  if c is None:
    print('No current canvas to end with pbpend.')
    return

  # FIXME: check that we have popped everything off of the canvas stack?
  c.end()

  rv = c
  if not _finalcanvas is None:
    # The top canvas should be an inset.  Determine its bounding box, set the boundingbox of the cavnas, and do a simple draw.
    bbox = c._extents
    if bbox is None:
      bbox=c.markedbox()
    _finalcanvas.begin(bbox=bbox)
    _finalcanvas.draw(c)
    _finalcanvas.end()
    rv = _finalcanvas
  canvas.popcanvas()
  _finalcanvas=None
  return rv

def inset(*args,**kwargs):
  return InsetGuard(*args,**kwargs)

class InsetGuard:
  def __init__(self,*args,**kwargs):
    self.i_args = args
    self.i_kwargs = kwargs

  def __enter__(self):
    self.i = Inset(*self.i_args,**self.i_kwargs)
    # self.i.begin()
    canvas.getcanvas().gstate.copystyle(self.i)
    canvas.pushcanvas(self.i)
    return self.i

  def __exit__(self,*args):
    # self.i.end()
    canvas.popcanvas()
    return False

def drawtex(text,*args,**kwargs):
  c=canvas.getcanvas()
  i = texinset(text)
  if not kwargs.has_key('origin'):
    kwargs['origin']='origin'
  i.drawto(c,**kwargs)

