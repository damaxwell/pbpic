import os, random, string, re, cStringIO
from subprocess import Popen, PIPE
import tex.dvi
import inset
from tex.devicefont import FontTable
from geometry import BBox

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

class TexProcessor:
  
  standard_LaTeX_command = r'latex -interaction=nonstopmode'
  standard_LaTeX_preamble = r'\documentclass{article}\pagestyle{empty}\begin{document}'
  standard_LaTeX_postamble = r'\end{document}'

  def __init__(self,command,preamble,postamble):
    self.command = command
    self.preamble = preamble
    self.postamble = postamble
    self._dvi = None
    self.errmsg = None
    
  def run(self,text,texFileName=None):
    body = self.preamble+text+self.postamble
    if texFileName is None:
      texFileName = 'pbpic_'+(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10)))

    basename = os.path.splitext(texFileName)[0]
    
    with FileSweeper([ basename+ext for ext in ['.aux','.log','.tex','.dvi']]):
      with open(basename+'.tex','wb') as f:
        f.write(body)
      command = self.command + (' %s' % texFileName)
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

  def dvi(self):
    return self._dvi

def texinset(text):
  p=TexProcessor(TexProcessor.standard_LaTeX_command,TexProcessor.standard_LaTeX_preamble,TexProcessor.standard_LaTeX_postamble)
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

    self.canvas.settextpoint(x,-y)
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
