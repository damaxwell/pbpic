codes = """
0 endchar 14
2 hsbw 13
5 seac 12 6
4 sbw 12 7
0 closepath 9
1 hlineto 6
1 hmoveto 22
4 hvcurveto 31
2 rlineto 5
2 rmoveto 21
6 rrcurveto 8
4 vhcurveto 30
1 vlineto 7
1 vmoveto 4
0 dotsection 12 0
2 hstem 1
6 hstem3 12 2
2 vstem 3
6 vstem3 12 1
2 div 12 12
0 callothersubr 12 16
1 callsubr 10
0 pop 12 17
0 return 11
2 setcurrentpoint 12 33
"""

import re
r = re.compile('([0-9]) ([^ ]+) (?:([0-9]+) ([0-9]+)|([0-9]+))')
print '{'
i=0
s=''
for m in r.finditer( codes ):
  opname = m.group(2)
  opargs = m.group(1)
  opcode = m.group(5)
  if m.group(5) is None:
    opcode = 32+int(m.group(4))
  else:
    opcode = int(m.group(5))
  s += "%d:('%s',%s,True),  " % (opcode,opname,opargs)
  i = (i+1)%4
  if i==0:
    print s
    s = ''
print '}'

i=0
s=''
print '{'
for m in r.finditer( codes ):
  opname = m.group(2)
  opargs = m.group(1)
  opcode = m.group(5)
  if m.group(5) is None:
    opcode = 32+int(m.group(4))
  else:
    opcode = int(m.group(5))
  
  s+= "'%s':%d, " % (opname,opcode)
  i = (i+1)%4
  if i==0:
    print s
    s = ''
print '}'

i=0
s=''
print '{'
for m in r.finditer( codes ):
  opname = m.group(2)
  opargs = m.group(1)
  opcode = m.group(5)
  if m.group(5) is None:
    opcode = 32+int(m.group(4))
  else:
    opcode = int(m.group(5))
  
  s+= "%d:self.%s, " % (opcode,opname)
  i = (i+1)%4
  if i==0:
    print s
    s = ''
print s
print '}'
