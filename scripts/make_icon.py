# 锚 MindAnchor — 图标生成工具：用 PIL 绘制呼吸圆环风格应用图标。用法：python make_icon.py（输出 app/icons/）
"""生成 锚 MindAnchor 应用图标：深色圆角底 + 呼吸圆环 + 顶部锚点"""
from PIL import Image, ImageDraw, ImageFilter
import math

def make_icon(size):
    S = size
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 圆角背景（maskable：铺满整图，内容居中）
    r = int(S * 0.22)
    bg = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    bd.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=(15, 28, 38, 255))
    # 柔和渐变：上深下浅
    grad = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        t = y / S
        c = (int(15 + 8 * t), int(28 + 6 * t), int(38 + 5 * t), 255)
        gd.line([(0, y), (S, y)], fill=c)
    bg = Image.composite(grad, bg, bg.split()[3].point(lambda a: a))
    img = Image.alpha_composite(img, bg)

    cx, cy = S / 2, S / 2

    # 外圈（半透明细环）
    r_out = int(S * 0.335)
    lw_out = max(2, int(S * 0.018))
    d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out],
              outline=(78, 201, 176, 90), width=lw_out)

    # 内圈（主环）
    r_in = int(S * 0.235)
    lw_in = max(3, int(S * 0.045))
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in],
              outline=(78, 201, 176, 255), width=lw_in)

    # 顶部锚点（小圆点，像呼吸的"吸"）
    dot_r = max(3, int(S * 0.030))
    dot_x, dot_y = cx, cy - r_in - int(S * 0.075)
    d.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
              fill=(127, 214, 196, 255))

    # 中心小亮点
    dot2_r = max(2, int(S * 0.014))
    d.ellipse([cx - dot2_r, cy - dot2_r, cx + dot2_r, cy + dot2_r],
              fill=(127, 214, 196, 200))

    return img

for s in (192, 512):
    make_icon(s).save(f'C:/Users/25671/mindanchor/icons/icon-{s}.png')
    print(f'icon-{s}.png written')
