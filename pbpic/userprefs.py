import os, atexit, pickle

def ensureDirExists(path):
  path = os.path.expanduser(path)
  if(os.path.isdir(path)):
    return True
  os.makedirs(path)
  
def pbp_prefs_home():
  # FIXME: should do something different for Windows...
  defaultPath = '~/.pbpic'
  ensureDirExists(defaultPath)
  return defaultPath

def prefsPathForFile(filename):
  return os.path.expanduser(os.path.join(pbp_prefs_home(),filename))

class PersistantCache:
  def __init__(self,coreclass,filename):
    self.instance = None
    self.cachepath = prefsPathForFile(filename)
    try:
      with open(self.cachepath,"r") as f:
        self.instance = pickle.load(f)
    except:
      pass
    if self.instance is None:
      self.instance = coreclass()
  
    atexit.register(self.save)

  def __call__(self):
    return self.instance

  def save(self):
    try:
      with open(self.cachepath,'wb') as f:
        pickle.dump(self.instance,f)
    except:
      pass

  def reset(self):
    self.instance.clear()
    self.save()
