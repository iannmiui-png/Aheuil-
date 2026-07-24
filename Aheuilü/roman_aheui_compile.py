"""
Compiles a sequence of romanized-Aheui-syllable tokens directly into
ABCLang bytecode (the base27 a/b/c encoding your tlsb.py / ABCLang
interpreter expects) — no Hangul, no 2D grid, no Aheui interpreter
involved at all. This is a "third skin": Aheui's op semantics, spoken
in English, compiled straight to the dual-stack VM.

Design choices (deliberately simplified vs. full 28-storage Aheui):
  - Only two logical storages are modeled: storage 0 (default) and
    "everything else" (any nonzero storage number), mapped onto
    ABCLang's two real stacks A and B respectively. This covers every
    example in the "known Aheui programs" set except the FIFO Queue
    Demo (storage 21), which would need real queue emulation on top
    of a stack — not implemented here.
  - 초 (cho, ㅊ+ㅗ) and 추 (chu, ㅊ+ㅜ) are loop bracket syllables,
    matched like BF's [ ] : 초 is the entry guard (skip forward if the
    top of stack is zero), 추 is the repeat check (jump back if the
    top is nonzero). This mirrors real usage in the Countdown/Collatz
    examples, just unrolled into linear jz/jmp instead of 2D routing.
  - ㅎ (hui, halt) stops compilation outright: ABCLang has no runtime
    halt opcode, the VM simply stops when it runs off the end of the
    instruction list, so "halt" just means "compile nothing further".
"""

from roman_aheui import parse_syllable

STROKES = [0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0]

BASE27_TO_ABC = {
    0: 'aaa', 1: 'aab', 2: 'aac', 3: 'aba', 4: 'abb',
    5: 'abc', 6: 'aca', 7: 'acb', 8: 'acc', 9: 'baa',
    10: 'bab', 11: 'bac', 12: 'bba', 13: 'bbb', 14: 'bbc',
    15: 'bca', 16: 'bcb', 17: 'bcc', 18: 'caa', 19: 'cab',
    20: 'cac', 21: 'cba', 22: 'cbb', 23: 'cbc', 24: 'cca',
    25: 'ccb', 26: 'ccc'
}
INSTRUCTIONS = [
    'push','drop','swap','dup','rot','over','switch','pick',
    'add','sub','mul','div','mod','not','load','store',
    'readnum','readchar','writenum','writechar',
    'jmp','jz','jn','call','ret','label','end',
]
INSTRUCTION_TO_ID = {name: i for i, name in enumerate(INSTRUCTIONS)}


class ParseError(Exception):
    pass


def _target_stack(storage_idx):
    return 'A' if storage_idx == 0 else 'B'


class Compiler:
    def __init__(self):
        self.code = []          # list of (mnemonic, *args)
        self.current_storage = 0
        self.abc_active = 'A'
        self.loop_stack = []    # open 초 labels awaiting a matching 추
        self._loop_ctr = 0
        self._cmp_ctr = 0

    def _ensure_active(self, stack):
        if self.abc_active != stack:
            self.code.append(('switch',))
            self.abc_active = stack

    def compile_tokens(self, tokens):
        for tok in tokens:
            if tok.startswith(':'):
                self.code.append(('label', tok[1:]))
                continue
            cho, jung, jong = parse_syllable(tok)
            self._compile_syllable(tok, cho, jung, jong)
        if self.loop_stack:
            raise ParseError(f"unmatched 초 (open loop entries: {self.loop_stack})")

    def _compile_syllable(self, tok, cho, jung, jong):
        stack = _target_stack(self.current_storage)

        if cho in (0, 1, 11, 13):
            return  # noop consonants (ㄱ/ㄲ/ㅇ/ㅉ)

        if cho == 2:      # div
            self._ensure_active(stack); self.code.append(('div',))
        elif cho == 3:    # add
            self._ensure_active(stack); self.code.append(('add',))
        elif cho == 4:    # mul
            self._ensure_active(stack); self.code.append(('mul',))
        elif cho == 5:    # mod
            self._ensure_active(stack); self.code.append(('mod',))
        elif cho == 6:    # output/pop
            self._ensure_active(stack)
            if jong == 21:
                self.code.append(('writenum',))
            elif jong == 27:
                self.code.append(('writechar',))
            else:
                self.code.append(('drop',))
        elif cho == 7:    # push
            self._ensure_active(stack)
            if jong == 21:
                self.code.append(('readnum',))
            elif jong == 27:
                self.code.append(('readchar',))
            else:
                self.code.append(('push', STROKES[jong]))
        elif cho == 8:    # dup
            self._ensure_active(stack); self.code.append(('dup',))
        elif cho == 9:    # select storage
            self.current_storage = jong
        elif cho == 10:   # move value to storage `jong`
            src, dst = _target_stack(self.current_storage), _target_stack(jong)
            if src != dst:
                self._ensure_active(src); self.code.append(('store',))
                self._ensure_active(dst); self.code.append(('load',))
            self.current_storage = jong
        elif cho == 12:   # compare: push (b>=a)?1:0
            self._ensure_active(stack)
            self.code.append(('sub',))  # a=pop, b=pop, push b-a  (matches Aheui's ㅈ pop order)
            self._cmp_ctr += 1
            neg, end = f"__cmpneg{self._cmp_ctr}", f"__cmpend{self._cmp_ctr}"
            self.code += [('jn', neg), ('push', 1), ('jmp', end),
                          ('label', neg), ('push', 0), ('label', end)]
        elif cho == 14:   # ㅊ : loop control (초 = entry guard, 추 = repeat check)
            self._ensure_active(stack)
            if jung == 8:      # 초 (cho): skip forward past matching 추 if zero
                self._loop_ctr += 1
                lbl = f"__loop{self._loop_ctr}"
                self.loop_stack.append(lbl)
                self.code += [('jz', lbl + "_end"), ('label', lbl + "_start")]
            elif jung == 13:   # 추 (chu): jump back if nonzero
                if not self.loop_stack:
                    raise ParseError(f"'{tok}' (추) has no matching 초")
                lbl = self.loop_stack.pop()
                skip = lbl + "_noloop"
                self.code += [('jz', skip), ('jmp', lbl + "_start"),
                              ('label', skip), ('label', lbl + "_end")]
            else:
                raise ParseError(f"'{tok}': only 초 (cho) / 추 (chu) supported for loop control, "
                                  f"got jungseong index {jung}")
        elif cho == 15:   # swap
            self._ensure_active(stack); self.code.append(('swap',))
        elif cho == 16:   # subtract
            self._ensure_active(stack); self.code.append(('sub',))
        elif cho == 17:   # copy value to storage `jong` (keep original too)
            src, dst = _target_stack(self.current_storage), _target_stack(jong)
            self._ensure_active(src); self.code.append(('dup',))
            if dst != src:
                self.code.append(('store',))
                self._ensure_active(dst); self.code.append(('load',))
        elif cho == 18:   # halt: ABCLang has no halt opcode, just stop compiling
            raise StopIteration
        else:
            raise ParseError(f"unhandled choseong index {cho} in token {tok!r}")


def _encode_number(value):
    if value == 0:
        return [BASE27_TO_ABC[0]]
    digits = []
    v = value
    while v > 0:
        digits.append(v % 26)
        v //= 26
    return [BASE27_TO_ABC[d] for d in digits]


def _assemble(code):
    label_ids = {}

    def label_chunks(name):
        if name not in label_ids:
            label_ids[name] = len(label_ids)
        return _encode_number(label_ids[name])

    out = []
    for instr in code:
        name = instr[0]
        out.append(BASE27_TO_ABC[INSTRUCTION_TO_ID[name]])
        if name == 'push':
            out.append(''.join(_encode_number(instr[1])))
            out.append('ccc')
        elif name in ('jmp', 'jz', 'jn', 'call', 'label'):
            out.append(''.join(label_chunks(instr[1])))
            out.append('ccc')
    return ''.join(out)


def compile_roman_aheui(source):
    tokens = source.split()
    comp = Compiler()
    try:
        comp.compile_tokens(tokens)
    except StopIteration:
        pass  # halt encountered
    return _assemble(comp.code)
