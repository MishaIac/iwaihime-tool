import codecs, io, os
from wand import image
from PIL import Image

dds_first = b"\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00"
dds_last = b"\x00\x00\x01\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x04\x00\x00\x00\x44\x58\x54\x35\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

def get_x(i, width, level): 
    v1 = (level >> 2) + (level >> 1 >> (level >> 2))
    v2 = i << v1
    v3 = (v2 & 0x3F) + ((v2 >> 2) & 0x1C0) + ((v2 >> 3) & 0x1FFFFE00)
    return ((((level << 3) - 1) & ((v3 >> 1) ^ ((v3 ^ (v3 >> 1)) & 0xF))) >> v1)+  ((((((v2 >> 6) & 0xFF) + ((v3 >> (v1 + 5)) & 0xFE)) & 3)
            + (((v3 >> (v1 + 7)) % (((width + 31)) >> 5)) << 2)) << 3)

def get_y(i, width, level):
    v1 = (level >> 2) + (level >> 1 >> (level >> 2))
    v2 = i << v1
    v3 = (v2 & 0x3F) + ((v2 >> 2) & 0x1C0) + ((v2 >> 3) & 0x1FFFFE00)
    return ((v3 >> 4) & 1) + ((((v3 & ((level << 6) - 1) & -0x20)
            + ((((v2 & 0x3F)
                + ((v2 >> 2) & 0xC0)) & 0xF) << 1)) >> (v1 + 3)) & -2) + ((((v2 >> 10) & 2) + ((v3 >> (v1 + 6)) & 1)
            + (((v3 >> (v1 + 7)) // ((width + 31) >> 5)) << 2)) << 3)

orig_xtx = "orig_xtx\\"
pngs = "png\\"
dest_xtx = "dest_xtx\\"

for fs in os.listdir(orig_xtx):
    orig = codecs.open(orig_xtx + fs, "rb")
    magic = orig.read(4)
    if magic!=b"xtx\0":
        print(f"Error: {fs} - is not xtx")
        continue
    type = int.from_bytes(orig.read(4), 'little')
    if type != 2:
        print("Error: "+ fs + " - is not type 2 but type %d, skip convert"%(type))
        continue

    aligned_width = int.from_bytes(orig.read(4), 'big')
    aligned_height = int.from_bytes(orig.read(4), 'big')
    width = int.from_bytes(orig.read(4), 'big')
    height = int.from_bytes(orig.read(4), 'big')
    offset_x = int.from_bytes(orig.read(4), 'big')
    offset_y = int.from_bytes(orig.read(4), 'big')

    tex_width = aligned_width >> 2
    total = tex_width * (aligned_height >> 2)
    texture = orig.read(aligned_width*aligned_height)
    packed = [0]*(aligned_width*aligned_height)
    src = 0
    for i in range(total):
        y = get_y (i, tex_width, 0x10)
        x = get_x (i, tex_width, 0x10)

        dst = (x + y * tex_width) * 16
        for j in range(8):
            try:
                packed[int(dst)] = texture[src+1]
                packed[int(dst+1)] = texture[src]
                dst += 2
                src += 2
            except:
                print(fs + " - error")

    xtx = io.BytesIO()
    xtx.write(dds_first)
    xtx.write(int.to_bytes(aligned_height, 4, 'little'))
    xtx.write(int.to_bytes(aligned_width, 4, 'little'))
    xtx.write(dds_last)
    xtx.write(bytes(packed))
    xtx.seek(0)
    with image.Image(blob=xtx) as img:
        img.compression = "no"
        img.save(file=xtx)
    img = Image.open(xtx)
    img = img.crop((0, 0, width, height))
    img.save(pngs + fs.replace(".xtx", ".png"))

    print(fs.replace(".xtx", ".png"))