# -*- coding: utf-8 -*-
"""裁切 / 压缩飞利浦插排拆解照片，并在图片下部打上「图 x.y.z」角标。"""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = os.environ.get('PS_SRC') or r'Y:\Camera'
OUT = os.path.dirname(os.path.abspath(__file__))

FONT_BOLD = r'C:\Windows\Fonts\msyhbd.ttc'
FONT_FALLBACK = r'C:\Windows\Fonts\simhei.ttf'

# (源文件, 输出名, 图号, 裁剪模式, 额外参数)
# 模式 'p34' 竖图裁 3:4，参数为垂直中心百分比（0-100）
# 模式 'trim' 横图四边各裁掉百分比，参数为裁掉的比例
FIGS = [
    ('IMG_20261031_091438.jpg',         '01-strip-front.jpg',      '图 1.1.1', 'full', 0),
    ('IMG_20261012_213653.jpg',         '02-bottom-overview.jpg',  '图 1.2.1', 'rot_cw', 0),
    ('IMG_20261031_091416.jpg',         '03-triangle-screws.jpg',  '图 2.1.1', 'rot_cw', 0),
    ('IMG_20261031_102433.jpg',         '04-bit-set.jpg',          '图 2.2.1', 'trim', 0.03),
    ('IMG_20261031_091430.jpg',         '05-foot-pads.jpg',        '图 3.1.1', 'trim', 0.02),
    ('IMG_20261031_093822.jpg',         '06-caps-removed.jpg',     '图 3.2.1', 'trim', 0.01),
    ('IMG_20261031_095516.jpg',         '07-inside-overview.jpg',  '图 4.1.1', 'rot_cw', 0),
    ('IMG_20261031_095650.jpg',         '09-copper-busbar.jpg',    '图 4.2.2', 'trim', 0.02),
    ('IMG_20261031_095533.jpg',         '08-usb-psu-board.jpg',    '图 4.2.1', 'rot_ccw', 0, (0.21, 0.0, 0.0, 0.0)),
    ('IMG_20261031_095815.jpg',         '10-transformer-usb.jpg',  '图 4.2.3', 'trim', 0.02),
    ('IMG_20261031_095718.jpg',         '11-board-in-hand.jpg',    '图 4.2.4', 'trim', 0.02),
    ('IMG_20261031_100730.jpg',         '12-cracked-plastic.jpg',  '图 5.1.1', 'rot_cw', 0),
]

MAX_LONG_EDGE = 1600      # 长边上限
QUALITY = 82
BADGE = False             # 是否把图号烧进图片（章节结构会拽，平时关掉，图号只写在 markdown 里）


try:
    _ROT_CW = Image.Transpose.ROTATE_270   # 顺时针 90°
    _ROT_CCW = Image.Transpose.ROTATE_90   # 逆时针 90°
except AttributeError:          # 老版 Pillow
    _ROT_CW = Image.ROTATE_270
    _ROT_CCW = Image.ROTATE_90


def crop(pil, mode, arg):
    w, h = pil.size
    if mode == 'rot_cw':
        return pil.transpose(_ROT_CW)
    if mode == 'rot_ccw':
        return pil.transpose(_ROT_CCW)
    if mode == 'trim':
        dx, dy = int(w * arg), int(h * arg)
        return pil.crop((dx, dy, w - dx, h - dy))
    if mode in ('p34', 'p58'):
        # 目标宽高比 3:4 或 5:8
        target_h = int(w * (4 / 3 if mode == 'p34' else 8 / 5))
        if target_h >= h:
            return pil
        cy = int(h * arg / 100)
        top = cy - target_h // 2
        top = max(0, min(top, h - target_h))
        return pil.crop((0, top, w, top + target_h))
    return pil


def load_font(size):
    for path in (FONT_BOLD, FONT_FALLBACK):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def add_badge(pil, text):
    w, h = pil.size
    font = load_font(max(26, int(w / 30)))
    layer = Image.new('RGBA', pil.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = int(font.size * 0.62), int(font.size * 0.42)
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    margin = int(min(w, h) * 0.035)
    x0, y0 = margin, h - margin - bh
    radius = int(bh * 0.28)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=radius, fill=(15, 15, 18, 165))
    d.text((x0 + pad_x - bbox[0], y0 + pad_y - bbox[1]), text, font=font, fill=(255, 255, 255, 250))
    return Image.alpha_composite(pil.convert('RGBA'), layer).convert('RGB')


def main():
    for entry in FIGS:
        src_name, out_name, fig, mode, arg = entry[:5]
        post = entry[5] if len(entry) > 5 else None
        src = os.path.join(SRC, src_name)
        im = Image.open(src)
        im = im.convert('RGB')
        im = crop(im, mode, arg)
        if post:
            pw, ph = im.size
            l, r, t, b = post
            im = im.crop((int(pw * l), int(ph * t), pw - int(pw * r), ph - int(ph * b)))

        w, h = im.size
        scale = MAX_LONG_EDGE / max(w, h)
        if scale < 1:
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        if BADGE:
            im = add_badge(im, fig)

        dst = os.path.join(OUT, out_name)
        im.save(dst, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
        print('%-28s %-26s %s  %6.0f KB' % (src_name, out_name, fig,
                                            os.path.getsize(dst) / 1024))


if __name__ == '__main__':
    main()
