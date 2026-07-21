local hangul = require("律")

local Aheui = {}

local STROKES = {
    [0] = 0, [1] = 2, [2] = 4, [3] = 4, [4] = 2, [5] = 5, [6] = 5, [7] = 3,
    [8] = 5, [9] = 7, [10] = 9, [11] = 9, [12] = 7, [13] = 9, [14] = 9, [15] = 8,
    [16] = 4, [17] = 4, [18] = 6, [19] = 2, [20] = 4, [21] = 0, [22] = 3, [23] = 4,
    [24] = 3, [25] = 4, [26] = 4, [27] = 0
}

local storage = {}
local current_storage_idx = 0
local code = {}
local x, y = 0, 0
local dx, dy = 1, 0
local halted = false

local output_buffer = {}
local input_buffer = {}
local input_ptr = 1

local function reset_storage()
    storage = {}
    for i = 0, 27 do
        storage[i] = {}
    end
    current_storage_idx = 0
end

local function push(i, n)
    if i == 27 then return end -- ㅎ acts as discard/no-op storage
    table.insert(storage[i], n)
end

local function pop(i)
    if i == 27 then return nil end
    if i == 21 then
        -- queue ㅇ: pop from the front
        if #storage[i] == 0 then return nil end
        local v = storage[i][1]
        table.remove(storage[i], 1)
        return v
    else
        -- stack: pop from the end
        if #storage[i] == 0 then return nil end
        return table.remove(storage[i])
    end
end

local function get_input_num()
    if input_ptr <= #input_buffer then
        local val = input_buffer[input_ptr]
        input_ptr = input_ptr + 1
        return tonumber(val) or 0
    end
    io.write("Input number: ")
    local line = io.read("*l")
    return tonumber(line) or 0
end

local function get_input_char()
    if input_ptr <= #input_buffer then
        local val = input_buffer[input_ptr]
        input_ptr = input_ptr + 1
        if type(val) == "string" then
            return utf8.codepoint(val) or 0
        else
            return tonumber(val) or 0
        end
    end
    io.write("Input char: ")
    local line = io.read("*l")
    if not line or line == "" then return 0 end
    return utf8.codepoint(line) or 0
end

local function move_ptr()
    x = x + dx
    y = y + dy

    if y < 0 then y = #code - 1 end
    if y >= #code then y = 0 end

    local row = code[y + 1]
    if not row or #row == 0 then
        x = 0
    else
        if x < 0 then x = #row - 1 end
        if x >= #row then x = 0 end
    end
end

function Aheui.load(text)
    code = {}
    for line in text:gmatch("[^\r\n]+") do
        local row = {}
        for _, cp in utf8.codes(line) do
            table.insert(row, cp)
        end
        table.insert(code, row)
    end
    reset_storage()
    x, y = 0, 0
    dx, dy = 1, 0
    halted = false
    output_buffer = {}
    input_buffer = {}
    input_ptr = 1
end

function Aheui.set_input(inputs)
    input_buffer = inputs
    input_ptr = 1
end

function Aheui.get_output()
    return table.concat(output_buffer)
end

function Aheui.get_state()
    local copy_storage = {}
    for i = 0, 27 do
        local stack_copy = {}
        for j = 1, #storage[i] do
            stack_copy[j] = storage[i][j]
        end
        copy_storage[i] = stack_copy
    end
    return {
        x = x,
        y = y,
        dx = dx,
        dy = dy,
        halted = halted,
        current_storage = current_storage_idx,
        storage = copy_storage
    }
end

function Aheui.step()
    if halted then return end

    local row = code[y + 1]
    if not row or #row == 0 then
        move_ptr()
        return
    end

    local cp = row[x + 1]
    if not cp then
        move_ptr()
        return
    end

    local ch, ju, jo = hangul.decompose_cp(cp)
    if not ch then
        move_ptr()
        return
    end

    -- Direction update based on vowel (jungseong)
    if ju == 0 then dx, dy = 1, 0       -- ㅏ
    elseif ju == 2 then dx, dy = 2, 0   -- ㅑ
    elseif ju == 4 then dx, dy = -1, 0  -- ㅓ
    elseif ju == 6 then dx, dy = -2, 0  -- ㅕ
    elseif ju == 8 then dx, dy = 0, -1  -- ㅗ
    elseif ju == 12 then dx, dy = 0, -2 -- ㅛ
    elseif ju == 13 then dx, dy = 0, 1  -- ㅜ
    elseif ju == 17 then dx, dy = 0, 2  -- ㅠ
    elseif ju == 18 then dy = -dy       -- ㅡ
    elseif ju == 19 then dx, dy = -dx, -dy -- ㅢ
    elseif ju == 20 then dx = -dx       -- ㅣ
    end

    local op = ch
    local idx = jo

    -- Op execution
    local success = true

    if op == 0 then
        -- ㄱ: no-op
    elseif op == 1 then
        -- ㄲ: no-op
    elseif op == 2 then
        -- ㄴ: divide (pop a, pop b, push b / a)
        local a = pop(current_storage_idx)
        local b = pop(current_storage_idx)
        if a and b and a ~= 0 then
            push(current_storage_idx, math.floor(b / a))
        else
            if a then push(current_storage_idx, a) end
            if b then push(current_storage_idx, b) end
            success = false
        end
    elseif op == 3 then
        -- ㄷ: add
        local a = pop(current_storage_idx)
        local b = pop(current_storage_idx)
        if a and b then
            push(current_storage_idx, b + a)
        else
            if a then push(current_storage_idx, a) end
            if b then push(current_storage_idx, b) end
            success = false
        end
    elseif op == 4 then
        -- ㄸ: multiply
        local a = pop(current_storage_idx)
        local b = pop(current_storage_idx)
        if a and b then
            push(current_storage_idx, b * a)
        else
            if a then push(current_storage_idx, a) end
            if b then push(current_storage_idx, b) end
            success = false
        end
    elseif op == 5 then
        -- ㄹ: modulo
        local a = pop(current_storage_idx)
        local b = pop(current_storage_idx)
        if a and b and a ~= 0 then
            push(current_storage_idx, b % a)
        else
            if a then push(current_storage_idx, a) end
            if b then push(current_storage_idx, b) end
            success = false
        end
    elseif op == 6 then
        -- ㅁ: pop and print or discard
        local a = pop(current_storage_idx)
        if a then
            if idx == 21 then
                -- ㅇ: output as integer
                table.insert(output_buffer, tostring(a))
            elseif idx == 27 then
                -- ㅎ: output as UTF-8 character
                table.insert(output_buffer, utf8.char(a))
            end
        else
            success = false
        end
    elseif op == 7 then
        -- ㅂ: push
        if idx == 21 then
            -- ㅇ: read integer
            local num = get_input_num()
            push(current_storage_idx, num)
        elseif idx == 27 then
            -- ㅎ: read character
            local cp_in = get_input_char()
            push(current_storage_idx, cp_in)
        else
            -- push stroke count
            push(current_storage_idx, STROKES[idx])
        end
    elseif op == 8 then
        -- ㅃ: duplicate
        local a = pop(current_storage_idx)
        if a then
            push(current_storage_idx, a)
            push(current_storage_idx, a)
        else
            success = false
        end
    elseif op == 9 then
        -- ㅅ: select storage
        current_storage_idx = idx
    elseif op == 10 then
        -- ㅆ: move from current storage to storage `idx`
        local a = pop(current_storage_idx)
        if a then
            push(idx, a)
        else
            success = false
        end
    elseif op == 11 then
        -- ㅇ: no-op
    elseif op == 12 then
        -- ㅈ: compare (pop a, pop b, push b >= a and 1 or 0)
        local a = pop(current_storage_idx)
        local b = pop(current_storage_idx)
        if a and b then
            push(current_storage_idx, (b >= a) and 1 or 0)
        else
            if a then push(current_storage_idx, a) end
            if b then push(current_storage_idx, b) end
            success = false
        end
    elseif op == 13 then
        -- ㅉ: no-op
    elseif op == 14 then
        -- ㅊ: conditional (pop a, if a == 0 reverse direction)
        local a = pop(current_storage_idx)
        if a then
            if a == 0 then
                dx, dy = -dx, -dy
            end
        else
            success = false
        end
    elseif op == 15 then
        -- ㅋ: swap
        local a = pop(current_storage_idx)
        local b = pop(current_storage_idx)
        if a and b then
            push(current_storage_idx, a)
            push(current_storage_idx, b)
        else
            if a then push(current_storage_idx, a) end
            if b then push(current_storage_idx, b) end
            success = false
        end
    elseif op == 16 then
        -- ㅌ: subtract
        local a = pop(current_storage_idx)
        local b = pop(current_storage_idx)
        if a and b then
            push(current_storage_idx, b - a)
        else
            if a then push(current_storage_idx, a) end
            if b then push(current_storage_idx, b) end
            success = false
        end
    elseif op == 17 then
        -- ㅍ: copy from current storage to storage `idx`
        local a = pop(current_storage_idx)
        if a then
            push(current_storage_idx, a) -- push back to current
            push(idx, a) -- push to target
        else
            success = false
        end
    elseif op == 18 then
        -- ㅎ: halt
        halted = true
    end

    if not success then
        -- If an operation fails, reverse direction!
        dx, dy = -dx, -dy
    end

    move_ptr()
end

function Aheui.run()
    local limit = 1000000 -- safeguard
    local steps = 0
    while not halted and steps < limit do
        Aheui.step()
        steps = steps + 1
    end
    return Aheui.get_output()
end

return Aheui
