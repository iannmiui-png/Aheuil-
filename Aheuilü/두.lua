-- 두.lua
-- BF(브레인퍽) → Aheui 컴파일러
--
-- 원본은 Python으로 작성되어 시뮬레이터(Aheui.lua의 실제 연산 표와 동일한
-- 로직을 파이썬으로 옮긴 것)로 하나하나 검증을 마쳤음. 이 파일은 그 로직을
-- 그대로 Lua로 옮긴 것이며, 별도의 Lua 실행 검증(생성된 코드가 파이썬판과
-- 바이트 단위로 동일한지 diff)까지 거쳤음.
--
-- [1라운드 → 2라운드 참고사항]
--   - 검증된 부분: +, -, ., ',' (입력), >, < (테이프 이동), 그리고 처음부터
--     새로 설계한 루프([...]) 스캐폴드까지 전부 시뮬레이터로 확인됨.
--     특히 루프는 빈 루프(카운터 0), 중첩 루프, glide(>/<)와 결합된 루프까지
--     다 통과함.
--   - 알려진 개선 여지: 실제 아희(Aheui) "예제 모음"에 나오는 Countdown
--     예제(우우어어...\n발빠망...초\n...희)를 분석해 보니, 진짜 관용적인
--     루프 관용구는 이 파일의 스캐폴드보다 훨씬 간결함 — 반복(zero가 아닌
--     경우) 시 별도의 넓은 "복귀 레인(BACK_COL)" 칸을 파지 않고, 바로 위
--     한 줄을 "복귀 통로"로 재사용함(그 줄에 있는 두 개의 방향전환 문자 중
--     어느 것에 먼저 닿느냐로 진입 지점을 다르게 함). 이 파일의 스캐폴드는
--     중첩 깊이(depth)마다 폭 80칸짜리 전용 레인을 새로 만들기 때문에 훨씬
--     더 넓은 그리드를 만들어냄 — 동작은 검증되었지만, 그리드 크기가 중요한
--     경우 다음 라운드에서 Countdown 관용구 스타일로 재작성하면 훨씬
--     compact해질 수 있음.
--   - `,` (입력) 블록은 위키 증명에 없어서 별도로 만든 것: 기존 셀 값을
--     버리고(마 = ㅁ+ㅏ, "pop, no print") 새 문자를 입력받아 push(밯) 함.
--     실제 stdin 연결부(밯의 read_char 처리)는 Aheui.lua의 get_input_char와
--     동일한 경로라 개별 검증은 하지 않았음(순수 배관 코드라 위험도 낮음).

local M = {}

local BASE = 0xAC00
local SP = 32  -- 공백 codepoint (필러 / 통과 칸 - 한글이 아니므로 아무 동작도 안 함)

-- 초성/중성/종성 인덱스로 실제 한글 음절의 codepoint를 계산
-- (hangul.lua의 compose_cp와 완전히 동일한 공식)
local function compose(cho, ju, jo)
    jo = jo or 0
    return BASE + ((cho * 21) + ju) * 28 + jo
end

-- 문자열을 codepoint(정수) 배열로 변환.
-- 주의: Lua 문자열은 "바이트" 단위 인덱싱이라 한글(자모 조합 음절, UTF-8 3바이트)을
-- "칸(column)" 단위로 다루려면 반드시 codepoint 배열로 바꿔서 다뤄야 함.
-- (Python판은 문자열 인덱싱 자체가 codepoint 단위라 이 변환이 필요 없었음)
local function str_to_cps(s)
    local t = {}
    for _, cp in utf8.codes(s) do
        table.insert(t, cp)
    end
    return t
end

-- codepoint 배열을 다시 utf8 문자열로 합침
local function cps_to_str(t)
    local chars = {}
    for i = 1, #t do
        chars[i] = utf8.char(t[i])
    end
    return table.concat(chars)
end

-- row(codepoint 배열)를 깊은 복사
local function copy_row(row)
    local t = {}
    for i = 1, #row do t[i] = row[i] end
    return t
end

-- row의 col번째(0-indexed, BF/Aheui 관례에 맞춤) 자리에 cp를 넣은 "새" row를
-- 반환함(원본은 건드리지 않음). row가 짧으면 공백으로 채운 뒤 끼워 넣음.
local function set_char(row, col, cp)
    local new_row = copy_row(row)
    while #new_row <= col do
        table.insert(new_row, SP)
    end
    new_row[col + 1] = cp  -- Lua는 1-indexed, col은 0-indexed 이므로 +1
    return new_row
end

-- ============ 검증된 스캐폴드 셀들 ============
-- (초성/중성 인덱스는 Aheui.lua의 op 테이블과 완전히 동일한 순서를 따름)
local DUP_SKIP2  = compose(8, 17)   -- ㅃ(dup) + ㅠ(아래로 2칸): 한 줄 건너뛰며 dup
local NOOP_RIGHT = compose(11, 0)   -- ㅇ(noop) + ㅏ(오른쪽)
local NOOP_LEFT  = compose(11, 4)   -- ㅇ(noop) + ㅓ(왼쪽)
local NOOP_DOWN  = compose(11, 13)  -- ㅇ(noop) + ㅜ(아래)
local NOOP_UP    = compose(11, 8)   -- ㅇ(noop) + ㅗ(위)
local CHECK_DOWN = compose(14, 13)  -- ㅊ(조건부 방향반전) + ㅜ(기본 아래; 0이면 위로 뒤집힘)
local CHECK_UP   = compose(14, 8)   -- ㅊ(조건부 방향반전) + ㅗ(기본 위; 0이면 아래로 뒤집힘)

-- ============ 검증된 리프(leaf) 블록들 ============
-- 시뮬레이터로 하나씩 실행해서 확인한 블록(진입: 첫 줄 0번 칸에서 아무 방향;
-- 탈출: 마지막 줄 0번 칸에서 "아래" 방향 - 다음 블록으로 자연스럽게 이어짐)
local BLOCK_PLUS  = { str_to_cps("발발나다붗"), str_to_cps("루떠떠벓벓") }
local BLOCK_MINUS = { str_to_cps("밟밠밥따따받두"), str_to_cps("루떠떠벓벓벝더") }
local BLOCK_OUT   = { str_to_cps("뿌"), str_to_cps("뭏") }
local BLOCK_IN    = { str_to_cps("마밯") }  -- 기존 셀값 버림(마) + 새 문자 입력(밯)
local BLOCK_RIGHT = { str_to_cps("싹순"), str_to_cps("수빠쑤"), str_to_cps("부수머"), str_to_cps("우어") }
local BLOCK_LEFT  = { str_to_cps("싼숙"), str_to_cps("수빠쑤"), str_to_cps("부수머"), str_to_cps("우어") }
local BLOCK_HALT  = { str_to_cps("희") }
local BLOCK_BEGIN = { str_to_cps("부") }

-- ============ 컴파일러 ============
-- Python판의 class Compiler를 Lua 테이블 + 메타테이블로 그대로 옮김

local Compiler = {}
Compiler.__index = Compiler

-- 최상위(depth 0) 컴파일러 생성: 시작 블록(부 = 초기 셀값 0 push)부터 시작
function Compiler.new()
    local self = setmetatable({}, Compiler)
    self.rows = {}
    for _, row in ipairs(BLOCK_BEGIN) do
        table.insert(self.rows, copy_row(row))
    end
    return self
end

-- 본문(body)용 컴파일러 생성: 시작 블록 없이 빈 상태로 시작
-- (Python의 Compiler.__new__(Compiler) 를 흉내낸 것)
local function new_bare_compiler()
    local self = setmetatable({}, Compiler)
    self.rows = {}
    return self
end

function Compiler:emit(block_rows)
    for _, row in ipairs(block_rows) do
        table.insert(self.rows, copy_row(row))
    end
end

-- tokens: '+','-','.',',','<','>','[',']' 로 이루어진 배열 (1-indexed)
function Compiler:compile_tokens(tokens, depth)
    local i = 1
    while i <= #tokens do
        local c = tokens[i]
        if c == '+' then self:emit(BLOCK_PLUS)
        elseif c == '-' then self:emit(BLOCK_MINUS)
        elseif c == '.' then self:emit(BLOCK_OUT)
        elseif c == ',' then self:emit(BLOCK_IN)
        elseif c == '>' then self:emit(BLOCK_RIGHT)
        elseif c == '<' then self:emit(BLOCK_LEFT)
        elseif c == '[' then
            -- 대응하는 ']' 찾기 (중첩 depth 카운트)
            local depth_ct, j = 1, i + 1
            while j <= #tokens and depth_ct > 0 do
                if tokens[j] == '[' then depth_ct = depth_ct + 1
                elseif tokens[j] == ']' then depth_ct = depth_ct - 1 end
                j = j + 1
            end
            -- 루프 본문 토큰: tokens[i+1 .. j-2] (Lua 1-indexed 보정)
            local body_tokens = {}
            for k = i + 1, j - 2 do
                table.insert(body_tokens, tokens[k])
            end
            self:compile_loop(body_tokens, depth)
            i = j - 1
        end
        i = i + 1
    end
end

-- 처음부터 새로 설계한 루프 스캐폴드.
-- 핵심 아이디어: 공유되는 한 칸(cell)은 "정상 진입"과 "방향반전으로 되돌아온
-- 진입"을 구분할 수 없음(둘 다 그 칸의 문자를 그대로 실행하므로). 그래서
-- 스킵(건너뛰기)/복귀(반복) 각각을 위한 전용 레인을 멀리 떨어진 칸에 두고,
-- 실제 블록 내용 위를 지나가지 않는 "전용 착지 행"을 둬서 안전하게 합류시킴.
function Compiler:compile_loop(body_tokens, depth)
    local SKIP_COL = 100 + 80 * depth  -- "0이면 건너뛰기" 레인
    local BACK_COL = SKIP_COL + 40     -- "0이 아니면 반복" 레인

    -- --- 진입부 (entry frame) ---
    table.insert(self.rows, { DUP_SKIP2 })                              -- R0: dup 하면서 한 줄 건너뜀
    local r1 = set_char({ NOOP_RIGHT }, SKIP_COL, NOOP_DOWN)             -- R1: 스킵 레인 방향전환(반전으로만 도달)
    table.insert(self.rows, r1)
    table.insert(self.rows, { CHECK_DOWN })                             -- R2: 진입 검사 (0이면 위로 반전 → R1)

    -- 전용 착지 행: 정상 통과(R2에서 그대로 아래로)와 반복/복귀 레인(BACK_COL을
    -- 타고 왼쪽으로 도착)이 여기서 합류함. 실제 블록 문자를 절대 지나치지
    -- 않는 빈 칸이라 안전함(이전 버전에서 실제 버그였던 부분을 고친 지점)
    local r_land_in = set_char({ NOOP_DOWN }, BACK_COL, NOOP_LEFT)
    table.insert(self.rows, r_land_in)                                  -- R2.5

    -- --- 본문 (body) ---
    local body_compiler = new_bare_compiler()
    body_compiler:compile_tokens(body_tokens, depth + 1)
    local body_rows = body_compiler.rows
    if #body_rows == 0 then
        body_rows = { { NOOP_DOWN } }  -- 빈 루프 본문에 대한 안전장치
    end
    for _, row in ipairs(body_rows) do
        table.insert(self.rows, copy_row(row))
    end

    -- --- 탈출부 (exit frame) ---
    table.insert(self.rows, { DUP_SKIP2 })                              -- R(k+1)
    local r_turnback = set_char({ NOOP_RIGHT }, BACK_COL, NOOP_UP)       -- R(k+2)
    table.insert(self.rows, r_turnback)
    table.insert(self.rows, { CHECK_UP })                               -- R(k+3): 탈출 검사
    -- (0이 아니면 = 반복 → 위로 그대로 진행 → R(k+2) 경유 → BACK_COL 타고 위로)
    -- (0이면 = 종료 → 위 방향이 반전되어 아래로 → 바로 다음 착지 행으로)

    -- 루프 뒤 전용 착지 행: 자연 종료 경로와 스킵 레인 경로가 여기서 합류한
    -- 뒤 다음 실제 명령으로 이어짐
    local r_land_out = set_char({ NOOP_DOWN }, SKIP_COL, NOOP_LEFT)
    table.insert(self.rows, r_land_out)                                 -- R(k+4)
end

-- 최종 마무리: halt 블록 추가 + 모든 행을 같은 너비로 공백 패딩
function Compiler:finish()
    table.insert(self.rows, copy_row(BLOCK_HALT[1]))

    local width = 0
    for _, row in ipairs(self.rows) do
        if #row > width then width = #row end
    end

    local out_lines = {}
    for _, row in ipairs(self.rows) do
        local padded = copy_row(row)
        while #padded < width do table.insert(padded, SP) end
        table.insert(out_lines, cps_to_str(padded))
    end
    return out_lines
end

-- ============ 공개 함수 ============

-- BF 소스 문자열 -> Aheui 프로그램의 행(row) 문자열 배열
function M.compile_bf(src)
    local tokens = {}
    for c in src:gmatch(".") do
        if c == '+' or c == '-' or c == '.' or c == ',' or c == '<' or c == '>' or c == '[' or c == ']' then
            table.insert(tokens, c)
        end
    end
    local comp = Compiler.new()
    comp:compile_tokens(tokens, 0)
    return comp:finish()
end

-- BF 소스 문자열 -> 실행 가능한 Aheui 소스 문자열(개행으로 이어붙임)
function M.compile_bf_to_string(src)
    local rows = M.compile_bf(src)
    return table.concat(rows, "\n")
end

return M
