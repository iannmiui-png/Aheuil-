#!/usr/bin/env python3
"""play.py <image.png> [input.txt] — run the Aheui program stored in a PNG.
Embedded game: Lost Kingdom (C) Jon Ripley 2004, 2005, Brainfuck Edition v0.11."""
import sys, itertools
from PIL import Image

AL = "abcdefghijklmnopqrstuvwxyz0123456789 :_"
S = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0]
J = "|k|kk|ks|n|nj|nh|t|l|lg|lm|lb|ls|lt|lp|lh|m|p|bs|s|ss|ng|j|ch|kh|th|ph|h".split("|")
PUSH = {}
for i, s in enumerate(S):
    if i not in (21, 27):
        PUSH.setdefault("ba" + J[i], s)
OPS = {'ma':1,'ka':2,'ppa':3,'na':5,'da':8,'ta':9,'tta':10,'ra':12,
       'pa':14,'ssa':15,'bah':17,'mah':19,'jja':24}

px = Image.open(sys.argv[1]).tobytes()
src = ''.join(AL[b % 40] for b in itertools.takewhile(lambda b: b % 40 != 39, px))
code, lab, act = [], {}, 'A'
for t in src.split():
    if t[0] == ':':                lab[t[1:]] = len(code)
    elif t in OPS:                 code.append((OPS[t], 0))
    elif t in PUSH:                code.append((0, PUSH[t]))
    elif t in ('sa', 'sak'):
        w = 'A' if t == 'sa' else 'B'
        if w != act: code.append((6, 0)); act = w
    elif t[:4] == 'cho:':          code.append((21, t[4:]))
    elif t[:4] == 'chu:':          code.append((20, t[4:]))
    elif t[:3] == 'ja:':           code.append((23, t[3:]))
    else:                          raise SystemExit("bad token: " + t)

feed = list(reversed(open(sys.argv[2]).read())) if len(sys.argv) > 2 else []
cur, oth, cs, reg, pc, n, w = [], [], [], 0, 0, len(code), sys.stdout.write
while 0 <= pc < n:
    o, a = code[pc]; pc += 1
    if   o == 0:  cur.append(a)
    elif o == 14: cur.append(reg)
    elif o == 15:
        if cur: reg = cur.pop()
    elif o == 5:
        if oth: cur.append(oth[-1])
    elif o == 3:
        if cur: cur.append(cur[-1])
    elif o == 1:
        if cur: cur.pop()
    elif o == 8:
        if len(cur) > 1: v = cur.pop(); cur[-1] += v
    elif o == 9:
        if len(cur) > 1: v = cur.pop(); cur[-1] -= v
    elif o == 10:
        if len(cur) > 1: v = cur.pop(); cur[-1] *= v
    elif o == 12:
        if len(cur) > 1: v = cur.pop(); cur[-1] = cur[-1] % v if v else 0
    elif o == 6:  cur, oth = oth, cur
    elif o == 21:
        if cur and cur.pop() == 0: pc = lab[a]
    elif o == 20: pc = lab[a]
    elif o == 23: cs.append(pc); pc = lab[a]
    elif o == 24: pc = cs.pop() if cs else n
    elif o == 19:
        if cur:
            c = cur.pop()
            if c >= 0: w(chr(c)); sys.stdout.flush()
    elif o == 17: cur.append(ord(feed.pop() if feed else (sys.stdin.read(1) or '\n')))
    elif o == 2:
        if len(cur) > 1: cur[-1], cur[-2] = cur[-2], cur[-1]
