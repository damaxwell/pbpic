import cStringIO
import common, resource

class TexFont:
  def __init__(self,fontname,s,d,index):
    """A font record in a DVI file consists of the font's name, its scaled size (s), its design size (d), 
    and the number by which the font is referred to in the DVI file (index).
    """
    self.fontname = fontname
    self.s = s
    self.d = d
    self.index = index

    self.metrics = None
    self.vchars = None
    self.isLoaded = False

  def __str__(self):
    return 'TexFont %s s=%s d=%d index=%d' %(self.fontname, self.s, self.d, self.index)
  
  def isVirtual(self):
    if not self.isLoaded:
      self.load()
    return not( self.vchars is None)

  def load(self):
    if self.isLoaded:
      return

    self.metrics = resource.findTFM( self.fontname )
    self.vchars = None
    try:
      self.vchars  = resource.findVF( self.fontname )
    except resource.TexResourceNotFound:  
      pass

    self.isLoaded = True

class TFM:
  # A TFM file has the following format: (http://www.tug.org/TUGboat/Articles/tb02-1/tb02fuchstfm.pdf)
  #   6 32-bit words in which is encoded the sizes of various portions and parameters of the file
  #   A header of length 'lh' (a parameter found in the previous 6 words)
  #   A table of entries for each character giving indices into the width/height/depth/italic correction tables
  #   A table of 32-bit fixs for widths
  #   A table of 32-bit fixs for heights
  #   A table of 32-bit fixs for depths
  #   A table of 32-bit fixs for italic-corrections
  #   Remaining data concerning kerning, extensible characters, and so forth.  
  #
  # This class extracts the w/h/d information and stores them in arrays of floating point numbers, one for
  # each character. To access the width of character c, simply use: tfm.w[c], etc.

  def __init__(self,path):
    with file(path,'rb') as f: 
      self.data = f.read()
    self.input = cStringIO.StringIO(self.data); input = self.input
    self.lf = common.readUInt2(input) # length of file
    self.lh = common.readUInt2(input) # length of header
    self.bc = common.readUInt2(input) # smallest char code
    self.ec = common.readUInt2(input) # largest char code
    self.nc = self.ec-self.bc+1
    self.nw = common.readUInt2(input) # number of words in width table
    self.nh = common.readUInt2(input) # height table
    self.nd = common.readUInt2(input) # depth table
    self.ni = common.readUInt2(input) # italic cor table
    self.nl = common.readUInt2(input) # lig/kern table
    self.nk = common.readUInt2(input) # kern table
    self.ne = common.readUInt2(input) # extensible char table
    self.np = common.readUInt2(input) # font parameters
  
    self.loadCharInfo()
    
    offset = 6+self.lh+self.nc
    self.w = self.readFixWordTable(offset,self.nw,self.w_ind)
    offset += self.nw
    self.h = self.readFixWordTable(offset,self.nh,self.h_ind)
    offset += self.nh
    self.d = self.readFixWordTable(offset,self.nd,self.d_ind)

  def loadCharInfo(self):
    input = self.input
    input.seek(4*(6+self.lh))
    nchars = self.nc
    self.w_ind = [0]*nchars
    self.h_ind = [0]*nchars
    self.d_ind = [0]*nchars
    for k in range(nchars):
      self.w_ind[k] = ord(input.read(1))      
      hd = ord(input.read(1))
      self.h_ind[k] = hd >> 4
      self.d_ind[k] = hd & 0x0F
      input.seek(input.tell()+2)
  
  def readFixWordTable(self,offset,length,inds):
    t = [0.]*length
    self.input.seek(4*offset)
    for k in range(length):
      t[k]=common.readFixWord(self.input)

    d = [0.]*256
    for k in range(self.nc):
      d[k+self.bc] = t[inds[k]]
    return d



"""  The virtual font file format is as follows
Header:

PRE   VFID  comment     checksum    design size
247   202   k[l] x[k]   cs[4]       ds[4]

Font Definitions:
FNTDEF_N (1<=N<=4) number checksum  scalefactor  designsize  arealength filelength  area+file
242+N              k[N]   c[4]      s[4]         d[4]        a[1]       l[1]        n[a + l].

These are identical to the font definitions of a DVI file.  The scalefactor is interpreted
as a fixword relative to the design size of the VIRTUAL font.  The designsize of these
fonts seem to never be used.

Following the font definitions we have

Character Definitions: (two packet types, short or long)

SHORTCHAR_N (0<N<242)   char code  char width  dvi packet
N                       c[1]       tfm[3]      dvi[N]

LONGCHAR    packet length  char code    char width  div packet
243         pl[4]          c[4]         tfm[3]      dvi[pl]

At the end of the packets, there is a trival postamble, one or more bytes of

POST
248
"""

VFID = 202
LONGCHAR=242
FNTDEF1 = 243
FNTDEF2 = 244
FNTDEF3 = 245
FNTDEF4 = 246
PRE = 247
POST = 248

# Structure for keeping all data associated with an individual virtual font character
class VFChar:
  def __init__(self,cc,width,dvi):
    self.cc = cc
    self.width = width
    self.dvi = dvi

# Exception for reporting errors reading a virtual font. Is there a more pythonic way
# to do this?
class VFFormatException(Exception):
  pass

class VirtualFont:

  def __init__(self, vffile):

    self.vffile = vffile
    input = open(self.vffile, "rb")

    # The dictionary of fonts used by this virtual font.  The first one defined is the default
    self.fontTable={}
    self.defaultFont = None

    # Assume at least 256 characters for the font.
    self.packets= [None]*256
    self.pcount = 0

    c1 = (ord)(input.read(1))
    c2 = (ord)(input.read(1))
    if( (c1!=PRE) | (c2!=VFID) ):
      raise VFFormatException("Invalid header for virtual font %s.\nExpecting %d %d, found %d %d." % (vffile, PRE, VFID, c1, c2) )

    # Comment
    self.comment = common.readString(input,common.readByte(input))

    # Checksum
    self.cs = common.readUInt4(input)

    # Design size
    self.ds = common.readUInt4(input);

    # Next comes a sequence of font definitions and character defs
    while(True):
      c = common.readByte(input)

      # Font Definitons
      if( (FNTDEF1 <= c) & (c<=FNTDEF4) ):
        # In theory, all font defs occur first. Warn if this is not true.
        if(self.pcount!=0):
          logging.warning("Found a FNTDEF after the first char packet in a virtual font")
        m = c - 243
        k = common.readUIntK[m](input)
        c = common.readUInt4(input)
        s = common.readUInt4(input)
        d = common.readUInt4(input)
        a = common.readByte(input)
        ell = common.readByte(input)
        directory = common.readString(input, a)
        fontfile = common.readString(input, ell)

        # Add to font table.
        tf = TexFont(fontfile, s, d, k)
        if( len(self.fontTable) == 0 ):
          self.defaultFont = tf
        self.fontTable[tf.index]=tf

      # Character packets
      elif( c<= LONGCHAR ):
        self.pcount += 1
        if c == LONGCHAR:
          pl = common.readUInt4(input)
          cc = common.readUInt4(input)
        else:
          pl = c
          cc = common.readByte(input)
        width = common.readUInt3( input)
        dvi = common.readString(input,pl)
        if( cc >= len(self.packets) ):
          self.packets.extend( [None]*(cc+1-len(self.packets)) )
        self.packets[cc] = VFChar(cc,width,dvi)

      #Postamble
      elif( c==POST ):
        break;
      else:
        raise VFFormatException( "Unknown opcode %d in virtual font %s" % c, vfname )

    input.close()
