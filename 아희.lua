local hangul = require("律")

local Aheui = {}

local storage = {}
for i = 0, 27 do storage[i] = {} end

local x, y = 0, 0
local dx, dy = 1, 0
local halted = false

local code = {}

local function push(i, n)
    if i == 27 then return end -- ㅎ = no-op
    table.insert(storage[i], n)
end

local function pop(i)
    if i == 21 then
        -- ㅇ = queue
        local v = storage[i][1]
        table.remove(storage[i], 1)
        return v
    elseif i == 27 then
        return nil
    else
        return table.remove(storage[i])
    end
end

local function move()
    x = x + dx
    y = y + dy

    if y < 0 then y = #code - 1 end
    if y >= #code then y = 0 end

    local row = code[y]
    if x < 0 then x = #row - 1 end
    if x >= #row then x = 0 end
end

function Aheui.step()
    if halted then return end

    local row = code[y]
    local char = row:sub(x+1, x+2) -- UTF-8 safe enough for Hangul

    local cp = utf8.codepoint(char)
    if not cp then move(); return end

    local ch, ju, jo = hangul.decompose_cp(cp)
    if not ch then move(); return end

    if ju == 0 then dx, dy = 1, 0
    elseif ju == 2 then dx, dy = 2, 0
    elseif ju == 4 then dx, dy = -1, 0
    elseif ju == 6 then dx, dy = -2, 0
    elseif ju == 8 then dx, dy = 0, -1
    elseif ju == 12 then dx, dy = 0, -2
    elseif ju == 13 then dx, dy = 0, 1
    elseif ju == 17 then dx, dy = 0, 2
    elseif ju == 18 then dy = -dy
    elseif ju == 19 then dx, dy = -dx, -dy
    elseif ju == 20 then dx = -dx
    end

    local op = ch
    local idx = jo

    if op == 3 then
        local a = pop(idx)
        local b = pop(idx)
        push(idx, b + a)

    elseif op == 4 then
        local a = pop(idx)
        local b = pop(idx)
        push(idx, b * a)

    elseif op == 5 then
        local a = pop(idx)
        local b = pop(idx)
        push(idx, b % a)

    elseif op == 12 then
        local a = pop(idx)
        local b = pop(idx)
        push(idx, (b >= a) and 1 or 0)

    elseif op == 14 then
        if pop(idx) == 0 then dx, dy = -dx, -dy end

    elseif op == 18 then
        halted = true
    end

    move()
end

function Aheui.load(text)
    code = {}
    for line in text:gmatch("[^\n]+") do
        table.insert(code, line)
    end
    x, y = 0, 0
    dx, dy = 1, 0
    halted = false
end

return Aheui
