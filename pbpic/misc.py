import inspect, os

class FileSweeper:
  def __init__(self,paths):
    if isinstance(paths,str):
      paths = [paths]
    self.paths = paths
  def __enter__(self):
    pass
    
  def release(self,path):
    while True:
      try:
        self.paths.remove(path)
      except ValueError:
        break

  def __exit__(self,exc_type, exc_value, traceback):
    for p in self.paths:
      try:
        os.remove(p)
      except:
        pass


def msg(s,*args):
  """
  Print a nicely formatted message.
  """
  framerec = inspect.stack()[1]
  calling_module = inspect.getmodule(framerec[0])
  f=inspect.getouterframes(inspect.currentframe())[1]
  caller_name = os.path.basename(f[1])
  if isinstance(f[3],str):
    caller_name += (':%s' % f[3])
  message = '%s: %s' % (caller_name, s % args)
  print( message )

