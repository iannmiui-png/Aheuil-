"""
hangul_tlsb.py — a variant of the TernLSB embedding technique, sized for
romanized-Aheui source text instead of raw Brainfuck.

Original TernLSB (tlsb.py): each pixel byte's value mod 9 selects one of
8 Brainfuck instructions; the 9th residue (mod 9 == 8) is reserved as a
terminator. This variant keeps exactly the same idea — overwrite only
the low residue of each byte, leaving the high part (orig // BASE * BASE)
intact so the pixel barely changes — just with a bigger alphabet sized
for our romanized-Aheui token text (lowercase letters, digits, space,
':', '_' — the last two needed for label syntax like ':loop' and the
compiler's auto-generated '__loop1_start' names).

Usage mirrors tlsb.py:
    encode_image(in_png, message_text, out_png)
    decode_image(png) -> message_text
    run_image(png)    -> compiles + runs the embedded romanized-Aheui program
"""

from PIL import Image
from roman_aheui_compile import compile_roman_aheui
from abclang_vm import ABCLang
import io
import contextlib

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789 :_"
assert len(ALPHABET) == 39
BASE = len(ALPHABET) + 1          # 40; residue 39 is the terminator
TERMINATOR_DIGIT = len(ALPHABET)  # 39

_INDEX = {ch: i for i, ch in enumerate(ALPHABET)}


def _set_byte(orig, digit):
    """Set orig's residue mod BASE to `digit`, changing orig as little as possible."""
    v = (orig // BASE) * BASE + digit
    while v >= 256:
        v -= BASE
    return v


def encode_bytes(d, message):
    """d: mutable list of pixel bytes (modified in place). message: str."""
    needed = len(message) + 1  # +1 for terminator byte
    if needed > len(d):
        raise ValueError(f"image too small: need {needed} bytes, have {len(d)}")
    for i, ch in enumerate(message):
        if ch not in _INDEX:
            raise ValueError(f"character {ch!r} not in alphabet: {ALPHABET!r}")
        d[i] = _set_byte(d[i], _INDEX[ch])
    d[len(message)] = _set_byte(d[len(message)], TERMINATOR_DIGIT)


def decode_bytes(d):
    out = []
    for b in d:
        idx = b % BASE
        if idx == TERMINATOR_DIGIT:
            break
        out.append(ALPHABET[idx])
    return ''.join(out)


def encode_image(in_path, message, out_path):
    im = Image.open(in_path)
    d = list(im.tobytes())
    encode_bytes(d, message)
    Image.frombytes(im.mode, im.size, bytes(d)).save(out_path)


def decode_image(path):
    im = Image.open(path)
    return decode_bytes(im.tobytes())


def run_image(path, stdin_text=''):
    message = decode_image(path)
    code = compile_roman_aheui(message)
    vm = ABCLang()
    vm.load_program(code)
    if stdin_text:
        vm.char_buffer = list(reversed(stdin_text))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        vm.run()
    return message, buf.getvalue()


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python hangul_tlsb.py <image.png>")
        sys.exit(1)
    _, output = run_image(sys.argv[1])
    print(output, end='')
