from . import exception
import sys, inspect

_stylestack = [{}]

_stylereport = {}

class Style(dict):
  def __init__(self,**kwargs):
    self.update(kwargs)

def stylesave():
  global _stylestack
  _stylestack.append({})

def stylerestore():
  global _stylestack
  if len(_stylestack)<=1:
    raise exception.StackUnderflow()
  return _stylestack.pop()

def clearstyles():
  global _stylestack
  _stylestack = [{}]

def getstyle(obj,keys):
  if isinstance(keys,str):
    return _onestyle(obj,keys)
  rv = {}
  for k in keys:
    rv[k] = _onestyle(obj,k)
  return rv

def _onestyle(obj,key,toplevel=True):
  global _stylestack
  k = len(_stylestack)-1
  while(k>=0):
    s = _stylestack[k].get(obj)
    if s is not None:
      if key in s:
        return s[key]
    k-=1

  if(hasattr(obj,'defaultStyle')):
    defaults = obj.defaultStyle
    if callable(defaults):
      defaults = defaults()
    if key in defaults:
      return defaults.get(key)

  if hasattr(obj,'__module__'):
    return _onestyle(sys.modules[obj.__module__],key,toplevel=False)

  if hasattr(obj,'__package__'):
    p = obj.__package__
    if (p is not None) and obj.__name__ != p:
      return _onestyle(sys.modules[obj.__package__],key,toplevel=False)

  return None

def setstyle(obj,**kwargs):
  global _stylestack
  topstyle = _stylestack[-1]
  if not (obj in topstyle):
    topstyle[obj]={}

  topstyle[obj].update(kwargs)

def updatefromstyle(obj,keys,overrides,stylekey=None):
  if stylekey is None:
    if hasattr(obj,'__class__'):
      stylekey = obj.__class__
    else:
      stylekey = obj
  d = obj.__dict__
  for k in keys:
    if k in overrides:
      d[k] = overrides[k]
    else:
      d[k] = _onestyle(stylekey,k)


class StyleTarget:
  def __init__(self,obj,parent=None):
    self.__dict__['_obj']=obj
    self.__dict__['_parent']=parent

  def __getattr__(self,name):
    obj = self.__dict__['_obj']

    if obj is None:
      child = None
      # Look up the name in the caller's namespace
      frame = inspect.stack()[1][0]
      try:
        if name in frame.f_locals:
          child = frame.f_locals.get(name)
        elif name in frame.f_globals:
          child = frame.f_globals.get(name)
      finally:
        del frame
      if inspect.ismodule(child):
        return StyleTarget(child,None)
      raise Exception("Style tree: no style target for %s" % name)

    moduletype = type(inspect.getmodule(inspect))

    if inspect.ismodule(obj):
      child = obj.__dict__.get(name)
      if child is not None:
        return StyleTarget(child,parent=self)

    return getstyle(obj,name)

  def __setattr__(self,name,value):
    obj = self.__dict__['_obj']
    setstyle(obj,name=value)

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    obj = self.__dict__['_obj']
    parent = self.__dict__['_parent']
    return "StyleTarget %s (parent = %s)" % (obj,parent)
