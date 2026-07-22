-- bf_to_aheui.lua
local hangul = require("律")

-- Choseong indices (from your interpreter):
-- 3  = ㄷ (add)
-- 7  = ㅂ (push)
-- 9  = ㅅ (select storage)
-- 14 = ㅊ (conditional)
-- 16 = ㅌ (subtract)
-- 18 = ㅎ (halt)
-- 6  = ㅁ (pop/output)

local BFToAheui = {}

-- Simple 1D grid: we’ll emit a single row of syllables.
-- You can extend this to 2D if you want more elaborate loop geometry.

local function syllable(ch, ju, jo)
    return utf8.char(hangul.compose_cp(ch, ju, jo))
end

-- Storage model:
-- We treat BF cells as Aheui storages 0..N.
-- Pointer movement >/< becomes ㅅ with appropriate jongseong index.
local function compile(bf_src, max_cells)
    max_cells = max_cells or 10  -- you can raise this

    local out = {}
    local ptr = 0  -- current BF cell index, maps to current_storage_idx

    -- Helper: select storage (BF pointer move)
    local function select_storage(idx)
        -- ㅅ (ch=9), jongseong = idx
        table.insert(out, syllable(9, 0, idx))
        ptr = idx
    end

    -- Helper: increment current cell
    local function bf_inc()
        -- You’ll want to tune this to your numeric encoding.
        -- Minimal placeholder: push some constant then add.
        -- ㅂ (ch=7, jo=1) -> STROKES[1] = 2
        -- ㄷ (ch=3)       -> add
        table.insert(out, syllable(7, 0, 1))  -- push 2
        table.insert(out, syllable(3, 0, 0))  -- add
    end

    -- Helper: decrement current cell
    local function bf_dec()
        -- ㅂ (ch=7, jo=1) -> push 2
        -- ㅌ (ch=16)      -> subtract
        table.insert(out, syllable(7, 0, 1))  -- push 2
        table.insert(out, syllable(16, 0, 0)) -- subtract
    end

    -- Helper: output current cell as char
    local function bf_out()
        -- ㅁ (ch=6) with jongseong 27 (ㅎ) -> output UTF-8 char
        table.insert(out, syllable(6, 0, 27))
    end

    -- Helper: input char into current cell
    local function bf_in()
        -- ㅂ (ch=7) with jongseong 27 (ㅎ) -> read char
        table.insert(out, syllable(7, 0, 27))
    end

    -- Loop handling:
    -- We’ll do a simple structural mapping:
    -- [ -> conditional ㅊ that reverses direction if zero
    -- ] -> movement vowel that brings us back.
    --
    -- For a 1D row, this is limited, but it gives you a working skeleton
    -- you can extend into a 2D grid later.

    local loop_stack = {}
    local loop_pos   = {}

    for i = 1, #bf_src do
        local c = bf_src:sub(i, i)

        if c == "+" then
            bf_inc()

        elseif c == "-" then
            bf_dec()

        elseif c == ">" then
            if ptr + 1 > max_cells then
                error("BF pointer moved beyond max_cells")
            end
            select_storage(ptr + 1)

        elseif c == "<" then
            if ptr - 1 < 0 then
                error("BF pointer moved below 0")
            end
            select_storage(ptr - 1)

        elseif c == "." then
            bf_out()

        elseif c == "," then
            bf_in()

        elseif c == "[" then
            -- Record position of loop start in output
            table.insert(loop_stack, #out + 1)
            table.insert(out, syllable(14, 0, 0)) -- ㅊ conditional (placeholder)

        elseif c == "]" then
            local start = table.remove(loop_stack)
            if not start then
                error("Unmatched ] at position " .. i)
            end
            local end_pos = #out + 1

            -- For now, we just emit a movement syllable as a marker.
            -- You can later replace this with a proper 2D jump using vowels.
            table.insert(out, syllable(0, 0, 0)) -- ㄱ no-op, placeholder

            loop_pos[#loop_pos + 1] = {start = start, ["end"] = end_pos}
        end
    end

    if #loop_stack > 0 then
        error("Unmatched [ in BF source")
    end

    -- Terminate: ㅎ
    table.insert(out, syllable(18, 0, 0))

    return table.concat(out)
end

BFToAheui.compile = compile

return BFToAheui
