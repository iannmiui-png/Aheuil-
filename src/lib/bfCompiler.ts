/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

const BASE = 0xac00;

export const compose = (cho: number, ju: number, jo = 0): string =>
  String.fromCharCode(BASE + (cho * 21 + ju) * 28 + jo);

// Scaffold cells
export const DUP_SKIP2 = compose(8, 17); // 쀼 (ㅃ, ㅠ) - double step down
export const NOOP_RIGHT = compose(11, 0); // 아 (ㅇ, ㅏ) - move right
export const NOOP_LEFT = compose(11, 4); // 어 (ㅇ, ㅓ) - move left
export const NOOP_DOWN = compose(11, 13); // 우 (ㅇ, ㅜ) - move down
export const NOOP_UP = compose(11, 8); // 오 (ㅇ, ㅗ) - move up
export const CHECK_DOWN = compose(14, 13); // 추 (ㅊ, ㅜ) - down check
export const CHECK_UP = compose(14, 8); // 초 (ㅊ, ㅗ) - up check

// Verified leaf blocks
export const BLOCK_PLUS = ["발발나다붗", "루떠떠벓벓"];
export const BLOCK_MINUS = ["밟밠밥따따받두", "루떠떠벓벓벝더"];
export const BLOCK_OUT = ["뿌", "뭏"];
export const BLOCK_IN = ["마밯"];
export const BLOCK_RIGHT = ["싹순", "수빠쑤", "부수머", "우어"];
export const BLOCK_LEFT = ["싼숙", "수빠쑤", "부수머", "우어"];
export const BLOCK_HALT = ["희"];
export const BLOCK_BEGIN = ["부"];

export function setChar(row: string, col: number, ch: string): string {
  if (row.length <= col) {
    row = row + " ".repeat(col - row.length + 1);
  }
  return row.slice(0, col) + ch + row.slice(col + 1);
}

export class BfCompiler {
  rows: string[];

  constructor() {
    this.rows = [...BLOCK_BEGIN];
  }

  emit(blockRows: string[]) {
    this.rows.push(...blockRows);
  }

  compileTokens(tokens: string[], depth: number) {
    let i = 0;
    while (i < tokens.length) {
      const c = tokens[i];
      if (c === "+") this.emit(BLOCK_PLUS);
      else if (c === "-") this.emit(BLOCK_MINUS);
      else if (c === ".") this.emit(BLOCK_OUT);
      else if (c === ",") this.emit(BLOCK_IN);
      else if (c === ">") this.emit(BLOCK_RIGHT);
      else if (c === "<") this.emit(BLOCK_LEFT);
      else if (c === "[") {
        let depthCt = 1;
        let j = i + 1;
        while (j < tokens.length && depthCt > 0) {
          if (tokens[j] === "[") depthCt++;
          else if (tokens[j] === "]") depthCt--;
          j++;
        }
        this.compileLoop(tokens.slice(i + 1, j - 1), depth);
        i = j - 1;
      }
      i++;
    }
  }

  compileLoop(bodyTokens: string[], depth: number) {
    const SKIP_COL = 8 + 2 * depth;
    const BACK_COL = SKIP_COL + 1;

    // Entry frame
    this.rows.push(DUP_SKIP2);
    const r1 = setChar(NOOP_RIGHT, SKIP_COL, NOOP_DOWN);
    this.rows.push(r1);
    this.rows.push(CHECK_DOWN);

    const rLandIn = setChar(NOOP_DOWN, BACK_COL, NOOP_LEFT);
    this.rows.push(rLandIn);

    // Body
    const bodyCompiler = new BfCompiler();
    bodyCompiler.rows = [];
    bodyCompiler.compileTokens(bodyTokens, depth + 1);
    const bodyRows = bodyCompiler.rows.length ? bodyCompiler.rows : [NOOP_DOWN];
    this.rows.push(...bodyRows);

    // Exit frame
    this.rows.push(DUP_SKIP2);
    const rTurnback = setChar(NOOP_RIGHT, BACK_COL, NOOP_UP);
    this.rows.push(rTurnback);
    this.rows.push(CHECK_UP);

    const rLandOut = setChar(NOOP_DOWN, SKIP_COL, NOOP_LEFT);
    this.rows.push(rLandOut);
  }

  finish(): string[] {
    this.rows.push(BLOCK_HALT[0]);
    const width = Math.max(...this.rows.map((r) => r.length));
    return this.rows.map((r) => r.padEnd(width, " "));
  }
}

export function compileBfToAheui(src: string): string[] {
  const tokens = src.split("").filter((c) => "+-.,<>[]".includes(c));
  const comp = new BfCompiler();
  comp.compileTokens(tokens, 0);
  return comp.finish();
}

export interface BfPreset {
  name: string;
  description: string;
  code: string;
  defaultInput?: string;
}

export const BF_PRESETS: BfPreset[] = [
  {
    name: "Hello, World!",
    description: "Classic Brainfuck Hello World program generating ASCII character outputs.",
    code: "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.",
  },
  {
    name: "Multiplication (5 * 10 = '20')",
    description: "Multiplies 5 * 10 = 50 (ASCII '2'), prints '2', then subtracts 2 to get 48 (ASCII '0') and prints '0' -> outputs '20'.",
    code: "+++++[>++++++++++<-]>.--.",
  },
  {
    name: "Addition (3 + 5 = '8')",
    description: "Sets ASCII base 48 ('0'), adds 3 and 5 to reach ASCII 56 ('8'), and prints '8'.",
    code: "++++++[>++++++++<-]>+++>+++++[<+>-]<[<+>-]<.",
  },
  {
    name: "AHEUI Text Generator",
    description: "Generates letters 'A', 'H', 'E', 'U', 'I' (ASCII 65, 72, 69, 85, 73) via cell increment loops.",
    code: "+++++[>+++++++++++++<-]>.+++++++.---.++++++++++++++++.------------.",
  },
];
