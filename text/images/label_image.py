from PIL import Image, ImageDraw, ImageFont

src = r'C:\Users\yunny\Downloads\stick\IMG_20260516_192641.jpg'
dst = r'C:\Users\yunny\Downloads\stick\IMG_20260516_192641_labeled.jpg'

img = Image.open(src).convert('RGB')
W, H = img.size
print('size:', W, H)

draw = ImageDraw.Draw(img)

font_path = r'C:\Windows\Fonts\msyhbd.ttc'
try:
    font = ImageFont.truetype(font_path, 80)
except Exception:
    font = ImageFont.truetype(r'C:\Windows\Fonts\simhei.ttf', 80)

RED = (230, 20, 20)
WHITE = (255, 255, 255)

# (item_x, item_y) point to the item; (label_x, label_y) is the label anchor.
# Coordinates are in original 1680x3648 space.
labels = [
    # name, (item_x, item_y), (label_x, label_y), anchor
    ('吸锡带',  (885, 945),  (40,   820), 'lt'),
    ('拔键器',  (870, 1130), (1300, 1050),'lt'),
    ('拔轴器',  (885, 1320), (40,  1290), 'lt'),
    ('焊锡丝',  (870, 1540), (1300, 1530),'lt'),
    ('螺丝刀',  (910, 1730), (1320, 1860),'lt'),
    ('吸锡器',  (880, 2150), (40,  2080), 'lt'),
    ('助焊膏',  (790, 2360), (1300, 2380),'lt'),
    ('电烙铁',  (945, 2620), (40,  2700), 'lt'),
    ('铜丝球',  (925, 2950), (1300, 2950),'lt'),
]

def draw_text_outlined(xy, text, font, fill, outline=WHITE, ow=4):
    x, y = xy
    for dx in range(-ow, ow+1):
        for dy in range(-ow, ow+1):
            if dx*dx + dy*dy <= ow*ow:
                draw.text((x+dx, y+dy), text, font=font, fill=outline)
    draw.text(xy, text, font=font, fill=fill)

for name, (ix, iy), (lx, ly), anchor in labels:
    # Draw arrow line from label to item
    lx_end = lx + 90
    ly_end = ly + 50
    draw.line([(lx_end, ly_end), (ix, iy)], fill=RED, width=6)
    # Draw small filled dot ON the item
    r = 10
    draw.ellipse([(ix - r, iy - r), (ix + r, iy + r)], fill=RED)
    # Draw label text with white outline
    draw_text_outlined((lx, ly), name, font=font, fill=RED)

img.save(dst, quality=92)
print('saved:', dst)
