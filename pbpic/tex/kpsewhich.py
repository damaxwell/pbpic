import os
import platform

VF_TYPE="vf"
TFM_TYPE="tfm"
ENC_TYPE="enc files"
TYPE1_TYPE="type1 fonts"
FONTMAP_TYPE="map"

kpsewhichCmd = 'kpsewhich'
# kpsewhich is called something else under windows:
if platform.platform().find('indows') > -1:
  kpsewhichCmd = 'findtexmf'

def find( name, kind ):
  p = os.popen('%s -format="%s" %s' % (kpsewhichCmd, kind, name), 'r' )
  path = p.read()[:-1] # Remove trailing newline
  if len(path) == 0:
    return None
  return path
