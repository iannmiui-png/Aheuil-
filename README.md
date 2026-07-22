# Aheui Playground (아희 플레이그라운드)

An elegant, interactive playground and visualizer for the esoteric 2D Hangul-based programming language **Aheui** (아희). 

---

## 🌐 Language Navigation / 언어 바로가기
- [English](#english)
- [한국어 (Korean)](#한국어-korean)
- [中文 (Chinese)](#中文-chinese)
- [日本語 (Japanese)](#日本語-japanese)
- [العربية (Arabic)](#العربية-arabic)

---

## English

### 🌟 About Aheui
**Aheui** is a famous two-dimensional, stack-based esoteric programming language modeled after the Hangul (Korean) writing system. Every syllable block in Hangul acts as a single instruction:
- **Initial Consonant (초성):** Defines the operation (e.g., arithmetic, push/pop, input/output).
- **Vowel (중성):** Determines the cursor velocity and movement direction in the 2D grid.
- **Final Consonant (종성):** Acts as a parameter (determines integer values to push or selects the storage container).

### 🚀 Key Features
- **Interactive 2D Grid Visualizer:** Watch the instruction pointer (PC) sweep across your grid with dynamic direction arrows and highlighted execution cells in real-time.
- **Comprehensive Debugging Suite:** Run, pause, execute step-by-step, or reset. Control execution speed (from slow-motion tracing up to lightning-fast execution).
- **Live Memory Inspector:** View the contents of all 26 stacks, 1 queue (통), and 1 extension port in real-time as elements are pushed, popped, and transferred.
- **Aheui Code Assistant & Engine:** Get help writing Aheui code, optimizing 2D grids, or translating algorithms into direct Hangul instructions.
- **Built-in Program Presets:**
  - **Hello World:** Prints the standard Esoteric greeting.
  - **Fibonacci Sequence:** Generates numbers in the Fibonacci sequence.
  - **Countdown:** A loop-back routing layout counting down from 5 to 1.
  - **2D Grid Prime Checker:** High-fidelity 2D search loop checking if an input is prime (yielding `1` or `0`).
  - **Project Euler 7 (10,001st Prime):** Solves Euler 7 by utilizing optimized stack factorization to print `104743`.

### 🛠️ Getting Started
Ensure you have Node.js installed on your machine.
```bash
# Install dependencies
npm install

# Start the interactive development server
npm run dev

# Build for production deployment
npm run build
```

---

## 한국어 (Korean)

### 🌟 아희(Aheui)에 대하여
**아희**는 한글의 기하학적이고 논리적인 특성을 활용하여 설계된 2차원 스택 기반 난해한 프로그래밍 언어입니다. 한글의 각 음절 하나하나가 하나의 독립된 명령어로 작동합니다:
- **초성:** 수행할 연산(예: 산술 연산, 값 밀어넣기/빼기, 입출력 등)을 결정합니다.
- **중성:** 2D 격자 위에서 실행 포인터(PC)가 이동할 방향과 속도를 제어합니다.
- **종성:** 연산에 동반되는 매개변수(스택에 쌓을 정수값 또는 사용할 메모리 공간의 번호) 역할을 합니다.

### 🚀 주요 기능
- **대화형 2D 격자 시각화:** 실시간으로 움직이는 실행 포인터(PC)의 방향 화살표와 현재 실행 중인 음절 셀을 화면 상에서 직관적으로 파악할 수 있습니다.
- **강력한 디버깅 도구:** 실행(Play), 일시 정지(Pause), 단계별 단일 실행(Step), 초기화(Reset) 및 추적 속도 제어 인터페이스를 완벽 제공합니다.
- **실시간 메모리 모니터링:** 26개의 스택, 1개의 큐(통), 확장 포트의 상태를 한눈에 볼 수 있으며, 데이터가 밀려들고 빠져나가는 과정을 실시간 관찰할 수 있습니다.
- **아희 코딩 어시스턴트:** 난해한 아희 소스코드를 분석하고, 알고리즘 아이디어를 아희 프로그램으로 변환해주는 스마트 엔진을 탑재했습니다.
- **풍부한 기본 프리셋 탑재:**
  - **Hello World:** 전통적인 인사말을 출력합니다.
  - **피보나치 수열:** 연속적인 피보나치 정수를 동적으로 생성합니다.
  - **카운트다운:** 3줄짜리 루프백 경로 레이아웃을 통해 5부터 1까지 감소시킵니다.
  - **2D 격자 소수 판별기:** 고정밀 2D 검색 루프를 사용해 소수 여부를 검사하고 `1` 또는 `0`을 결과로 도출합니다.
  - **프로젝트 오일러 7 (10,001번째 소수):** 최적화된 스택 인수분해 기법을 통해 10,001번째 소수인 `104743`을 빠르게 계산하고 출력합니다.

### 🛠️ 시작하기
컴퓨터에 Node.js가 설치되어 있는지 확인해 주세요.
```bash
# 의존성 패키지 설치
npm install

# 개발 환경 실행 (로컬 서버 시작)
npm run dev

# 프로덕션 빌드 작성
npm run build
```

---

## 中文 (Chinese)

### 🌟 关于 Aheui
**Aheui**（아희）是一种著名的基于韩文（Hangul）书写系统的二维堆栈奇异编程语言。每一个韩文音节块都代表着一个独特的程序指令：
- **声母（初声 / Initial Consonant）：** 定义了具体的操作（例如算术运算、推入/弹出、输入输出等）。
- **韵母（中声 / Vowel）：** 决定了指令指针（PC）在二维网格上的移动方向和速度。
- **韵尾（终声 / Final Consonant）：** 作为指令的操作参数（定义要推入堆栈的整数值或选定存储容器）。

### 🚀 核心特性
- **交互式 2D 网格可视化：** 实时直观地展示指令指针（PC）在网格中的扫掠轨迹，并伴有动态方向箭头和高亮突出显示当前执行的单元格。
- **全方位调试套件：** 支持运行、暂停、单步执行（Step）及重置。支持从慢动作步进追踪到极速运行的宽频速度调节。
- **实时内存监视器：** 实时动态渲染全部 26 个堆栈、1 个队列（통）及扩展端口的内部状态，捕获其数据压入、弹出、以及数据转换的每一个微观过程。
- **Aheui 智能代码助手：** 为您解读复杂的 Aheui 指令，并将您的算法思路转换翻译成韩文 Aheui 代码。
- **内置经典预设程序：**
  - **Hello World (世界你好):** 打印经典的 esoteric 语言问候。
  - **斐波那契数列:** 生成一系列的斐波那契数。
  - **倒计时 (Countdown):** 基于 3 行回环路由设计，从 5 依次倒数到 1。
  - **2D网格素数检验器:** 复杂的二维回环，测试输入数字是否为素数并返回 `1` 或 `0`。
  - **Project Euler 7 (欧拉计划第7题):** 通过优化的堆栈因数乘积和加法，直接计算出第 10,001 个素数并打印：`104743`。

### 🛠️ 快速上手
请确保您的设备上已安装 Node.js 运行时。
```bash
# 安装所需依赖项
npm install

# 启动交互式本地开发服务器
npm run dev

# 打包生产环境应用
npm run build
```

---

## 日本語 (Japanese)

### 🌟 Aheui について
**Aheui**（アヒ / 아희）は、ハングル文字の論理的な構造をベースにして設計された、ユニークな2次元スタック型難解プログラミング言語（Esoteric Language）です。ハングルを形成する1つの音節文字が、それぞれ独立した1つの命令に対応しています：
- **子音（初声）：** 演算内容（四則演算、スタックへのPush/Pop、数値入出力など）を定義します。
- **母音（中声）：** 2次元グリッド上でのプログラムカウンタ（PC）の移動方向と速度（ジャンプ）を制御します。
- **パッチム（終声）：** 命令のパラメータ（スタックする数値や、アクセスするメモリ領域の番号）を表します。

### 🚀 主な機能
- **直感的な2次元実行ビジュアライザ：** 2Dグリッド上を移動するプログラムカウンタ（PC）の動きを、進路矢印アニメーションやセルハイライトによってリアルタイムで追跡。
- **統合型デバッグツール：** 実行、一時停止、1ステップ実行（Step）、初期化（Reset）を完備。1秒あたりの動作ステップ数をスライダーで自在に調節可能。
- **ライブメモリインスペクタ：** 26個のスタック、1個のキュー（통）、拡張ポートそれぞれのストレージデータをリアルタイムに可視化。
- **Aheui コードアシスタント：** 難読なコードの解釈や、ユーザーの望むロジックを Aheui コードへ変換可能。
- **高品質なプログラムプリセット：**
  - **Hello World:** 標準的なテキスト出力サンプル。
  - **フィボナッチ数列 (Fibonacci):** 動的に変化するフィボナッチ数を生成。
  - **カウントダウン (Countdown):** 3行に渡るループバック構造で、5から1までをカウントダウン。
  - **2Dグリッド素数チェッカー:** 2D空間のループパスを縦横に往復しながら素数判定を行い、`1`（素数）か`0`（合成数）を応答。
  - **Project Euler 7 (第10,001番目の素数):** 最適化されたスタック演算を行い、10,001番目の素数である `104743` を瞬時に計算して出力。

### 🛠️ 起動手順
お使いの環境に Node.js があらかじめインストールされている必要があります。
```bash
# 依存ライブラリのインストール
npm install

# ローカル開発用サーバーの起動
npm run dev

# 本番公開用ファイルのビルド
npm run build
```

---

## العربية (Arabic)

### 🌟 حول لغة أهوي (Aheui)
**أهوي (Aheui)** هي واحدة من أشهر لغات البرمجة ثنائية الأبعاد والغريبة (Esoteric Languages) التي تعتمد على تصميم وأحرف الأبجدية الكورية (Hangul). يعمل كل مقطع لفظي كوري كأمر برمجي مستقل كالتالي:
- **الحرف الساكن الأول (초성):** يحدد نوع العملية المراد تنفيذها (كالعمليات الحسابية، الدفع/السحب من الذاكرة، الإدخال/الإخراج).
- **الحرف الصامت الأوسط (중성):** يتحكم في اتجاه وسرعة مؤشر البرنامج (PC) على الشبكة ثنائية الأبعاد.
- **الحرف الساكن الأخير (종성):** يعمل كمعامل أو قيمة إضافية للأمر (مثل تحديد العدد الذي سيتم دفعه للذاكرة، أو تحديد الحاوية المخزنة المستهدفة).

### 🚀 أهم الميزات
- **مُحاكي تفاعلي للشبكة ثنائية الأبعاد:** شاهد مسار مؤشر التعليمات (PC) وهو يتحرك على الشبكة في البعدين مع مؤشرات حية ومتحركة للاتجاهات وتلوين الخلية الحالية قيد التنفيذ.
- **أدوات تصحيح وتتبع متكاملة:** تشغيل، إيقاف مؤقت، تقدم خطوة بخطوة (Step)، وإعادة تعيين. تحكم مرن في سرعة تتبع الأكواد من البطء الشديد وحتى السرعة القصوى.
- **مراقب الذاكرة الفوري:** تابع محتويات 26 كدسة مخزنة (Stacks)، وطابوراً واحداً (Queue / 통)، ومنفذ الإدخال الإضافي فور دفع البيانات أو سحبها.
- **مساعد برميجي محلي:** مساعد متكامل يشرح لك الأكواد المعقدة، ويولد أكواداً برمجية بلغة "أهوي" بناءً على خوارزمياتك.
- **أمثلة برمجية كلاسيكية مدمجة:**
  - **أهلاً بالعالم (Hello World):** طباعة جملة الترحيب الشهيرة.
  - **متتالية فيبوناتشي:** توليد الأعداد المتتالية ديناميكياً.
  - **العد التنازلي:** حلقة برمجية مكررة من 3 أسطر تعود تنازلياً من 5 إلى 1.
  - **فاحص الأعداد الأولية ثنائي الأبعاد:** حلقة تكرارية تبحث في شبكة البعدين لتأكيد أولية الأعداد، لتعيد `1` (أولي) أو `0` (غير أولي).
  - **مسألة مشروع أولر 7 (العدد الأولي رقم 10,001):** يطبع العدد الأولي ذي الترتيب 10001 وهو `104743` بالاستعانة بعمليات ضرب وجمع سريعة في الكدسة.

### 🛠️ طريقة البدء والتشغيل
تأكد من تنصيب منصة Node.js في جهازك.
```bash
# تثبيت الحزم والمكتبات المطلوبة
npm install

# بدء تشغيل خادم التطوير المحلي
npm run dev

# بناء نسخة الإنتاج النهائية للرفع والرفع السحابي
npm run build
```

---

*Crafted with 💖 by the Google AI Studio Coding Assistant. Enjoy coding in Aheui!*
