#!/usr/bin/env python3
"""play_pure.py <image.png> [input.txt]

Runs the pure-Hangul Aheui program stored in a PNG. No Brainfuck, no
romanization, no bytecode -- the decoded text is a real Aheui 2D grid
that any conforming Aheui interpreter can execute.

Embedded game: Lost Kingdom (C) Jon Ripley 2004, 2005,
Brainfuck Edition v0.11 -- mechanically translated to Aheui.

Storage: each pixel byte's residue mod 40 indexes the alphabet in
aheui_alphabet.txt (36 Hangul syllables + space + newline); residue 39
terminates. Rows are stored right-stripped and re-padded on load, since
the bypass lanes need a rectangular grid at run time but not on disk.

Note: `python play_pure.py --dump out.aheui image.png` writes the Aheui
source out instead of running it.
"""
import sys
from PIL import Image

BASE = 0xAC00
STROKES = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0]


def decode(png, alphabet):
    data = Image.open(png).tobytes()
    out = []
    for b in data:
        r = b % 40
        if r == 39:
            break
        out.append(alphabet[r])
    return ''.join(out)


def build(text):
    rows = text.split('\n')
    if rows and rows[-1] == '':
        rows.pop()
    w = max(len(r) for r in rows)
    h = len(rows)
    alpha = sorted({c for r in rows for c in r} | {' '})
    idx = {c: i for i, c in enumerate(alpha)}
    blank = idx[' ']
    grid = bytearray([blank]) * (w * h)
    trans = {ord(c): i for c, i in idx.items()}
    pos = 0
    for r in rows:
        if r:
            grid[pos:pos + len(r)] = r.translate(trans).encode('latin-1')
        pos += w
    cho = [-1] * len(alpha); ju = [0] * len(alpha); jo = [0] * len(alpha)
    for c, i in idx.items():
        o = ord(c) - BASE
        if 0 <= o < 19 * 21 * 28:
            cho[i] = o // 588; ju[i] = (o % 588) // 28; jo[i] = o % 28
    return grid, w, h, cho, ju, jo


def run(grid, W, H, CHO, JU, JO, feed):
    st = [[] for _ in range(28)]
    cur = 0; x = y = 0; dx, dy = 1, 0
    w = sys.stdout.write
    feed = list(reversed(feed)) if feed else []
    while True:
        s = grid[y * W + x]
        c = CHO[s]
        if c < 0:
            x += dx; y += dy
            y = H - 1 if y < 0 else (0 if y >= H else y)
            x = W - 1 if x < 0 else (0 if x >= W else x)
            continue
        v = JU[s]; j = JO[s]
        if   v == 0:  dx, dy = 1, 0
        elif v == 2:  dx, dy = 2, 0
        elif v == 4:  dx, dy = -1, 0
        elif v == 6:  dx, dy = -2, 0
        elif v == 8:  dx, dy = 0, -1
        elif v == 12: dx, dy = 0, -2
        elif v == 13: dx, dy = 0, 1
        elif v == 17: dx, dy = 0, 2
        elif v == 18: dy = -dy
        elif v == 19: dx, dy = -dx, -dy
        elif v == 20: dx = -dx
        ok = True; S = st[cur]
        if c == 2:
            if len(S) < 2: ok = False
            else: a = S.pop(); b = S.pop(); S.append(0 if a == 0 else int(b / a))
        elif c == 3:
            if len(S) < 2: ok = False
            else: a = S.pop(); S[-1] += a
        elif c == 4:
            if len(S) < 2: ok = False
            else: a = S.pop(); S[-1] *= a
        elif c == 5:
            if len(S) < 2: ok = False
            else: a = S.pop(); b = S.pop(); S.append(0 if a == 0 else b % a)
        elif c == 6:
            if not S: ok = False
            else:
                n = S.pop(0) if cur == 21 else S.pop()
                if j == 21: w(str(n))
                elif j == 27: w(chr(n) if 0 <= n < 0x110000 else '?')
        elif c == 7:
            if j == 27:
                S.append(ord(feed.pop() if feed else (sys.stdin.read(1) or '\n')))
            elif j != 21:
                S.append(STROKES[j])
        elif c == 8:
            if not S: ok = False
            else: S.append(S[0] if cur == 21 else S[-1])
        elif c == 9: cur = j
        elif c == 10:
            if not S: ok = False
            else:
                n = S.pop(0) if cur == 21 else S.pop()
                if j != 27: st[j].append(n)
        elif c == 12:
            if len(S) < 2: ok = False
            else: a = S.pop(); b = S.pop(); S.append(1 if b >= a else 0)
        elif c == 14:
            if not S: ok = False
            else:
                n = S.pop(0) if cur == 21 else S.pop()
                if n == 0: dx, dy = -dx, -dy
        elif c == 15:
            if len(S) < 2: ok = False
            else: S[-1], S[-2] = S[-2], S[-1]
        elif c == 16:
            if len(S) < 2: ok = False
            else: a = S.pop(); S[-1] -= a
        elif c == 17:
            if not S: ok = False
            else:
                n = S[0] if cur == 21 else S[-1]
                if j != 27: st[j].append(n)
        elif c == 18:
            return
        if not ok: dx, dy = -dx, -dy
        x += dx; y += dy
        y = H - 1 if y < 0 else (0 if y >= H else y)
        x = W - 1 if x < 0 else (0 if x >= W else x)


def main():
    a = sys.argv[1:]
    dump = None
    if a and a[0] == '--dump':
        dump = a[1]; a = a[2:]
    if not a:
        print(__doc__); return 1
    alphabet = open('aheui_alphabet.txt', encoding='utf-8').read()
    sys.stderr.write('픽셀에서 아희 격자를 복원하는 중...\n')
    text = decode(a[0], alphabet)
    if dump:
        open(dump, 'w', encoding='utf-8').write(text)
        sys.stderr.write(f'{len(text)}자를 {dump}에 저장했습니다\n')
        return 0
    feed = open(a[1], encoding='utf-8').read() if len(a) > 1 else None
    grid, W, H, C, J, O = build(text)
    sys.stderr.write(f'{H:,}행 x {W}열 격자, 실행 시작\n\n')
    run(grid, W, H, C, J, O, feed)
    return 0


if __name__ == '__main__':
    sys.exit(main())
