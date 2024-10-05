import codecs, os, lzss

orig = "orig\\"
unpacked = "unpacked\\"

for fs in os.listdir(orig):

    fp = codecs.open(orig + fs, "rb")

    fp.seek(0xC)
    temp = int.from_bytes(fp.read(4), 'little')
    if temp == 0:
        print(fs + " is not lzss compressed")
        continue
    fp.seek(0)

    data = fp.read()
    fp = lzss.decode_lzss(data)
    fp.seek(0)

    offsets = []
    size_info = int.from_bytes(fp.read(4), 'little')
    offsets.append(size_info)
    fp.read(0xC)
    while True:
        if fp.tell() >= size_info:
            break
        offset = int.from_bytes(fp.read(4), 'little')
        offsets.append(offset)
        fp.read(0xC)
    fp.seek(0, 2)
    end = fp.tell()
    os.makedirs(f"{unpacked}{fs}", exist_ok=True)
    for f1 in enumerate(offsets):

        if f1[1] == offsets[-1]:
            size = end - f1[1]
        else:
            size = offsets[f1[0]+1] - f1[1]
        fp.seek(f1[1])
        magic = fp.read(4)
        if magic!=b"xtx\0":
            print(fs + " - File %03d is not xtx"%(f1[0]))
            continue
        fp.seek(f1[1])

        xtx = codecs.open(f"{unpacked}{fs}" + "\\%03d.xtx"%(f1[0]), "wb")
        xtx.write(fp.read(size))

    print(fs)