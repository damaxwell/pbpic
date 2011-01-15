#!/usr/bin/python

from setuptools import setup, Extension
import ConfigParser

# pykpse_module = Extension('pbpic/pykpse',
#                     define_macros = [('MAJOR_VERSION', '1'),
#                                      ('MINOR_VERSION', '0')],
#                     libraries = ['kpathsea'],
#                     sources = ['pbpic/pykpse_module.c'])
# 
pscodec_module = Extension('pbpic/pscodec',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                    sources = ['pbpic/pscodec.c'])


sysfont_mac_module = Extension('pbpic/sysfont_mac',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                    extra_link_args = ['-framework', 'ApplicationServices'],
                    sources = ['pbpic/sysfont_mac.c'])

ExtensionModules = []

# obtain information on which modules have to be built from setup.cfg file
cfg = ConfigParser.ConfigParser()
cfg.read("setup.cfg")

# try:
#   build_pykpse = cfg.getboolean("PBPicture", "build_pykpse")
#   if build_pykpse:
#     ExtensionModules.append( pykpse_module )
#     
# except:
#   pass
# 
try:
  build_pscodec = cfg.getboolean("PBPicture", "build_pscodec")
  if build_pscodec:
    ExtensionModules.append( pscodec_module )
except:
  pass

try:
  build_mac = cfg.getboolean("PBPicture", "build_mac")
  if build_mac:
    print 'sysfont_mac!'
    ExtensionModules.append( sysfont_mac_module )
except:
  pass

setup(name="pbpic",
    description="Methmatical vector graphics",
    author="David Maxwell",
    author_email="damaxwell@alaska.edu",
    packages = [ "pbpic" ],
    ext_modules = ExtensionModules,
    # package_data = { 
    #   "pbpic":   [ "examples/*.py", 
    #           "examples/*.eps", 
    #           "docs/*.pdf", 
    #           "configs/*.py"
    #           "texfonts/bluesky/*/*", 
    #           "texfonts/tfm/*/*/*", 
    #         ], 
    # }
  )



