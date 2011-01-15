from canvas import Canvas
from render_bbox import BBoxRenderer

class Inset(Canvas):
  
  def __init__(self):
    Canvas.__init__(self)
    self.script=[]

  def drawto(self,canvas):
    for f in self.script:
      args=f[1]; kwargs=f[2]
      f[0](canvas,*args,**kwargs)

  wrapped_methods = [ 'setlinewidth', 'setcolor', 'setrgbcolor', 'setgray', 'newpath',
                'lineto', 'moveto', 'closepath', 'stroke', 
                'kstroke', 'scaleto', 'scale', 'translate', 'gsave', 'grestore', 'setphysicalfont', 
                'setfontsize', 'showglyphs', 'textpoint', 'settextpoint', 'rotate', 
                'setfont' ]

  template = '''def %s(self,*args,**kwargs): 
                   self.script.append((Canvas.%s,args,kwargs)); 
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
    self.extents=bbox.copy()

  def markedbox(self):
    c = Canvas()
    r=BBoxRenderer()
    c.begin(r)
    self.drawto(c)
    return r.bbox()
