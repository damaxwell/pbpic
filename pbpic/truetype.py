import logging
# import AsciiHex # For conversion to Type42
from geometry import Path
import cStringIO as StringIO
from font import FontMetrics

logging.basicConfig(level=logging.DEBUG)

"""
Documentation on the TrueType file format can be found at:

Apple: http://developer.apple.com/textfonts/ttrefman/RM06/Chap6.html
MS: http://www.microsoft.com/typography/SpecificationsOverview.mspx


A file consists of a number of tables, starting with a directory that indicates the table layout.
Tables are named by a four character name.  The important ones are:

head: 'header', some global font information
maxp: 'maximum profile', contains number of glyphs in font.

hhea: global horizontal metrics
hmtx: glyph horizontal metrics

glyf: individual glyph descriptions
loca: layout of the glyph table

name: a table of strings associated with the font including the font name, postscript name, copyright, etc.
      the strings are not ASCII necessarily, but are described with a variety of encoding schemes

post: data for the postscript interpreter.  some global info (e.g. /ItalicAngle).  Most important:
      a map from glyph index to postscript name (needed to wrap the font in Type 42 format).

The following tables are various subroutines that can be run by the hinting instruction programs.
If we subset a font, we have to keep them.  But we will not use them. Ever.
cvt : 
fpgm:
prep:

OS/2: Windows (!) specific info. Windows says the table is mandatory.  Apple says it's optional. 
It does not seem to appear in subsetted fonts for PostScript.

kern: kerning table

cmap: Maps from character codes in different encoding schemes to glyph indices.  These play
the role of the encoding vector of a Type 1 font but are more sophisticated.  Maps may use
platform specific encodings (e.g. MacRoman) or unicode.  We will rely on some kind of unicode 
table being present for now.

glyphs in a TrueType font are named by an index from 0 to maxp.numGlyphs
A glyph description consists of a header, followed by a hinting instruction program(!), followed
by control point locations that describe the glyph before any gridfitting.  

Glyphs are packed into the glyf table.  The location of a glyph
with a given index can be found in the 'loca' table.
"""


### Constants

# Platform ids, used in multiple tables
PLAT_ID_UNICODE = 0
PLAT_ID_MAC = 1
PLAT_ID_WIN = 3

# id's of defined names in 'name'
NAME_ID_FONT_FAMILY = 1
NAME_ID_FONT_SUBFAMILY = 2
NAME_ID_FONT_FULL_NAME = 4
NAME_ID_PS_NAME = 6

# types of 'post' tables
POST_TYPE_1   = 0x00010000
POST_TYPE_2   = 0x00020000
POST_TYPE_2_5 = 0x00028888
POST_TYPE_3   = 0x00030000
POST_TYPE_4   = 0x00040000


class TTException(Exception):
  def __init__( self, msg ):
    Exception.__init__(self , msg)

class TTMalformedException(TTException):
  def __init__( self, msg ):
    Exception.__init__(self, msg)

class TTUnimplementedException(TTException):
  def __init__( self, msg ):
    Exception.__init__( self, msg)


# Tables are packed binary data.  In many cases a C struct would be the perfect way
# to access the data.  In some cases, the tables have variable length structures.
# The following class treats the table as a stream of data to be interpreted by
# the end user.  It maintains a current position and allows one to read 
# data of a specific type out of the stream (and advance the cuurrent position)

class ttReader:
  def __init__( self, ttdata ):
    self.data = ttdata
    self.pos = 0
    self.end = len(ttdata)

  def skip( self, n ):
    self.pos += n

  def seek( self, p ):
    # Fixme: rangecheck?
    self.pos = p
    
  def tell(self):
    return self.pos

  def dataRemaining( self ):
    return len(self.data)- self.pos
  
  def hasData( self, n ):
    return self.pos+n <= self.end

  # For debugging - print out everything left in the table as integers
  def remainder( self ):
    return [ ord(c) for c in self.data[self.pos:] ]

  # For debugging - print out everything left in the table as a string
  def remainderStr( self ):
    return self.data[self.pos:]

  # Get a Pascal string
  def getPString( self ):
    n = ord(self.data[self.pos])
    v = self.data[self.pos+1: self.pos+1+n]
    self.pos += (1+n)
    return v

  # Get a string of a given length
  def getString( self, len ):
    v = self.data[self.pos: self.pos+len ]
    self.pos+=len
    return v

  # Get an unsigned byte
  def getByte( self ):
    v = ord( self.data[self.pos] )
    self.pos += 1
    return v

  def getUInt16( self ):
    v = 0
    p = self.pos
    for c in self.data[p:p+2]:
      v = v << 8
      v += ord(c)
    self.pos += 2
    return v

  def getUInt32( self ):
    v = 0
    p = self.pos
    for c in self.data[p:p+4]:
      v = v << 8
      v += ord(c)
    self.pos += 4
    return v

  def getInt16( self ):
    v = 0
    p = self.pos
    for c in self.data[p:p+2]:
      v = v << 8
      v += ord(c)
    self.pos += 2
    if v & 1<<15:
      v = v ^ 0xFFFF
      v = -v -1
    return v

  def getInt32( self ):
    v = 0
    p = self.pos
    for c in self.data[p:p+4]:
      v = v << 8
      v += ord(c)
    self.pos += 4
    if v  & 1 << 31:
      v = v ^ 0xFFFFFFFF
      v = -v -1
    return v

  # get a four character code tage (e.g. 'glyf')
  def getTag( self ):
    p = self.pos
    t = self.data[p:p+4];
    self.pos += 4
    return t


# nifty class to set up a struct like object given keyword arguments.
# r = Record( a=3, b='hello')
# r.a -> 3
# r.b -> 'hello'
class Record:
  def __init__(self, **kw):
    self.__dict__.update(kw);


class TrueTypeCollection:
  
  def __init__(self,f):
    self.f = f
    header=ttReader(f.read(12))
    tag = header.getString(4)
    version = header.getUInt32()
    self.nFonts = header.getUInt32()
    oreader = ttReader(f.read(4*self.nFonts))
    self.offsets = [ oreader.getUInt32() for k in xrange(self.nFonts) ]

    directories = []
    for o in self.offsets:
      f.seek(o)
      directories.append(tt_directory(f))
    self.directories = directories
    
    self._psNames = None

  def psNames(self):
    if not self._psNames is None:
      return self._psNames
      
    names = self.nFonts * [ None ]
    for k in xrange(len(self.directories)):
      d = self.directories[k]
      name_t = d.getTable( 'name', self.f)
      if name_t == None:
        logging.warning("Using a TrueType font without a name table")
        continue
      name = tt_name(name_t)
      names[k] = name.nameForId( NAME_ID_PS_NAME )
    self._psNames = names
    return names

  def offsetForFontIndex(self,index):
    return self.offsets[index]

  def offsetForPSName(self,psname):
    i = self.indexForPSName(psname)
    if i < 0:
      return -1    
    return self.offsets[i]

  def indexForPSName(self,psname):
    psNames = self.psNames()
    for k in xrange(len(psNames)):
      if psname == psNames[k]:
        return k
    return -1

class tt_directory:
  def __init__(self, f):
    header = ttReader( f.read(12) )
    self.type = header.getUInt32();
    TRUETYPE_TYPE = 0x00010000
    WIN_TRUETYPE_TYPE = 0x74727565 # 'true'
    TTC_TYPE = 0x74746366
    if self.type != TRUETYPE_TYPE and self.type != WIN_TRUETYPE_TYPE and self.type != TTC_TYPE:
      raise TTMalformedException( "Unknown truetype font type %4x (expected %4x, %4x, or %4x)" % (self.type, TRUETYPE_TYPE, WIN_TRUETYPE_TYPE, TTC_TYPE) )
    self.numTables = header.getUInt16()
    self.tableDirectory = f.read(16*self.numTables)

  def findTable( self, tag ):
    d = ttReader( self.tableDirectory )
    for k in xrange( self.numTables ):
      this_tag = d.getTag()
      if( this_tag == tag ):
        checksum = d.getUInt32();
        offset = d.getUInt32();
        length = d.getUInt32();
        return( offset, length, checksum );
      d.skip( 12 );
    return ( 0 , 0, 0)

  def getTable(self,tag,f):
    (tOffset,tLength, checksum) = self.findTable( tag )
    if tOffset != 0:
      f.seek( tOffset )
      return ttReader( f.read( tLength) )

  def printTables(self):
    d = ttReader( self.tableDirectory )
    for k in xrange( self.numTables ):
      print d.getTag()
      d.skip( 12 );
    

class TrueTypeFont:
  def fromPath( p ):
    f = file( p, 'rb' )
    return TrueTypeFont( f )
  fromPath = staticmethod( fromPath )

  def fromData( d ):
    return TrueTypeFont( StringIO.StringIO( d ) )
  fromData = staticmethod( fromData )

  def __init__( self, f, offsetTableStart=0 ):
    """Initialize font from a seekable stream. (e.g. a file or memory stream).  We take ownership
    of the stream.  Use factory methods fromPath and fromData for convenience."""
    self.f = f;
    self.offsetTableStart = offsetTableStart
    f.seek(self.offsetTableStart)
    
    self.directory = tt_directory(f)
    
    self.metrics = {}
    self.paths={}

    t_maxp = self.getTable( 'maxp' )
    if not t_maxp:
      raise TTMalformedException( "Missing 'maxp' table." )
    self.maxp = self._getmaxp( t_maxp )

    t_head = self.getTable( 'head' )
    if not t_head:
      raise TTMalformedException( "Missing 'head' table." )
    self.head = self._gethead( t_head )
    
    
    t_hhea = self.getTable( 'hhea' )
    if not t_hhea:
      raise TTMalformedException( "Missing 'hhea' table." )
    self.hhea = self._gethhea( t_hhea)
    

    t_loca = self.getTable( 'loca' )
    if not t_loca:
      raise TTMalformedException( "Missing 'loca' table." )
    self.loca = self._getloca( t_loca )

    t_hmtx = self.getTable( 'hmtx' )
    if not t_hmtx:
      raise TTMalformedException( "Missing 'hmtx' table." )
    self.hmtx = t_hmtx

    (self.glyfOffset, self.glyfLen, checksum) = self.findTable( 'glyf' )
    if self.glyfOffset == 0:
      raise TTMalformedException( "Missing 'glyf' table." )

    # Wait to load name table
    self.name = None
    
    # Wait to load post table
    self.post = None

    self.cmap = None

  # def asType42( self, name=None ):
  #   if name == None:
  #     name = self.PSName()
  #   if name[0] != '/':
  #     name = '/' + name
  #   ps_str =  "14 dict begin /FontName %s def\n" % name
  #   ps_str += "/FontType 42 def /FontMatrix [ 1 0 0 1 0 0 ] def /PaintType 0 def\n "
  #   # For now put a standard encoding.  The name /StandardEncoding doesn't seem to work, so
  #   # we'll make it explicit.
  #   ps_str += "/Encoding 256 array 0 1 255{1 index exch/.notdef put}for\n"
  #   k = 0
  #   for s in AdobeStandardEncoding:
  #     ps_str += "dup %d %s put\n" % (k,s)
  #     k += 1
  #   ps_str +="readonly def\n"
  # 
  #   # Copy computation of BBox from adobe output
  #   ps_str += "/FontBBox [1000 %d 1 index div %d 2 index div %d 3 index div %d 5 -1 roll div]cvx def\n" \
  #     % (self.head.xMin, self.head.yMin, self.head.xMax, self.head.yMax )
  #   ps_str += "/CharStrings << \n"
  #   self._load_post()
  #   n = 0
  #   for glyphName in self.post.glyphNames( self.maxp.numGlyphs):
  #     ps_str += "%s %d\n" % (glyphName,n)
  #     n+=1
  #   ps_str += ">> def\n/sfnts [\n"
  #   # The Type 42 spec says that to support older PS drivers (older than 2.012) we need to 
  #   # ensure that any breaks in the font data occur at table or glyph boundaries.  I'm
  #   # in a hurry, so we won't do this for now.  But we do have to ensure that we don't break the
  #   # string length implementation limit of 65536.  We'll AsciiHex for now (Ascii85 would be best
  #   # when it's written, and we have to pad each string with a null byte.
  # 
  #   # Find the file length
  #   f = self.f
  #   f.seek(0,2)
  #   remaining = f.tell()
  #   f.seek(0)
  #   desired = 65000/2
  #   while remaining > 0:
  #     if desired > remaining:
  #       desired = remaining
  #     s = f.read( desired )
  #     ps_str += "<"
  #     ps_str += AsciiHex.asciihex_encode( s )[0]
  #     ps_str += "00>\n"
  #     remaining -= desired
  #   
  #   ps_str += "] def\ncurrentdict dup/FontName get exch definefont pop end"
  #   return ps_str

  def _load_name( self ):
    if self.name == None:
      name_t = self.getTable( 'name' )
      if name_t == None:
        logging.warning("Using a TrueType font without a name table")
        return
      self.name = tt_name( name_t)

  def _load_post( self ):
    if self.post == None:
      post_t = self.getTable( 'post' )
      if post_t == None:
        raise TTMalformedException( "Missing 'post' table." )
      self.post = tt_post( post_t)

  def _load_cmap( self ):
    if self.cmap == None:
      cmap_t = self.getTable( 'cmap' )
      if cmap_t == None:
        raise TTMalformedException( "Missing 'cmap' table." )
      self.cmap = cmap_t

  # Times, Helvetica, Optima, etc.
  def familyName( self ):
    self._load_name()
    if( self.name == None ):
      return None
    return self.name.nameForId( NAME_ID_FONT_FAMILY )


  # Regular, Bold, Italic, Bold Italic, etc.
  def subfamilyName( self ):
    self._load_name()
    if( self.name == None ):
      return None
    return self.name.nameForId( NAME_ID_FONT_SUBFAMILY )

  # Times Italic, etc.
  def fullName( self ):
    self._load_name()
    if( self.name == None ):
      return None
    return self.name.nameForId( NAME_ID_FONT_FULL_NAME )

  # Times-Roman (no slash)
  def PSName( self ):
    self._load_name()
    if( self.name == None ):
      return None
    return self.name.nameForId( NAME_ID_PS_NAME )

  def printTables( self ):
    d = ttReader( self.tableDirectory )
    print "Font with %d tables" % self.numTables
    for k in xrange( self.numTables ):
      this_tag = d.getTag()
      d.skip(4)
      offset = d.getUInt32();
      length = d.getUInt32();
      print("Table %d %s offset %d length %d" %( k, this_tag, offset, length) )
    
  def findTable( self, tag ):
    return self.directory.findTable(tag)

  def metricsForGlyph( self, glyph ):
    m = self.metrics.get(glyph,None)
    if m == None:
      hmtx = self.hmtx
      hmtx.seek(0)
      nLHM = self.hhea.numOfLongHorMetrics 
      if( glyph > nLHM ):
        hmtx.seek( 4*(nLHM-1) )
        advance = hmtx.getUInt16()
        hmtx.skip( 2+(glyph-nLHM) )
        lsb = hmtx.getInt16()
        return ( advance, lsb )
      hmtx.seek( 4*(glyph - nLHM) )
      hadvance = float(hmtx.getUInt16())/self.head.unitsPerEm
      hsb = float(hmtx.getInt16())/self.head.unitsPerEm
      
      return FontMetrics(hadvance,0,hsb,0)

  def pathForGlyph( self, glyph ):
    p = self.paths.get(glyph,None)
    if p == None:
      p = self.glyphDataForGlyph(glyph).charPath()
      self.paths[glyph] = p
    return p

  def getTableAsString( self, tag ):
    (tOffset,tLength, checksum) = self.findTable( tag )
    if tOffset != 0:
      self.f.seek( tOffset )
      return self.f.read( tLength)
    return None

  def getTable( self, tag ):
    (tOffset,tLength, checksum) = self.findTable( tag )
    if tOffset != 0:
      self.f.seek( tOffset )
      return ttReader( self.f.read( tLength) )
    return None

  def glyphDataForGlyph( self, glyph ):
    start = self.loca[glyph];
    end = self.loca[glyph+1];
    if start == end:
      return GlyphData( ttReader( '' ), self.head.unitsPerEm )
    self.f.seek( self.glyfOffset + start )    
    return GlyphData( ttReader(self.f.read(end-start)), self.head.unitsPerEm )

  # def stringPath( self, s, size ):
  #   p = Path.Path()
  #   pos = 0;
  #   self._load_cmap()
  #   # FIXME: Not sure if this calculation is correct
  #   scale = (1.*size) / self.head.unitsPerEm 
  #   tm = [ scale, 0, 0, scale, 0, 0 ]
  #   for c in s:
  #     gIndex = self.cmap.indexForChar( ord(c) )
  #     g = self.glyphForIndex( gIndex )
  #     gPath = g.charPath()
  #     gPath.transform( tm )
  #     p += gPath
  #     (advance, lsb) = self.metricsForGlyph( gIndex )
  #     tm[4] += advance * scale
  #   return p

  def cmapForPlatformEncoding(self, platform, encoding):
    self._load_cmap()
    cmap = self.cmap

    cmap.seek(0)
    version = cmap.getUInt16()
    numTables = cmap.getUInt16()

    for k in xrange(numTables):
      platID = cmap.getUInt16()
      platEnc = cmap.getUInt16()
      offset = cmap.getUInt32()
      if platID == platform:
        if (encoding is None) or (encoding==platEnc):
          cmap.seek( offset )
          return tt_cmap(cmap)

    return None

  def cmapForUnicode(self):
    cmap = self.cmapForPlatformEncoding(PLAT_ID_UNICODE,None) # any unicode encoding
    if cmap is None:
      cmap = self.cmapForPlatformEncoding(PLAT_ID_WIN,1) # encoding 1 is unicode
    return cmap
    

  def psNameForIndex( self, n ):
    self._load_post()
    return self.post.glyphForIndex( n )

  def _gethead( self, head ):
    head.skip( 16 )
    flags = head.getUInt16()
    unitsPerEm = head.getUInt16()
    head.skip( 16 ) 
    xMin = head.getInt16()
    yMin = head.getInt16()
    xMax = head.getInt16()
    yMax = head.getInt16()
    head.skip( 6 )    
    locType = head.getUInt16()

    return Record( flags = flags, unitsPerEm=unitsPerEm, locType=locType, xMin=xMin, xMax=xMax,
    yMin=yMin, yMax = yMax )

  def _getmaxp( self, maxp ):
    maxp.skip( 4 )
    numGlyphs = maxp.getUInt16()
    return Record(numGlyphs=numGlyphs)

  def _gethhea( self, hhea ):
    hhea.skip(4) # skip version
    ascent = hhea.getInt16()
    descent = hhea.getInt16()
    lineGap = hhea.getInt16()
    hhea.skip(24)
    numOfLongHorMetrics = hhea.getUInt16()
    return Record( ascent=ascent, descent=descent, lineGap=lineGap, numOfLongHorMetrics=numOfLongHorMetrics )

  def _getloca( self, loca ):
    if self.head.locType == 0:
      return [ 2*loca.getUInt16() for k in xrange( self.maxp.numGlyphs + 1 ) ]
    return [ loca.getUInt32() for k in xrange( self.maxp.numGlyphs + 1 ) ]


class GlyphData:
  def __init__( self, g, unitsPerEm ):
    self.g = g
    self.unitsPerEm = float(unitsPerEm)

  # Composite glyphs are denoted by a negative number of contours.
  def isComposite( self ):
    self.g.seek( 0 )
    return self.g.getInt16( ) < 0

  def size( self ):
    return len(self.g.data)
  
  # Helper functions to read coordinate data from a path
  def readXCoords( self, flags ):
    x = [0] * len(flags)
    np = 0
    for f in flags:
      onoff = f & 1 # zero means off
      xShort = f  & (1<<1);
      xSame = f   & (1<<4);
      if xShort:
        thisx = self.g.getByte()/self.unitsPerEm
        if( xSame == 0 ):
          thisx*= -1
        x[np] = thisx
      elif xSame:
        thisx = 0
      else:
        thisx = self.g.getInt16()/self.unitsPerEm

      if np == 0:
        x[np] = thisx
      else:
        x[np] = x[np-1]+thisx
      np = np + 1
    return x

  # Helper functions to read coordinate data from a path
  def readYCoords( self, flags ):
    y = [0] * len(flags)
    np = 0
    for f in flags:
      onoff = f & 1 # zero means off
      yShort = f  & (1<<2);
      ySame = f   & (1<<5);
      if yShort:
        thisy = self.g.getByte()/self.unitsPerEm
        if( ySame == 0 ):
          thisy*= -1
        y[np] = thisy
      elif ySame:
        thisy = 0
      else:
        thisy = self.g.getInt16()/self.unitsPerEm

      if np == 0:
        y[np] = thisy
      else:
        y[np] = y[np-1]+thisy
      np = np + 1
    return y

  def getOutline( self ):
      numContours = self.g.getInt16()
      if numContours == 0:
        return ( [],[],[],[] )
      "%d contours xMin %d yMin %s xMax %d yMax %d" % ( numContours, self.g.getInt16(), self.g.getInt16(),self.g.getInt16(), self.g.getInt16() )
      endContours = [ self.g.getInt16() for k in xrange(numContours) ]
      #print "contour end", endContours
      instLength = self.g.getInt16()
      #print "instruction length %d" % instLength
      self.g.skip( instLength )
      numPts = endContours[-1] + 1
      flags = [0]*numPts
      k = 0
      #print self.g.remainder()
      while k < numPts:
        flag = self.g.getByte()
        onCurve = flag & 1;
        xShort = flag  & (1<<1);
        yShort = flag  & (1<<2);
        repeat = flag  & (1<<3);
        xSame = flag   & (1<<4);
        ySame = flag   & (1<<5);
      
        if repeat:
          reps = self.g.getByte();
          flags[k:k+reps+1] = [flag] * (reps+1)
          k += (reps+1)
        else:
          flags[k] = flag
          k += 1
      onoff = [0] * numPts
      y = [0] * numPts

      x = self.readXCoords( flags );
      y = self.readYCoords( flags );
      offon = [ f & 1 for f in flags ]
      return (endContours, x, y, offon )

  # Conversion of a TT outline to a sequence of path operations.  Contours are simply an arbitrary
  # sequence of points each with a flag of of or on.  A path can consist entirely of 'off' points.
  # If two adjacent points are 'off', then their midpoint is an implicit 'on' point.  An 'off' point is
  # the control point of a quadratic bezier. Two adjacent 'on' points yield a straight line segment.
  #
  # The outline consists of a number of contours of the above form.  There is an implicit closepath
  # at the end of each contour.
  #
  # FIXME: The following code works, but it should be simplified.  Looks like  no need to track
  # the current point anymore. Also, seems like you should be able to analyse by segment rather
  # than by point for easier control flow.
  def charPath( self ):
    (contourEnds,x,y,on) = self.getOutline()
    p = Path()
    start = 0
    for end in contourEnds:
      i = end; j = start
      # If we are starting on an off point, we don't have a current point yet!
      if not on[j]:
        # The previous point isn't on either! Use the midpoint.
        if not on[i]:
          prevOn = False
          cpx = (x[i] + x[j])/2.
          cpy = (y[i] + y[j])/2.
        else:
          # The previous point is on.  Use it as the start point (and swallow it).
          prevOn = True
          cpx = x[i];
          cpy = y[i];
          i -= 1
      else:
        # The easy case: starting on an 'on' point
        prevOn = True
        cpx = x[j]
        cpy = y[j]
        j+=1
      p.moveto( cpx, cpy )
      while j <= i:
        if on[j]:
          # Two adjacent 'on' points are a lineto, otherwise we've already curveto'ed to
          # get here and we do nothing.
          if prevOn:
            p.lineto( x[j], y[j] )
#           print "%d %d lineto" % ( x[j], y[j] )
            cpx = x[j]
            cpy = y[j]
            j += 1
          prevOn = True
        else:
          # A curve to from the currentpoint via x[j] y[j] to a point we need to
          # determine
          prevOn = False
          # Find the next index; wrap if need be.
          nj = j+1
          if nj > end:
            nj = start
          # Determine the next onto point. It will either be implicit or explicit.
          if not on[nj]:
            tx = (x[j]+x[nj])/2
            ty = (y[j]+y[nj])/2
          else:
            tx = x[nj]
            ty = y[nj]
#         p.quadto( x[j], y[j], tx, ty )
          p.curveto( cpx/3.+2/3.*x[j], cpy/3.+2/3.*y[j],  2*x[j]/3. + tx/3., 2*y[j]/3.+ty/3., tx, ty )
#         print "%d %d %d %d %d %d curveto" % ( cpx/3.+2/3.*x[j], cpy/3.+2/3.*y[j], 
#         2*x[j]/3. + tx/3., 2*y[j]/3.+ty/3., tx, ty )
          cpx = tx; cpy = ty
          j+=1
      p.closepath()
      start = end + 1
    
    return p

"""
def outlineToPS( contours, x, y, on ):
  start = 0
  print "newpath"
  first = True
  for i in contours:
    end = i
    j = start
    if not on[j]:
      if not on[i]:
        prevOn = False
        cpx = (x[i] + x[j])/2.
        cpy = (y[i] + y[j])/2.
      else:
        prevOn = True
        cpx = x[i];
        cpy = y[i];
        i -= 1
    else:
      prevOn = True
      cpx = x[j]
      cpy = y[j]
      j+=1
    print "%d %d moveto" % ( cpx, cpy )
    while j <= i:
      if on[j]:
        if prevOn:
          print "%d %d lineto" % ( x[j], y[j] )
          cpx = x[j]
          cpy = y[j]
          j += 1
        prevOn = True
      else:
        prevOn = False
        nj = j+1
        if nj > i:
          nj = start
        if not on[nj]:
          tx = (x[j]+x[nj])/2
          ty = (y[j]+y[nj])/2
        else:
          tx = x[nj]
          ty = y[nj]
        print "%d %d %d %d %d %d curveto" % ( cpx/3.+2/3.*x[j], cpy/3.+2/3.*y[j], 
        2*x[j]/3. + tx/3., 2*y[j]/3.+ty/3., tx, ty )
        cpx = tx; cpy = ty
        j+=1
    start = end + 1
    print "closepath\n"
"""

class tt_post:
    
  def __init__( self, post ):
    self.post = post

    format = post.getInt32()
    self.format = format
    
    self.italicAngle = post.getInt32()
    self.underlinePos = post.getInt16()
    self.underlineThick = post.getInt16()
    self.isFixedPitch = post.getInt32() # For a flag!
    self.minMemT42 = post.getInt32()
    self.maxMemT42 = post.getInt32()
    self.minMemT1 = post.getInt32()
    self.maxMemT1 = post.getInt32()

    if format == POST_TYPE_1:
      self.glyphForIndex = StdMacTrueTypeEncoding
    elif format == POST_TYPE_2:
      self.glyphForIndex = self._type2GlyphForIndex
      self.numGlyphs = post.getUInt16()
      self._loadType2GlyphNameTable()
    elif format == POST_TYPE_2_5:
      self.glyphForIndex = self._type25GlyphForIndex
      self.numGlyphs = post.getUInt16()
    elif format == POST_TYPE_3:
      self.glyphForIndex = self._type3GlyphForIndex
    elif format == POST_TYPE_4:
      self.glyphForIndex = self._type4GlyphForIndex
    else:
      raise TTMalformedException( "Unknown format type for 'post' table: %x", format )

  def __repr__( self ):
    if self.format == POST_TYPE_1:
      return "'post' table type 1: standard mac encoding"
    elif self.format == POST_TYPE_2:
      return "'post' table type 2: standard mac encoding +...\n%s" % self.extraGlyphNames
    elif self.format == POST_TYPE_2_5:
      return "'post' table type 2.5: shuffled standard mac encoding:%s" % [ self.glyphForIndex(k) for k in xrange(self.numGlyphs) ]
    elif self.format == POST_TYPE_3:
      return "'post' table type 3: no glyph names given"
    elif self.format == POST_TYPE_4:
      return "'post' table type 4: a CJK encoding"
  
  def glyphNames( self, maxGlyph ):
    # FIXME Do something faster in the future. (Write custom iterators...)
    return (self.glyphForIndex(k) for k in xrange( maxGlyph ))

  def _loadType2GlyphNameTable( self ):
    self.post.seek( 8*4 + 2 )
    self.glyphNameInd = [ self.post.getUInt16() for k in xrange( self.numGlyphs ) ]
    maxInd = max(self.glyphNameInd )
    nExtra = maxInd - 257
    if nExtra <= 0:
      self.extraGlyphNames = []
    else:
      self.extraGlyphNames = [ "/" + self.post.getPString() for k in xrange( nExtra ) ]

  def _type1GlyphForIndex( self, k ):
    return StdMacTrueTypeEncoding[k]
  
  def _type2GlyphForIndex( self, k ):
    name_ind = self.glyphNameInd[ k ]
    if name_ind < 258:
      return StdMacTrueTypeEncoding[name_ind]
    return self.extraGlyphNames[name_ind-258]

  def _type25GlyphForIndex( self, k ):
    self.post.seek( 8*4 + 2 + k )
    return StdMacTrueTypeEncoding[ self.post.getByte() ] 

  # For type three there is no table.  So what to do? Our convention:
  # 0 -> /.notdef (of course)
  # k -> /unknownglyph[k]
  # These strings can then be put in the encoding table
  def _type3GlyphForIndex( self, k ):
    if k == 0:
      return "/.notdef"
    return "/unknownglyph%d" % k

  # For CJK fonts, the PS name is /a<hex>
  def _type4GlyphForIndex( self, k ):
    self.post.seek( 8*4 + 2*k )
    index = self.post.getUInt16()
    return "/a%x" % index
    

AdobeStandardEncoding = [
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/space',
'/exclam',
'/quotedbl',
'/numbersign',
'/dollar',
'/percent',
'/ampersand',
'/quoteright',
'/parenleft',
'/parenright',
'/asterisk',
'/plus',
'/comma',
'/hyphen',
'/period',
'/slash',
'/zero',
'/one',
'/two',
'/three',
'/four',
'/five',
'/six',
'/seven',
'/eight',
'/nine',
'/colon',
'/semicolon',
'/less',
'/equal',
'/greater',
'/question',
'/at',
'/A',
'/B',
'/C',
'/D',
'/E',
'/F',
'/G',
'/H',
'/I',
'/J',
'/K',
'/L',
'/M',
'/N',
'/O',
'/P',
'/Q',
'/R',
'/S',
'/T',
'/U',
'/V',
'/W',
'/X',
'/Y',
'/Z',
'/bracketleft',
'/backslash',
'/bracketright',
'/asciicircum',
'/underscore',
'/quoteleft',
'/a',
'/b',
'/c',
'/d',
'/e',
'/f',
'/g',
'/h',
'/i',
'/j',
'/k',
'/l',
'/m',
'/n',
'/o',
'/p',
'/q',
'/r',
'/s',
'/t',
'/u',
'/v',
'/w',
'/x',
'/y',
'/z',
'/braceleft',
'/bar',
'/braceright',
'/asciitilde',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/exclamdown',
'/cent',
'/sterling',
'/fraction',
'/yen',
'/florin',
'/section',
'/currency',
'/quotesingle',
'/quotedblleft',
'/guillemotleft',
'/guilsinglleft',
'/guilsinglright',
'/fi',
'/fl',
'/.notdef',
'/endash',
'/dagger',
'/daggerdbl',
'/periodcentered',
'/.notdef',
'/paragraph',
'/bullet',
'/quotesinglbase',
'/quotedblbase',
'/quotedblright',
'/guillemotright',
'/ellipsis',
'/perthousand',
'/.notdef',
'/questiondown',
'/.notdef',
'/grave',
'/acute',
'/circumflex',
'/tilde',
'/macron',
'/breve',
'/dotaccent',
'/dieresis',
'/.notdef',
'/ring',
'/cedilla',
'/.notdef',
'/hungarumlaut',
'/ogonek',
'/caron',
'/emdash',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/AE',
'/.notdef',
'/ordfeminine',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/Lslash',
'/Oslash',
'/OE',
'/ordmasculine',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef',
'/ae',
'/.notdef',
'/.notdef',
'/.notdef',
'/dotlessi',
'/.notdef',
'/.notdef',
'/lslash',
'/oslash',
'/oe',
'/germandbls',
'/.notdef',
'/.notdef',
'/.notdef',
'/.notdef'
]


# TrueType files use a postscript encoding based on MacRoman. The 'post' table of a truetype
# file encodes whether the glyphs uses this encoding, and if not what the deviations from
# it are.
StdMacTrueTypeEncoding = [
"/.notdef",
"/.null",
"/nonmarkingreturn",
"/space",
"/exclam",
"/quotedbl",
"/numbersign",
"/dollar",
"/percent",
"/ampersand",
"/quotesingle",
"/parenleft",
"/parenright",
"/asterisk",
"/plus",
"/comma",
"/hyphen",
"/period",
"/slash",
"/zero",
"/one",
"/two",
"/three",
"/four",
"/five",
"/six",
"/seven",
"/eight",
"/nine",
"/colon",
"/semicolon",
"/less",
"/equal",
"/greater",
"/question",
"/at",
"/A",
"/B",
"/C",
"/D",
"/E",
"/F",
"/G",
"/H",
"/I",
"/J",
"/K",
"/L",
"/M",
"/N",
"/O",
"/P",
"/Q",
"/R",
"/S",
"/T",
"/U",
"/V",
"/W",
"/X",
"/Y",
"/Z",
"/bracketleft",
"/backslash",
"/bracketright",
"/asciicircum",
"/underscore",
"/grave",
"/a",
"/b",
"/c",
"/d",
"/e",
"/f",
"/g",
"/h",
"/i",
"/j",
"/k",
"/l",
"/m",
"/n",
"/o",
"/p",
"/q",
"/r",
"/s",
"/t",
"/u",
"/v",
"/w",
"/x",
"/y",
"/z",
"/braceleft",
"/bar",
"/braceright",
"/asciitilde",
"/Adieresis",
"/Aring",
"/Ccedilla",
"/Eacute",
"/Ntilde",
"/Odieresis",
"/Udieresis",
"/aacute",
"/agrave",
"/acircumflex",
"/adieresis",
"/atilde",
"/aring",
"/ccedilla",
"/eacute",
"/egrave",
"/ecircumflex",
"/edieresis",
"/iacute",
"/igrave",
"/icircumflex",
"/idieresis",
"/ntilde",
"/oacute",
"/ograve",
"/ocircumflex",
"/odieresis",
"/otilde",
"/uacute",
"/ugrave",
"/ucircumflex",
"/udieresis",
"/dagger",
"/degree",
"/cent",
"/sterling",
"/section",
"/bullet",
"/paragraph",
"/germandbls",
"/registered",
"/copyright",
"/trademark",
"/acute",
"/dieresis",
"/notequal",
"/AE",
"/Oslash",
"/infinity",
"/plusminus",
"/lessequal",
"/greaterequal",
"/yen",
"/mu",
"/partialdiff",
"/summation",
"/product",
"/pi",
"/integral",
"/ordfeminine",
"/ordmasculine",
"/Omega",
"/ae",
"/oslash",
"/questiondown",
"/exclamdown",
"/logicalnot",
"/radical",
"/florin",
"/approxequal",
"/Delta",
"/guillemotleft",
"/guillemotright",
"/ellipsis",
"/nonbreakingspace",
"/Agrave",
"/Atilde",
"/Otilde",
"/OE",
"/oe",
"/endash",
"/emdash",
"/quotedblleft",
"/quotedblright",
"/quoteleft",
"/quoteright",
"/divide",
"/lozenge",
"/ydieresis",
"/Ydieresis",
"/fraction",
"/currency",
"/guilsinglleft",
"/guilsinglright",
"/fi",
"/fl",
"/daggerdbl",
"/periodcentered",
"/quotesinglbase",
"/quotedblbase",
"/perthousand",
"/Acircumflex",
"/Ecircumflex",
"/Aacute",
"/Edieresis",
"/Egrave",
"/Iacute",
"/Icircumflex",
"/Idieresis",
"/Igrave",
"/Oacute",
"/Ocircumflex",
"/apple",
"/Ograve",
"/Uacute",
"/Ucircumflex",
"/Ugrave",
"/dotlessi",
"/circumflex",
"/tilde",
"/macron",
"/breve",
"/dotaccent",
"/ring",
"/cedilla",
"/hungarumlaut",
"/ogonek",
"/caron",
"/Lslash",
"/lslash",
"/Scaron",
"/scaron",
"/Zcaron",
"/zcaron",
"/brokenbar",
"/Eth",
"/eth",
"/Yacute",
"/yacute",
"/Thorn",
"/thorn",
"/minus",
"/multiply",
"/onesuperior",
"/twosuperior",
"/threesuperior",
"/onehalf",
"/onequarter",
"/threequarters",
"/franc",
"/Gbreve",
"/gbreve",
"/Idotaccent",
"/Scedilla",
"/scedilla",
"/Cacute",
"/cacute",
"/Ccaron",
"/ccaron",
"/dcroat"]

class tt_cmap:
  def __init__( self, cmap ):
    format = cmap.getUInt16()
    if format != 4:
      raise TTUnimplementedException( "truetype cmap type %d not supported.  Wanted type 4." % format )
    
    map_len = cmap.getUInt16() # Will we ever use this?
    cmap.skip(2)
    segCount = cmap.getUInt16()/2
        
    cmap.skip( 6 )# At endcode array
    self.endCode = [ cmap.getUInt16() for k in xrange( segCount ) ]
    zero = cmap.getUInt16()
    if( zero != 0 ):
      raise Exception( "Malformed tt font: expected a zero in the cmap array found %x" % zero )
    self.startCode = [ cmap.getUInt16() for k in xrange( segCount ) ]
    self.delta = [ cmap.getInt16() for k in xrange( segCount ) ]
    self.rangeOffset = [ cmap.getUInt16() for k in xrange( segCount ) ]

    self.glyphIndexArray = [ cmap.getUInt16() for k in xrange( cmap.dataRemaining() ) ]

  def glyphForChar( self, c ):
    if isinstance(c,str):
      c=ord(c)
    k = 0
    for n in self.endCode:
      if n > c:
        break
      k += 1

    # See if c falls in the range of this segment
    if c < self.startCode[k]:
      return 0
    
    delta = self.delta[k]
    ro = self.rangeOffset[k]

    if ro == 0:
      return  c+delta
    
    gIndex = (ro/2) - (len(self.rangeOffset) - k ) + ( c - self.startCode[k] ) 
    index = self.glyphIndexArray[ gIndex  ] 
    return index

  def glyphsForString( self, s ):
    return [ self.glyphForChar(c) for c in s ]

class tt_name:
  def __init__( self, name ):
    self.name = name

    self.format = name.getUInt16()
    self.count = name.getUInt16()
    self.stringOffset = name.getUInt16()

  def nameRecord( self, k ):
    self.name.seek( 6 + k * 12) # Start of name records + k * len_name_rec
    names = self.name
    platform_id = names.getUInt16()
    platform_spec_id = names.getUInt16()
    language_id = names.getUInt16()
    name_id = names.getUInt16()
    length = names.getUInt16()
    offset = names.getUInt16()
    return Record( platform_id = platform_id, platform_spec_id = platform_spec_id, language_id=language_id,
      name_id = name_id, length = length, offset = offset )
  
  def nameForId( self, id, platform_id = -1 ):
    for k in xrange( self.count ):
      nr = self.nameRecord( k )
      if( nr.name_id == id ):
        if( platform_id < 0 or (platform_id == nr.platform_id) ):
          # FIXME: Ought to do something about the encoding of the string!
          self.name.seek( self.stringOffset + nr.offset );
          return self.name.getString( nr.length )
    return None
    
  def printNameRecords( self ):
    for k in xrange( self.count ):
      nr = self.nameRecord( k )
      print "Name record: plat_id %d plat_spec_id %d lang_id %d name_id %d len %d off %d" % (nr.platform_id,
        nr.platform_spec_id, nr.language_id, nr.name_id, nr.length, nr.offset ) 

  def printStringsForPlatform( self, plat_id ):
    for k in xrange( self.count ):
      nr = self.nameRecord( k )
      if nr.platform_id == plat_id:
        self.name.seek( self.stringOffset + nr.offset );
        s = self.name.getString( nr.length )
        print "String %d: (id %d) %s" % (k, nr.name_id, s )

if __name__ == '__main__':

  import sys
  ttf_file=sys.argv[1]
  font = TrueTypeFont( open(ttf_file,'r') )
  
  font.printTables()
    
# cmap = tt_cmap( font.getTable('cmap') )
  post = tt_post( font.getTable('post'))
  print post
# print font.familyName()
# print font.subfamilyName()
# print font.fullName()
# print font.PSName()
# quit()

  """
  print font.asType42(name="O-R")
  print ""/O-R findfont 12 scalefont setfont
40 40 translate
0 0 moveto
(Hello world!) show""
  quit()
"""   
  if len(sys.argv) > 2:
    s = sys.argv[2]

    print "72 72 translate 0.001 0.001 scale 50 50 scale"
    for c in s:
#     n = cmap.indexForChar( ord(c) )
      n = 1
      g = font.glyphForIndex( n )
      (contours, x, y, on ) = g.getOutline( )
      if len(contours) > 0:
        outlineToPS( contours, x, y, on )
        print "fill\n"
      (advance,lsb) = font.metricsForGlyph( n )
      print "%d 0 translate" % advance
