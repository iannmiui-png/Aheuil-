#!/usr/bin/env python3
"""
bf_to_png.py <source.b> [out.png] [options]

Compiles a Brainfuck program into a pure-Hangul Aheui grid and stores that
grid in a PNG, in the form aheui_console.html expects: each pixel byte's
residue mod 40 is an index into the alphabet, and residue 39 ends the data.

The alphabet is derived from bf_to_aheui's own block constants rather than
read from a file, so it can never drift from the compiler that produced the
grid. It is written back to aheui_alphabet.txt, and --sync will rewrite the
ALPHABET constant in the console page to match. (Skipping that step is how a
page ends up decoding a perfectly good PNG into garbage: change one leaf
block and every index past the first difference shifts.)

Options:
  --width N     pixels per row of the image        (default 1067)
  --dump F      also write the Aheui grid as text
  --sync F      rewrite the ALPHABET constant in an HTML page (repeatable)
  --flat        store raw indices: a near-black image, smallest file
  --verify      decode the PNG back and diff against the grid

Examples:
  python3 bf_to_png.py adv.b lost_kingdom_pure_aheui.png --sync aheui_console.html
  python3 bf_to_png.py hello.b hello.png --dump hello.aheui --verify
"""
import os
import re
import sys
import tempfile

from PIL import Image

import bf_to_aheui as C
import bf_to_aheui_stream as S

BASE = 40
TERM_DIGIT = 39

# Six brightness bands are available: any index 0..37 plus 40*k stays inside a
# byte for k <= 5. Bands are cosmetic only -- the decoder sees the residue --
# so they can be used to give the image visible structure.
BAND_BLANK = 0      # spaces: the bypass lanes, most of the picture
BAND_NL = 5         # row ends: a bright edge down the right of each row
BAND_CODE = 3       # syllables


def alphabet():
    """The full set of symbols this compiler can emit, in index order."""
    syms = set()
    for name in ('BLOCK_PLUS', 'BLOCK_MINUS', 'BLOCK_OUT', 'BLOCK_IN',
                 'BLOCK_RIGHT', 'BLOCK_LEFT', 'BLOCK_HALT', 'BLOCK_BEGIN'):
        for row in getattr(C, name):
            syms |= set(row)
    for name in ('DUP_SKIP2', 'NOOP_RIGHT', 'NOOP_LEFT', 'NOOP_DOWN',
                 'NOOP_UP', 'CHECK_DOWN', 'CHECK_UP'):
        syms.add(getattr(C, name))
    syms |= {' ', '\n'}
    a = ''.join(sorted(syms))
    if len(a) > TERM_DIGIT:
        raise SystemExit(f'alphabet has {len(a)} symbols; only {TERM_DIGIT} fit')
    return a


def compile_grid(src_path, grid_path):
    """BF source -> Aheui grid text on disk, streamed (the full game is ~10 MB)."""
    src = open(src_path, encoding='utf-8', errors='replace').read()
    with open(grid_path, 'w', encoding='utf-8') as f:
        rows, width = S.compile_to_file(src, f)
    return rows, width


def encode(grid_path, png_path, alpha, width=1067, flat=False):
    idx = {c: i for i, c in enumerate(alpha)}
    if flat:
        val = {c: i for c, i in idx.items()}
    else:
        val = {}
        for c, i in idx.items():
            band = BAND_NL if c == '\n' else BAND_BLANK if c == ' ' else BAND_CODE
            val[c] = i + BASE * band
    trans = {ord(c): v for c, v in val.items()}

    out = bytearray()
    with open(grid_path, encoding='utf-8') as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            try:
                out += chunk.translate(trans).encode('latin-1')
            except (TypeError, ValueError):
                bad = sorted({c for c in chunk if c not in idx})
                raise SystemExit(f'grid contains symbols outside the alphabet: {bad}')
    out.append(TERM_DIGIT + BASE * 5)          # 239: bright, and unmistakable

    h = (len(out) + width - 1) // width
    out += bytes(width * h - len(out))         # tail padding is never read
    im = Image.frombytes('L', (width, h), bytes(out))
    im.save(png_path, optimize=True)
    return width, h


def decode(png_path, alpha):
    """The reader's half, kept here so --verify tests the round trip."""
    data = Image.open(png_path).tobytes()
    out = []
    for b in data:
        r = b % BASE
        if r == TERM_DIGIT:
            break
        out.append(alpha[r])
    return ''.join(out)


def sync_html(path, alpha):
    esc = ''.join('\\n' if c == '\n' else c if c == ' ' else '\\u%04X' % ord(c)
                  for c in alpha)
    src = open(path, encoding='utf-8').read()
    new, n = re.subn(r'const\s+ALPHABET\s*=\s*"[^"]*";',
                     lambda _m: 'const ALPHABET = "%s";' % esc, src, count=1)
    if n:
        open(path, 'w', encoding='utf-8').write(new)
    return bool(n)


def main(argv):
    args, opts = [], {'width': 1067, 'sync': [], 'dump': None,
                      'flat': False, 'verify': False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--width':
            i += 1; opts['width'] = int(argv[i])
        elif a == '--dump':
            i += 1; opts['dump'] = argv[i]
        elif a == '--sync':
            i += 1; opts['sync'].append(argv[i])
        elif a == '--flat':
            opts['flat'] = True
        elif a == '--verify':
            opts['verify'] = True
        elif a in ('-h', '--help'):
            print(__doc__); return 0
        else:
            args.append(a)
        i += 1

    if not args:
        print(__doc__); return 1
    src = args[0]
    png = args[1] if len(args) > 1 else os.path.splitext(src)[0] + '.png'

    alpha = alphabet()
    with open('aheui_alphabet.txt', 'w', encoding='utf-8') as f:
        f.write(alpha)

    grid = opts['dump'] or tempfile.mktemp(suffix='.aheui')
    say = sys.stderr.write
    say(f'{src}: compiling to Aheui...\n')
    rows, width = compile_grid(src, grid)
    say(f'  {rows:,} rows x {width} cols, {os.path.getsize(grid):,} bytes of text\n')

    say('  encoding to PNG...\n')
    W, H = encode(grid, png, alpha, opts['width'], opts['flat'])
    say(f'  {png}: {W} x {H} px, {os.path.getsize(png):,} bytes\n')

    if opts['verify']:
        say('  verifying round trip...\n')
        want = open(grid, encoding='utf-8').read()
        got = decode(png, alpha)
        if got != want:
            n = next((k for k in range(min(len(got), len(want)))
                      if got[k] != want[k]), min(len(got), len(want)))
            say(f'  MISMATCH at char {n:,} '
                f'(got {len(got):,} chars, want {len(want):,})\n')
            return 1
        say(f'  round trip exact: {len(got):,} chars\n')

    for h in opts['sync']:
        say(f'  {h}: {"ALPHABET synced" if sync_html(h, alpha) else "no ALPHABET found"}\n')

    if not opts['dump']:
        os.unlink(grid)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
