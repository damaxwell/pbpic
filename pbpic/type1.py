import StringIO
import array
from geometry import AffineTransform, Path
from metric import Vector, Point
from font import FontMetrics
import re

class Type1Exception(Exception):
  pass

class Type1Font:

  @staticmethod
  def fromPath( p ):
    f = file( p, 'rb' )
    return Type1Font( f )

  @staticmethod
  def fromData( d ):
    return Type1Font( StringIO.StringIO( d ) )
  
  def __init__(self,stream):
    self.data = stream.read()
    stream = StringIO.StringIO(self.data)
    self.stream = stream
    self.metrics = {}
    self.paths = {}
    self.glyphnames = None

    self._fontName = None
    self._fontMatrix = None
    self._encoding = None
    
    self.isPFB = False
    c=ord(stream.read(1))    
    if c == 128:
      self.isPFB = True
      stream.seek(0)
      self.segments=[]
      self.stride_pfb()
      self.start_public = 6
    else:
      self.start_public = 0

    eexec_re = re.compile(".*currentfile[ ]+eexec[ \n\r\t]",re.DOTALL)    
    m = eexec_re.match(self.data) 
    if m is None:
      raise Type1Exception('Mangled Type1 Font: unable to partiton into public/private parts')
      
    self.end_public = m.end(0)
    if self.isPFB:
      self.start_private = self.segments[1][0]
      self.end_private = self.start_private + self.segments[1][1]
    else:
      self.start_private = self.end_public + 1
      raise NotImplementedError() # FIXME: Need to find end of eexec part
        
    self.private = decrypt(self.data[self.start_private:self.end_private],eexec_R)

    self.public = self.data[self.start_public:self.end_public]

    self.parse_public()

    self.parse_private()

  def fontName(self):
    return self._fontName
    
  def fontMatrix(self):
    return self._fontMatrix.copy()
    
  def encoding(self):
    return self._encoding

  def parse_public(self):

    ############################################################
    # FontName
    m = re.search("/FontName[ \t]+/([^ \t]+)",self.public)
    if m is None:
      raise Type1Exception('Type1 font missing FontName')
    self._fontName = m.groups()[0]

    ############################################################
    ## FontMatrix
    fm_re = "/FontMatrix[ \t\n\r]+\[[ \t\n\r]*"
    float_re = "([-+]?(?:\d+(?:\.\d*)?|\.\d+))"
    for k in xrange(5):
      fm_re +=float_re
      fm_re +="[ \t\n\r]+"
    fm_re +=float_re
    fm_re +="[ \t\n\r]*\]"
    m = re.search(fm_re, self.public)

    self._fontMatrix = AffineTransform([ float(m.group(k+1)) for k in range(6) ])
    if m is None:
      raise Type1Exception('Type1 font missing FontMatrix')

    ############################################################
    ## Encoding vector
    encoding_re = re.compile( "/Encoding[ \n\r\t]+(?:(StandardEncoding)|([0-9]+))")
    m = encoding_re.search( self.public )
    
    encodingStart = m.start(0)
    if m.groups()[0]:
      self._encoding = EncodingVector('StandardEncoding')
    else:
      numEntries = int(m.groups()[1])
      a = self.public[encodingStart:]
      entry_re = re.compile( "([0-9]+)[ ]*/([^ ]+)[ \n\r\t]+")

      encodingList = [ ".notDef" ] * numEntries
      for m in entry_re.finditer( a ):
        encodingList[int(m.groups()[0])] = m.groups()[1]

      self._encoding = EncodingVector(encodingList)

  def parse_private(self):
    # lenIV
    m = re.search("/lenIV[ \t\n\r]+([0-9]+)",self.private)
    if m is None:
      self.lenIV = 4
    else:
      try:
        self.lenIV = int(m.groups()[0])
      except ValueException:
        raise Type1Exception('Type1 font has mangled lenIV')

    # Subrs
    m = re.search('/Subrs[ \t\r\n]+([0-9]+)[ \t\r\n]',self.private)
    if m == None:
      raise Type1Exception('')
    numSubrs = int(m.groups()[0])
    subr_base = m.end(0)
    tail = self.private[subr_base+1:]
    
    subr_re = re.compile( "dup[ \t\r\n]+([0-9]+)[ \t\r\n]+([0-9]+)[ \t\r\n]+[^ ]+[ \t\r\n]")

    subrs = [ None ] * numSubrs
    send = 0
    for m in subr_re.finditer(tail):
      # We might match the interior of a binary section.  If so, just continue on.
      if m.start(0) < send:
        continue
      sstart = m.end(0)
      send = sstart+int(m.groups()[1])
      subrs[int(m.groups()[0])] = tail[sstart:send]
    self.subrs = subrs

    #CharStrings
    m = re.search('/CharStrings[ \t\r\n]+([0-9]+)[ \t\r\n]',self.private)
    if m == None:
      raise Type1Exception('Font missing CharStrings')
    numCharStrings = int(m.groups()[0])

    charstring_base = m.end(0)
    tail = self.private[charstring_base+1:]
    
    charstring_re = re.compile( "/([^ \t\r\n/]+)[ \t\r\n]+([0-9]+)[ \t\r\n]+[^ \t\r\n]+[ \t\r\n]")

    charstrings = {}
    k = 0
    cend = 0
    for m in charstring_re.finditer(tail):
      # We might match the interior of a binary section.  If so, just continue on.
      if m.start(0) < cend:
        continue
      cstart = m.end(0)
      cend = cstart+int(m.groups()[1])
      charstrings[m.groups()[0]] = (k,tail[cstart:cend])
      k += 1
    self.charstrings = charstrings
    
    self.glyphnames = [None]*len(self.charstrings)
    for cs in self.charstrings.items():
      self.glyphnames[cs[1][0]] = cs[0]
    
  def subroutine(self,i):
    return CharString(i,self.subrs[i],self.lenIV)

  def charstring(self,c):
    return CharString(c,self.charstrings[c][1],self.lenIV)
  
  def pathForGlyphname(self,g):
    p = self.paths.get(g,None)
    if p is None:
      p = BuildChar(self,g).path()
      self.paths[g]=p
    return p

  def pathForGlyph(self,c):
    return self.pathForGlyphname(self.glyphnames[c])
  
  def metricsForGlyphname(self,c):
    m = self.metrics.get(c,None)
    if m is None:
      m = CharMetrics(self,self.charstring(c)).metrics()
      self.metrics[c] = m
    return m

  def metricsForGlyph(self,c):
    return self.metricsForGlyphname(self.glyphnames[c])

  def glyphIndices(self,glyphnames):
    return [ self.charstrings[g][0] for g in glyphnames ]

  def stride_pfb(self):
    stream = self.stream
    while True:
      c=ord(stream.read(1))
      if c != 128:
        raise Type1Exception('Mangled PFB font: incoherent section markers')
      c=ord(stream.read(1))
      if c == 3:
        break

      slen = ord(stream.read(1))
      slen |= (ord(stream.read(1)) << 8)
      slen |= (ord(stream.read(1)) << 16)
      slen |= (ord(stream.read(1)) << 24)

      self.segments.append((stream.tell(),slen))
      stream.seek(slen,1)


class CharStringOp:

  def __init__(self,val):
    self.val = val
  def __repr__(self):
    return 'CharStringOp(%d)' % self.val

class CharString:
  def __init__(self,name,text,lenIV):
    self.name = name
    self.text = text
    self.lenIV = lenIV
    s =  decrypt(text,charstring_R)
    self.plainText = array.array('B',decrypt(text,charstring_R)[lenIV:])
    
  def codes(self):
    i = 0
    s = self.plainText
    n = len(s)
    while i < n:
      v=s[i]
      i+=1
      if v <= 31:
        if v == 12:
          v = 32 + s[i]
          i += 1
        v = CharStringOp(v)
      elif v<=246:
        v = v-139
      elif v<=250:
        w = s[i];
        i += 1
        v = ((v-247)<<8)+w+108
      elif v<=254:
        w = s[i];
        i += 1
        v = -((v-251)<<8)-w-108
      else:
        v = s[i]
        i += 1
        for k in range(3):
          v = v << 8
          v |= s[i]
          i += 1
        if v>= (1<<31):
          v = (1<<32) - v
      yield v

class Halt(Exception):
  pass
  
class CharStringParser:
# CharStringParser:

  # The fields are the command name, number of arguments (aside from callothersuber, which is way too special),
  # and a boolean to indicate if the stack should be cleared.
  opcodeToCmd = \
  { 14:('endchar',0,True),  13:('hsbw',2,True),  38:('seac',5,True),  39:('sbw',4,True),  
  9:('closepath',0,True),  6:('hlineto',1,True),  22:('hmoveto',1,True),  31:('hvcurveto',4,True),  
  5:('rlineto',2,True),  21:('rmoveto',2,True),  8:('rrcurveto',6,True),  30:('vhcurveto',4,True),  
  7:('vlineto',1,True),  4:('vmoveto',1,True),  32:('dotsection',0,True),  1:('hstem',2,True),  
  34:('hstem3',6,True),  3:('vstem',2,True),  33:('vstem3',6,True),  44:('div',2,False),  
  48:('callothersubr',-1,False),  10:('callsubr',1,False),  49:('pop',0,False),  11:('return',0,False),
  65:('setcurrentpoint',2,True) }

  cmdToOpcode =\
  { 'endchar':14, 'hsbw':13, 'seac':38, 'sbw':39, 
  'closepath':9, 'hlineto':6, 'hmoveto':22, 'hvcurveto':31, 
  'rlineto':5, 'rmoveto':21, 'rrcurveto':8, 'vhcurveto':30, 
  'vlineto':7, 'vmoveto':4, 'dotsection':32, 'hstem':1, 
  'hstem3':34, 'vstem':3, 'vstem3':33, 'div':44, 
  'callothersubr':48, 'callsubr':10, 'pop':49, 'return':11, 'setcurrentpoint':65 }


  def __init__(self,font,charstring):
    self.font = font
    if isinstance(charstring,str):
      charstring = font.charstring(charstring)
    self.charstring = charstring
    self.stack = 32*[0]
    self.top = 0

    self.callbacks = {44:self.div, 48:self.callothersubr, 10:self.callsubr, 49:self.pop, 11:self.subreturn}

    self.flexpoints = 12*[0]
    self.flexstate = -1

  def printstack(self):
    s = '[ '
    for k in self.stack[:self.top]:
      s += str(k)
      s += ' '
    s += ']'
    print s
  
  def rrcurveto(*args):
    pass

  def div(self,p,q):
    self.stack[self.top-2]  = float(p)/q
    self.top -= 1
  
  def callothersubr(self,n,args):
    self.top -= (len(args) + 2)
    if n == 1: # Start Flex
      self.flexstate = 0
    elif n == 2: # Flex vector (ish)
      self.flexstate += 1
    elif n == 0: #
      self.flexstate = -1
      self.rrcurveto(*self.flexpoints[0:6])
      self.rrcurveto(*self.flexpoints[6:13])
      self.stack[self.top] = self.cpx
      self.stack[self.top+1] = self.cpy
    elif n == 3: # Hint replacement. We do nothing, noting that a subroutine number is lurking at the top of the 
                 # stack and is about to reappear in a subsequent 'pop' that always follows callothersubr
      pass
    else:
      print 'warning: unknown othersubr %d called' % n

  def pop(self):
    self.top += 1 
    
  def subreturn(self):
    raise StopIteration()

  def callsubr(self,n):
    self.callstack.append(self.f)
    self.top -= 1
    self.f=iter(self.font.subroutine(n).codes())

  def run(self):
    self.callstack=[]
    self.f = iter(self.charstring.codes())

    while True:
      try:
        c = self.f.next()
        if isinstance(c,int):
          self.stack[self.top] = c
          self.top += 1
        else:
          opcode = c.val
          cmd = self.opcodeToCmd[opcode]
          callback = self.callbacks.get(opcode,None)
          if callback is None:
            if cmd[2]: self.top = 0
          else:
            if cmd[2]: # clear-stack type operator
              assert(self.top==cmd[1])
              args = self.stack[0:cmd[1]]
              self.top = 0
            else:
              if opcode == 48: # callothersuber
                subr = self.stack[self.top-1]
                nargs = self.stack[self.top-2]
                args = (subr,self.stack[self.top-2-nargs:self.top-2])
              else:
                nargs = cmd[1]
                args = self.stack[self.top-nargs:self.top]
            callback(*args)
      except StopIteration:
        if len(self.callstack) == 0:
          break
        self.f = self.callstack.pop()
      except Halt:
        break

class CharMetrics(CharStringParser):
  def __init__(self,font,charstring):
    CharStringParser.__init__(self,font,charstring)
    self._metrics = None
    self.fontMatrix = font.fontMatrix()
    self.callbacks.update({  13:self.hsbw, 39:self.sbw })

  def metrics(self):
    if self._metrics is None:
      self.run()
    return self._metrics

  def hsbw(self,sbx,wx):
    advance = self.fontMatrix.Tv(Vector(wx,0))
    sb = self.fontMatrix.T(Point(sbx,0))
    self._metrics = FontMetrics(advance[0],advance[1],sb[0],sb[1])
    raise Halt()

  def sbw(self,sbx,sby,wx,wy):
    advance = self.fontMatrix.Tv(Vector(wx,wy))
    sb = self.fontMatrix.T(Point(sbx,sby))
    self._metrics = FontMetrics(advance[0],advance[1],sb[0],sb[1])
    raise Halt()

class BuildChar(CharStringParser):
  def __init__(self,font,charstring):
    CharStringParser.__init__(self,font,charstring)
    self._path = None
    self.fontMatrix = font.fontMatrix()

    self.callbacks.update( { 13:self.hsbw, 
                        # FIXME: 38:self.seac, 
                        39:self.sbw, 
                        9:self.closepath, 6:self.hlineto, 22:self.hmoveto, 31:self.hvcurveto, 
                        5:self.rlineto, 21:self.rmoveto, 8:self.rrcurveto, 30:self.vhcurveto, 
                        7:self.vlineto, 4:self.vmoveto, 
                        65:self.setcurrentpoint} )

  def path(self):
    if self._path is None:
      self._path = Path()
      self.run()
    return self._path # FIXME: reutrn a copy

  def hsbw(self,sbx,wx):
    self.cpx = sbx;
    self.cpy = 0;
    self._path.moveto(self.fontMatrix.T(Point(sbx,0)))

  def sbw(self,sbx,sby,wx,wy):
    self.cpx = sbx;
    self.cpy = sby;
    self._path.moveto(self.fontMatrix.T(Point(sbx,sby)))

  def closepath(self):
    self._path.closepath()

  def hlineto(self,dx):
    self.rlineto(dx,0)

  def hmoveto(self,dx):
    self.rmoveto(dx,0)

  def hvcurveto(self,dx1,dx2,dy2,dy3):
    self.rrcurveto(dx1,0,dx2,dy2,0,dy3)

  def vlineto(self,dy):
    self.rlineto(0,dy)

  def vmoveto(self,dy):
    self.rmoveto(0,dy)

  def vhcurveto(self,dy1,dx2,dy2,dx3):
    self.rrcurveto(0,dy1,dx2,dy2,dx3,0)

  def rlineto(self,dx,dy):
    self._path.rlineto(self.fontMatrix.Tv(Vector(dx,dy)))
    self.cpx += dx
    self.cpy += dy

  def rmoveto(self,dx,dy):
    if self.flexstate < 0:
      self._path.rmoveto(self.fontMatrix.Tv(Vector(dx,dy)))
      self.cpx += dx; self.startx = self.cpx
      self.cpy += dy; self.starty = self.cpy
    elif self.flexstate == 0:
      self.flexpoints[0] = dx
      self.flexpoints[1] = dy
    elif self.flexstate == 1:
      self.flexpoints[0] += dx
      self.flexpoints[1] += dy
    else:
      k = self.flexstate-1
      self.flexpoints[2*k] = dx
      self.flexpoints[2*k+1] = dy

  def rrcurveto(self,dx1,dy1,dx2,dy2,dx3,dy3):
    fm = self.fontMatrix
    self._path.rcurveto(self.fontMatrix.Tv(Vector(dx1,dy1)),
                        self.fontMatrix.Tv(Vector(dx1+dx2,dy1+dy2)),
                        self.fontMatrix.Tv(Vector(dx1+dx2+dx3,dy1+dy2+dy3)) )
    self.cpx += (dx1+dx2+dx3)
    self.cpy += (dy1+dy2+dy3)
  
  def setcurrentpoint(self,x,y):
    self.cpx = x;
    self.cpy = y;
    self._path.setcurrentpoint(self.fontMatrix.T(Point(x,y)))


AdobeStandardEncoding = \
[ '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'space', 'exclam', 'quotedbl', 'numbersign', 'dollar', 'percent', 'ampersand', 'quoteright', 
'parenleft', 'parenright', 'asterisk', 'plus', 'comma', 'hyphen', 'period', 'slash', 
'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 
'eight', 'nine', 'colon', 'semicolon', 'less', 'equal', 'greater', 'question', 
'at', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 
'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 
'X', 'Y', 'Z', 'bracketleft', 'backslash', 'bracketright', 'asciicircum', 'underscore', 
'quoteleft', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 
'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 
'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 
'x', 'y', 'z', 'braceleft', 'bar', 'braceright', 'asciitilde', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', 'exclamdown', 'cent', 'sterling', 'fraction', 'yen', 'florin', 'section', 
'currency', 'quotesingle', 'quotedblleft', 'guillemotleft', 'guilsinglleft', 'guilsinglright', 'fi', 'fl', 
'.notdef', 'endash', 'dagger', 'daggerdbl', 'periodcentered', '.notdef', 'paragraph', 'bullet', 
'quotesinglbase', 'quotedblbase', 'quotedblright', 'guillemotright', 'ellipsis', 'perthousand', '.notdef', 'questiondown', 
'.notdef', 'grave', 'acute', 'circumflex', 'tilde', 'macron', 'breve', 'dotaccent', 
'dieresis', '.notdef', 'ring', 'cedilla', '.notdef', 'hungarumlaut', 'ogonek', 'caron', 
'emdash', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', 'AE', '.notdef', 'ordfeminine', '.notdef', '.notdef', '.notdef', '.notdef', 
'Lslash', 'Oslash', 'OE', 'ordmasculine', '.notdef', '.notdef', '.notdef', '.notdef', 
'.notdef', 'ae', '.notdef', '.notdef', '.notdef', 'dotlessi', '.notdef', '.notdef' ]

class EncodingVector:
  
  def __init__(self,encoding):
    if encoding == 'StandardEncoding':
      self.ev = AdobeStandardEncoding
    else:
      self.ev = [g.split('/')[-1] for g in encoding] # Remove any leading slash
    
    
  def __repr__(self):
    if self.ev == AdobeStandardEncoding:
      return "EncodingVector(AdobeStandard)"
    else:
      return "EncodingVector"

  def __getitem__(self,i):
    return self.ev[i]

  def glyphNamesForChars(self,chars):
    if isinstance(chars,str):
      return [ self.ev[ord(c)] for c in chars ]
    else:
      return [ self.ev[c] for c in chars ]
      

eexec_R = 55665
charstring_R = 4330
encrypt_c1 = 52845
encrypt_c2 = 22719

def decrypt( s, R ):
  bytes = array.array('B', s )
  return decryptBytes( bytes, R).tostring()

def decryptBytes( bytes, R):
  try:
    import pscodec
    return pscodec.t1_decrypt( bytes, R )
  except ImportError:
    return decryptBytesSlow( bytes, R )

def decryptBytesSlow(bytes, R):
  mask = (1<<16)-1
  i = 0
  for C in bytes:
    P = C ^ (R >> 8)
    bytes[i] = P
    i = i + 1
    R = ((C + R)*encrypt_c1 + encrypt_c2) & mask
  return bytes

def encrypt( s, R):
  bytes = array.array('B',s)
  return encryptBytes( bytes, R).tostring()

def encryptBytes( bytes, R):
  try:
    import pscodec
    return pscodec.t1_encrypt( bytes, R )
  except ImportError:
    return encryptBytesSlow( bytes, R )
  
def encryptBytesSlow(bytes, R):
  i = 0
  for P in bytes:
    C = P^(R >> 8)
    bytes[i] = C
    i = i + 1
    R = ((C + R)*encrypt_c1 + encrypt_c2) & ((1 << 16)-1)
  return(bytes)

if __name__ == '__main__':
  # f = Type1Font.fromPath('../test/cmr10.pfb')
  f = Type1Font.fromPath('../test/MinionPro-Regular.pfb')
  print BuildChar(f,'A').path()
  # subr = f.subroutine(2)
  # print subr.text
  # print subr.plainText
  # for c in subr.codes():
  #   print c
  # CharStringParser(f,'A').run()
  # print f.private
  # print f.fontName
  # print f.fontMatrix
  # print f.encoding