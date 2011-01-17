import pbpfont
import os.path

try:
  import sysfont_mac
  sysfont_platform = sysfont_mac
except:
  class sysfont_none:
    @staticmethod
    def find_font(fontname): return None
  sysfont_platform = sysfont_none
import pbpfont

def findfont(name):
  fd = sysfont_platform.find_font(name)
  if fd is None: return None
  return pbpfont.FontDescriptor(fd[0],0)

if __name__ == '__main__':
  import sys
  print findfont(sys.argv[1])