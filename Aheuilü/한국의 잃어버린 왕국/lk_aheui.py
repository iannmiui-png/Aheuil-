#!/usr/bin/env python3
"""
lk_aheui.py — 잃어버린 왕국 아희 에디션 (Lost Kingdom, Aheui Edition)

    python lk_aheui.py lost_kingdom_aheui.png
    python lk_aheui.py lost_kingdom_aheui.png save.txt    # scripted input

The game embedded in this PNG is:

    Lost Kingdom
    (C) Jon Ripley 2004, 2005
    Brainfuck Edition v0.11

Jon Ripley's original program and its copyright are unchanged — the
Brainfuck source was mechanically translated into romanized Aheui and
then stored in the pixels of a Korean parody webpage. The banner the
game prints at startup is his, verbatim.

──────────────────────────────────────────────────────────────────────
HOW IT WORKS

1. Storage.  Each pixel byte's residue mod 40 encodes one character of
   the alphabet "a-z 0-9 space : _"; residue 39 terminates the program.
   This is a widened variant of the TernLSB scheme (which uses mod 9 to
   encode Brainfuck's eight symbols). Only the residue is rewritten, so
   every byte moves by at most 39 and the page still looks like a page.

2. Source.  The decoded text is romanized Aheui — Aheui syllables
   spelled by their Korean pronunciation:

       sa/sak  ㅅ  select storage (→ ABCLang stack A / B)
       ba…     ㅂ  push (value = stroke count of the final consonant)
       da ta tta ra    ㄷ ㅌ ㄸ ㄹ   add subtract multiply modulo
       ppa ma ka       ㅃ ㅁ ㅋ      dup drop swap
       pa ssa          ㅍ ㅆ         load / store the register
       bah mah         ㅂㅎ ㅁㅎ     read char / write char
       na jja          ㄴ ㅉ         over / return   (DSL extensions)
       cho:L chu:L ja:L  초 추 ㅈ    jump-if-zero / jump / call
       :L                             label

3. Machine.  Tokens assemble to ABCLang bytecode and run on its
   dual-stack VM. The Brainfuck tape is modelled as:

       register = the current cell
       stack A  = the tape to the left   (-1 sentinel at the bottom)
       stack B  = the tape to the right  (-1 sentinel at the bottom)

   Moving the pointer pushes the current cell onto one stack and pops
   the neighbour off the other; hitting a sentinel yields a fresh 0
   cell. Runs of pointer moves are done with doubling subroutines
   (r1, r2, r4 … r1024), which is what keeps 2.13M Brainfuck
   instructions down to a 4.5 MB source instead of 218 MB.
"""

import sys
from PIL import Image

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789 :_"
BASE, TERM = 40, 39

# ── romanized Aheui token → ABCLang opcode id ────────────────────────────────
PUSH, DROP, SWAP, DUP, ROT, OVER, SWITCH, PICK = 0, 1, 2, 3, 4, 5, 6, 7
ADD, SUB, MUL, DIV, MOD, NOT, LOAD, STORE      = 8, 9, 10, 11, 12, 13, 14, 15
READNUM, READCHAR, WRITENUM, WRITECHAR         = 16, 17, 18, 19
JMP, JZ, JN, CALL, RET, LABEL, END             = 20, 21, 22, 23, 24, 25, 26

SIMPLE = {
    'ma': DROP, 'ka': SWAP, 'ppa': DUP, 'da': ADD, 'ta': SUB,
    'tta': MUL, 'ra': MOD, 'pa': LOAD, 'ssa': STORE,
    'bah': READCHAR, 'mah': WRITECHAR, 'na': OVER, 'jja': RET,
}
# push tokens: ㅂ + ㅏ + final consonant, value = that consonant's stroke count
STROKES = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0]
JONG = ["","k","kk","ks","n","nj","nh","t","l","lg","lm","lb","ls","lt","lp",
        "lh","m","p","bs","s","ss","ng","j","ch","kh","th","ph","h"]
PUSHTOK = {}
for _j, _s in enumerate(STROKES):
    if _j in (21, 27):
        continue
    _t = 'ba' + JONG[_j]
    if _t not in PUSHTOK:
        PUSHTOK[_t] = _s


def decode(path):
    """Recover the romanized-Aheui source text from the image."""
    out = []
    for b in Image.open(path).tobytes():
        r = b % BASE
        if r == TERM:
            break
        out.append(ALPHABET[r])
    return ''.join(out)


def assemble(tokens):
    """Romanized-Aheui tokens → (code, labels) for the VM."""
    code, labels, active = [], {}, 'A'
    for t in tokens:
        if t[0] == ':':
            labels[t[1:]] = len(code)
        elif t in SIMPLE:
            code.append((SIMPLE[t], 0))
        elif t in PUSHTOK:
            code.append((PUSH, PUSHTOK[t]))
        elif t == 'sa':
            if active != 'A':
                code.append((SWITCH, 0)); active = 'A'
        elif t == 'sak':
            if active != 'B':
                code.append((SWITCH, 0)); active = 'B'
        elif t.startswith('cho:'):
            code.append((JZ, t[4:]))
        elif t.startswith('chu:'):
            code.append((JMP, t[4:]))
        elif t.startswith('ja:'):
            code.append((CALL, t[3:]))
        else:
            raise ValueError('unknown token: %r' % t)
    return code, labels


def run(code, labels, feed=None):
    A, B, calls = [], [], []
    cur, other = A, B
    reg, pc = 0, 0
    buf = []
    w = sys.stdout.write
    n = len(code)

    def readch():
        if buf:
            return buf.pop()
        if feed is not None and feed:
            return feed.pop()
        c = sys.stdin.read(1)
        return c if c else '\n'

    while 0 <= pc < n:
        op, arg = code[pc]
        pc += 1

        if op == PUSH:      cur.append(arg)
        elif op == LOAD:    cur.append(reg)
        elif op == STORE:
            if cur: reg = cur.pop()
        elif op == OVER:
            if other: cur.append(other[-1])
        elif op == DUP:
            if cur: cur.append(cur[-1])
        elif op == DROP:
            if cur: cur.pop()
        elif op == ADD:
            if len(cur) > 1:
                a = cur.pop(); cur[-1] += a
        elif op == SUB:
            if len(cur) > 1:
                a = cur.pop(); cur[-1] -= a
        elif op == MUL:
            if len(cur) > 1:
                a = cur.pop(); cur[-1] *= a
        elif op == MOD:
            if len(cur) > 1:
                a = cur.pop()
                cur[-1] = cur[-1] % a if a else 0
        elif op == SWITCH:
            cur, other = other, cur
        elif op == JZ:
            if cur and cur.pop() == 0:
                pc = labels[arg]
        elif op == JMP:
            pc = labels[arg]
        elif op == CALL:
            calls.append(pc); pc = labels[arg]
        elif op == RET:
            pc = calls.pop() if calls else n
        elif op == WRITECHAR:
            if cur:
                c = cur.pop()
                if c >= 0:
                    w(chr(c)); sys.stdout.flush()
        elif op == READCHAR:
            cur.append(ord(readch()))
        elif op == SWAP:
            if len(cur) > 1:
                cur[-1], cur[-2] = cur[-2], cur[-1]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    feed = None
    if len(sys.argv) >= 3:
        with open(sys.argv[2], encoding='utf-8') as f:
            feed = list(reversed(f.read()))

    sys.stderr.write("픽셀에서 아희 소스를 복원하는 중... ")
    src = decode(sys.argv[1])
    tokens = src.split()
    sys.stderr.write("%d개 토큰\n" % len(tokens))

    sys.stderr.write("ABCLang 바이트코드로 변환하는 중... ")
    code, labels = assemble(tokens)
    sys.stderr.write("%d개 명령어\n\n" % len(code))

    run(code, labels, feed)
    return 0


if __name__ == '__main__':
    sys.exit(main())
