from pbpic.font import type1

minion = type1.Type1Font.fromPath('/Users/david/Library/texmf/fonts/type1/adobe/MinionPro/MinionPro-Regular.pfb')

print minion.glyphnames[35]
print minion.charstrings['B']
print minion.metricsForGlyphname('B')
for c in  minion.charstring('B').codes():
    print "code", c

print "subroutine 2003"
for c in  minion.subroutine(2003).codes():
    print "code", c