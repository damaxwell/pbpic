from canvas import Canvas
from geometry import BBox
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
        canvas.translate(canvas.currentpoint())
      canvas.scaleto(1*pt)
      # canvas.gstate.ctm.makeortho() # FIXME This is rude -- modifying the gstate of a different canvas directly

      if not origin is None:
        canvas.translate(-(origin[0]),-(origin[1]))

      canvas.newpath()  
      # FIXME: shouldn't we set the canvas gstate so that it matches what the inset had at the start of its life?
      for f in self.script:
        args=f[1]; kwargs=f[2]
        fcn=canvas.__class__.__dict__[f[0]]
        fcn(canvas,*args,**kwargs)


  wrapped_methods = [ 'setlinewidth', 'setlinecolor', 'setlinecap', 'setlinejoin', 'setmiterlimit', 'setdash',
                      'setcolor', 'setrgbcolor', 'setgray', 'newpath',
                      'setfillcolor', 'setfillrule', 
                      'lineto', 'moveto', 'curveto', 'closepath', 
                      'kstroke', 'kfill', 'stroke', 'fill', 'scaleto', 'scale', 'translate', 'gsave', 'grestore', 'setphysicalfont', 
                      'setfontsize', 'showglyphs', 'rotate', 'setfont' ]

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
    print 'setextentds %s' % bbox
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
