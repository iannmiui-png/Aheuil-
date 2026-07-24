import sys

BASE27_TO_ABC = {
    0: 'aaa', 1: 'aab', 2: 'aac', 3: 'aba', 4: 'abb',
    5: 'abc', 6: 'aca', 7: 'acb', 8: 'acc', 9: 'baa',
    10: 'bab', 11: 'bac', 12: 'bba', 13: 'bbb', 14: 'bbc',
    15: 'bca', 16: 'bcb', 17: 'bcc', 18: 'caa', 19: 'cab',
    20: 'cac', 21: 'cba', 22: 'cbb', 23: 'cbc', 24: 'cca',
    25: 'ccb', 26: 'ccc'
}

ABC_TO_BASE27 = {v: k for k, v in BASE27_TO_ABC.items()}

INSTRUCTIONS = [
    'push',
    'drop',
    'swap',
    'dup',
    'rot',
    'over',
    'switch',
    'pick',
    'add',
    'sub',
    'mul',
    'div',
    'mod',
    'not',
    'load',
    'store',
    'readnum',
    'readchar',
    'writenum',
    'writechar',
    'jmp',
    'jz',
    'jn',
    'call',
    'ret',
    'label',
    'end',
]

INSTRUCTION_TO_ID = {name: i for i, name in enumerate(INSTRUCTIONS)}
ID_TO_ABC = {i: BASE27_TO_ABC[i] for i in range(27)}
ABC_TO_ID = {v: k for k, v in ID_TO_ABC.items()}

INSTRUCTION_WITH_PARAM = {'push', 'jmp', 'jz', 'jn', 'call', 'label'}

class ABCLang:
    def __init__(self):
        self.stackA = []
        self.stackB = []
        self.active_stack = 'A'
        self.call_stack = []
        self.reg = 0
        self.char_buffer = []
        self.pc = 0
        self.code = []
        self.labels = {}
        self.running = True

    def _current_stack(self):
        return self.stackA if self.active_stack == 'A' else self.stackB

    def _other_stack(self):
        return self.stackB if self.active_stack == 'A' else self.stackA

    def _switch_stack(self):
        self.active_stack = 'B' if self.active_stack == 'A' else 'A'

    def _read_char(self):
        if self.char_buffer:
            return self.char_buffer.pop()
        ch = sys.stdin.read(1)
        return ch if ch else ''

    def _unget_char(self, ch):
        if ch and ch != '':
            self.char_buffer.append(ch)

    def _resolve_target(self, target):
        if isinstance(target, str):
            if target not in self.labels:
                raise RuntimeError(f'Undefined label: {target}')
            return self.labels[target]
        return target

    def _decode_number(self, parts):
        value = 0
        place = 1
        for chunk in parts:
            value += ABC_TO_BASE27[chunk] * place
            place *= 26
        return value

    def op_push(self, value):
        self._current_stack().append(value)

    def op_drop(self):
        stack = self._current_stack()
        if stack:
            stack.pop()

    def op_swap(self):
        stack = self._current_stack()
        if len(stack) >= 2:
            stack[-1], stack[-2] = stack[-2], stack[-1]

    def op_dup(self):
        stack = self._current_stack()
        if stack:
            stack.append(stack[-1])

    def op_rot(self):
        stack = self._current_stack()
        if len(stack) >= 3:
            a, b, c = stack[-3], stack[-2], stack[-1]
            stack[-3:] = [b, c, a]

    def op_over(self):
        other = self._other_stack()
        if other:
            self._current_stack().append(other[-1])

    def op_switch(self):
        self._switch_stack()

    def op_pick(self):
        stack = self._current_stack()
        n = stack.pop()
        if n < 0:
            raise ValueError(f"'pick' argument cannot be negative: {n}")
        if len(stack) >= n:
            stack.append(stack[-n])
        else:
            raise ValueError(f"'pick {n}' stack depth insufficient (depth={len(stack)})")

    def op_add(self):
        stack = self._current_stack()
        if len(stack) >= 2:
            a = stack.pop()
            b = stack.pop()
            stack.append(b + a)

    def op_sub(self):
        stack = self._current_stack()
        if len(stack) >= 2:
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)

    def op_mul(self):
        stack = self._current_stack()
        if len(stack) >= 2:
            a = stack.pop()
            b = stack.pop()
            stack.append(b * a)

    def op_div(self):
        stack = self._current_stack()
        if len(stack) >= 2:
            a = stack.pop()
            b = stack.pop()
            if a == 0:
                stack.append(0)
            else:
                stack.append(int(b / a))

    def op_mod(self):
        stack = self._current_stack()
        if len(stack) >= 2:
            a = stack.pop()
            b = stack.pop()
            if a == 0:
                stack.append(0)
            else:
                stack.append(b % a)

    def op_not(self):
        stack = self._current_stack()
        if stack:
            val = stack.pop()
            stack.append(1 if val == 0 else 0)

    def op_load(self):
        self._current_stack().append(self.reg)

    def op_store(self):
        stack = self._current_stack()
        if stack:
            self.reg = stack.pop()

    def op_readnum(self):
        ch = self._read_char()
        while ch and ch.isspace():
            ch = self._read_char()

        if not ch:
            self._current_stack().append(0)
            return

        negative = False
        if ch == '-':
            negative = True
            ch = self._read_char()
            if not ch or not ch.isdigit():
                self._current_stack().append(0)
                return

        num = 0
        while ch and ch.isdigit():
            num = num * 10 + int(ch)
            ch = self._read_char()

        if ch:
            self._unget_char(ch)

        self._current_stack().append(-num if negative else num)

    def op_readchar(self):
        ch = self._read_char()
        self._current_stack().append(ord(ch) if ch else 0)

    def op_writenum(self):
        stack = self._current_stack()
        if stack:
            print(stack.pop(), end='')
            sys.stdout.flush()

    def op_writechar(self):
        stack = self._current_stack()
        if stack:
            code = stack.pop()
            if 0 <= code:
                print(chr(code), end='')
                sys.stdout.flush()

    def op_jmp(self, target):
        self.pc = self._resolve_target(target)

    def op_jz(self, target):
        stack = self._current_stack()
        if stack and stack.pop() == 0:
            self.pc = self._resolve_target(target)

    def op_jn(self, target):
        stack = self._current_stack()
        if stack and stack.pop() < 0:
            self.pc = self._resolve_target(target)

    def op_call(self, target):
        self.call_stack.append(self.pc)
        self.pc = self._resolve_target(target)

    def op_ret(self):
        if self.call_stack:
            self.pc = self.call_stack.pop()
        else:
            raise RuntimeError("'ret' call stack is empty")

    def load_program(self, source):
        source = ''.join(ch for ch in source if ch in 'abc')

        self.code = []
        self.labels = {}

        i = 0
        while i < len(source):
            if i + 3 > len(source):
                raise SyntaxError(f'incomplete instruction: {source[i:]}')

            instr_code = source[i:i+3]
            i += 3

            if instr_code not in ABC_TO_ID:
                raise SyntaxError(f'invalid instruction code: {instr_code}')

            instr_id = ABC_TO_ID[instr_code]
            instr_name = INSTRUCTIONS[instr_id]

            if instr_name == 'push':
                number_parts = []
                while i + 3 <= len(source):
                    chunk = source[i:i+3]
                    if chunk == 'ccc':
                        i += 3
                        break
                    if chunk in ABC_TO_BASE27:
                        number_parts.append(chunk)
                        i += 3
                    else:
                        break

                if not number_parts:
                    raise SyntaxError("'push' missing number argument")

                value = self._decode_number(number_parts)
                self.code.append((instr_id, value))

            elif instr_name in ('jmp', 'jz', 'jn', 'call', 'label'):
                label_parts = []
                while i + 3 <= len(source):
                    chunk = source[i:i+3]
                    if chunk == 'ccc':
                        i += 3
                        break
                    label_parts.append(chunk)
                    i += 3
                else:
                    raise SyntaxError(f"'{instr_name}' missing label argument")

                label_name = ''.join(label_parts)

                if instr_name == 'label':
                    self.labels[label_name] = len(self.code)
                else:
                    self.code.append((instr_id, label_name))

            elif instr_name == 'end':
                pass

            else:
                self.code.append((instr_id,))

        return self

    def run(self):
        self.pc = 0
        self.running = True
        self.call_stack = []

        while self.running and 0 <= self.pc < len(self.code):
            instr = self.code[self.pc]
            self.pc += 1
            self._execute(instr)

    def _execute(self, instr):
        instr_id = instr[0]
        instr_name = INSTRUCTIONS[instr_id]

        if instr_name == 'push':
            self.op_push(instr[1])
        elif instr_name == 'drop':
            self.op_drop()
        elif instr_name == 'swap':
            self.op_swap()
        elif instr_name == 'dup':
            self.op_dup()
        elif instr_name == 'rot':
            self.op_rot()
        elif instr_name == 'over':
            self.op_over()
        elif instr_name == 'switch':
            self.op_switch()
        elif instr_name == 'pick':
            self.op_pick()
        elif instr_name == 'add':
            self.op_add()
        elif instr_name == 'sub':
            self.op_sub()
        elif instr_name == 'mul':
            self.op_mul()
        elif instr_name == 'div':
            self.op_div()
        elif instr_name == 'mod':
            self.op_mod()
        elif instr_name == 'not':
            self.op_not()
        elif instr_name == 'load':
            self.op_load()
        elif instr_name == 'store':
            self.op_store()
        elif instr_name == 'readnum':
            self.op_readnum()
        elif instr_name == 'readchar':
            self.op_readchar()
        elif instr_name == 'writenum':
            self.op_writenum()
        elif instr_name == 'writechar':
            self.op_writechar()
        elif instr_name == 'jmp':
            self.op_jmp(instr[1])
        elif instr_name == 'jz':
            self.op_jz(instr[1])
        elif instr_name == 'jn':
            self.op_jn(instr[1])
        elif instr_name == 'call':
            self.op_call(instr[1])
        elif instr_name == 'ret':
            self.op_ret()
        else:
            raise RuntimeError(f"Unknown instruction: {instr_name}")
