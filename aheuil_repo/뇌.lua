local hangul = require("律")

local function emit_syllable(ch, ju, jo)
    return utf8.char(hangul.compose_cp(ch, ju, jo))
end

local function bf_to_aheui(bf)
    local grid = {}
    local x = 1

    local function put(ch, ju, jo)
        grid[x] = emit_syllable(ch, ju, jo)
        x = x + 1
    end

    for i = 1, #bf do
        local c = bf:sub(i, i)
        if c == "+" then
            -- example: push constant then add
            -- ㅂ (ch=7), some jo; then ㄷ (ch=3)
            put(7, 0, 2)  -- placeholder
            put(3, 0, 0)
        elseif c == "-" then
            put(7, 0, 2)
            put(16, 0, 0)
        elseif c == ">" then
            -- storage select: ㅅ (ch=9), jo = next index
            put(9, 0, 1)  -- placeholder
        elseif c == "<" then
            put(9, 0, 0)  -- placeholder
        elseif c == "." then
            -- ㅁ with jongseong ㅇ (21) for integer output
            put(6, 0, 21)
        elseif c == "," then
            -- ㅂ with jongseong 21/27 for input
            put(7, 0, 21)
        elseif c == "[" then
            -- loop entry: ㅊ with movement vowel
            put(14, 8, 0) -- placeholder
        elseif c == "]" then
            -- loop back: movement vowel
            put(0, 13, 0) -- placeholder
        end
    end

    -- terminate
    put(18, 0, 0) -- ㅎ

    return table.concat(grid)
end
