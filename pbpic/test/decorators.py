from PIL import Image
import numpy as np
import os, sys
import pbpic as pbp
from pbpic import cm
from pbpic.render_cairo import PNGRenderer

images_test_dir = "images-test"
images_baseline_dir = "images-baseline"

class ImageComparisonFailure(Exception):
  pass


class ReroutePDFRenderer(PNGRenderer):

  output_directory=""

  def __init__(self,filename):
    filename = os.path.splitext(os.path.basename(filename))[0]+".png"
    filename=os.path.join(self.output_directory,filename)
    PNGRenderer.__init__(self,filename)

    

class ExampleTest:
  def __init__(self,filename,threshold=1.):
    self.filename = filename
    self.threshold = threshold
  
  def __call__(self,func):
    func_dir = os.path.dirname(sys.modules.get( func.__module__ ).__file__)
    image_name = os.path.splitext(os.path.basename(self.filename))[0]
    image_name += ".png"

    output_dir = os.path.join(func_dir,images_test_dir)
    ReroutePDFRenderer.output_directory=output_dir

    output_filename = os.path.join(output_dir,image_name)
    baseline_filename = os.path.join(func_dir,images_baseline_dir,image_name)

    def EgTest():
      old_renderer=pbp.getrenderer('pdf')
      try:
        pbp.setrenderer('pdf',ReroutePDFRenderer)
        exec 'import %s' % self.filename in locals()

        output_image = np.array(Image.open(output_filename),dtype='uint8')
        baseline_image = np.array(Image.open(baseline_filename),dtype='uint8')
    
        if output_image.shape != baseline_image.shape:
          raise ImageComparisonFailure("Image %s size does not match baseline %s:\n%s <=> %s" % \
                     (output_filename,baseline_filename,str(output_image.shape),str(baseline_image.shape)))
        N=3.*output_image.shape[0*output_image.shape[1]]
        l1err = np.sum(np.abs(output_image-baseline_image))/N
    
        if l1err >= self.threshold:
          raise ImageComparisonFailure("Image %s is not closed to %s\nL1 error %f" %(output_filename,baseline_filename,l1err) )

        os.remove(output_filename)
      finally:
        pbp.setrenderer('pdf',old_renderer)
        pbp.style.clearstyles()
      
    EgTest.__name__ = func.__name__
    return EgTest
    
class PngTest:
  def __init__(self,w=3,h=3,threshold=1.):
    self.w=w; self.h=h; self.threshold = threshold
  
  def __call__(self,func):
    func_dir = os.path.dirname(sys.modules.get( func.__module__ ).__file__)
    output_filename = os.path.join(func_dir,images_test_dir,func.__name__+".png")
    baseline_filename = os.path.join(func_dir,images_baseline_dir,func.__name__+".png")

    def PngTest():
      try:
        pbp.pbpbegin(self.w*cm,self.h*cm,output_filename)
        pbp.scaleto(1*cm)
        func()
      finally:
        pbp.pbpend()
        pbp.style.clearstyles()

      output_image = np.array(Image.open(output_filename),dtype='uint8')
      baseline_image = np.array(Image.open(baseline_filename),dtype='uint8')
      
      N=3.*output_image.shape[0*output_image.shape[1]]
      l1err = np.sum(np.abs(output_image-baseline_image))/N
      
      if l1err >= self.threshold:
        raise ImageComparisonFailure("Image %s is not closed to %s\nL1 error %f" %(output_filename,baseline_filename,l1err) )

      os.remove(output_filename)
      

    PngTest.__name__ = func.__name__
    return PngTest

class TaciturnTest:
  """Decorator for test cases that requires a Canvas to run, but does not generate
  an image for comparison with a baseline."""
  def __init__(self,w=3,h=3):
    self.w=w; self.h=h;

  def __call__(self,func):
    func_dir = os.path.dirname(sys.modules.get( func.__module__ ).__file__)
    output_filename = os.path.join(func_dir,images_test_dir,"TaciturnTest.png")

    def decorator():
      try:
        pbp.pbpbegin(self.w*cm,self.h*cm,output_filename)
        pbp.scaleto(1*cm)
        func()
      finally:
        pbp.pbpend()
        os.remove(output_filename)

    decorator.__name__ = func.__name__
    return decorator
