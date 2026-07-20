local hangul = {}

local BASE   = 0xAC00
local N_CH   = 19   -- choseong
local N_JU   = 21   -- jungseong
local N_JO   = 28   -- jongseong

hangul.choseong = {
  "ᄀ","ᄁ","ᄂ","ᄃ","ᄄ","ᄅ","ᄆ","ᄇ","ᄈ",
  "ᄉ","ᄊ","ᄋ","ᄌ","ᄍ","ᄎ","ᄏ","ᄐ","ᄑ","ᄒ"
}

hangul.jungseong = {
  "ᅡ","ᅢ","ᅣ","ᅤ","ᅥ","ᅦ","ᅧ","ᅨ","ᅩ","ᅪ","ᅫ",
  "ᅬ","ᅭ","ᅮ","ᅯ","ᅰ","ᅱ","ᅲ","ᅳ","ᅴ","ᅵ"
}

hangul.jongseong = {
  "",   -- 0 = no batchim
  "ᆨ","ᆩ","ᆪ","ᆫ","ᆬ","ᆭ","ᆮ","ᆯ","ᆰ","ᆱ","ᆲ",
  "ᆳ","ᆴ","ᆵ","ᆶ","ᆷ","ᆸ","ᆹ","ᆺ","ᆻ","ᆼ","ᆽ",
  "ᆾ","ᆿ","ᇀ","ᇁ","ᇂ"
}

function hangul.compose_cp(ch, ju, jo)
  return BASE + ((ch * N_JU) + ju) * N_JO + jo
end

function hangul.decompose_cp(cp)
  local offset = cp - BASE
  if offset < 0 or offset >= N_CH * N_JU * N_JO then
    return nil, nil, nil
  end
  local ch = math.floor(offset / (N_JU * N_JO))
  local rem = offset % (N_JU * N_JO)
  local ju = math.floor(rem / N_JO)
  local jo = rem % N_JO
  return ch, ju, jo
end

function hangul.lattice_19(cp)
  local ch, ju, jo = hangul.decompose_cp(cp)
  if not ch then return nil end

  -- Use the internal syllable index as a generator for the lattice.
  local n = ((ch * N_JU) + ju) * N_JO + jo  -- 0 .. (19*21*28-1)
  local edo19 = n % 19

  -- Example “half‑flat” collapse: treat positions 9 and 10 as non‑primitive.
  local primitive = (edo19 ~= 9 and edo19 ~= 10)

  return edo19, primitive
end

function hangul.describe_cp(cp)
  local ch, ju, jo = hangul.decompose_cp(cp)
  if not ch then
    return string.format("U+%04X: not a Hangul syllable", cp)
  end
  local edo19, primitive = hangul.lattice_19(cp)
  local ch_jamo = hangul.choseong[ch+1]
  local ju_jamo = hangul.jungseong[ju+1]
  local jo_jamo = hangul.jongseong[jo+1]
  return string.format(
    "U+%04X: [%s][%s][%s] -> edo19=%d, primitive=%s",
    cp, ch_jamo, ju_jamo, jo_jamo, edo19, primitive and "true" or "false"
  )
end

return hangul
