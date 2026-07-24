"""
Generates an original, purely programmatic background image — a grid of
concentric ring motifs in a few accent colors. This is my own generative
pattern, not a reproduction of any existing artwork, sized generously so
the LSB-embedding step barely perturbs any pixel.
"""

from PIL import Image, ImageDraw
import math

W, H = 240, 240
im = Image.new('RGBA', (W, H), (24, 28, 38, 255))
draw = ImageDraw.Draw(im)

palette = [(224, 122, 95, 255), (129, 178, 154, 255), (242, 204, 143, 255), (61, 90, 128, 255)]

cell = 40
for gy in range(0, H, cell):
    for gx in range(0, W, cell):
        cx, cy = gx + cell // 2, gy + cell // 2
        color = palette[(gx // cell + gy // cell) % len(palette)]
        for r in range(cell // 2 - 2, 2, -6):
            bbox = [cx - r, cy - r, cx + r, cy + r]
            draw.ellipse(bbox, outline=color, width=2)

im.save('/home/claude/original.png')
print('saved', im.size, im.mode)
