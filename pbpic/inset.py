from canvas import Canvas
from geometry import BBox, AffineTransform
from render_bbox import BBoxRenderer
from metric import pt
class Inset(Canvas):
  
  def __init__(self,*args):
    Canvas.__init__(self,*args)
    self.script=[]

  def drawto(self,canvas,origin=None):

    # If we have a named point, use it.  This will raise an exception if the point doesn't exist.
    if isinstance(origin,str):
      origin = self.pagemark(origin)
    # Otherwise, try looking for a point named 'origin'. It's ok if there isn't one.
    elif origin is None:
      try:
        origin = self.pagemark(origin)
      except KeyError:
        pass

    with canvas.gsave():
      if canvas.currentpointexists():
        p=canvas.currentpoint()
      else:
        p=(0,0)
      page_p = canvas.gstate.ctm.T(p)
      ptm = canvas.gstate.ptm
      device_p=ptm.T(page_p)
      canvas.pagetranslate(device_p)
      v=ptm.Tv(canvas.Tv((1,0)))
      canvas.pagerotate(v.angle())
      if not origin is None:
        canvas.pagetranslate(-(origin[0]),-(origin[1]))
      
      canvas.setctm(AffineTransform())
      
      canvas.newpath()
      # FIXME: shouldn't we set the canvas gstate so that it matches what the inset had at the start of its life?
      for f in self.script:
        args=f[1]; kwargs=f[2]
        fcn=canvas.__class__.__dict__[f[0]]
        fcn(canvas,*args,**kwargs)
      

  wrapped_methods = [ 'setlinewidth', 'setlinecolor', 'setlinecap', 'setlinejoin', 'setmiterlimit', 'setdash',
                      'setcolor', 'setrgbcolor', 'setgray', 'newpath',
                      'setctm',
                      'setfillcolor', 'setfillrule', 
                      'lineto', 'moveto', 'curveto', 'closepath', 
                      'rlineto', 'rmoveto', 
                      'kstroke', 'kfill', 'stroke', 'fill', 'clip', 'scaleto', 'scale', 'translate', 'gsave', 'grestore', 
                      'setphysicalfont', 'setfontsize', 'setfontangle', 'setfontcolor', 'setfonteffect',
                      'pagetranslate', 'pagerotate',
                      'showglyphs', 'rotate' ]

  template = '''def %s(self,*args,**kwargs): 
                   self.script.append(('%s',args,kwargs)); 
                   return Canvas.%s(self,*args,**kwargs)'''

  for m in wrapped_methods:
    filled_template = template % (m,m,m)
    exec filled_template in globals(), locals()

  def __repr__(self):
    s=''
    for c in self.script:
      s += str(c)
      s += '\n'
    return s
    
  def setextents(self,bbox):
    if bbox is None:
      self._extents = None
    else:
      self._extents=bbox.copy()
    self.markedpoints.setbbox(self._extents)

  def markedbox(self):
    c = Canvas()
    r=BBoxRenderer()
    c.begin(renderer=r)
    c.draw(self)
    return r.bbox()
