/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * 
 * Client-side Aheui Interpreter and Decomposer in TypeScript.
 */

export const BASE_CODEPOINT = 0xAC00;
export const N_CH = 19; // choseong (initials)
export const N_JU = 21; // jungseong (medials)
export const N_JO = 28; // jongseong (finals)

export const CHOSEONG = [
  "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
  "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
];

export const JUNGSEONG = [
  "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ",
  "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"
];

export const JONGSEONG = [
  "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ",
  "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ",
  "ㅋ", "ㅌ", "ㅍ", "ㅎ"
];

// Stroke count values for final consonants
export const STROKES = [
  0, 2, 4, 4, 2, 5, 5, 3, 5, 7, 9, 9, 7, 9, 9, 8, 4, 4, 6, 2, 4, 0, 3, 4, 3, 4, 4, 0
];

export interface DecomposedJamo {
  ch: number; // initial index
  ju: number; // medial index
  jo: number; // final index
}

/**
 * Decomposes a Hangul Syllable character into Choseong, Jungseong, and Jongseong indices.
 */
export function decomposeChar(char: string): DecomposedJamo | null {
  if (!char || char.length === 0) return null;
  const cp = char.charCodeAt(0);
  const offset = cp - BASE_CODEPOINT;
  if (offset < 0 || offset >= N_CH * N_JU * N_JO) {
    return null;
  }
  const ch = Math.floor(offset / (N_JU * N_JO));
  const rem = offset % (N_JU * N_JO);
  const ju = Math.floor(rem / N_JO);
  const jo = rem % N_JO;
  return { ch, ju, jo };
}

export interface InterpreterState {
  x: number;
  y: number;
  dx: number;
  dy: number;
  halted: boolean;
  currentStorage: number;
  storage: bigint[][];
  output: string;
}

export interface InterpreterSnapshot {
  x: number;
  y: number;
  dx: number;
  dy: number;
  halted: boolean;
  currentStorage: number;
  storage: bigint[][];
  output: string;
  infinityCount: number;
  inputPtr: number;
}

export class AheuiInterpreter {
  public code: string[][] = [];
  public x: number = 0;
  public y: number = 0;
  public dx: number = 1;
  public dy: number = 0;
  public halted: boolean = false;
  public storage: bigint[][] = [];
  public currentStorage: number = 0;
  public output: string = "";
  public infinityCount: number = 0;
  public history: InterpreterSnapshot[] = [];
  public maxHistory: number = 200;
  
  private inputBuffer: string = "";
  private inputPtr: number = 0;

  constructor() {
    this.reset();
  }

  public reset() {
    this.x = 0;
    this.y = 0;
    this.dx = 1;
    this.dy = 0;
    this.halted = false;
    this.currentStorage = 0;
    this.storage = Array.from({ length: 28 }, () => []);
    this.output = "";
    this.infinityCount = 0;
    this.inputPtr = 0;
    this.history = [];
  }

  public load(sourceCode: string) {
    this.reset();
    const lines = sourceCode.split(/\r?\n/).map(line => Array.from(line));
    const maxLen = Math.max(0, ...lines.map(l => l.length));
    this.code = lines.map(line => {
      const padded = [...line];
      while (padded.length < maxLen) {
        padded.push(' ');
      }
      return padded;
    });
  }

  public setInput(input: string) {
    this.inputBuffer = input;
    this.inputPtr = 0;
  }

  private pushVal(storageIdx: number, val: bigint) {
    if (storageIdx === 27) return; // ㅎ is throwaway storage
    this.storage[storageIdx].push(val);
  }

  private popVal(storageIdx: number): bigint | null {
    if (storageIdx === 27) return null;
    const store = this.storage[storageIdx];
    if (store.length === 0) return null;
    
    if (storageIdx === 21) {
      // ㅇ is queue (FIFO)
      const val = store[0];
      this.storage[storageIdx] = store.slice(1);
      return val;
    } else {
      // stacks (LIFO)
      return store.pop() ?? null;
    }
  }

  private readInputNum(): bigint {
    // Read next whitespace-delimited integer or parse characters
    const text = this.inputBuffer.slice(this.inputPtr).trim();
    if (!text) return 0n;
    
    const match = text.match(/^(-?\d+)/);
    if (match) {
      const num = BigInt(match[1]);
      this.inputPtr += this.inputBuffer.slice(this.inputPtr).indexOf(match[1]) + match[1].length;
      return num;
    }
    return 0n;
  }

  private readInputChar(): bigint {
    if (this.inputPtr < this.inputBuffer.length) {
      const char = this.inputBuffer[this.inputPtr];
      this.inputPtr++;
      return BigInt(char.charCodeAt(0));
    }
    return 0n;
  }

  private move() {
    this.x += this.dx;
    this.y += this.dy;

    if (this.code.length === 0) {
      this.x = 0;
      this.y = 0;
      return;
    }

    if (this.y < 0) {
      this.y = this.code.length - 1;
    } else if (this.y >= this.code.length) {
      this.y = 0;
    }

    const row = this.code[this.y];
    if (!row || row.length === 0) {
      this.x = 0;
    } else {
      if (this.x < 0) {
        this.x = row.length - 1;
      } else if (this.x >= row.length) {
        this.x = 0;
      }
    }
  }

  public getSnapshot(): InterpreterSnapshot {
    return {
      x: this.x,
      y: this.y,
      dx: this.dx,
      dy: this.dy,
      halted: this.halted,
      currentStorage: this.currentStorage,
      storage: this.storage.map(arr => [...arr]),
      output: this.output,
      infinityCount: this.infinityCount,
      inputPtr: this.inputPtr,
    };
  }

  public restoreSnapshot(snapshot: InterpreterSnapshot) {
    this.x = snapshot.x;
    this.y = snapshot.y;
    this.dx = snapshot.dx;
    this.dy = snapshot.dy;
    this.halted = snapshot.halted;
    this.currentStorage = snapshot.currentStorage;
    this.storage = snapshot.storage.map(arr => [...arr]);
    this.output = snapshot.output;
    this.infinityCount = snapshot.infinityCount;
    this.inputPtr = snapshot.inputPtr;
  }

  public canStepBack(): boolean {
    return this.history.length > 0;
  }

  public stepBack(): boolean {
    if (this.history.length === 0) return false;
    const prev = this.history.pop()!;
    this.restoreSnapshot(prev);
    return true;
  }

  public step(recordHistory: boolean = true) {
    if (this.halted) return;

    if (this.code.length === 0) {
      this.halted = true;
      return;
    }

    if (recordHistory) {
      if (this.history.length >= this.maxHistory) {
        this.history.shift();
      }
      this.history.push(this.getSnapshot());
    }

    const row = this.code[this.y];
    if (!row || row.length === 0 || this.x >= row.length) {
      this.move();
      return;
    }

    const char = row[this.x];
    const decomp = decomposeChar(char);
    if (!decomp) {
      this.move();
      return;
    }

    const { ch: op, ju, jo: idx } = decomp;

    // 1. Update Direction Pointer based on Vowel (jungseong)
    switch (ju) {
      case 0:  this.dx = 1;  this.dy = 0;  break; // ㅏ (right 1)
      case 2:  this.dx = 2;  this.dy = 0;  break; // ㅑ (right 2)
      case 4:  this.dx = -1; this.dy = 0;  break; // ㅓ (left 1)
      case 6:  this.dx = -2; this.dy = 0;  break; // ㅕ (left 2)
      case 8:  this.dx = 0;  this.dy = -1; break; // ㅗ (up 1)
      case 12: this.dx = 0;  this.dy = -2; break; // ㅛ (up 2)
      case 13: this.dx = 0;  this.dy = 1;  break; // ㅜ (down 1)
      case 17: this.dx = 0;  this.dy = 2;  break; // ㅠ (down 2)
      case 18: this.dy = -this.dy;         break; // ㅡ (reflect vertical)
      case 19: this.dx = -this.dx; this.dy = -this.dy; break; // ㅢ (reflect both)
      case 20: this.dx = -this.dx;         break; // ㅣ (reflect horizontal)
      default: break; // Other vowels preserve the movement direction
    }

    // 2. Perform Operation based on Consonant (choseong)
    let success = true;

    switch (op) {
      case 0: // ㄱ: no-op
      case 1: // ㄲ: no-op
        break;

      case 2: { // ㄴ: divide (pop a, pop b, push b / a)
        const a = this.popVal(this.currentStorage);
        const b = this.popVal(this.currentStorage);
        if (a !== null && b !== null && a !== 0n) {
          this.pushVal(this.currentStorage, b / a);
        } else {
          if (a !== null) this.pushVal(this.currentStorage, a);
          if (b !== null) this.pushVal(this.currentStorage, b);
          success = false;
        }
        break;
      }

      case 3: { // ㄷ: add (pop a, pop b, push b + a)
        const a = this.popVal(this.currentStorage);
        const b = this.popVal(this.currentStorage);
        if (a !== null && b !== null) {
          this.pushVal(this.currentStorage, b + a);
        } else {
          if (a !== null) this.pushVal(this.currentStorage, a);
          if (b !== null) this.pushVal(this.currentStorage, b);
          success = false;
        }
        break;
      }

      case 4: { // ㄸ: multiply (pop a, pop b, push b * a)
        const a = this.popVal(this.currentStorage);
        const b = this.popVal(this.currentStorage);
        if (a !== null && b !== null) {
          this.pushVal(this.currentStorage, b * a);
        } else {
          if (a !== null) this.pushVal(this.currentStorage, a);
          if (b !== null) this.pushVal(this.currentStorage, b);
          success = false;
        }
        break;
      }

      case 5: { // ㄹ: modulo (pop a, pop b, push b % a)
        const a = this.popVal(this.currentStorage);
        const b = this.popVal(this.currentStorage);
        if (a !== null && b !== null && a !== 0n) {
          // BigInt modulo can be negative, need standard mathematical modulo
          const mod = ((b % a) + a) % a;
          this.pushVal(this.currentStorage, mod);
        } else {
          if (a !== null) this.pushVal(this.currentStorage, a);
          if (b !== null) this.pushVal(this.currentStorage, b);
          success = false;
        }
        break;
      }

      case 6: { // ㅁ: pop and print
        const a = this.popVal(this.currentStorage);
        if (a !== null) {
          if (idx === 21) {
            // ㅇ: print as integer (arbitrary precision BigInt)
            const strVal = a.toString();

            if (strVal.includes("Infinity")) {
              this.infinityCount++;
              if (this.infinityCount >= 8) {
                this.halted = true;
              }
            } else {
              this.infinityCount = 0;
            }

            this.output += strVal;
            if (this.output.length > 200000) {
              this.output = this.output.substring(this.output.length - 100000);
            }
          } else if (idx === 27) {
            // ㅎ: print as character
            try {
              this.output += String.fromCodePoint(Number(a));
            } catch {
              this.output += "";
            }
            if (this.output.length > 200000) {
              this.output = this.output.substring(this.output.length - 100000);
            }
          }
          // Other finals: discard popped value
        } else {
          success = false;
        }
        break;
      }

      case 7: { // ㅂ: push
        if (idx === 21) {
          // ㅇ: input integer
          const num = this.readInputNum();
          this.pushVal(this.currentStorage, num);
        } else if (idx === 27) {
          // ㅎ: input character
          const cp = this.readInputChar();
          this.pushVal(this.currentStorage, cp);
        } else {
          // push stroke count of final consonant
          this.pushVal(this.currentStorage, BigInt(STROKES[idx]));
        }
        break;
      }

      case 8: { // ㅃ: duplicate
        const a = this.popVal(this.currentStorage);
        if (a !== null) {
          this.pushVal(this.currentStorage, a);
          this.pushVal(this.currentStorage, a);
        } else {
          success = false;
        }
        break;
      }

      case 9: // ㅅ: select storage
        this.currentStorage = idx;
        break;

      case 10: { // ㅆ: move value to storage index `idx`
        const a = this.popVal(this.currentStorage);
        if (a !== null) {
          this.pushVal(idx, a);
        } else {
          success = false;
        }
        break;
      }

      case 11: // ㅇ: no-op
      case 13: // ㅉ: no-op
        break;

      case 12: { // ㅈ: compare (pop a, pop b, push b >= a ? 1 : 0)
        const a = this.popVal(this.currentStorage);
        const b = this.popVal(this.currentStorage);
        if (a !== null && b !== null) {
          this.pushVal(this.currentStorage, b >= a ? 1n : 0n);
        } else {
          if (a !== null) this.pushVal(this.currentStorage, a);
          if (b !== null) this.pushVal(this.currentStorage, b);
          success = false;
        }
        break;
      }

      case 14: { // ㅊ: conditional (pop a, reverse direction if a == 0)
        const a = this.popVal(this.currentStorage);
        if (a !== null) {
          if (a === 0n) {
            this.dx = -this.dx;
            this.dy = -this.dy;
          }
        } else {
          success = false;
        }
        break;
      }

      case 15: { // ㅋ: swap top two values
        const a = this.popVal(this.currentStorage);
        const b = this.popVal(this.currentStorage);
        if (a !== null && b !== null) {
          this.pushVal(this.currentStorage, a);
          this.pushVal(this.currentStorage, b);
        } else {
          if (a !== null) this.pushVal(this.currentStorage, a);
          if (b !== null) this.pushVal(this.currentStorage, b);
          success = false;
        }
        break;
      }

      case 16: { // ㅌ: subtract (pop a, pop b, push b - a)
        const a = this.popVal(this.currentStorage);
        const b = this.popVal(this.currentStorage);
        if (a !== null && b !== null) {
          this.pushVal(this.currentStorage, b - a);
        } else {
          if (a !== null) this.pushVal(this.currentStorage, a);
          if (b !== null) this.pushVal(this.currentStorage, b);
          success = false;
        }
        break;
      }

      case 17: { // ㅍ: copy value to storage index `idx`
        const a = this.popVal(this.currentStorage);
        if (a !== null) {
          this.pushVal(this.currentStorage, a); // keep in current
          this.pushVal(idx, a); // copy to target
        } else {
          success = false;
        }
        break;
      }

      case 18: // ㅎ: halt
        this.halted = true;
        break;

      default:
        break;
    }

    // Standard Aheui behaviour: reverse direction if operation fails (e.g. stack underflow)
    if (!success) {
      this.dx = -this.dx;
      this.dy = -this.dy;
    }

    this.move();
  }

  public getState(): InterpreterState {
    return {
      x: this.x,
      y: this.y,
      dx: this.dx,
      dy: this.dy,
      halted: this.halted,
      currentStorage: this.currentStorage,
      storage: this.storage.map(s => [...s]),
      output: this.output,
    };
  }
}
