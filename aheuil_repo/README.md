optomized lua interpreter + defined bf to Aheuilü compiler
compiler use:
```bash
local Aheui     = require("아희")
local BFToAheui = require("뇌")

local bf_code = ... -- your brainfuck code

local aheui_code = BFToAheui.compile(bf_code)

Aheui.load(aheui_code)
local out = Aheui.run()
print(out)
```
