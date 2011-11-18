from canvas import Canvas
from geometry import BBox, AffineTransform
from render_bbox import BBoxRenderer
from metric import pt
class Inset(Canvas):
  
  def __init__(self,*args):
    Canvas.__init__(self,*args)
    self.script=[]

  def drawto(self,canvas,origin=None):

    # Build the map from page to 'device' coordinates
    ptm = canvas.gstate.ptm

    page_cp=canvas.pagePoint(canvas.currentpoint())
    device_cp = ptm.T(page_cp)
    
    tm = AffineTransform()
    tm.translate(device_cp[0],device_cp[1])
    
    v=ptm.Tv(canvas.pageVector((1,0)))
    tm.rrotate(v.angle())
    
    if origin is not None:
      origin = self.pagePoint(origin)
      tm.translate(-origin[0],-origin[1])

    with canvas.gsave():
      
      canvas.pageconcat(tm)

      canvas.setctm(AffineTransform())
      
      canvas.newpath()
      # FIXME: shouldn't we set the canvas gstate so that it matches what the inset had at the start of its life?
      for f in self.script:
        args=f[1]; kwargs=f[2]
        fcn=canvas.__class__.__dict__[f[0]]
        fcn(canvas,*args,**kwargs)
      

  wrapped_methods = [ 'scaleto', 'scale', 'rotate', 'rrotate', 'drotate', 'setctm',
                      'gsave', 'grestore',
                      'setlinewidth', 'setlinecap', 'setlinejoin', 'setmiterlimit', 
                      'kstroke', 'kfill', 'clip', 'setfillrule',
                      'newpath', 
                      'translate', 'moveto', 'lineto', 'curveto', 'rmoveto', 'rlineto', 
                      'closepath',
                      'setlinecolor', 'setfillcolor',
                      'setfontsize', 'setwritingvector', 'setfontcolor',
                      'showglyphs' ]

  template = '''def %s(self,*args,**kwargs): 
                   self.script.append(('%s',args,kwargs)); 
                   return Canvas.%s(self,*args,**kwargs)'''

  for m in wrapped_methods:
    filled_template = template % (m,m,m)
    exec filled_template in globals(), locals()

  def translate(self,*args):
    p=self.point(*args)
    self.script.append('translate',p,{})
    return Canvas.translate(self,p)

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
    # self.markedpoints.setbbox(self._extents)

  def markedbox(self):
    c = Canvas()
    r=BBoxRenderer()
    c.begin(renderer=r)
    c.draw(self)
    return r.bbox()
