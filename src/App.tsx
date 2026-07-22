/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Play,
  Square,
  SkipForward,
  RotateCcw,
  Layers,
  Terminal,
  ArrowRight,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  Info,
  Code,
  Sparkles,
  HelpCircle,
  Hash,
  Activity,
  Maximize2,
  Compass,
  Zap,
  AlertTriangle,
  CheckCircle2
} from "lucide-react";
import {
  AheuiInterpreter,
  decomposeChar,
  CHOSEONG,
  JUNGSEONG,
  JONGSEONG,
  STROKES
} from "./lib/aheui";

// Preset Programs
const PRESETS = [
  {
    name: "Adder (3 + 5 = 8)",
    description: "Pushes 3 (받) and 5 (발), adds them (다), prints the result (망), and halts (희).",
    code: "받발다망희"
  },
  {
    name: "Multiplier (4 * 5 = 20)",
    description: "Pushes 4 (밤) and 5 (발), multiplies them (따), prints (망), and halts (희).",
    code: "밤발따망희"
  },
  {
    name: "Hello, World!",
    description: "Generates and prints the text 'Hello, World!' by constructing character ASCII code points using Aheui stack arithmetic and character output (맣).",
    code: "밞밣따맣밞밞반다따반다맣밞밞받다따맣밞밞받다따맣밞밞받다따받다맣밤밞반다따맣밤밣따맣밞밞따밦다맣밞밞받다따받다맣밞밞받다따밦다맣밞밞받다따맣밞밞반다따박반나다맣밤밣따박반나다맣희"
  },
  {
    name: "Square Calculator (N²)",
    description: "Takes an integer input N (방), duplicates it (빠), multiplies N * N (따), prints the result (망), and halts (희).",
    code: "방빠따망희",
    defaultInput: "12"
  },
  {
    name: "Cumulative Sum (1 to N)",
    description: "Calculates the sum of integers from 1 to N using stack arithmetic N * (N + 1) / 2.",
    code: "방빠박반나다따반나망희",
    defaultInput: "100"
  },
  {
    name: "Even / Odd Checker",
    description: "Takes an integer input N and calculates N % 2 (라). Outputs 0 if N is even, or 1 if N is odd.",
    code: "방반라망희",
    defaultInput: "7"
  },
  {
    name: "AHEUI! Text Generator",
    description: "Outputs the string 'AHEUI!' by calculating ASCII character values (65, 72, 69, 85, 73, 33) and popping with character output (맣).",
    code: "밞밠따반다맣밞밣따맣밞밠따밦다맣밞밞따밤다맣밞밣따박반나다맣밤밣따박반나다맣희"
  },
  {
    name: "Stack Demo (LIFO)",
    description: "Demonstrates LIFO (Last-In, First-Out). Pushes 3 then 5, pops and prints both. Output: 53.",
    code: "받발망망희"
  },
  {
    name: "Queue Demo (FIFO)",
    description: "Demonstrates FIFO (First-In, First-Out). Selects queue (상), pushes 3 then 5, pops both. Output: 35.",
    code: "상받발망망희"
  },
  {
    name: "Visual 2D Bounce Loop",
    description: "Loops infinitely in 2D using directional bounce vowels (ㅡ, ㅣ) until stack becomes empty.",
    code: "받발다망아\n배자차희어"
  },
  {
    name: "Countdown (5 to 1)",
    description: "A beautifully structured 3-line 2D loop. Counts down from 5 to 1 using loop-back routes and conditional branching (초) to gracefully halt (희) when the counter reaches 0.",
    code: "우우어어어어어어어어어어어어어어어어\n발빠망삭밤밤따빠다맣사빠반반나타빠초\n                 희"
  },
  {
    name: "Collatz Conjecture (3N + 1)",
    description: "A complete 5-row 2D grid program implementing the Collatz sequence. Given starting integer N (방), prints each step (망) and computes N/2 if even or 3N+1 if odd using 2D direction routing (추, 초) until N reaches 1 and halts (희).",
    code: "방빠망밤밣따맣빠박반나타추   아받따박반나다우\n            아빠반라초\n                아반나우\n 오어어어어어어어어어어 어어어어어어어어어어어\n            희 오어어어어어어어어어어어어어",
    defaultInput: "7"
  },
  {
    name: "Infinite Fibonacci Sequence",
    description: "An elegant 3-line 2D loop that computes and prints the Fibonacci sequence endlessly (0 1 1 2 3 5 8 ...). Demonstrates memory copy (팍), multi-stack exchange, and horizontal wrap-around.",
    code: "바반반나우\n우어어어어\n카빠망삭밤밤따빠다맣사카팍다삭쓰사카"
  },
  {
    name: "Prime Checker (2D Grid Loop)",
    description: "Takes an integer input N and outputs 1 if N is prime, or 0 if composite. Features a beautifully aligned 2D search loop with custom horizontal routing (어) and vertical branching (초).",
    code: "방반아아아아아우      사반반나망희\n아사사받반타다사팍카팍카삭자초\n초어어어어어러어석퍽커퍽커서어\n사반반타망희",
    defaultInput: "7"
  },
  {
    name: "Project Euler 7 (10,001st Prime)",
    description: "Solves Project Euler Problem 7 by computing and printing the 10,001st prime number (104,743) using optimized Aheui stack arithmetic on its prime factors ((2 * 3 * 3 * 11 * 23 * 23) + 1).",
    code: "반받따받따밞반다따밞반따발다따밞반따발다따반반나다망희"
  }
];

export default function App() {
  const [sourceCode, setSourceCode] = useState(PRESETS[0].code);
  const [inputBuffer, setInputBuffer] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(200); // ms per step
  const [activeTab, setActiveTab] = useState<"visualizer" | "docs">("visualizer");
  
  // Interpreter state
  const interpreterRef = useRef(new AheuiInterpreter());
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const [grid, setGrid] = useState<string[][]>([]);
  const [ip, setIp] = useState({ x: 0, y: 0, dx: 1, dy: 0 });
  const [halted, setHalted] = useState(false);
  const [currentStorage, setCurrentStorage] = useState(0);
  const [storage, setStorage] = useState<bigint[][]>(Array.from({ length: 28 }, () => []));
  const [output, setOutput] = useState("");
  const [stepCount, setStepCount] = useState(0);
  const [executionMessage, setExecutionMessage] = useState<{ type: "success" | "warning"; text: string } | null>(null);

  // Initialize interpreter and reset run state with current code/input changes
  useEffect(() => {
    setIsRunning(false);
    setStepCount(0);
    handleLoad();
  }, [sourceCode, inputBuffer]);

  // Load code into interpreter
  const handleLoad = () => {
    const interpreter = interpreterRef.current;
    interpreter.load(sourceCode);
    interpreter.setInput(inputBuffer);
    updateStates();
    setExecutionMessage(null);
  };

  const updateStates = () => {
    const interpreter = interpreterRef.current;
    const state = interpreter.getState();
    setGrid(interpreter.code);
    setIp({ x: state.x, y: state.y, dx: state.dx, dy: state.dy });
    setHalted(state.halted);
    setCurrentStorage(state.currentStorage);
    setStorage(state.storage);
    setOutput(state.output);
  };

  // Run stepping
  const step = () => {
    const interpreter = interpreterRef.current;
    if (interpreter.halted) {
      setIsRunning(false);
      return;
    }
    interpreter.step();
    setStepCount(prev => prev + 1);
    updateStates();
    setExecutionMessage(null);
  };

  // Autoplay effect
  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        if (interpreterRef.current.halted) {
          setIsRunning(false);
        } else {
          step();
        }
      }, speed);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isRunning, speed]);

  // Input buffer is fully synchronized and loaded as part of the main effect above

  const handleReset = () => {
    setIsRunning(false);
    setStepCount(0);
    handleLoad();
    setExecutionMessage(null);
  };

  const handlePresetSelect = (preset: typeof PRESETS[number]) => {
    setIsRunning(false);
    setStepCount(0);
    setSourceCode(preset.code);
    setInputBuffer(preset.defaultInput || "");
    setExecutionMessage(null);
  };

  const runToHalt = () => {
    const interpreter = interpreterRef.current;
    if (interpreter.halted) return;
    
    setIsRunning(false);
    setExecutionMessage(null);
    let steps = 0;
    const maxSteps = 5000000; // safe limit to prevent browser freezing (5M steps runs in ~400ms)
    
    while (!interpreter.halted && steps < maxSteps) {
      interpreter.step();
      steps++;
    }
    
    setStepCount(prev => prev + steps);
    updateStates();

    if (!interpreter.halted && steps >= maxSteps) {
      setExecutionMessage({
        type: "warning",
        text: `안전을 위해 5,000,000단계에서 일시 정지되었습니다. 무한 루프 상태이거나 복잡한 계산일 수 있습니다. '번개 실행'을 다시 누르면 이어서 추가 5,000,000단계를 진행합니다. (Paused at 5,000,000 steps to prevent freezing. Click Instant Run again to continue.)`
      });
    } else if (interpreter.halted) {
      setExecutionMessage({
        type: "success",
        text: `번개처럼 실행이 완료되었습니다! 총 ${steps.toLocaleString()}걸음이 성공적으로 처리되었습니다. (Completed successfully! Processed ${steps.toLocaleString()} steps.)`
      });
    }
  };

  const activeStorageCount = storage.filter(s => s.length > 0).length;

  const getDirectionIcon = (dx: number, dy: number) => {
    if (dx > 0) return <ArrowRight className="w-4 h-4 text-dancheong-red" />;
    if (dx < 0) return <ArrowLeft className="w-4 h-4 text-dancheong-red" />;
    if (dy > 0) return <ArrowDown className="w-4 h-4 text-dancheong-red" />;
    if (dy < 0) return <ArrowUp className="w-4 h-4 text-dancheong-red" />;
    return null;
  };

  // Helper to resolve storage descriptor
  const getStorageLabel = (idx: number) => {
    if (idx === 21) return "ㅇ (Queue)";
    if (idx === 27) return "ㅎ (Discard)";
    const char = JONGSEONG[idx];
    return `${char || "Stack 0"} (${idx})`;
  };

  return (
    <div className="min-h-screen bg-hanji-white text-ink-black flex flex-col font-sans">
      {/* Header Banner */}
      <header className="border-b border-clay-gray bg-hanji-paper/70 backdrop-blur px-6 py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-celadon-green/10 p-2.5 rounded-xl border border-celadon-green/20 text-celadon-green shadow-[0_4px_12px_rgba(61,110,87,0.1)]">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 id="app-title" className="text-xl font-bold tracking-tight text-ink-black font-serif flex items-center gap-1">
                아희 <span className="text-xs font-sans text-ink-muted ml-1 font-normal tracking-wide">Aheui Playground</span>
              </h1>
              <span className="bg-dancheong-red/10 text-dancheong-red text-xs px-2.5 py-0.5 rounded-full border border-dancheong-red/20 font-serif font-semibold">
                律 Verification
              </span>
            </div>
            <p className="text-xs text-ink-muted mt-0.5">
              Interactive visual environment for the Korean esoteric programming language
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-hanji-paper/50 p-1 rounded-lg border border-clay-gray">
          <button
            onClick={() => setActiveTab("visualizer")}
            className={`px-4 py-1.5 rounded-md text-xs font-semibold font-serif transition-all flex items-center gap-2 ${
              activeTab === "visualizer"
                ? "bg-celadon-green text-hanji-white shadow-md"
                : "text-ink-muted hover:text-ink-black"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            활성판 (Visualizer)
          </button>
          <button
            onClick={() => setActiveTab("docs")}
            className={`px-4 py-1.5 rounded-md text-xs font-semibold font-serif transition-all flex items-center gap-2 ${
              activeTab === "docs"
                ? "bg-celadon-green text-hanji-white shadow-md"
                : "text-ink-muted hover:text-ink-black"
            }`}
          >
            <Code className="w-3.5 h-3.5" />
            아희 규격 (Specs)
          </button>
        </div>
      </header>

      {/* Main Panel */}
      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1600px] w-full mx-auto">
        <AnimatePresence mode="wait">
          {activeTab === "visualizer" ? (
            <motion.div
              key="visualizer"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="lg:col-span-12 grid grid-cols-1 lg:grid-cols-12 gap-6"
            >
              {/* Left Column: Input and Preset Selectors */}
              <div className="lg:col-span-4 flex flex-col gap-6">
                {/* Preset List */}
                <div className="bg-hanji-paper border border-clay-gray rounded-xl p-5 flex flex-col gap-3 shadow-sm">
                  <div className="flex items-center gap-2 text-ink-black font-semibold font-serif text-sm border-b border-clay-gray/60 pb-2 mb-1">
                    <Sparkles className="w-4 h-4 text-dancheong-red" />
                    디딤돌 예제 (Presets)
                  </div>
                  <div className="flex flex-col gap-2">
                    {PRESETS.map((preset) => (
                      <button
                        key={preset.name}
                        onClick={() => handlePresetSelect(preset)}
                        className={`text-left p-3 rounded-lg border transition-all hover:bg-hanji-white/50 group ${
                          sourceCode === preset.code
                            ? "bg-hanji-white border-dancheong-red/40 text-ink-black shadow-sm"
                            : "bg-hanji-white/30 border-clay-gray/40 text-ink-muted"
                        }`}
                      >
                        <div className="font-semibold text-sm text-ink-black group-hover:text-dancheong-red transition-colors flex items-center gap-2 font-serif">
                          <span className={`w-1.5 h-1.5 rounded-full ${sourceCode === preset.code ? 'bg-dancheong-red' : 'bg-ink-muted/30'}`} />
                          {preset.name}
                        </div>
                        <p className="text-xs text-ink-muted mt-1 line-clamp-2 leading-relaxed">
                          {preset.description}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Code Editor Box */}
                <div className="bg-hanji-paper border border-clay-gray rounded-xl p-5 flex flex-col gap-4 shadow-sm">
                  <div className="flex items-center justify-between border-b border-clay-gray/60 pb-2">
                    <div className="flex items-center gap-2 text-ink-black font-semibold font-serif text-sm">
                      <Code className="w-4 h-4 text-celadon-green" />
                      글꼴틀 (Code Editor)
                    </div>
                    <span className="text-xs text-ink-muted font-serif">한글 자소 (UTF-8)</span>
                  </div>
                  <div className="relative">
                    <textarea
                      value={sourceCode}
                      onChange={(e) => setSourceCode(e.target.value)}
                      placeholder="Type or paste Aheui Hangul code here..."
                      className="w-full h-44 bg-hanji-white border border-clay-gray rounded-lg p-3 text-ink-black font-mono text-sm leading-relaxed focus:outline-none focus:border-celadon-green/50 resize-y shadow-inner"
                    />
                  </div>

                  {/* Input Buffer Panel */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-serif text-ink-dark flex items-center gap-1.5 justify-between">
                      <span className="flex items-center gap-1.5">
                        <Terminal className="w-3.5 h-3.5 text-[#0046ff]" />
                        기록틀 (Input Buffer)
                      </span>
                      <span className="font-mono text-[9px] text-[#0046ff] font-bold tracking-wider uppercase bg-[#0046ff]/10 px-1.5 py-0.5 select-none">
                        DS_CONSOLE_IN
                      </span>
                    </label>
                    <div className="relative flex items-center bg-[#05091e] border-2 border-[#0046ff] px-3 py-2 text-sm text-[#00f0ff] font-mono rounded-none shadow-[0_0_15px_rgba(0,70,255,0.12)]">
                      <span className="text-[#0046ff] mr-2 shrink-0 select-none font-bold">&gt;</span>
                      <input
                        type="text"
                        value={inputBuffer}
                        onChange={(e) => setInputBuffer(e.target.value)}
                        placeholder="e.g. 10 20"
                        className="w-full bg-transparent border-none outline-none p-0 text-[#00f0ff] placeholder-[#0046ff]/40 font-mono focus:ring-0 focus:outline-none select-text caret-[#00f0ff]"
                      />
                    </div>
                  </div>

                  {/* Manual trigger reload if modified */}
                  <button
                    onClick={handleLoad}
                    className="w-full bg-celadon-green hover:bg-celadon-hover text-hanji-white text-xs py-2 rounded-lg font-serif transition-all flex items-center justify-center gap-1.5 shadow-md font-semibold cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    디딤돌 올리기 (Load to Engine)
                  </button>
                </div>
              </div>

              {/* Center/Right Column: Interactive Grid and State Visualizer */}
              <div className="lg:col-span-8 flex flex-col gap-6">
                {/* Control Panel */}
                <div className="bg-hanji-paper border border-clay-gray rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-sm">
                  {/* Action Buttons */}
                  <div className="flex items-center gap-2">
                    {isRunning ? (
                      <button
                        onClick={() => setIsRunning(false)}
                        className="bg-dancheong-red hover:bg-dancheong-hover text-hanji-white px-4 py-2 rounded-lg text-xs font-serif font-semibold transition-all flex items-center gap-2 shadow-md cursor-pointer"
                      >
                        <Square className="w-3.5 h-3.5 fill-current" />
                        멈춤 (Pause)
                      </button>
                    ) : (
                      <button
                        onClick={() => setIsRunning(true)}
                        disabled={halted}
                        className={`px-4 py-2 rounded-lg text-xs font-serif font-semibold transition-all flex items-center gap-2 ${
                          halted
                            ? "bg-ink-muted/10 text-ink-muted/40 border border-clay-gray/45 cursor-not-allowed"
                            : "bg-dancheong-red hover:bg-dancheong-hover text-hanji-white shadow-md cursor-pointer"
                        }`}
                      >
                        <Play className="w-3.5 h-3.5 fill-current" />
                        달리기 (Run)
                      </button>
                    )}
                    <button
                      onClick={runToHalt}
                      disabled={halted || isRunning}
                      className={`px-4 py-2 rounded-lg text-xs font-serif font-semibold transition-all flex items-center gap-2 ${
                        halted || isRunning
                          ? "bg-ink-muted/10 text-ink-muted/40 border border-clay-gray/45 cursor-not-allowed opacity-50"
                          : "bg-celadon-green hover:bg-celadon-hover text-hanji-white shadow-md cursor-pointer"
                      }`}
                    >
                      <Zap className="w-3.5 h-3.5 fill-current" />
                      번개 실행 (Instant Run)
                    </button>
                    <button
                      onClick={step}
                      disabled={halted || isRunning}
                      className="bg-hanji-white hover:bg-hanji-paper disabled:opacity-40 disabled:cursor-not-allowed border border-clay-gray text-ink-black px-4 py-2 rounded-lg text-xs font-serif font-semibold transition-all flex items-center gap-2 shadow-sm cursor-pointer"
                    >
                      <SkipForward className="w-3.5 h-3.5" />
                      한 걸음 (Step)
                    </button>
                    <button
                      onClick={handleReset}
                      className="bg-hanji-white hover:bg-hanji-paper border border-clay-gray text-ink-black px-4 py-2 rounded-lg text-xs font-serif font-semibold transition-all flex items-center gap-2 shadow-sm cursor-pointer"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      비우기 (Reset)
                    </button>
                  </div>

                  {/* Settings & Speed */}
                  <div className="flex items-center gap-4 flex-1 sm:justify-end min-w-[200px]">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-serif text-ink-dark">빠르기 (Speed):</span>
                      <input
                        type="range"
                        min="50"
                        max="1000"
                        step="50"
                        value={1050 - speed} // Inverse to make higher speed = shorter interval
                        onChange={(e) => setSpeed(1050 - parseInt(e.target.value))}
                        className="w-24 accent-celadon-green cursor-pointer h-1 bg-clay-gray rounded-lg"
                      />
                      <span className="text-xs font-mono text-celadon-green min-w-[50px] text-right font-bold">
                        {Math.round(1000 / speed)} Hz
                      </span>
                    </div>

                    <div className="h-6 w-px bg-clay-gray/60" />

                    <div className="text-xs font-serif text-ink-dark">
                      걸음수 (Steps): <span className="text-dancheong-red font-bold font-mono text-sm">{stepCount}</span>
                    </div>
                  </div>
                </div>

                {executionMessage && (
                  <div className={`p-4 rounded-xl border font-serif text-xs leading-relaxed flex items-start gap-2.5 shadow-sm transition-all animate-in fade-in slide-in-from-top-2 duration-300 ${
                    executionMessage.type === "warning"
                      ? "bg-dancheong-red/5 border-dancheong-red/20 text-ink-black animate-pulse"
                      : "bg-celadon-green/5 border-celadon-green/20 text-ink-black"
                  }`}>
                    {executionMessage.type === "warning" ? (
                      <AlertTriangle className="w-4 h-4 text-dancheong-red shrink-0 mt-0.5" />
                    ) : (
                      <Zap className="w-4 h-4 text-celadon-green shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <p className="font-semibold mb-0.5">
                        {executionMessage.type === "warning" ? "실행 일시 정지 (Execution Paused)" : "실행 완료 (Execution Completed)"}
                      </p>
                      <p className="text-ink-muted leading-relaxed">{executionMessage.text}</p>
                    </div>
                    <button 
                      onClick={() => setExecutionMessage(null)}
                      className="text-ink-muted hover:text-ink-black text-[10px] font-sans hover:bg-ink-muted/10 px-1.5 py-0.5 rounded cursor-pointer"
                    >
                      닫기 (Close)
                    </button>
                  </div>
                )}

                {/* 2D Program Execution Map */}
                <div className="bg-hanji-paper border border-clay-gray rounded-xl p-5 flex flex-col gap-4 flex-1 min-h-[300px] shadow-sm">
                  <div className="flex items-center justify-between border-b border-clay-gray/60 pb-2">
                    <div className="flex items-center gap-2 text-ink-black font-semibold font-serif text-sm">
                      <Maximize2 className="w-4 h-4 text-celadon-green" />
                      아희 활성판 (Interactive 2D Grid)
                    </div>
                    <div className="flex items-center gap-3 text-xs text-ink-dark font-mono">
                      <div className="flex items-center gap-1 bg-hanji-white/80 px-2 py-0.5 rounded border border-clay-gray/40">
                        <span className="text-ink-muted">위치 (IP):</span>
                        <span className="text-ink-black font-bold">({ip.x}, {ip.y})</span>
                      </div>
                      <div className="flex items-center gap-1 bg-hanji-white/80 px-2 py-0.5 rounded border border-clay-gray/40">
                        <span className="text-ink-muted">흐름 (Vector):</span>
                        <span className="flex items-center gap-1 text-ink-black font-bold">
                          ({ip.dx}, {ip.dy})
                          {getDirectionIcon(ip.dx, ip.dy)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Visual Grid Container */}
                  <div className="flex-1 bg-hanji-white border border-clay-gray rounded-lg p-5 overflow-auto flex items-center justify-center min-h-[220px] shadow-inner">
                    {grid.length === 0 ? (
                      <div className="text-ink-muted text-sm font-serif flex items-center gap-2">
                        <Info className="w-4 h-4" />
                        아직 글자판이 비어 있습니다. 왼쪽에서 올리기 버튼을 눌러주세요.
                      </div>
                    ) : (
                      <div className="flex flex-col gap-2 p-2">
                        {grid.map((row, rIdx) => (
                          <div key={rIdx} className="flex gap-2">
                            {row.map((char, cIdx) => {
                              const isActive = ip.x === cIdx && ip.y === rIdx;
                              const decomp = decomposeChar(char);
                              const hasDecomp = decomp !== null;
                              
                              return (
                                <div
                                  key={cIdx}
                                  className={`relative w-12 h-12 flex flex-col items-center justify-center rounded-lg border text-sm transition-all duration-100 ${
                                    isActive
                                      ? "bg-dancheong-red text-hanji-white border-dancheong-hover shadow-[0_4px_12px_rgba(178,58,34,0.3)] font-bold scale-105 z-10 font-serif"
                                      : hasDecomp
                                      ? "bg-hanji-paper border-clay-gray text-ink-black hover:border-ink-muted font-serif"
                                      : "bg-hanji-white border-clay-gray/30 text-ink-muted/30 border-dashed font-sans"
                                  }`}
                                >
                                  <span className="text-sm font-bold">{char}</span>
                                  {hasDecomp && !isActive && (
                                    <span className="text-[9px] text-ink-muted font-mono mt-0.5 scale-90">
                                      {decomp.ch}:{decomp.jo}
                                    </span>
                                  )}
                                  {isActive && (
                                    <span className="absolute -top-1.5 -right-1.5 bg-imperial-gold text-ink-black text-[8px] font-bold px-1 rounded-full border border-hanji-white">
                                      IP
                                    </span>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Grid row: Stacks and Outputs */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Execution Output Stream */}
                  <div className="bg-[#030712] border-2 border-[#0046ff] rounded-none p-5 flex flex-col gap-3 shadow-[0_0_20px_rgba(0,70,255,0.12)]">
                    <div className="flex items-center justify-between border-b border-[#0046ff]/30 pb-2">
                      <div className="flex items-center gap-2 text-[#00f0ff] font-semibold font-mono text-xs uppercase tracking-wider">
                        <Terminal className="w-4 h-4 text-[#0046ff]" />
                        Aheui Terminal :: stdout
                      </div>
                      {halted ? (
                        <span className="bg-[#ef4444] text-white text-[9px] font-bold px-2 py-0.5 rounded-none font-mono tracking-wider animate-pulse">
                          SYSTEM_HALTED
                        </span>
                      ) : (
                        <span className="bg-[#0046ff]/20 text-[#00f0ff] border border-[#0046ff]/40 text-[9px] font-bold px-2 py-0.5 rounded-none font-mono tracking-wider">
                          READY_TO_RUN
                        </span>
                      )}
                    </div>
                    <div className="flex-1 min-h-[140px] bg-[#020514] border border-[#0046ff]/20 rounded-none p-3.5 font-mono text-sm overflow-y-auto max-h-[180px] flex flex-col justify-between shadow-inner">
                      <div className="text-[#f1f5f9] leading-relaxed whitespace-pre-wrap font-bold text-xs">
                        {output.length > 5000 ? (
                          <>
                            {output.slice(-5000)}
                            <div className="text-red-400 text-[10px] mt-1.5 italic font-mono uppercase tracking-wider">
                              [OUTPUT STREAM TRUNCATED FOR PERFORMANCE - SHOWING LATEST 5000 CHARS]
                            </div>
                          </>
                        ) : (
                          output || (
                            <span className="text-[#0046ff]/50 italic font-mono text-xs animate-pulse">
                              &gt; waiting for output...
                            </span>
                          )
                        )}
                      </div>
                      <div className="text-[10px] text-[#0046ff]/60 border-t border-[#0046ff]/10 pt-2 flex justify-between items-center mt-4 font-mono uppercase tracking-wider">
                        <span>stdout stream</span>
                        <span>{output.length} chars emitted</span>
                      </div>
                    </div>
                  </div>

                  {/* Storage State Panel */}
                  <div className="bg-hanji-paper border border-clay-gray rounded-xl p-5 flex flex-col gap-3 shadow-sm">
                    <div className="flex items-center justify-between border-b border-clay-gray/60 pb-2">
                      <div className="flex items-center gap-2 text-ink-black font-semibold font-serif text-sm">
                        <Layers className="w-4 h-4 text-celadon-green" />
                        저장고 상태 (Storage Layers)
                      </div>
                      <span className="text-xs text-ink-muted font-serif">
                        현재 저장고: <strong className="text-celadon-green font-bold">#{currentStorage}</strong>
                      </span>
                    </div>

                    <div className="flex-1 min-h-[140px] max-h-[180px] bg-hanji-white border border-clay-gray rounded-lg p-3 overflow-y-auto flex flex-col gap-2.5 shadow-inner">
                      {activeStorageCount === 0 ? (
                        <div className="h-full flex items-center justify-center text-ink-muted/50 text-xs italic font-serif py-12">
                          모든 저장고(28개)가 비어 있습니다
                        </div>
                      ) : (
                        <div className="flex flex-col gap-3">
                          {storage.map((store, idx) => {
                            if (store.length === 0) return null;
                            const isActive = currentStorage === idx;
                            return (
                              <div
                                key={idx}
                                className={`p-2.5 rounded-lg border flex flex-col gap-1.5 transition-all ${
                                  isActive
                                    ? "bg-celadon-tint border-celadon-green/30 shadow-sm"
                                    : "bg-hanji-paper/50 border-clay-gray/30"
                                }`}
                              >
                                <div className="flex justify-between items-center">
                                  <span className={`text-xs font-serif font-semibold ${isActive ? 'text-celadon-green' : 'text-ink-muted'}`}>
                                    {getStorageLabel(idx)}
                                  </span>
                                  <span className="text-[10px] bg-hanji-white border border-clay-gray/40 text-ink-muted px-1.5 py-0.5 rounded font-mono font-bold">
                                    크기: {store.length}
                                  </span>
                                </div>
                                <div className="flex flex-wrap gap-1">
                                  {store.slice(-40).map((val, vIdx) => (
                                    <span
                                      key={vIdx}
                                      className="bg-hanji-white border border-clay-gray rounded px-2 py-0.5 text-xs font-mono text-ink-black font-semibold shadow-sm"
                                    >
                                      {val.toString()}
                                    </span>
                                  ))}
                                  {store.length > 40 && (
                                    <span className="text-[10px] text-ink-muted self-center italic px-1 font-mono">
                                      (+ {store.length - 40} more)
                                    </span>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                </div>


              </div>
            </motion.div>
          ) : (
            /* Bilingual Documentation and Instruction Reference panel */
            <motion.div
              key="docs"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="lg:col-span-12 bg-hanji-paper border border-clay-gray rounded-xl p-6 flex flex-col gap-6 shadow-sm"
            >
              <div className="flex items-center gap-2 border-b border-clay-gray/60 pb-4">
                <HelpCircle className="w-5 h-5 text-dancheong-red" />
                <div>
                  <h2 className="text-lg font-bold text-ink-black font-serif">아희 규격 일람 (Aheui Specification)</h2>
                  <p className="text-xs text-ink-muted font-serif">한글 자소별 명령, 흐름 방향 및 저장고 작동 방식 설명</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Consonants / Operations */}
                <div className="flex flex-col gap-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-ink-black font-serif border-b border-clay-gray/60 pb-1 flex items-center gap-1.5">
                    <Hash className="w-3.5 h-3.5 text-dancheong-red" />
                    첫소리 (Consonants / Commands)
                  </h3>
                  <div className="flex flex-col gap-2.5 max-h-[500px] overflow-y-auto pr-2">
                    {[
                      { symbol: "ㄷ", op: "Add (더하기)", desc: "Pops a, pops b, pushes (b + a)" },
                      { symbol: "ㄸ", op: "Multiply (곱하기)", desc: "Pops a, pops b, pushes (b * a)" },
                      { symbol: "ㅌ", op: "Subtract (빼기)", desc: "Pops a, pops b, pushes (b - a)" },
                      { symbol: "ㄴ", op: "Divide (나누기)", desc: "Pops a, pops b, pushes math.floor(b / a)" },
                      { symbol: "ㄹ", op: "Modulo (나머지)", desc: "Pops a, pops b, pushes (b % a)" },
                      { symbol: "ㅂ", op: "Push (집어넣기)", desc: "Pushes stroke count value, or reads inputs on ㅇ/ㅎ" },
                      { symbol: "ㅃ", op: "Duplicate (또넣기)", desc: "Pops a, pushes a twice" },
                      { symbol: "ㅁ", op: "Pop (뽑아내기)", desc: "Pops a; if final is ㅇ/ㅎ, prints it as integer/char" },
                      { symbol: "ㅋ", op: "Swap (바꾸기)", desc: "Swaps the top two values on the stack" },
                      { symbol: "ㅅ", op: "Select Storage (선택)", desc: "Selects storage matching final consonant" },
                      { symbol: "ㅆ", op: "Move (이동)", desc: "Pops a, pushes a to target storage" },
                      { symbol: "ㅍ", op: "Copy (복사)", desc: "Pops a, pushes to target AND current storage" },
                      { symbol: "ㅈ", op: "Compare (비교)", desc: "Pops a, pops b, pushes (b >= a) ? 1 : 0" },
                      { symbol: "ㅊ", op: "Conditional (조건갈래)", desc: "Pops a, if a == 0 reverse velocity vector" },
                      { symbol: "ㅎ", op: "Halt (끝내기)", desc: "Halts the program execution" },
                      { symbol: "ㅇ / ㄱ / ㄲ / ㅉ", op: "No-Op (쉬기)", desc: "No operation performed" }
                    ].map((c) => (
                      <div key={c.symbol} className="bg-hanji-white border border-clay-gray/40 p-2.5 rounded-lg flex gap-3 items-start shadow-sm">
                        <div className="bg-celadon-green/10 text-celadon-green font-serif font-bold border border-celadon-green/20 w-8 h-8 rounded flex items-center justify-center shrink-0">
                          {c.symbol}
                        </div>
                        <div>
                          <div className="font-bold text-xs text-ink-black font-serif">{c.op}</div>
                          <div className="text-[11px] text-ink-muted mt-0.5 leading-relaxed">{c.desc}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Vowels / Direction */}
                <div className="flex flex-col gap-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-ink-black font-serif border-b border-clay-gray/60 pb-1 flex items-center gap-1.5">
                    <Compass className="w-3.5 h-3.5 text-celadon-green" />
                    가운뎃소리 (Vowels / Directions)
                  </h3>
                  <div className="flex flex-col gap-2.5 max-h-[500px] overflow-y-auto pr-2">
                    {[
                      { symbol: "ㅏ", op: "Right 1 (오른쪽)", desc: "Sets velocity vector (dx = 1, dy = 0)" },
                      { symbol: "ㅑ", op: "Right 2 (오른쪽 두 칸)", desc: "Sets velocity vector (dx = 2, dy = 0)" },
                      { symbol: "ㅓ", op: "Left 1 (왼쪽)", desc: "Sets velocity vector (dx = -1, dy = 0)" },
                      { symbol: "ㅕ", op: "Left 2 (왼쪽 두 칸)", desc: "Sets velocity vector (dx = -2, dy = 0)" },
                      { symbol: "ㅗ", op: "Up 1 (위쪽)", desc: "Sets velocity vector (dx = 0, dy = -1)" },
                      { symbol: "ㅛ", op: "Up 2 (위쪽 두 칸)", desc: "Sets velocity vector (dx = 0, dy = -2)" },
                      { symbol: "ㅜ", op: "Down 1 (아래쪽)", desc: "Sets velocity vector (dx = 0, dy = 1)" },
                      { symbol: "ㅠ", op: "Down 2 (아래쪽 두 칸)", desc: "Sets velocity vector (dx = 0, dy = 2)" },
                      { symbol: "ㅡ", op: "Reflect Vertical (세로뒤집기)", desc: "Reverses vertical velocity (dy = -dy)" },
                      { symbol: "ㅣ", op: "Reflect Horizontal (가로뒤집기)", desc: "Reverses horizontal velocity (dx = -dx)" },
                      { symbol: "ㅢ", op: "Reflect Both (모두뒤집기)", desc: "Reverses both coordinates (dx = -dx, dy = -dy)" },
                      { symbol: "Others", op: "No Change (그대로)", desc: "Preserves current movement speed and vector" }
                    ].map((v) => (
                      <div key={v.symbol} className="bg-hanji-white border border-clay-gray/40 p-2.5 rounded-lg flex gap-3 items-start shadow-sm">
                        <div className="bg-celadon-green/10 text-celadon-green font-serif font-bold border border-celadon-green/20 w-8 h-8 rounded flex items-center justify-center shrink-0">
                          {v.symbol}
                        </div>
                        <div>
                          <div className="font-bold text-xs text-ink-black font-serif">{v.op}</div>
                          <div className="text-[11px] text-ink-muted mt-0.5 leading-relaxed">{v.desc}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Final Consonants / Stroke Counts */}
                <div className="flex flex-col gap-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-ink-black font-serif border-b border-clay-gray/60 pb-1 flex items-center gap-1.5">
                    <Hash className="w-3.5 h-3.5 text-imperial-gold" />
                    끝소리 (Final Consonants / Values)
                  </h3>
                  <div className="flex flex-col gap-3">
                    <p className="text-xs text-ink-muted font-serif leading-relaxed">
                      받침(끝소리)은 명령의 **인수(arguments)** 역할을 합니다. 집어넣기(`ㅂ`) 명령에서는 획수로 수치 값을 나타내며, 저장고 선택(`ㅅ`, `ㅆ`, `ㅍ`) 명령에서는 레이어의 인덱스를 지정합니다.
                    </p>
                    <div className="bg-hanji-white border border-clay-gray/40 p-3.5 rounded-lg flex flex-col gap-2 font-mono text-xs shadow-sm">
                      <div className="text-ink-black font-serif font-bold border-b border-clay-gray/40 pb-1.5 flex justify-between">
                        <span>글자 (Glyph)</span>
                        <span>획수 (Value / Action)</span>
                      </div>
                      <div className="grid grid-cols-2 gap-y-1.5 gap-x-4 max-h-[350px] overflow-y-auto pr-1">
                        {JONGSEONG.map((char, idx) => {
                          if (char === "") return null;
                          const stroke = STROKES[idx];
                          const desc = idx === 21 ? "입출력 (정수)" : idx === 27 ? "입출력 (문자)" : `${stroke}획`;
                          return (
                            <div key={idx} className="flex justify-between items-center border-b border-clay-gray/20 pb-1 font-serif">
                              <span className="font-bold text-ink-black text-sm">[{char}]</span>
                              <span className="text-ink-muted font-mono text-xs">{desc}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
