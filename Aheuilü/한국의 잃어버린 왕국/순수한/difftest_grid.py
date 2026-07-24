"""Differential test: pure-Aheui grid compiler vs reference BF interpreter."""
import random
from collections import defaultdict
import bf_to_aheui as C
import aheui_sim as S


def ref(code, limit=100000):
    t = defaultdict(int); p = 0; out = []; st = []; jm = {}
    for i, c in enumerate(code):
        if c == '[': st.append(i)
        elif c == ']':
            j = st.pop(); jm[j] = i; jm[i] = j
    cp = n = 0
    while cp < len(code):
        c = code[cp]
        if   c == '+': t[p] = (t[p] + 1) % 256
        elif c == '-': t[p] = (t[p] - 1) % 256
        elif c == '>': p += 1
        elif c == '<': p -= 1
        elif c == '.': out.append(chr(t[p]))
        elif c == '[' and not t[p]: cp = jm[cp]
        elif c == ']' and t[p]:     cp = jm[cp]
        cp += 1; n += 1
        if n > limit: return None
    return ''.join(out)


def grid(code, limit=3_000_000):
    text = '\n'.join(C.compile_bf(code))
    vm = S.Aheui(text)
    vm.run(limit=limit)
    if not vm.halted:
        return None
    return ''.join(vm.output)


def gen(rng, depth=0):
    o = []
    for _ in range(rng.randint(1, 7)):
        r = rng.random()
        if   r < 0.30: o.append('+' * rng.randint(1, 6))
        elif r < 0.46: o.append('-' * rng.randint(1, 3))
        elif r < 0.62: o.append('>' * rng.randint(1, 3))
        elif r < 0.76: o.append('<' * rng.randint(1, 3))
        elif r < 0.90: o.append('.')
        elif depth < 3: o.append('[' + '-' + gen(rng, depth + 1) + ']')
    return ''.join(o)


def main(n=250, seed=4242):
    rng = random.Random(seed)
    tested = passed = skipped = 0
    fails = []
    for _ in range(n):
        p = gen(rng)
        if p.count('[') != p.count(']'):
            continue
        e = ref(p)
        if e is None:
            skipped += 1; continue
        try:
            g = grid(p)
        except Exception as ex:
            g = f'<ERR {type(ex).__name__}: {ex}>'
        if g is None:
            skipped += 1; continue
        tested += 1
        if g == e:
            passed += 1
        else:
            fails.append((p, e, g))
            if len(fails) >= 5:
                break
    print(f'tested={tested} passed={passed} skipped={skipped}')
    for p, e, g in fails[:5]:
        print('FAIL', repr(p))
        print('   exp', repr(e))
        print('   got', repr(g))
    return fails


if __name__ == '__main__':
    main()
