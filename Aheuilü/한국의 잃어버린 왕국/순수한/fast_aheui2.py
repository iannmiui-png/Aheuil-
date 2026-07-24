"""
fast_aheui2.py — Aheui VM with glide-skip tables.

The scaffold's loop bypass lanes are long vertical runs of blank cells.
The naive VM pays one step per blank cell, so skipping a loop costs
O(body rows) — for Lost Kingdom's outer loops that is millions of steps
of doing nothing.

Blank (non-syllable) cells are pure no-ops: they cannot change direction
or touch storage, so a run of them is observationally equivalent to a
single jump to the next occupied cell. This VM precomputes, per column,
the sorted row indices holding real syllables, split by parity because
the ㅠ/ㅛ vowels move two rows at a time and therefore only ever land on
rows of one parity.

Vertical glides then cost one binary search instead of thousands of
steps. Horizontal glides are left alone: rows are at most 18 wide.
"""

import bisect
import sys

BASE = 0xAC00
STROKES = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0]
SHORT = 4          # step this many cells manually before consulting the table


def load(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    return build(text)


def build(text):
    rows = text.split('\n')
    if rows and rows[-1] == '':
        rows.pop()
    W = max(len(r) for r in rows)
    H = len(rows)

    alpha = sorted({c for r in rows for c in r} | {' '})
    idx = {c: i for i, c in enumerate(alpha)}
    blank = idx[' ']
    grid = bytearray([blank]) * (W * H)
    trans = {ord(c): i for c, i in idx.items()}
    pos = 0
    for r in rows:
        if r:
            grid[pos:pos + len(r)] = r.translate(trans).encode('latin-1')
        pos += W
    del rows

    cho = [-1] * len(alpha); ju = [0] * len(alpha); jo = [0] * len(alpha)
    for c, i in idx.items():
        o = ord(c) - BASE
        if 0 <= o < 19 * 21 * 28:
            cho[i] = o // 588; ju[i] = (o % 588) // 28; jo[i] = o % 28

    # per-column occupied rows, split by parity
    occ = [[[], []] for _ in range(W)]
    for y in range(H):
        base = y * W
        p = y & 1
        for x in range(W):
            if cho[grid[base + x]] >= 0:
                occ[x][p].append(y)
    both = [sorted(occ[x][0] + occ[x][1]) for x in range(W)]

    return grid, W, H, cho, ju, jo, occ, both


def run(state, feed=None, limit=None, out=None):
    grid, W, H, CHO, JU, JO, OCC, BOTH = state
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

        if c < 0:
            # blank: glide. Try a few plain steps, then jump via the table.
            n = SHORT
            while n and CHO[grid[y * W + x]] < 0:
                x += dx; y += dy
                if y < 0: y = H - 1
                elif y >= H: y = 0
                if x < 0: x = W - 1
                elif x >= W: x = 0
                n -= 1
            if CHO[grid[y * W + x]] >= 0:
                continue
            if dx == 0 and dy:
                lst = BOTH[x] if abs(dy) == 1 else OCC[x][y & 1]
                if not lst:
                    return steps, False            # column is empty: would spin
                if dy > 0:
                    i = bisect.bisect_right(lst, y)
                    y = lst[i] if i < len(lst) else lst[0]
                else:
                    i = bisect.bisect_left(lst, y)
                    y = lst[i - 1] if i else lst[-1]
                continue
            # horizontal or diagonal: rows are narrow, plain stepping is fine
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
                if j == 21: write(str(n))
                elif j == 27: write(chr(n) if 0 <= n < 0x110000 else '?')
        elif c == 7:
            if j == 27:
                S.append(ord(feed.pop() if feed else (sys.stdin.read(1) or '\n')))
            elif j != 21:
                S.append(STROKES[j])
        elif c == 8:
            if not S: ok = False
            else: S.append(S[0] if cur == 21 else S[-1])
        elif c == 9:
            cur = j
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
            return steps, True

        if not ok:
            dx, dy = -dx, -dy

        x += dx; y += dy
        if y < 0: y = H - 1
        elif y >= H: y = 0
        if x < 0: x = W - 1
        elif x >= W: x = 0
