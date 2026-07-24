from roman_aheui_compile import compile_roman_aheui
from abclang_vm import ABCLang
import io, contextlib

def run(source):
    code = compile_roman_aheui(source)
    vm = ABCLang()
    vm.load_program(code)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        vm.run()
    return buf.getvalue()

tests = [
    # (name, romanized source, expected output)
    ("Adder 3+5=8",       "bat bal da mang hui", "8"),
    ("Multiplier 4*5=20", "bam bal tta mang hui", "20"),
    ("Stack Demo LIFO",   "bat bal mang mang hui", "53"),
    ("Countdown 5..1",
     "bal ppa cho ppa mang bat bak ta ta ppa chu hui", "54321"),
]

all_ok = True
for name, src, expected in tests:
    try:
        out = run(src)
    except Exception as e:
        out = f"<ERROR: {e}>"
    ok = (out == expected)
    all_ok &= ok
    print(f"{name:20s} expected={expected!r:10s} got={out!r:10s} [{'OK' if ok else 'FAIL'}]")

print()
print("ALL OK:", all_ok)
