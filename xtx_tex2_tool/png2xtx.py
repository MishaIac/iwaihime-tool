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

    xtx_header = orig.read(0x20)
    orig.seek(0)

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

    img_new = Image.new(mode="RGBA", size=(aligned_width, aligned_height))
    img_png = Image.open(pngs + fs.replace(".xtx", ".png"))
    Image.Image.paste(img_new, img_png, (0, 0))
    img_stream = io.BytesIO()
    img_new.save(img_stream, format="PNG")
    img_stream.seek(0)

    dds = io.BytesIO()
    with image.Image(file=img_stream) as img_dds:
        img_dds.compression = "dxt5"
        dds.write(img_dds.make_blob("dds"))
    dds.seek(0x80)

    width = int.from_bytes(orig.read(4), 'big')
    height = int.from_bytes(orig.read(4), 'big')
    offset_x = int.from_bytes(orig.read(4), 'big')
    offset_y = int.from_bytes(orig.read(4), 'big')
    orig.close()
    tex_width = aligned_width >> 2
    total = tex_width * (aligned_height >> 2)
    packed = dds.read(aligned_width*aligned_height)
    texture = [0]*(aligned_width*aligned_height)

    src = 0
    for i in range(total):
        y = get_y (i, tex_width, 0x10)
        x = get_x (i, tex_width, 0x10)

        dst = (x + y * tex_width) * 16
        for j in range(8):
            try:
                texture[src] = packed[int(dst+1)]
                texture[src+1] = packed[int(dst)]
                dst += 2
                src += 2
            except:
                print(fs + " - error")

    dest_xtx1 = codecs.open(dest_xtx + fs, "wb")
    dest_xtx1.write(xtx_header)
    dest_xtx1.write(bytes(texture))
    dest_xtx1.close()

    print(fs)