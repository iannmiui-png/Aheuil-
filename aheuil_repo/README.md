optomized lua interpreter + defined bf to Aheuilü compiler
compiler use:
```bash
local Aheui     = require("아희")
local BFToAheui = require("bf_to_aheui")

local bf_code = ... -- your stegfuck-decoded Lost Kingdom BF

local aheui_code = BFToAheui.compile(bf_code)

Aheui.load(aheui_code)
local out = Aheui.run()
print(out)
```
