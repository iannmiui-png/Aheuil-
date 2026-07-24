"""
Romanized-pronunciation tables for Aheui syllables, plus a parser that
recovers (choseong, jungseong, jongseong) indices from an English-spelled
token like "bat", "mang", "cho", "chu".

Spelling is Revised-Romanization-flavored but chosen for BIJECTIVITY
(so parsing round-trips cleanly) rather than strict phonetic accuracy —
in particular jongseong ㅅ is spelled "s" (not the phonetically-neutralized
"t") to avoid colliding with ㄷ's "t", since both would otherwise sound
identical in real speech but need to stay distinguishable here.
"""

CHO_ROMAN = ["g","kk","n","d","tt","r","m","b","pp","s","ss","","j","jj","ch","k","t","p","h"]
JUNG_ROMAN = ["a","ae","ya","yae","eo","e","yeo","ye","o","wa","wae","oe","yo","u","wo","we","wi","yu","eu","ui","i"]
JONG_ROMAN = ["","k","kk","ks","n","nj","nh","t","l","lg","lm","lb","ls","lt","lp","lh",
              "m","p","bs","s","ss","ng","j","ch","kh","th","ph","h"]

assert len(CHO_ROMAN) == 19
assert len(JUNG_ROMAN) == 21
assert len(JONG_ROMAN) == 28

_JONG_LOOKUP = {s: i for i, s in enumerate(JONG_ROMAN)}


def parse_syllable(token):
    """token -> (cho_idx, jung_idx, jong_idx), or raises ValueError."""
    token = token.lower()

    # initial consonant: longest matching prefix; default to ㅇ (silent) if none
    cho_idx, best_len = None, -1
    for idx, spelling in enumerate(CHO_ROMAN):
        if spelling and token.startswith(spelling) and len(spelling) > best_len:
            cho_idx, best_len = idx, len(spelling)
    if cho_idx is None:
        cho_idx, consumed = 11, 0
    else:
        consumed = best_len
    rest = token[consumed:]

    # vowel: longest matching prefix of what's left
    jung_idx, best_len = None, -1
    for idx, spelling in enumerate(JUNG_ROMAN):
        if rest.startswith(spelling) and len(spelling) > best_len:
            jung_idx, best_len = idx, len(spelling)
    if jung_idx is None:
        raise ValueError(f"cannot parse vowel in token {token!r} (after initial, left with {rest!r})")
    rest2 = rest[best_len:]

    # final consonant: whatever's left must exactly match a jongseong spelling
    if rest2 not in _JONG_LOOKUP:
        raise ValueError(f"cannot parse final consonant in token {token!r} (leftover {rest2!r})")
    jong_idx = _JONG_LOOKUP[rest2]

    return cho_idx, jung_idx, jong_idx


def spell_syllable(cho_idx, jung_idx, jong_idx):
    """Inverse of parse_syllable, for round-trip checking / pretty-printing."""
    return CHO_ROMAN[cho_idx] + JUNG_ROMAN[jung_idx] + JONG_ROMAN[jong_idx]
