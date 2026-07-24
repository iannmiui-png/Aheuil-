"""
bf_to_roman_stream.py — streams BF → romanized-Aheui token text to a file.

Emits the canonical romanized token stream directly (rather than building
an ABCLang op list first), so memory stays flat while compiling Lost
Kingdom's 2.13M instructions. Semantics are identical to bf_to_abc2 —
same tape model, same doubling ladders, same "active stack = A at every
label, jump and call" invariant.

Label names are base-36 encoded to keep the stored source compact.
"""

from itertools import groupby
from roman_aheui import spell_syllable

_STROKES = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0]
_S2J = {}
for _j, _s in enumerate(_STROKES):
    if _j not in (21, 27) and _s not in _S2J:
        _S2J[_s] = _j

PUSH_TOK = {s: spell_syllable(7, 0, j) for s, j in _S2J.items()}

SEL_A = spell_syllable(9, 0, 0)     # sa
SEL_B = spell_syllable(9, 0, 1)     # sak
T_ADD = spell_syllable(3, 0, 0)     # da
T_SUB = spell_syllable(16, 0, 0)    # ta
T_MUL = spell_syllable(4, 0, 0)     # tta
T_MOD = spell_syllable(5, 0, 0)     # ra
T_DUP = spell_syllable(8, 0, 0)     # ppa
T_DROP= spell_syllable(6, 0, 0)     # ma
T_LOAD= spell_syllable(17, 0, 0)    # pa
T_STOR= spell_syllable(10, 0, 0)    # ssa
T_OVER= spell_syllable(2, 0, 0)     # na
T_RET = spell_syllable(13, 0, 0)    # jja
T_RCH = spell_syllable(7, 0, 27)    # bah
T_WCH = spell_syllable(6, 0, 27)    # mah

_B36 = '0123456789abcdefghijklmnopqrstuvwxyz'
def b36(n):
    if n == 0: return '0'
    s = ''
    while n:
        s = _B36[n % 36] + s
        n //= 36
    return s

# ── optimal push tables (values 0..1024 via arithmetic on stroke counts) ─────
def _build_expr():
    best = {}
    for s in _S2J:
        if 0 <= s <= 1024: best[s] = ('d', s)
    changed = True
    while changed:
        changed = False
        snap = list(best.keys())
        for a in snap:
            for b in snap:
                for r, k in ((a+b,'+'), (a-b,'-'), (a*b,'*')):
                    if 0 <= r <= 1024 and r not in best:
                        best[r] = (k, a, b); changed = True
    return best
_EXPR = _build_expr()


class TokenEmitter:
    def __init__(self, out, flush_at=200000):
        self.out = out
        self.buf = []
        self.active = 'A'
        self._lc = 0
        self.flush_at = flush_at
        self.count = 0

    def _t(self, tok):
        self.buf.append(tok)
        self.count += 1
        if len(self.buf) >= self.flush_at:
            self.out.write(' '.join(self.buf) + ' ')
            self.buf = []

    def finish(self):
        if self.buf:
            self.out.write(' '.join(self.buf))
            self.buf = []

    def lbl(self, p=''):
        self._lc += 1
        return p + b36(self._lc)

    def on_A(self):
        if self.active != 'A':
            self._t(SEL_A); self.active = 'A'
    def on_B(self):
        if self.active != 'B':
            self._t(SEL_B); self.active = 'B'

    # invariant: A active before every label / jump / call
    def label(self, n): self.on_A(); self._t(':' + n)
    def jz(self, n):    self.on_A(); self._t('cho:' + n)
    def jmp(self, n):   self.on_A(); self._t('chu:' + n)
    def call(self, n):  self.on_A(); self._t('ja:' + n)
    def ret(self):      self.on_A(); self._t(T_RET)

    def push_raw(self, v): self._t(PUSH_TOK[v])
    def dup(self):   self._t(T_DUP)
    def drop(self):  self._t(T_DROP)
    def over(self):  self._t(T_OVER)
    def add(self):   self._t(T_ADD)
    def sub(self):   self._t(T_SUB)
    def mul(self):   self._t(T_MUL)
    def mod(self):   self._t(T_MOD)
    def load(self):  self._t(T_LOAD)
    def store(self): self._t(T_STOR)
    def rchar(self): self._t(T_RCH)
    def wchar(self): self._t(T_WCH)

    def push_n(self, n):
        if n in _EXPR:
            k = _EXPR[n]
            if k[0] == 'd':
                self.push_raw(n)
            else:
                self.push_n(k[1]); self.push_n(k[2])
                {'+': self.add, '-': self.sub, '*': self.mul}[k[0]]()
        else:
            self.push_n(1024); self.push_n(n - 1024); self.add()


def _step(e, right):
    sent = e.lbl('s'); done = e.lbl('d')
    if right:
        e.on_A(); e.load()          # current cell joins the left tape
        e.over()                    # copy right-tape top onto A
        e.push_n(1); e.add()        # ==0 iff that top is the -1 sentinel
        e.jz(sent)
        e.on_A(); e.over(); e.store()
        e.on_B(); e.drop()
        e.jmp(done)
        e.label(sent); e.on_A(); e.push_n(0); e.store()
        e.label(done)
    else:
        e.on_B(); e.load()          # current cell joins the right tape
        e.on_A(); e.dup()
        e.push_n(1); e.add()
        e.jz(sent)
        e.on_A(); e.store()
        e.jmp(done)
        e.label(sent); e.on_A(); e.push_n(0); e.store()
        e.label(done)

MAXBIT = 1024

def _ladders(e):
    for pre, right in (('r', True), ('l', False)):
        e.label(pre + '1'); _step(e, right); e.ret()
        n = 2
        while n <= MAXBIT:
            e.label(f'{pre}{n}')
            e.call(f'{pre}{n//2}'); e.call(f'{pre}{n//2}')
            e.ret()
            n *= 2

def _run(e, pre, count):
    bit = 1
    while bit <= count:
        if count & bit: e.call(f'{pre}{bit}')
        bit <<= 1


def compile_to_file(bf, out):
    e = TokenEmitter(out)
    e.jmp('m')
    _ladders(e)
    e.label('m')

    e.on_B(); e.push_n(0); e.push_n(1); e.sub()    # sentinel -1 on right tape
    e.on_A(); e.push_n(0); e.push_n(1); e.sub()    # sentinel -1 on left tape
    e.push_n(0); e.store()                          # register = 0

    stack = []
    for ch, n in ((k, sum(1 for _ in g)) for k, g in groupby(bf)):
        if ch == '+':
            e.on_A(); e.load(); e.push_n(n); e.add()
            e.push_n(256); e.mod(); e.store()
        elif ch == '-':
            e.on_A(); e.load(); e.push_n(n); e.sub()
            e.push_n(256); e.mod(); e.store()
        elif ch == '.':
            for _ in range(n): e.on_A(); e.load(); e.wchar()
        elif ch == ',':
            for _ in range(n): e.on_A(); e.rchar(); e.store()
        elif ch == '>': _run(e, 'r', n)
        elif ch == '<': _run(e, 'l', n)
        elif ch == '[':
            for _ in range(n):
                ll = e.lbl('p'); stack.append(ll)
                e.label(ll + 's'); e.on_A(); e.load(); e.jz(ll + 'e')
        elif ch == ']':
            for _ in range(n):
                ll = stack.pop()
                e.on_A(); e.load(); e.jz(ll + 'e')
                e.jmp(ll + 's'); e.label(ll + 'e')
    e.finish()
    return e.count
