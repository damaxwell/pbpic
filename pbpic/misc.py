from metric import Point, PagePoint

def pToPoint(p):
  if isinstance(p,Point) or isinstance(p,PagePoint):
    return p
  return Point(p[0],p[1])

def toOnePoint(*args):
  if len(args) == 2:
    return Point(args[0],args[1])
  if len(args) != 1:
    raise ValueError()
  return pToPoint(args[0])

def toThreePoints(*args):
  if len(args) == 6:
    return (Point(args[0],args[1]),Point(args[2],args[3]),Point(args[4],args[5]))
  if len(args) != 3:
    raise ValueError()
  return [ pToPoint(p) for p in args]

import inspect, os
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

