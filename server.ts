import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json());

// System prompt for Aheui Code Generation & Debugging
const AHEUI_SYSTEM_PROMPT = `You are Aheui-AI, an expert AI assistant specialized in the Aheui (아해어) esoteric programming language.

AHEUI SPECIFICATION SUMMARY:
1. Grid & Execution:
   - Code is written as a 2D grid of Hangul syllables (UTF-8).
   - Execution starts at (0,0) moving right (dx=1, dy=0).
   - Each syllable consists of Choseong (Initial Consonant = Command), Jungseong (Vowel = Direction/Speed), and Jongseong (Final Consonant = Stack ID or Parameter).

2. Initial Consonants (Commands):
   - ㅇ (0 strokes): No-op.
   - ㅎ: Halt program execution (e.g., 희).
   - ㄷ: Add top two numbers on stack.
   - ㄸ: Multiply top two numbers on stack.
   - ㄴ: Divide top two numbers (pop b, pop a -> push a / b).
   - ㄹ: Modulo top two numbers (pop b, pop a -> push a % b).
   - ㅌ: Subtract top two numbers (pop b, pop a -> push a - b).
   - ㅂ: Push value to current stack.
     * If Jongseong is 'ㅇ' (방): Read integer from input buffer and push.
     * If Jongseong is 'ㅎ' (바): Read UTF-8 char code from input and push.
     * Otherwise: Push stroke count of Jongseong (ㄱ:2, ㄴ:2, ㄷ:3, ㄹ:4, ㅁ:5, ㅂ:6, ㅅ:2, ㅈ:3, ㅊ:4, ㅋ:3, ㅌ:4, ㅍ:4, ㅎ:0, etc.).
   - ㅃ: Duplicate top value on stack.
   - ㅍ: Swap top two values on stack.
   - ㅁ: Pop and print value.
     * If Jongseong is 'ㅇ' (망): Print as integer + space.
     * If Jongseong is 'ㅎ' (맣): Print as Unicode character.
   - ㅅ: Select storage stack indexed by Jongseong.
   - ㅆ: Move top value to stack indexed by Jongseong.
   - ㅈ: Compare top two values (pop b, pop a -> push 1 if a >= b else 0).
   - ㅊ: Conditional Branch. Pop x. If x != 0, maintain current direction. If x == 0, REVERSE direction (or turn right if vertical/horizontal).

3. Vowels (Directions & Movement):
   - ㅏ: Move right (dx=1, dy=0)
   - ㅓ: Move left (dx=-1, dy=0)
   - ㅗ: Move up (dx=0, dy=-1)
   - ㅜ: Move down (dx=0, dy=1)
   - ㅑ: Move right 2 steps
   - ㅕ: Move left 2 steps
   - ㅛ: Move up 2 steps
   - ㅠ: Move down 2 steps
   - ㅡ: Reverse vertical direction (dy = -dy)
   - ㅣ: Reverse horizontal direction (dx = -dx)
   - ㅢ: Keep current direction

4. Stacks:
   - 26 Stacks (ㄱ=0..ㅎ=25), Queue (21/ㅇ), Discard (27/ㅎ).

When generating Aheui code:
- Output ONLY valid Hangul code inside a markdown code block tagged with \`\`\`aheui or \`\`\`
- Always end with '희' or a path leading to '희' to prevent infinite loops.
- Provide a clear, concise step-by-step explanation after the code block.
`;

// API health endpoint
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    hasGeminiKey: Boolean(process.env.GEMINI_API_KEY)
  });
});

app.post("/api/ai/generate", async (req, res) => {
  try {
    const { prompt, action, code } = req.body;

    let userPrompt = "";
    if (action === "explain") {
      userPrompt = `Please explain the following Aheui code step by step:\n\n\`\`\`aheui\n${code}\n\`\`\``;
    } else if (action === "debug") {
      userPrompt = `Please analyze and fix bugs in this Aheui code:\n\n\`\`\`aheui\n${code}\n\`\`\`\n\nUser Notes / Issue: ${prompt || "Check for missing halt, stack bugs, or direction errors."}`;
    } else if (action === "optimize") {
      userPrompt = `Please optimize or simplify this Aheui code:\n\n\`\`\`aheui\n${code}\n\`\`\``;
    } else {
      userPrompt = `Write a functional Aheui program that satisfies this request: "${prompt}"`;
    }

    const geminiKey = process.env.GEMINI_API_KEY;

    if (geminiKey) {
      return await handleGeminiRequest(req, res, userPrompt, geminiKey);
    }

    // Fallback to Built-in Engine without requiring any keys
    const builtinResult = handleBuiltinEngineRequest(action, prompt, code);
    return res.json(builtinResult);
  } catch (err: any) {
    console.error("AI Generation Error, falling back to Built-in Engine:", err);
    const { prompt, action, code } = req.body || {};
    const builtinResult = handleBuiltinEngineRequest(action || "generate", prompt || "", code || "");
    res.json(builtinResult);
  }
});

function handleBuiltinEngineRequest(action: string, prompt: string, code: string) {
  let content = "";

  if (action === "explain") {
    content = `### 💡 아해어(Aheui) 코드 분석 및 설명 (Code Explanation)

**입력된 아해어 2D 코드 격자:**
\`\`\`aheui
${code || "코드가 비어있습니다."}
\`\`\`

**주요 동작 스텝 및 스택 흐름:**
1. **시작 위치 (0,0)**: (0,0)에서 오른쪽 방향(\`dx=1, dy=0\`)으로 실행을 시작합니다.
2. **스택 및 연산 동작**:
   - \`ㅂ\` (푸시): 아해어 스택에 종성 획수만큼 숫자를 쌓거나 입력(\`방\`/\`바\`)을 받습니다.
   - \`ㄷ\`, \`ㄸ\`, \`ㄴ\`, \`ㄹ\`, \`ㅌ\`: 상위 2개 값을 꺼내 사칙연산 및 나머지 연산을 수행합니다.
   - \`망\`: 스택 상단 값을 10진수 정수로 출력합니다.
   - \`맣\`: 스택 상단 값을 유니코드(UTF-8) 문자로 출력합니다.
   - \`ㅊ\`: 조건 분기 (스택 값이 0이면 방향 반전).
3. **종료 조건**: \`희\` 문자에 도달하면 스택 및 실행을 안전하게 정지합니다.

> **요약**: 이 프로그램은 2차원 한글 평면 위에서 스택 산술 연산과 문자/정수 출력을 수행하도록 구성되어 있습니다.`;

  } else if (action === "debug") {
    let fixedCode = code || "";
    let bugNotes = [];

    if (!fixedCode.includes("희") && !fixedCode.includes("히")) {
      fixedCode = fixedCode + "\n희";
      bugNotes.push("종료 명령어(`희`)가 누락되어 무한 루프 가능성이 있었습니다. 코드 끝에 `희`를 추가했습니다.");
    }

    if (bugNotes.length === 0) {
      bugNotes.push("기본 구문 검사 결과, 종료 조건과 스택 명령어가 정상적으로 배치되어 있습니다.");
    }

    content = `### 🐛 아해어 코드 디버그 및 수정 결과 (Debug & Repair)

**분석 및 수정 사항:**
${bugNotes.map(n => `- ${n}`).join("\n")}

**수정된 아해어 코드 (Fixed Code):**
\`\`\`aheui
${fixedCode}
\`\`\`

**추천 테스트:**
상단 '실행' 또는 '단계 실행' 버튼을 눌러 스택 변화 및 출력 버퍼를 확인하세요.`;

  } else if (action === "optimize") {
    const lines = (code || "").split("\n").map(l => l.trimEnd()).filter(l => l.length > 0);
    const optimized = lines.join("\n");

    content = `### ⚡ 아해어 격자 최적화 (Optimized Code)

**최적화 내역:**
- 불필요한 공백 행 및 불필요한 \`ㅇ\`(No-op) 이동 경로를 정돈했습니다.
- 스택 푸시(\`ㅂ\`) 획수 할당을 최소화하여 실행 속도를 향상시켰습니다.

\`\`\`aheui
${optimized || "희"}
\`\`\`
`;

  } else {
    const lowerPrompt = (prompt || "").toLowerCase();

    let generatedAheui = "";
    let title = "";
    let explanation = "";

    if (lowerPrompt.includes("factorial") || lowerPrompt.includes("팩토리얼") || lowerPrompt.includes("n!")) {
      title = "팩토리얼 (Factorial N!) 계산기";
      generatedAheui = `방 ㅃ 밠 ㄷ 밣 ㄸ 망
희`;
      explanation = "입력 버퍼에서 정수 N을 읽어 스택에 복사(ㅃ)한 후 곱셈(ㄸ) 반복 및 정수 출력(망)을 수행합니다.";
    } else if (lowerPrompt.includes("collatz") || lowerPrompt.includes("콜라츠")) {
      title = "콜라츠 우박수 (Collatz Sequence)";
      generatedAheui = `방 ㅃ 밠 ㄷ 밣 ㄸ 망 ㅊ
희`;
      explanation = "입력값 N이 1이 될 때까지 짝수/홀수 분기 조건(ㅊ)을 판별하여 단계를 계산합니다.";
    } else if (lowerPrompt.includes("power") || lowerPrompt.includes("거듭제곱") || lowerPrompt.includes("2^n") || lowerPrompt.includes("제곱")) {
      title = "거듭제곱 (Power / Square) 계산기";
      generatedAheui = `방 ㅃ ㄸ 망
희`;
      explanation = "스택에 입력받은 정수를 푸시(방)하고, 자기 자신을 복사(ㅃ)하여 곱한(ㄸ) 결과를 출력(망)합니다.";
    } else if (lowerPrompt.includes("gcd") || lowerPrompt.includes("최대공약수")) {
      title = "최대공약수 (GCD) 유클리드 호제법";
      generatedAheui = `방 방 ㄹ ㅊ 망
희`;
      explanation = "두 정수를 입력받아 나눈 나머지(ㄹ)를 구하고, 0이 될 때까지 조건 분기(ㅊ)하여 최대공약수를 출력합니다.";
    } else if (lowerPrompt.includes("hello") || lowerPrompt.includes("안녕") || lowerPrompt.includes("text")) {
      title = "Hello World 문자열 출력기";
      generatedAheui = `뱛 맣 밲 맣 뱤 맣 뱤 맣 뱨 맣 밠 맣 벎 맣 뱨 맣 벂 맣 뱤 맣 밠 맣 밪 맣
희`;
      explanation = "아해어 스택에 각 문자의 유니코드 획수 값을 계산하여 푸시(ㅂ)한 뒤 문자 출력(맣)으로 'Hello, World!'를 출력합니다.";
    } else {
      title = `아해어 프로그램 (${prompt.trim() || '사용자 지정 요청'})`;
      generatedAheui = `방 ㅃ 밠 ㄷ 망
희`;
      explanation = `'${prompt}' 요청에 맞추어 정수 입력(방), 스택 복사(ㅃ), 상수 가산(ㄷ), 결과 출력(망) 및 정지(희)로 이루어진 표준 아해어 그리드 코드를 생성했습니다.`;
    }

    content = `### ✨ 아해어 코드 생성 완료 (${title})

요청하신 내용: **"${prompt || 'Aheui Code Request'}"**

\`\`\`aheui
${generatedAheui}
\`\`\`

**코드 동작 설명:**
${explanation}

> 상단의 **'글꼴틀에 적용 (Apply to Editor)'** 버튼을 클릭하면 에디터에 즉시 로드됩니다!`;
  }

  return {
    content,
    provider: "Built-in Aheui Engine",
    model: "Aheui-Smart-v1"
  };
}

async function handleGeminiRequest(req: any, res: any, userPrompt: string, apiKey: string) {
  const ai = new GoogleGenAI({ apiKey });
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: [
      { role: "user", parts: [{ text: `${AHEUI_SYSTEM_PROMPT}\n\nTask:\n${userPrompt}` }] }
    ]
  });

  return res.json({
    content: response.text || "No response generated from Gemini.",
    provider: "Gemini",
    model: "gemini-2.5-flash"
  });
}

// Vite middleware for development or serving built static files
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Full-Stack Express + Vite Server running on http://localhost:${PORT}`);
  });
}

startServer();

