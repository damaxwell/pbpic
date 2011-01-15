import pbpfont
import os.path

try:
  import sysfont_mac
  sysfont_platform = sysfont_mac
except:
  sysfont_platform = sysfont_none
import pbpfont

def findfont(name):
  # Let's see if the operating system knows a font by this name.
  fd = sysfont_platform.find_font(name)
  if not fd is None:
    return pbpfont.FontDescriptor(fd[0],0)

if __name__ == '__main__':
  import sys
  print findfont(sys.argv[1])