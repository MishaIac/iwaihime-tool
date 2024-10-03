import codecs
import os
import subprocess
from struct import pack
from bin import BinaryStream
path1="txts\\"
path2="dats\\"
for fs in os.listdir(path1):
    off = []
    f = codecs.open(path1 + fs, "r", "utf-8")
    k = codecs.open(path2 + fs.replace(".txt", ".dat"), "wb")
    stream = BinaryStream(k)
    idx = 0
    for f1 in f:
        stream.writeInt32(0)
    f.close()
    f = codecs.open(path1 + fs, "r", "utf-8")
    for f2 in f:
        off.append(k.tell())
        stream.writeBytes(f2.replace("\n", "").encode("utf-8") + b"\x00")
    k.seek(0)
    for off1 in off:
        stream.writeInt32(off1)
    f.close()
    k.close()

dst = codecs.open("1__.m", "wb")
stream = BinaryStream(dst)
off2 = []
for hm in range(16):
    stream.writeInt32(0)
for fs in os.listdir(path2):
    off2.append(dst.tell())
    f = codecs.open(path2 + fs, "rb")
    dst.write(f.read())
    f.close()
dst.seek(0)
for off3 in off2:
    stream.writeInt32(off3)
    stream.writeInt32(0)
    stream.writeInt32(0)
    stream.writeInt32(0)
dst.close()
size = os.path.getsize('1__.m')
subprocess.Popen(['lzss.exe', 'e', '1__.m', '1_.m']).wait()
dst = codecs.open("1_.m", "rb")
dst1 = codecs.open("1.m", "wb")
dst1.write(pack('i', size) + dst.read())
dst.close()
dst1.close()
for file in ["1__.m", "1_.m", path2+"1.dat", path2+"2.dat", path2+"3.dat"]:
    os.remove(file)
