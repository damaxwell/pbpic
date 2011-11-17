import resource, font
import logging
import re
import pbpic.type1, pbpic.pbpfont, pbpic.sysfont

"""dvipdfm fontmap entries are described in the dvipdfm user's manual.

  each entry is a line:

  texFontName encoding psFontName options

  texFontName corresponds with the TFM file name.

  encoding contains the name of a .enc file.
    If missing, or equal to 'default' or 'none', use the Type 1 font's encoding vector.

  pfbFontName contains either the file name of a Type 1 pfb font, or a base 13 postscript font name.
    If missing, use texFontName.

  The options (which are all optional) are:
    -r (reencode to avoid control characters, something about a bug in Acrobat)
    -e number (extend font horizontally multiplying widths by 'number')
    -s number (slant the font by the given number)
"""

class MapFileEntry:
  def __init__(self, texFontName, encoding, pfbFontName, opts ):
    self.texFontName = texFontName
    self.encoding = encoding
    self.pfbFontName = pfbFontName
    # Dictionary of character keys / values for the options
    self.opts = opts

  def __str__(self):
    return "FontMapEntry:%s (encoding %s) (PFB Font %s) (opts %s)" % (self.texFontName, self.encoding, self.pfbFontName, self.opts)

class DviPdfMapFile:

  # When initially reading the font map, we just parse enough to determine which fonts are listed
  # the string that is the entry associated with each font.  When asked for a given font entry, we 
  # parse the entry and return a FontMapEntry
  
  def __init__( self, mapFilePath ):
    self.mapFilePath = mapFilePath
    self.mapDict = {}

    with open(mapFilePath, "r" ) as f:
      contents = f.read()
    
    # Matches: #1:filename #2:other stuff.  We decode the other stuff later if need be.
    line_re=re.compile("^(\w[\w-]+)(?:[ \t]+(.+))?",re.M)
    lineIter = line_re.finditer(contents)
    for line in lineIter:
      g=line.groups()
      entry = g[1]
      if entry == None:
        entry = ""
      self.mapDict[g[0]] = entry

  def __getitem__(self,texFontName):
    return self.getEntry(texFontName)

  def getEntry( self, texFontName ):
    mapEntry = self.mapDict.get( texFontName, None )
    if mapEntry == None:
      logging.warning("Missing font map entry for %s in mapfile %s", texFontName, self.mapFilePath )
      return MapFileEntry( texFontName, None, texFontName, None );
      
    entry_re = re.compile("(?:(\w[\w-]+))?(?:[ \t]+(\w[\w-]+))?(?:[ \t]+(.+))?")
    entry = entry_re.match( mapEntry )
    g = entry.groups();
    encoding = g[0];
    if (encoding == "default") or (encoding == "none"):
      encoding = None

    pfbFontName = g[1];
    if( pfbFontName == None ):
      pfbFontName = texFontName

    odict = {}
    if g[2] != None:
      opt_re=re.compile("-([esr])(?:[ \t]+([-+]?(?:\d+(?:\.\d*)?|\.\d+)))?")
      olist = opt_re.findall(g[2])
      for opt in olist:
        odict[opt[0]] = opt[1]

    return MapFileEntry( texFontName, encoding, pfbFontName, odict )

def encodingVectorFromFile( filePath ):
  with open( filePath, "r" ) as f:
    contents = f.read()

  start_re = re.compile("(/[^ ]+)[ ]+\[", re.M)
  m = start_re.search( contents )
  contents = contents[m.end(0):]

  name_re = re.compile("(/[^ \n\r\t]+)[ \n\r\t]")
  elist = [ m.group(1) for m in name_re.finditer( contents ) ]
  return pbpic.type1.EncodingVector( elist )


Base13Names = [ "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
                "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
                "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique", "Symbol"]
Base13Fonts = dict( (k,k) for k in Base13Names )


class FontTable:
  def __init__( self ):
    self.mapFile = resource.findMapFile( "dvipdfm" )
    self.fontdict = {}

  def findFont( self, texFontName ):
    """Look up a device font corresponding to the tex font with name "texFontName".  
    Currently a device font is a Type 1 font together with an encoding vector,
    as listed in tex's map file (dvipdfm.map).  If a font is found, it is added
    to the font table automatically."""
    
    font = self.fontdict.get(texFontName, None)
    if font:
      return font

    # Try the map file to see if there is an entry there.  There should be one.
    mapEntry=self.mapFile[texFontName]
    failSafeFont = 'cmr12'
    if mapEntry == None:
      if texFontName == failSafeFont:
        raise Exception( "Map file missing basic font %s." % failSafeFont ) 
      logging.warning( "Map file missing entry for tex font %s.\nUsing %s instead.", texFontName, failSafeFont )
      return self.findFont( failSafeFont )

    # The pfbFontName in the entry is either a base13 postscript name or the name of a pfb file in the tex
    # directory system.  I don't know what to do about the base13 case right now.

    if not Base13Fonts.get(mapEntry.pfbFontName) is None:
      # FIXME: Do something?
      raise NotImplementedException("Base 13 font %s in map file not supported" % pfbFontName)


    try:
      pfbpath = resource.findPFBPath(mapEntry.pfbFontName)
    except resource.TexResourceNotFound:
      if texFontName == failSafeFont:
        raise Exception("Tex system missing basic font %s." % failSafeFont)
      logging.warning("Tex system missing font %s.  Trying %s instead.", failSafeFont,failSafeFont )
      return self.findFont(failSafeFont)


    encodingVector = None
    if not mapEntry.encoding is None:
      encodingVector = resource.findEncoding(mapEntry.encoding)

    fd = pbpic.sysfont.FontDescriptor(pfbpath)
    font = pbpic.pbpfont.EncodedType1Font(fd,pbpic.sysfont.findcachedfont(fd),encodingVector)
    self.fontdict[texFontName] = font
    
    return font
