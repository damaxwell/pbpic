import os, random, string, re, cStringIO
from subprocess import Popen, PIPE
import tex.dvi
import inset
from misc import FileSweeper
from tex.devicefont import FontTable
from geometry import BBox
from style import Style, style, updatefromstyle
import color
from metric import pt
import userprefs
import hashlib



class _DviCache:
  
  @staticmethod
  def cachedir():
    return '.pbpdata'

  def __init__(self):
    self.clear()

  def clear(self):
    self.dviCache={}

  @staticmethod
  def hashKey(command,texsource):
    m = hashlib.md5();
    m.update(command)
    m.update(texsource)
    return m.digest()
    
  def load(self,command,texsource):
    dvi = None
    cacheFile = self.dviCache.get(self.hashKey(command,texsource),None)
    if not cacheFile is None:
      try: 
        with open(cacheFile,'rb') as f:
          dvi = f.read()
      except:
        pass
    return dvi

  def save(self,command,texsource,dvi):
    r = random.Random()
    r.seed(self.hashKey(command,texsource))
    dviFileName = 'pbpic_'+(''.join(r.choice(string.ascii_uppercase + string.digits) for x in range(10)))+'.dvi'
    cacheFile = os.path.join(self.cachedir(),dviFileName)
    try:
      with open(cacheFile,'wb') as f:
        f.write(dvi)
      self.dviCache[self.hashKey(command,texsource)] = cacheFile
    except:
      pass

class DviCache(userprefs.PersistantCache):

  def __init__(self):
    userprefs.PersistantCache.__init__(self,_DviCache,'dvi.cache',cachedir=_DviCache.cachedir() )


dviCache = DviCache()



class TexProcessor:

  @staticmethod
  def defaultStyle():
    return Style(tex=Style(command=r'latex -interaction=nonstopmode',
                                       preamble = r'\documentclass[12pt]{article}\pagestyle{empty}\begin{document}',
                                       postamble = r'\end{document}' ) )    

  def __init__(self,**kwargs):
    updatefromstyle(self,('command','preamble','postamble'),'tex',kwargs)
    self._dvi = None
    self.errmsg = None
    
  def run(self,text,texFileName=None):
    body = self.preamble + text + self.postamble

    self._dvi = dviCache().load(self.command,body)
    if not self._dvi is None:
      return

    if texFileName is None:
      texFileName = 'pbpic_'+(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10)))
      
    basename = os.path.splitext(texFileName)[0]
    
    with FileSweeper([ basename+ext for ext in ['.aux','.log','.tex','.dvi']]):
      with open(basename+'.tex','wb') as f:
        f.write(body)
      command = '%s %s' % (self.command,texFileName)
      p = Popen(command,stderr=PIPE,stdout=PIPE,shell=True)
      (stdout,stderr) = p.communicate()
      if p.returncode == 0:
        with open(basename+'.dvi') as f:
          self._dvi = f.read()
          self._errmsg = None
          dviCache().save(self.command,body,self._dvi)
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
  p = TexProcessor()
  p.run(text)
  dvi = p.dvi()

  f = cStringIO.StringIO(dvi)
  dvireader=DviToInset(f)
  dvireader.run()
  c = dvireader.pages[0]
  return c

class DviToInset(tex.dvi.DviReader):
  def __init__(self,f):
    tex.dvi.DviReader.__init__(self,f)
    self.pages = []
    self.color_stack=[]
    self.canvas = None
    self.fontTable = FontTable()
    self.bbox = BBox()
    self.firstChar = True

  def set(self,c):
    x = self.toPSScale*self.h
    y = self.toPSScale*self.v
    f = self.currentfont
    w=self.toPSScale*f.s*f.metrics.w[c]*self.scale
    h=self.toPSScale*f.s*f.metrics.h[c]*self.scale
    d=self.toPSScale*f.s*f.metrics.d[c]*self.scale
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
    xs = x.split()
    if xs[0] == 'color':
      cmd = xs[1]
      if cmd == 'push':
        colortype = xs[2]
        if colortype == 'Black':
          c = color.black
        elif colortype == 'rgb':
          comps = (float(comp_s) for comp_s in xs[3:])
          c = color.RGBColor(*comps)
        else:
          raise Exception('unknown color in special %s' % x)
        self.canvas.setfontcolor(c)
        self.color_stack.append(c)
      elif cmd == 'pop':
        self.canvas.setfontcolor(self.color_stack.pop())
      else:
        msg("warning: unknown color special %s" % x)

  def preamble(self):
    # All dimensions get multiplied by scale to convert to Adobe points
    self.toPSScale = (self.state.mag / 1000.) * (float(self.state.n)/ self.state.d)*(72e-5/2.54)

  def postamble(self):
    pass

  def postpostamble(self):
    pass
