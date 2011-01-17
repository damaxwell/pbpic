import cairo
import logging 
from metric import MeasuredLength, Point
import math
from color import GrayColor


line_join_to_cairo={'bevel':cairo.LINE_JOIN_BEVEL, 'miter':cairo.LINE_JOIN_MITER, 'round':cairo.LINE_JOIN_ROUND}
line_cap_to_cairo={'butt':cairo.LINE_CAP_BUTT, 'round':cairo.LINE_CAP_ROUND, 'square':cairo.LINE_CAP_SQUARE}


class PDFRenderer:
  def __init__(self,filename):
    self.surface = cairo.PDFSurface (filename, 0,0)
    self.lastOperation = None

  def begin(self,extents):
    w=extents.width()
    h=extents.height()
    self.surface.set_size(w,h)
    ll = extents.ll()
    self.tx = ll[0]
    self.ty = h + ll[1]
    self.ctx = cairo.Context (self.surface)
    self.defaultMatrix = self.ctx.get_matrix()

    self.setlinewidth(1)
    self.linecolor = GrayColor(1)
    self.setgray(1)
    self.ctx.set_font_size(1.)

  def end(self):
    self.surface.finish()
    del self.ctx
    self.ctx = None

  def stroke(self,path,gstate):
    self.initstroke(gstate)
    self.linecolor.renderto(self)
    # FIXME: is the newpath right?
    self.ctx.new_path()
    path.drawto(self)
    self.ctx.stroke()
    self.lastOperation='stroke'
  
  def moveto(self,p):
    x=p[0]; y=p[1]
    self.ctx.move_to(x-self.tx,self.ty-y)

  def lineto(self,p):
    x=p[0]; y=p[1]
    self.ctx.line_to(x-self.tx,self.ty-y)

  def curveto(self,p0,p1,p2):
    x0=p0[0]; y0=p0[1]
    x1=p1[0]; y1=p1[1]
    x2=p2[0]; y2=p2[1]
    self.ctx.curve_to(x0-self.tx,self.ty-y0,x1-self.tx,self.ty-y1,x2-self.tx,self.ty-y2)

  def closepath(self):
    self.ctx.close_path()

  def setrgbcolor(self,r,g,b):
    self.ctx.set_source_rgb(r,g,b)
    
  def setgray(self,g):
    self.ctx.set_source_rgb(1.-g,1.-g,1.-g)
    
  def setlinewidth(self,w):
    oldmatrix = self.ctx.get_matrix()
    self.ctx.set_matrix(self.defaultMatrix)
    if isinstance(w,MeasuredLength):
      self.ctx.set_line_width(w.ptValue())
    else:
      self.ctx.set_line_width(w)
    self.ctx.set_matrix(oldmatrix)

  def setlinecolor(self,c):
    self.linecolor = c

  def setlinecap(self,cap):
    self.ctx.set_line_cap(line_cap_to_cairo[cap])

  def setlinejoin(self,join):
    self.ctx.set_line_join(line_join_to_cairo[join])

  def setmiterlimit(self,miterlimit):
    self.ctx.set_miter_limit(miterlimit)

  def setdash(self,dash,phase):
    self.ctx.set_dash(dash,phase)
    

  def initstroke(self,gstate):
    # if self.lastOperation!='path':
    self.ctx.set_matrix(self.defaultMatrix)
    gstate.updatestrokestate(self)
    self.lastOperation = 'stroke'

  def inittext(self,gstate):
    tm=gstate.texttm()
    tm.c *= -1
    tm.b *= -1
    tm.tx = gstate.path.cp.x - self.tx
    tm.ty = self.ty-gstate.path.cp.y
    self.ctx.set_matrix(cairo.Matrix(*tm.asTuple()))
    gstate.updatetextstate(self)
    self.lastOperation = 'text'

  def setfont(self,fontdescriptor):
    ftFont = ftFontForDescriptor(fontdescriptor)
    self.ctx.set_font_face(ftFont)

  def setfontsize(self,size):
    pass
  
  def showglyphs(self,s,gstate,metrics):
    self.inittext(gstate)
    p = Point(0,0)
    g = len(s)*[None]
    for k in xrange(len(s)):
      g[k] = (s[k],p.x,p.y)
      p = p + metrics[k].advance
    self.ctx.show_glyphs(g)
    self.lastOperation='text'

import ctypes, ctypes.util
import cairo

ftFontCache = {}
def ftFontForDescriptor(descriptor):
  global ftFontCache
  ftFont = ftFontCache.get(descriptor,None)
  if ftFont:
    return ftFont
  ftFont = create_cairo_font_face_for_file(descriptor.path,descriptor.faceindex)
  ftFontCache[descriptor.path] = ftFont
  return ftFont


_initialized = False
class PycairoContext(ctypes.Structure):
    _fields_ = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
        ("ctx", ctypes.c_void_p),
        ("base", ctypes.c_void_p)]

def create_cairo_font_face_for_file (filename, faceindex=0, loadoptions=0):
    global _initialized
    global _freetype_so
    global _cairo_so
    global _ft_lib
    global _surface

    CAIRO_STATUS_SUCCESS = 0
    FT_Err_Ok = 0

    if not _initialized:

        # find shared objects
        _freetype_so = ctypes.CDLL (ctypes.util.find_library("freetype") )
        _cairo_so = ctypes.CDLL ( ctypes.util.find_library("cairo") )

        # initialize freetype
        _ft_lib = ctypes.c_void_p ()
        if FT_Err_Ok != _freetype_so.FT_Init_FreeType (ctypes.byref (_ft_lib)):
          raise "Error initialising FreeType library."

        _surface = cairo.ImageSurface (cairo.FORMAT_A8, 0, 0)

        _initialized = True

    # create freetype face
    ft_face = ctypes.c_void_p()
    cairo_ctx = cairo.Context (_surface)
    cairo_t = ctypes.c_void_p(PycairoContext.from_address(id(cairo_ctx)).ctx)
    if FT_Err_Ok != _freetype_so.FT_New_Face(_ft_lib, filename, faceindex, ctypes.byref(ft_face)):
        raise Exception("Error creating FreeType font face for " + filename)

    # create cairo font face for freetype face
    _cairo_so.cairo_ft_font_face_create_for_ft_face.restype = ctypes.c_void_p
    cr_face = _cairo_so.cairo_ft_font_face_create_for_ft_face (ft_face, loadoptions)
    cr_face = ctypes.c_void_p(cr_face) # Convert the returned integer to a pointer.
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_font_face_status (cr_face):
        raise Exception("Error creating cairo font face for " + filename)

    _cairo_so.cairo_set_font_face (cairo_t, cr_face)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_status (cairo_t):
        raise Exception("Error creating cairo font face for " + filename)

    face = cairo_ctx.get_font_face ()

    return face
