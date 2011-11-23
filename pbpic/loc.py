import exception
from geometry import BBox, Vector
from metric import PagePoint

__doc__="""Functions for extracting a desired page-point from a canvas."""

bboxcallbacks = { 'll':BBox.ll, 'lr':BBox.lr, 'ul':BBox.ul, 'ur':BBox.ur, 'center':BBox.center,
                  'cl':BBox.cl, 'cr':BBox.cr, 'uc':BBox.uc, 'lc':BBox.lc }

bboxcallback_longnames ={'ll':'lower-left', 'lr':'lower-right', 'ul':'upper-left', 'ur':'upper-right','center':'center', 'cl':'center-left', 'cr':'center-right', 'uc':'upper-center', 'lc':'lower-center'}
def bbox_loc(canvas,loc_name):
  cb = bboxcallbacks.get(loc_name)  
  if not cb is None:
    if canvas._extents is None:
      raise exception.PBPicException('No bounding box available to computed named point "%s"' % loc_name) 
    return PagePoint(cb(canvas._extents))
  return None

template = \
"""def %s(canvas):
  '''Returns canvas.pageExtents().%s().  This determines the "%s" location on
  the canvas's bounding box, in page coordinates.'''
  return bbox_loc(canvas,"%s")"""
for k in bboxcallbacks.keys():
  filled_template = template % (k,k,bboxcallback_longnames[k],k)
  exec filled_template in globals()

class border:
  """Determines the location on the border of the canvas' extents
  where a ray from the center of the extents pointing in
  a specified direction intersects the border.  E.g.: if
  :i: is an inset,
  
    place(i,at=loc.border(1,0)) 
  
  draws the inset with the center-right point on its boundary sitting on top
  of the current-point.  In this particular case, this is equivalent to
  
    place(i,at=loc.cl)
    
  but in general an arbitrary direction can be specified.
"""
  
  def __init__(self,*args):
    if len(args)==2:
      self.v=Vector(*args)
    elif len(args)==1:
      self.v=args[0]
    else:
      raise ValueError()
  
  def __call__(self,c):
    extents = c.pageExtents()
    w=extents.width();h=extents.height()
    vx=self.v[0]; vy=self.v[1]
    r0=abs(w*vy)
    r1=abs(h*vx)
    if r0>r1: # intersects top/bottom
      s=(vx/vy)*h/2
      if vy>0:
        return PagePoint((extents.xmin+extents.xmax)/2+s,extents.ymax)
      else:
        return PagePoint((extents.xmin+extents.xmax)/2-s,extents.ymin)
    else:
      s=(vy/vx)*w/2
      if vx>0:
        return PagePoint(extents.xmax,(extents.ymin+extents.ymax)/2+s)
      else:
        return PagePoint(extents.xmin,(extents.ymin+extents.ymax)/2-s)
    return None
