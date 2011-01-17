import os, random, string, re, cStringIO
from subprocess import Popen, PIPE
import tex.dvi
import inset
from tex.devicefont import FontTable
from geometry import BBox
from style import Style, style

class FileSweeper:
  def __init__(self,paths):
    self.paths = paths
  def __enter__(self):
    pass
    
  def release(self,path):
    while True:
      try:
        self.paths.remove(path)
      except ValueError:
        break

  def __exit__(self,exc_type, exc_value, traceback):
    for p in self.paths:
      try:
        os.remove(p)
      except:
        pass

_defaultTexStyle = Style(tex=Style(command=r'latex -interaction=nonstopmode',
                                   preamble = r'\documentclass[12pt]{article}\pagestyle{empty}\begin{document}',
                                   postamble = r'\end{document}' ) )
class TexProcessor:

  def __init__(self):
    self._dvi = None
    self.errmsg = None
    
  def run(self,text,texFileName=None):
    print'texstart'
    global _defaultTexStyle
    body = style('tex.preamble',_defaultTexStyle) + text + style('tex.postamble',_defaultTexStyle)

    if texFileName is None:
      texFileName = 'pbpic_'+(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10)))

    basename = os.path.splitext(texFileName)[0]
    
    with FileSweeper([ basename+ext for ext in ['.aux','.log','.tex','.dvi']]):
      with open(basename+'.tex','wb') as f:
        f.write(body)
      command = style('tex.command',_defaultTexStyle) + (' %s' % texFileName)
      p = Popen(command,stderr=PIPE,stdout=PIPE,shell=True)
      (stdout,stderr) = p.communicate()
      if p.returncode == 0:
        with open(basename+'.dvi') as f:
          self._dvi = f.read()
          self._errmsg = None
      else:
        self._dvi = None
        m=re.search("[\n\r]+(! [^\n\r]+[\n\r]+.*)",stdout,re.DOTALL)
        if m is None:
          self._errmsg='Unknown tex error:\n'  + stdout
        else:
          self._errmsg = m.group(0)
        raise Exception(self._errmsg)
    print'texend'

  def dvi(self):
    return self._dvi

def texinset(text):
  p = TexProcessor()
  p.run(text)
  dvi = p.dvi()

  f = cStringIO.StringIO(dvi)
  dvireader=DviToInset(f)
  dvireader.run()
  return dvireader.pages[0]

class DviToInset(tex.dvi.DviReader):
  def __init__(self,f):
    tex.dvi.DviReader.__init__(self,f)
    self.pages = []
    self.canvas = None
    self.fontTable = FontTable()
    self.bbox = BBox()
    self.firstChar = True

  def set(self,c):
    x = self.toPSScale*self.h
    y = self.toPSScale*self.v
    f = self.currentfont
    w=self.toPSScale*f.s*f.metrics.w[c]
    h=self.toPSScale*f.s*f.metrics.h[c]
    d=self.toPSScale*f.s*f.metrics.d[c]
    self.bbox.include(x,-y-d)
    self.bbox.include(x+w,-y+h)

    if self.firstChar:
      self.canvas.mark(point=(x,-y),name='origin')
      self.firstChar = False

    self.canvas.moveto(x,-y)
    s = chr(c)
    self.canvas.show(s)

  def put(self,c):
    self.set(c)

  def putrule(self, a, b):
    x = self.toPSScale*self.h
    y = -self.toPSScale*self.v
    w = self.toPSScale*a
    h = self.toPSScale*b
    self.bbox.include(x,-y)
    # FIXME: -y+h?  -y-h?
    self.bbox.include(x+w,-y+h)    
    self.canvas.path() + (x,-y) - (x+w,-y) - (x+w,-y+h) - (x,-y+h) - 0
    self.canvas.stroke() #FIXME
    # self.canvas.fill()

  def bop(self):
    self.canvas = inset.Inset()
    self.canvas.begin()

  def eop(self):
    self.canvas.setextents(self.bbox)
    self.pages.append(self.canvas)

    self.canvas = None
    self.bbox = BBox()
    self.firstChar = True

  def setfont(self):
    self.currentDeviceFont = self.fontTable.findFont(self.currentfont.fontname)
    fontsize = float(self.scale*self.currentfont.s)/(1 << 16)
    self.canvas.setfontsize(fontsize)
    self.canvas.setfont(self.currentDeviceFont)

  def special(self,x):
    pass

  def preamble(self):
    # All dimensions get multiplied by scale to convert to Adobe points
    self.toPSScale = (self.state.mag / 1000.) * (float(self.state.n)/ self.state.d)*(72e-5/2.54)

  def postamble(self):
    pass

  def postpostamble(self):
    pass
