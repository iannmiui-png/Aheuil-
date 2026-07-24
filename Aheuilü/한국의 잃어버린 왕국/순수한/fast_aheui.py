"""
fast_aheui.py — memory-efficient Aheui VM.

The reference simulator stores the grid as a list-of-lists of Python ints,
which for Lost Kingdom's 8.17M x 18 grid would be several GB. This keeps
the grid as a single flat bytearray of symbol indices (the generated code
uses only ~38 distinct characters), with the choseong/jungseong/jongseong
triples pre-decomposed into small lookup tables. ~147 MB instead.

Semantics follow aheui_sim.py, which was validated against Aheui.lua.
"""

import sys

BASE = 0xAC00
STROKES = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0]


def load(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
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
    del rows

    # pre-decompose each symbol
    cho = [-1] * len(alpha); ju = [-1] * len(alpha); jo = [-1] * len(alpha)
    for c, i in idx.items():
        o = ord(c) - BASE
        if 0 <= o < 19 * 21 * 28:
            cho[i] = o // (21 * 28)
            ju[i] = (o % (21 * 28)) // 28
            jo[i] = o % 28
    return grid, w, h, cho, ju, jo


def run(path, feed=None, limit=None, out=None):
    grid, W, H, CHO, JU, JO = load(path)
    st = [[] for _ in range(28)]
    cur = 0
    x = y = 0
    dx, dy = 1, 0
    steps = 0
    write = (out or sys.stdout).write
    feed = list(reversed(feed)) if feed else []

    while True:
        if limit is not None and steps >= limit:
            return steps, False
        steps += 1

        s = grid[y * W + x]
        c = CHO[s]
        if c < 0:                                  # blank / non-syllable: glide
            x += dx; y += dy
            if y < 0: y = H - 1
            elif y >= H: y = 0
            if x < 0: x = W - 1
            elif x >= W: x = 0
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

        ok = True
        S = st[cur]

        if c == 2:                                  # ㄴ div
            if len(S) < 2: ok = False
            else:
                a = S.pop(); b = S.pop(); S.append(0 if a == 0 else int(b / a))
        elif c == 3:                                # ㄷ add
            if len(S) < 2: ok = False
            else:
                a = S.pop(); b = S.pop(); S.append(b + a)
        elif c == 4:                                # ㄸ mul
            if len(S) < 2: ok = False
            else:
                a = S.pop(); b = S.pop(); S.append(b * a)
        elif c == 5:                                # ㄹ mod
            if len(S) < 2: ok = False
            else:
                a = S.pop(); b = S.pop(); S.append(0 if a == 0 else b % a)
        elif c == 6:                                # ㅁ pop / output
            if not S: ok = False
            else:
                n = S.pop(0) if cur == 21 else S.pop()
                if j == 21: write(str(n))
                elif j == 27: write(chr(n) if 0 <= n < 0x110000 else '?')
        elif c == 7:                                # ㅂ push
            if j == 21:
                pass
            elif j == 27:
                ch = feed.pop() if feed else (sys.stdin.read(1) or '\n')
                S.append(ord(ch))
            else:
                S.append(STROKES[j])
        elif c == 8:                                # ㅃ dup
            if not S: ok = False
            else: S.append(S[0] if cur == 21 else S[-1])
        elif c == 9:                                # ㅅ select
            cur = j
        elif c == 10:                               # ㅆ move
            if not S: ok = False
            else:
                n = S.pop(0) if cur == 21 else S.pop()
                if j != 27: st[j].append(n)
        elif c == 12:                               # ㅈ compare
            if len(S) < 2: ok = False
            else:
                a = S.pop(); b = S.pop(); S.append(1 if b >= a else 0)
        elif c == 14:                               # ㅊ conditional
            if not S: ok = False
            else:
                n = S.pop(0) if cur == 21 else S.pop()
                if n == 0: dx, dy = -dx, -dy
        elif c == 15:                               # ㅋ swap
            if len(S) < 2: ok = False
            else: S[-1], S[-2] = S[-2], S[-1]
        elif c == 16:                               # ㅌ sub
            if len(S) < 2: ok = False
            else:
                a = S.pop(); b = S.pop(); S.append(b - a)
        elif c == 17:                               # ㅍ copy
            if not S: ok = False
            else:
                n = S[0] if cur == 21 else S[-1]
                if j != 27: st[j].append(n)
        elif c == 18:                               # ㅎ halt
            return steps, True

        if not ok:
            dx, dy = -dx, -dy

        x += dx; y += dy
        if y < 0: y = H - 1
        elif y >= H: y = 0
        if x < 0: x = W - 1
        elif x >= W: x = 0
