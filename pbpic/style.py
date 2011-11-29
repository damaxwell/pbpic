import exception, sys

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

def style(obj,keys):
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
      if s.has_key(key):
        return s[key]
    k-=1

  if(hasattr(obj,'defaultStyle')):
    defaults = obj.defaultStyle
    if callable(defaults):
      defaults = defaults()
    if defaults.has_key(key):
      return defaults.get(key)

  if hasattr(obj,'__module__'):
    return _onestyle(sys.modules[obj.__module__],key)

  if hasattr(obj,'__package__'):
    p = obj.__package__
    if (p is not None) and obj.__name__ != p:
      return _onestyle(sys.modules[obj.__package__],key)

  return None

def setstyle(obj,**kwargs):
  global _stylestack
  topstyle = _stylestack[-1]
  if not topstyle.has_key(obj):
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
    if overrides.has_key(k):
      d[k] = overrides[k]
    else:
      d[k] = _onestyle(stylekey,k)
