import cairo
import logging 
from geometry import Point
import math
from color import GrayColor


line_join_to_cairo={'bevel':cairo.LINE_JOIN_BEVEL, 'miter':cairo.LINE_JOIN_MITER, 'round':cairo.LINE_JOIN_ROUND}
line_cap_to_cairo={'butt':cairo.LINE_CAP_BUTT, 'round':cairo.LINE_CAP_ROUND, 'square':cairo.LINE_CAP_SQUARE}
fill_rule_to_cairo={'evenodd':cairo.FILL_RULE_EVEN_ODD, 'winding':cairo.FILL_RULE_WINDING}

_None = 0
_Stroke = 1
_Fill = 2
_Font = 3

class RState:
  def __init__(self,other):
    self.lastOperation = other.lastOperation
    self.color = other.color
  
  def restore(self,renderer):
    renderer.lastOperation = self.lastOperation
    renderer.color = self.color

  def clone(self):
    return RState(self)
    

class CairoRenderer:
  def __init__(self,surface):
    self.surface = surface
    self.lastOperation = None

  def begin(self,extents):
    w=extents.width()
    h=extents.height()
    self.surface.set_size(w,h)
    ll = extents.ll()
    self.tx = ll[0]
    self.ty = h + ll[1]
    self.ctx = cairo.Context (self.surface)

    # Cairo CTM for its default coordinates with
    # origin at the upper left and positive y
    # pointing down.
    self.defaultMatrix = self.ctx.get_matrix()
  
    # A Cairo CTM with the origin at the lower left
    # and positive y pointing up.
    self.llOriginMatrix = self.ctx.get_matrix()
    self.llOriginMatrix.scale(1,-1)
    self.llOriginMatrix.translate(0,-self.ty)

    # self.setlinewidth(1)
    # self.linecolor = GrayColor(1)
    # self.fillcolor = GrayColor(1)
    self.ctx.set_font_size(1.)

    self.gstack = []

    self.lastOperation = _None
    self.color = _None

  def end(self):
    self.surface.finish()
    del self.ctx
    self.ctx = None


  def gsave(self):
    self.gstack.append(RState(self))
    self.ctx.save()

  def grestore(self):
    self.gstack.pop().restore(self)
    self.ctx.restore()  

  def stroke(self,path,gstate):

    gstate.updatestroke(self)    
    
    if self.color != _Stroke:
      gstate.linecolor.renderto(self)
      self.color = _Stroke
    
    # The path will be expressed in page coordinates, which i
    # need to be converted to device coordinates.
    # pageToDevice=cairo.Matrix(*gstate.ptm.asTuple())*self.llOriginMatrix
    pageToDevice=self.llOriginMatrix
    self.ctx.set_matrix(pageToDevice)        

    # Draw the path in page coordinates.
    self.ctx.new_path()
    path.buildpath(self)

    # # Before stroking, set to pen coordinates.
    u=gstate.unitsize.asTuple()
    penToPage=cairo.Matrix(*gstate.linewidth.units().affineTransform().asTuple())*\
    cairo.Matrix(u[0],u[1],u[2],u[3],0,0)

    self.ctx.set_matrix(penToPage*pageToDevice)

    self.ctx.stroke()

    self.lastOperation=_Stroke

  def fill(self,path,gstate):
  
    gstate.updatefill(self)    
    if self.color != _Fill:
      gstate.fillcolor.renderto(self)
      self.color = _Fill
  
    self.ctx.new_path()
  
    # pageToDevice=cairo.Matrix(*gstate.ptm.asTuple())*self.llOriginMatrix
    pageToDevice=self.llOriginMatrix
    self.ctx.set_matrix(pageToDevice)
    path.buildpath(self)
  
    self.ctx.fill()
    self.lastOperation=_Fill

  def clip(self,path,gstate):
    gstate.updatefill(self)

    self.ctx.new_path()

    # pageToDevice=cairo.Matrix(*gstate.ptm.asTuple())*self.llOriginMatrix
    pageToDevice=self.llOriginMatrix
    self.ctx.set_matrix(pageToDevice)
    path.buildpath(self)

    self.ctx.clip()
    self.lastOperation=_Fill

  def showglyphs(self,s,fontdescriptor,tm,metrics,gstate):

    tm=tm.copy()
    tm.scale(1,-1)
    # pageToDevice=cairo.Matrix(*gstate.ptm.asTuple())*self.llOriginMatrix
    pageToDevice=self.llOriginMatrix
    self.ctx.set_matrix(cairo.Matrix(*tm.asTuple())*pageToDevice)

    # FIXME: save fontdescriptor?
    ftFont = ftFontForDescriptor(fontdescriptor)
    self.ctx.set_font_face(ftFont)

    # gstate.updatefont(self)
    if self.color != _Font:
      gstate.fontcolor.renderto(self)
      self.color = _Font

    p = Point(0,0)
    g = len(s)*[None]
    for k in xrange(len(s)):
      g[k] = (s[k],p.x,p.y)
      p = p + metrics[k].advance
    self.ctx.show_glyphs(g)
    self.lastOperation = _Font


  def moveto(self,p):
    x=p[0]; y=p[1]
    self.ctx.move_to(x,y)

  def lineto(self,p):
    x=p[0]; y=p[1]
    self.ctx.line_to(x,y)

  def curveto(self,p0,p1,p2):
    x0=p0[0]; y0=p0[1]
    x1=p1[0]; y1=p1[1]
    x2=p2[0]; y2=p2[1]
    self.ctx.curve_to(x0,y0,x1,y1,x2,y2)

  def closepath(self):
    self.ctx.close_path()

  def setrgbcolor(self,r,g,b):
    self.ctx.set_source_rgb(r,g,b)
    
  def setgray(self,g):
    self.ctx.set_source_rgb(1.-g,1.-g,1.-g)

  def setlinewidth(self,w):
    self.ctx.set_line_width(float(w))

  def setlinecolor(self,c):
    if self.color == _Stroke:
      self.color = _None

  def setlinecap(self,cap):
    self.ctx.set_line_cap(line_cap_to_cairo[cap])

  def setlinejoin(self,join):
    self.ctx.set_line_join(line_join_to_cairo[join])

  def setmiterlimit(self,miterlimit):
    self.ctx.set_miter_limit(miterlimit)

  def setdash(self,dash,phase):
    self.ctx.set_dash(dash,phase)

  def setfillcolor(self,c):
    if self.color == _Fill:
      self.color = _None

  def setfillrule(self,fillrule):
    self.ctx.set_fill_rule(fill_rule_to_cairo[fillrule])

  def setfontcolor(self,c):
    if self.color == _Font:
      self.color = _None
  

import ctypes, ctypes.util
import cairo

ftFontCache = {}
def ftFontForDescriptor(descriptor):
  global ftFontCache
  ftFont = ftFontCache.get(descriptor,None)
  if ftFont:
    return ftFont
  ftFont = create_cairo_font_face_for_file(descriptor.path,descriptor.faceindex)
  ftFontCache[descriptor] = ftFont
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

class PDFRenderer(CairoRenderer):
  def __init__(self,filename):
    CairoRenderer.__init__(self,cairo.PDFSurface (filename, 0,0))


class PNGRenderer(CairoRenderer):
  def __init__(self,filename):
    self.filename = filename
    CairoRenderer.__init__(self,None)

  def begin(self,extents):
    w=extents.width()
    h=extents.height()
    
    W=4*int(w); H=4*int(h)
    self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24,W,H)
    
    # set_size(w,h)
    ll = extents.ll()
    self.tx = ll[0]
    self.ty = h + ll[1]
    self.ctx = cairo.Context (self.surface)

    self.ctx.set_source_rgb(1,1,1)
    self.ctx.move_to(0,0)
    self.ctx.line_to(W,0)
    self.ctx.line_to(W,H)
    self.ctx.line_to(0,H)
    self.ctx.close_path()
    self.ctx.fill()
    self.ctx.set_source_rgb(0,0,0)



    # Cairo CTM for its default coordinates with
    # origin at the upper left and positive y
    # pointing down.
    self.defaultMatrix = self.ctx.get_matrix()
    self.defaultMatrix.scale(W/w,H/h)

    # A Cairo CTM with the origin at the lower left
    # and positive y pointing up.
    self.llOriginMatrix = self.ctx.get_matrix()
    self.llOriginMatrix.scale(W/w,H/h)
    self.llOriginMatrix.scale(1,-1)
    self.llOriginMatrix.translate(0,-self.ty)

    # self.setlinewidth(1)
    # self.linecolor = GrayColor(1)
    # self.fillcolor = GrayColor(1)
    self.ctx.set_font_size(1.)

    self.gstack = []

    self.lastOperation = _None
    self.color = _None


  def end(self):
    self.surface.write_to_png(self.filename)
    CairoRenderer.end(self)
