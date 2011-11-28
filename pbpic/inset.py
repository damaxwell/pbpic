from canvas import Canvas
from geometry import BBox, AffineTransform
from render_bbox import BBoxRenderer
from metric import pt, PagePoint
import mark

class Inset(Canvas):
  
  def __init__(self,w=None, h=None,init=None):
    Canvas.__init__(self,w=w,h=h)
    self.script=[]
    if init is not None:
      init.gstate.copystyle(self)
      self.gstate.ctm = init.gstate.ctm.copy()

  # begin/end don't seem to make sense for an inset.  Or much else
  # for that matter.
  def begin(self):
    raise NotImplementedError()

  def end(self):
    raise NotImplementedError()

  def markup(self,canvas,name='inset',origin=None):
    with canvas.ctmsave():
      canvas.translate(canvas.currentpoint())
      canvas.scaleto(1*pt)
      if origin is not None:
        origin = self.pagePoint(origin)
        canvas.translate(-origin[0],-origin[1])
      last_ctm = canvas.gstate.ctm.copy()

    m=mark.NamedMarks()
    for (k,p) in self.marks[0]:
      m.addpoint(k,PagePoint(last_ctm.T(p[0],p[1])))

    canvas.marks.append(mark.SubNamedMarks(m,name))

  def drawto(self,canvas,origin=None,marks=None):
    if marks is not None:
      self.markup(canvas,name=marks,origin=origin)

    with canvas.gsave():
      canvas.translate(canvas.currentpoint())
      canvas.scaleto(1*pt)
      if origin is not None:
        origin = self.pagePoint(origin)
        canvas.translate(-origin[0],-origin[1])
      self.last_ctm = canvas.gstate.ctm.copy()

      stm=AffineTransform()
      w=canvas.pageVector(1,0)
      stm.rotate(w.angle())
      canvas.sizeconcat(stm)

      canvas.newpath()
      # FIXME: shouldn't we set the canvas gstate so that it matches what the inset had at the start of its life?
      for f in self.script:
        args=f[1]; kwargs=f[2]
        fcn=canvas.__class__.__dict__[f[0]]
        fcn(canvas,*args,**kwargs)

  wrapped_methods = [ 'gsave', 'grestore', 'ctmsave', 'ctmrestore',
                      'setlinewidth', 'setlinecap', 'setlinejoin', 'setmiterlimit', 'setdash',
                      'kstroke', 'kfill', 'clip', 'setfillrule',
                      'newpath', 
                      'closepath',
                      'setlinecolor', 'setfillcolor',
                      'setfontsize', 'setwritingvector', 'setfontcolor',
                      'showglyphs',
                      'sizeconcat' ]

  template = '''def %s(self,*args,**kwargs): 
                   self.script.append(('%s',args,kwargs)); 
                   return Canvas.%s(self,*args,**kwargs)'''

  for m in wrapped_methods:
    filled_template = template % (m,m,m)
    exec filled_template in globals(), locals()

  def  moveto(self,*args):
    p=self.pagePoint(*args)
    self.script.append(('moveto',(p[0],p[1]),{}))
    return Canvas.moveto(self,p)
  
  def  lineto(self,*args):
    p=self.pagePoint(*args)
    self.script.append(('lineto',(p[0],p[1]),{}))
    return Canvas.lineto(self,p)

  def curveto(self,*args):
    if len(args) == 6:
      q = (self.pagePoint(args[0],args[1]),self.pagePoint(args[2],args[3]),self.pagePoint(args[4],args[5]))
    elif len(args) == 3:
      q = [self.pagePoint(p) for p in args]
    else:
      raise ValueError()
    self.script.append(('curveto',(q[0][0],q[0][1],q[1][0],q[1][1],q[2][0],q[2][1]),{}))
    self.gstate.path.curveto(q[0],q[1],q[2])

  def  rmoveto(self,*args):
    p=self.pageVector(*args)
    self.script.append(('rmoveto',(p[0],p[1]),{}))
    return Canvas.rmoveto(self,p)

  def  rlineto(self,*args):
    p=self.pageVector(*args)
    self.script.append(('rlineto',(p[0],p[1]),{}))
    return Canvas.rlineto(self,p)

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
    # Returns a box, in page coordinates, that approximately contains
    # all the contents of the inset.
    r=BBoxRenderer()
    c = Canvas(renderer=r)
    c.begin()
    c.moveto(0,0)
    self.drawto(c)
    box = r.bbox()
    if box.isEmpty():
      box.include(0,0)
    return box

