def readUInt1(f):
  return ord(f.read(1))

def readUInt2(f):
  v = ord(f.read(1))
  v = (v<<8) | ord(f.read(1))
  return v

def readUInt3(f):
  v = ord(f.read(1))
  v = (v<<8) | ord(f.read(1))
  v = (v<<8) | ord(f.read(1))
  return v

def readUInt4(f):
  v = ord(f.read(1))
  v = (v<<8) | ord(f.read(1))
  v = (v<<8) | ord(f.read(1))
  v = (v<<8) | ord(f.read(1))
  return v

def readInt1(f):
  v = readUInt1(f)
  if(v & 0x80):
      v = -0x10 + v
  return v

def readInt2(f):
  v = readUInt2(f)
  if(v & 0x8000):
      v = -0x10000 + v
  return v

def readInt3(f):
  v = readUInt3(f)
  if(v & 0x800000):
      v = -0x1000000 + v
  return v

def readInt4(f):
  v = readUInt4(f)
  if(v & 0x80000000):
      v = -0x100000000 + v
  return v

def readString(f,k):
  return f.read(k)

def readFixWord(f):
  return float(readInt4(f)) / 0x100000

def asFixWord(n):
  return float(n) / 0x100000


readByte = readUInt1
readIntK=[readInt1,readInt2,readInt3,readInt4]
readUIntK=[readUInt1,readUInt2,readUInt3,readUInt4]
