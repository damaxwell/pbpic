import common, font
import cStringIO

class DviReader:
  def __init__(self, input):
    self.input = input    
    self.h=0; self.v=0; self.w=0; self.x=0; self.y=0; self.z=0;
    
    self.buildStates()
    self.states = self.standard_states

    self.end = End()
    self.state = Begin()

    self.stack = []
    self.globalState=[]

    self.currentfont = None
    self.fonttable = {}
    
    self.scale = 1.

  def pushGlobalState( self ):
    self.push()
    self.globalState.append([self.currentfont, self.fonttable, self.input, self.stack, self.states, self.state, self.scale])

  def popGlobalState( self ):
    self.input.close()
    [ self.currentfont, self.fonttable, self.input, self.stack, self.states, self.state, self.scale ] = self.globalState.pop()
    self.pop()

  def push(self):
    self.stack.append( (self.h,self.v,self.w,self.x,self.y,self.z) )

  def pop(self):
    (self.h,self.v,self.w,self.x,self.y,self.z)  = self.stack.pop()

  def buildStates(self):
    states = 256*[None]
    k0 = 0

    for k in range(128):
      states[k] = SetC(k)
    k0 += 128

    for k in range(4):
      states[k0+k] = Set(k)
    k0 += 4
    
    states[k0] = SetRule()
    k0 += 1
    
    for k in range(4):
      states[k0+k] = Put(k)
    k0 += 4

    states[k0] = PutRule()
    k0 += 1
    
    states[k0] = NoOp()
    k0 += 1

    states[k0] = BOP()
    k0 += 1

    states[k0] = EOP()
    k0 += 1

    states[k0] = Push()
    k0 += 1
    
    states[k0] = Pop()
    k0 += 1

    for k in range(4):
      states[k0+k] = Right(k)
    k0 += 4

    states[k0] = W0()
    k0 += 1

    for k in range(4):
      states[k0+k] = W(k)
    k0 += 4

    states[k0] = X0()
    k0 += 1

    for k in range(4):
      states[k0+k] = X(k)
    k0 += 4

    for k in range(4):
      states[k0+k] = Down(k)
    k0 += 4

    states[k0] = Y0()
    k0 += 1

    for k in range(4):
      states[k0+k] = Y(k)
    k0 += 4

    states[k0] = Z0()
    k0 += 1

    for k in range(4):
      states[k0+k] = Z(k)
    k0 += 4

    for k in range(64):
      states[k0+k] = SetFnt(k)
    k0 += 64
    
    for k in range(4):
      states[k0+k] = SetFntK(k)
    k0 += 4
    
    for k in range(4):
      states[k0+k] = XXX(k)
    k0 += 4
    
    for k in range(4):
      states[k0+k] = FntDef(k)
    k0 += 4
    
    states[k0] = Preamble()
    k0 += 1

    states[k0] = Postamble()
    k0 += 1

    states[k0] = PostPostamble()
    k0 += 1

    for k in range(6):
      states[k0+k]=DviCmd(k)
    k0 += 6
    
    assert(k0==256)
    
    self.standard_states = states;
    
    self.vfont_states = [s for s in self.standard_states]
    illegal = VFontIllegal()
    
    self.vfont_states[139] = illegal
    self.vfont_states[140] = illegal
    for i in range(243,248):
      self.vfont_states[i]=illegal

  def run(self):
    while(not (self.state is self.end) ):
      self.next()

  def next(self):
    self.state.execute(self)
    return self.state
  
  def setStateFromInput(self):
    index = self.input.read(1)
    if(len(index)):
      self.state = self.states[ord(index)]
      self.state.read(self.input)
    else:
      if( len(self.globalState) > 0):
        self.state = PopVChar()
      else:
        self.state = self.end
    return self.state

  def set(self,c):
    pass
    
  def put(self,c):
    pass

  def putrule(self, a, b):
    pass

  def bop(self):
    pass
    
  def eop(self):
    pass

  def fntdef(self):
    key = self.state.k
    if not self.fonttable.has_key(key):
      f = font.TexFont(self.state.fontname,self.state.s,self.state.d,self.state.k)
      self.fonttable[key] = f

  def setfont(self):
    pass
    
  def special(self,x):
    pass
  
  def preamble(self):
    pass
    
  def postamble(self):
    pass

  def postpostamble(self):
    pass

class DviCmd:
  def __init__(self,index=0):
    self.index = index
  def read(self,f):
    pass
  def __str__(self):
    return 'undefined %d' % self.index
  def isChar(self):
    False
  def execute(self,r):
    r.setStateFromInput()

class SetC(DviCmd):
  def __init__(self,c):
    self.c = c
  def __str__(self):
    return 'set %d' % self.c
  def execute(self,r):
    if r.currentfont.isVirtual():
      r.state = FinishSetVChar(self.c)
      r.pushGlobalState()
      r.state = StartVChar(self.c)
      return
    r.set(self.c)
    r.h = r.h + r.currentfont.s*r.currentfont.metrics.w[self.c]
    s = r.setStateFromInput();
    if s.isChar() == False:
      r.finishString()
  def isChar(self):
    return True

class Set(SetC):
  def __init__(self,k):
    SetC.__init__(self,0)
    self.readUInt = common.readUIntK[k]
  def __str__(self):
    return 'set %d' % self.c
  def read(self,f):
    self.c=self.readUInt(f)

class SetRule(DviCmd):
  def __init__(self):
    self.a=0; self.b=0
  def __str__(self):
    return 'set rule %d %d' %(self.a,self.b)
  def read(self,f):
    self.a=common.readInt4(f)
    self.b=common.readInt4(f)
  def execute(self,r):
    r.putrule(r.scale*self.a,r.scale*self.b)
    r.h = r.h + r.scale*self.a
    r.setStateFromInput()

class Put(Set):
  def __str__(self):
    return 'put %d' % self.c
  def execute(self,r):
    if r.currentfont.isVirtual():
      r.state = NoOp()
      r.pushGlobalState()
      r.state = StartVChar(self.c)
      return
    r.put(self.c)
    r.setStateFromInput()

class PutRule(SetRule):
  def __str__(self):
    return 'put rule %d %d' %(self.a,self.b)
  def execute(self,r):
    r.putrule(r.scale*self.a,r.scale*self.b)
    r.setStateFromInput()

class NoOp(DviCmd):
  def __str__(self):
    return 'nop'

class BOP(DviCmd):
  def __init__(self):
    self.c =10*[0]
    self.p = 0
  def read(self,f):
    for k in range(10):
      self.c[k]=common.readUInt4(f)
    self.p = common.readInt4(f)
  def __str__(self):
    return 'bop prev=%d' % self.p
  def execute(self,r):
    r.bop()
    r.setStateFromInput()

class EOP(DviCmd):
  def __str__(self):
    return 'eop'
  def execute(self,r):
    r.eop()
    r.setStateFromInput()

class Push(DviCmd):
  def __str__(self):
    return 'push'
  def execute(self,r):
    r.push()
    r.setStateFromInput()

class Pop(DviCmd):
  def __str__(self):
    return 'pop'
  def execute(self,r):
    r.pop()
    r.setStateFromInput()

class Right(DviCmd):
  def __init__(self,k):
    self.readUInt = common.readIntK[k]
    self.b = 0
  def __str__(self):
    return 'right %d' % self.b
  def read(self,f):
    self.b=self.readUInt(f)
  def execute(self,r):
    r.h = r.h + r.scale*self.b
    r.setStateFromInput()

class W0(DviCmd):
  def __str__(self):
    return 'w0'
  def execute(self,r):
    r.h = r.h + r.w
    r.setStateFromInput()

class W(DviCmd):
  def __init__(self,k):
    self.readInt = common.readIntK[k]
    self.b = 0
  def __str__(self):
    return 'w b=%d' % self.b
  def read(self,f):
    self.b=self.readInt(f)
  def execute(self,r):
    r.w = r.scale*self.b
    r.h = r.h + r.w
    r.setStateFromInput()

class X0(DviCmd):
  def __str__(self):
    return 'x0'
  def execute(self,r):
    r.h = r.h + r.x
    r.setStateFromInput()

class X(DviCmd):
  def __init__(self,k):
    self.readInt = common.readIntK[k]
    self.b = 0
  def __str__(self):
    return 'x b=%d' % self.b
  def read(self,f):
    self.b=self.readInt(f)
  def execute(self,r):
    r.x = r.scale*self.b
    r.h = r.h + self.b
    r.setStateFromInput()

class Down(DviCmd):
  def __init__(self,k):
    self.a=0
    self.readInt = common.readIntK[k]
  def read(self,f):
    self.a=self.readInt(f)
  def __str__(self):
    return 'down %d' % self.a
  def execute(self,r):
    r.v = r.v + r.scale*self.a
    r.setStateFromInput()

class Y0(DviCmd):
  def __str__(self):
    return 'y0'
  def execute(self,r):
    r.v = r.v + r.scale*r.y
    r.setStateFromInput()

class Y(DviCmd):
  def __init__(self,k):
    self.readInt = common.readIntK[k]
    self.a = 0
  def __str__(self):
    return 'y a=%d' % self.a
  def read(self,f):
    self.a=self.readInt(f)
  def execute(self,r):
    r.y = r.scale*self.a
    r.v = r.v + r.y
    r.setStateFromInput()

class Z0(DviCmd):
  def __str__(self):
    return 'z0'
  def execute(self,r):
    r.v = r.v + r.z
    r.setStateFromInput()

class Z(DviCmd):
  def __init__(self,k):
    self.readInt = common.readIntK[k]
    self.a = 0
  def __str__(self):
    return 'z a=%d' % self.a
  def read(self,f):
    self.a=self.readInt(f)
  def execute(self,r):
    r.z = r.scale*self.a
    r.v = r.v + r.z
    r.setStateFromInput()

class SetFnt(DviCmd):
  def __init__(self,fontnum):
    self.fontnum = fontnum
  def __str__(self):
    return 'font %d' % self.fontnum
  def execute(self,r):
    r.currentfont = r.fonttable[self.fontnum]
    if not r.currentfont.isLoaded:
      r.currentfont.load()    
    if(not r.currentfont.isVirtual()):
      r.setfont()
    r.setStateFromInput()

class SetFntK(SetFnt):
  def __init__(self,k):
    SetFnt.__init__(self,0)
    self.readUInt = common.readUIntK[k]
  def read(self,f):
    self.fontnum = self.readUInt(f)
  def __str__(self):
    return 'font %d' % self.fontnum

class XXX(DviCmd):
  def __init__(self,k):
    self.readUInt = common.readUIntK[k]
    self.x = ""
  def __str__(self):
    return 'special %s' % self.x
  def read(self,f):
    self.x = f.read(self.readUInt(f))
  def execute(self,r):
    r.special(self.x)
    r.setStateFromInput()

class FntDef(DviCmd):
  def __init__(self,k):
    self.readUInt = common.readUIntK[k]
    self.k = 0
    self.c = 0
    self.s = 0
    self.d = 0
    self.area = ''
    self.fontname = ''
  def __str__(self):
    return 'fntdef k=%d c=%d s=%d d=%d font:%s:%s' % (self.k,self.c,self.s,self.d,self.area,self.fontname)

  def read(self,f):
    self.k = self.readUInt(f)
    self.c = common.readUInt4(f)
    self.s = common.readUInt4(f)
    self.d = common.readUInt4(f)
    a = common.readByte(f)
    l = common.readByte(f)
    self.area = f.read(a)
    self.fontname = f.read(l)

  def execute(self,r):
    r.fntdef()
    r.setStateFromInput()

class Preamble(DviCmd):
  def __init__(self):
    self.i=0; self.n=0; self.d=0; self.mag=0; self.x=""
  def __str__(self):
    return "pre i=%d n=%d d=%d mag=%d %s" % (self.i,self.n,self.d,self.mag,self.x)
  def read(self,f):
    self.i=common.readByte(f)
    self.n = common.readUInt4(f)
    self.d = common.readUInt4(f)
    self.mag = common.readUInt4(f)
    k = common.readByte(f)
    if k>0:
      self.x=f.read(k)
    else:
      self.x=''
  def execute(self,r):
    r.preamble()
    r.setStateFromInput()

class Postamble(DviCmd):
  def __init__(self):
    self.p=0; self.n=0; self.d=0; self.mag=0; self.l=0; self.u=0; self.s=0; self.t=0;
  def __str__(self):
    return "post p=%d n=%d d=%d mag=%d l=%d u=%d s=%s t=%d" % (self.p,self.n,self.d,self.mag,self.l,self.u,self.s,self.t)
  def read(self,f):
    self.p=common.readUInt4(f)
    self.n=common.readUInt4(f)
    self.d=common.readUInt4(f)
    self.mag=common.readUInt4(f)
    self.l=common.readUInt4(f)
    self.u=common.readUInt4(f)
    self.s=common.readUInt2(f)
    self.t=common.readUInt2(f)
  def execute(self,r):
    r.postamble()
    r.setStateFromInput()

class PostPostamble(DviCmd):
  def __init__(self):
    self.q=0;
    self.i=0;
  def __str__(self):
    return "post post q=%d i=%d" % (self.q,self.i) 
  def read(self,f):
    self.q=common.readUInt4(f)
    self.i=common.readByte(f)
  def execute(self,r):
    r.postpostamble()
    r.state = r.end

class Begin(DviCmd):
  def __str__(self):
    return 'begin'

class End(DviCmd):
  def __str__(self):
    return 'end'
  def execute(self,r):
    pass

class PopVChar(DviCmd):
  def __str__(self):
    return 'PopVChar'
  def execute(self,r):
    r.popGlobalState()
    # The next state was set just before the push, so
    # we don't read a state here

class StartVChar(DviCmd):
  def __init__(self,c):
    self.c = c
  def __str__(self):
    return "StartVChar %d" % self.c

  def execute(self,r):
    r.w=0; r.x=0; r.y=0; r.z=0;
    r.stack=[]    
    vFont = r.currentfont.vchars

    r.fonttable = vFont.fontTable

    r.scale *= (r.currentfont.s*1.0/(1 << 20))

    r.input = cStringIO.StringIO(vFont.packets[self.c].dvi)
    r.states = r.vfont_states

    defaultFont = vFont.defaultFont
    r.currentfont = defaultFont

    if not (defaultFont is None):
      if not r.currentfont.isLoaded:
        r.currentfont.load()    
      if(not r.currentfont.isVirtual()):
        r.setfont()

    r.setStateFromInput()

class FinishSetVChar(DviCmd):
  def __init__(self,c):
    self.c = c
  def __str__(self):
    return 'FinishSetVChar %d' % self.c
  def execute(self,r):
    r.h = r.h + r.currentfont.s*r.currentfont.metrics.w[self.c]
    r.setStateFromInput()

class VFontIllegal(DviCmd):
  def __str__(self):
    return 'vfont illegal'
  def execute(self,r):
    raise Exception('Illegal DVI command for VFont')


if __name__ == '__main__':
  f = open('blat.dvi')
  r = DviReader(f)
  r.run()
