from exception import StylePropertyNotFound

class Style:
  
  def __init__(self,*args,**kwargs):
    self.sdict = {}
    # FIXME: should allow 'a.b.c' as the first arg
    if len(args) == 1 and isinstance(args[0],str):
      s = Style()
      self.sdict[args[0]] = s
    else:
      s = self
    s.sdict.update(**kwargs)

  def __repr__(self):
    s = 'Style:\n'
    for (key,value) in self.sdict.items():
      s += ('%s: %s' % (key,value))
    return s

  def __setitem__(self,item,value):
    self.setstyle(item,value)

  def __getitem__(self,item):
    return self.getstyle(item)

  def copy(self):
    cp = Style()
    for (key,val) in self.sdict.items():
      if isinstance(val,Style):
        cp.sdict[key]=val.copy()
      else:
        cp.sdict[key]=val

  def update(self,otherStyle):
    for (key,value) in otherStyle.sdict.items():
      if isinstance(value,Style):
        # if we currently have a style for this value, then recursively update, otherwise clobber
        currentVal = self.sdict.get(key)
        if isinstance( currentVal, Style ):
          currentVal.update(value)
        else:
          self.sdict[key] = value
      else:
        self.sdict[key] = value

  def getstyle(self,sname):
    if isinstance(sname,str):
      sarray = sname.split('.')
    else:
      sarray = sname
    
    while(len(sarray)>0):
      try:
        child = self.sdict[sarray[0]]
        if len(sarray) == 1:
          return child
        else:
          if isinstance(child,Style):
            try:
              return child.getstyle(sarray[1:])
            except StylePropertyNotFound:
              pass
      except KeyError:
        pass
      # Shorten the array and try again
      sarray = sarray[1:]

    raise StylePropertyNotFound(sname)

  def _basedict(self,sname):
    if isinstance(sname,str):
      sarray = sname.split('.')
    else:
      sarray = sname
    if len(sarray) == 0:
      raise ValueError()
    
    child = self
    while len(sarray) > 1:
      try:
        child = child.sdict[sarray[0]]
      except KeyError:
        for k in sarray[:-1]:
          nc = Style()
          child.sdict[k] = nc
          child = nc
        sarray = sarray[-1:]
        break
      sarray = sarray[1:]
    return (child,sarray[0])

  def setstyle(self,sname,value):
    (style,name) = self._basedict(sname)
    style.sdict[name] = value

  def updatestyle(self,sname,value):
    (style,name) = self._basedict(sname)
    currentVal = style.sdict.get(name)
    if isinstance(currentVal,Style) and isinstance(value,Style):
      currentVal.update(value)
    else:
      style.sdict[name] = value


_stylestack = [Style()]

def style(*args):
  global _stylestack
  topstyle = _stylestack[-1]
  if len(args) == 0:
    return topstyle
  if len(args) == 1:
    return topstyle[args[0]]
  if len(args) != 2:
    raise ValueError()
  name = args[0]; default=args[1]
  try:
    return topstyle[name]
  except:
    return default[name]

def setstyle(*args):
  global _stylestack
  if len(args) == 2:
    name = args[0]; value=args[1]
    _stylestack[-1].updatestyle(name,value)
  elif len(args) == 1:
    value=args[0]
    _stylestack[-1].update(value)

def stylesave():
  global _stylestack
  _stylestack.append(_stylestack[-1].copy())

def stylerestore(style):
  global _stylestack
  return _stylestack.pop()

