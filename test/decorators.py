from PIL import Image
import numpy as np
import os, sys
import pbpic as pbp
from pbpic import cm

images_test_dir = "images-test"
images_baseline_dir = "images-baseline"

class ImageComparisonFailure(Exception):
  pass

class ExampleTest:
  def __init__(self,filename):
    self.filename = filename
  
  def __call__(self,func):
    func_dir = os.path.dirname(sys.modules.get( func.__module__ ).__file__)
    output_filename = os.path.join(func_dir,images_test_dir,func.__name__+".png")
    baseline_filename = os.path.join(func_dir,images_baseline_dir,func.__name__+".png")

    def EgTest(self):
      exec 'import %s' % self.filename

      output_image = np.array(Image.open(output_filename),dtype='uint8')
      baseline_image = np.array(Image.open(baseline_filename),dtype='uint8')
    
      N=3.*output_image.shape[0*output_image.shape[1]]
      l1err = np.sum(np.abs(output_image-baseline_image))/N
    
      if l1err >= self.threshold:
        raise ImageComparisonFailure("Image %s is not closed to %s\nL1 error %f" %(output_filename,baseline_filename,l1err) )

      os.remove(output_filename)
      
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
