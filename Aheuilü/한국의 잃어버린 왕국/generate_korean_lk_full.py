"""
generate_korean_lk_full.py
Renders the Korean parody page at 1067×1303 (matching the original
Lost Kingdom BF page dimensions) with enough body content to fill the height.
All Korean text is original parody content.
"""

from PIL import Image, ImageDraw, ImageFont

SANS   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SANS_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF  = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
MONO   = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

# ── target dimensions (match original) ──────────────────────────────────────
W, H = 1067, 1500

# ── palette ─────────────────────────────────────────────────────────────────
BG         = (250, 250, 248)
SIDEBAR_BG = (235, 235, 228)
BORDER     = (185, 185, 170)
LINK       = (0,   0,   180)
HEADING    = (20,  20,  20 )
BODY_COL   = (40,  40,  40 )
RULE       = (165, 165, 150)
NAV_HEAD   = (15,  15,  110)
CODE_BG    = (222, 222, 216)
HDR_BG     = (215, 215, 205)
FOOTER_COL = (100, 100, 100)

def fnt(path, size):
    return ImageFont.truetype(path, size)

f_site  = fnt(SANS_B,  22)
f_nav_h = fnt(SANS_B,  14)
f_nav   = fnt(SANS,    13)
f_title = fnt(SERIF,   28)
f_sub   = fnt(MONO,    12)
f_body  = fnt(SANS,    14)
f_mono  = fnt(MONO,    12)
f_small = fnt(SANS,    12)

SIDEBAR_W = 170
CX        = SIDEBAR_W + 28   # content left edge
CW        = W - CX - 24      # content width

# ── navigation ──────────────────────────────────────────────────────────────
NAV = [
    ("아희",        ["기사", "문법", "역사"]),
    ("BBC 베이직",  ["기사", "라이브러리", "소프트웨어"]),
    ("리스크 OS",   ["소프트웨어"]),
    ("윈도우",      ["소프트웨어"]),
    ("인터랙티브 픽션", ["게임", "알림", "지도", "지금 플레이"]),
    ("브레인퍽",    ["기사", "게임", "도구"]),
    ("게이밍",      ["디아블로 (전체)", "PSO"]),
    ("뉴스",        []),
    ("사이트맵",    []),
]

# ── body text ────────────────────────────────────────────────────────────────
HEADER_BLOCK = (
    "잃어버린 왕국\n"
    "(C) 김철수 2004, 2005\n"
    "아희 에디션 v0.11"
)

PARAS = [
    ("잃어버린 왕국은 2004년 제1회 클래식 2k 텍스트 어드벤처 대회에서 우승한 원작 게임을 "
     "아희(아희 프로그래밍 언어)로 변환한 작품입니다. 원작은 고도로 최적화된 BBC BASIC으로 "
     "작성되었으며 크기는 2.74Kb에 불과했습니다. 이 아희 에디션은 상당히 커졌습니다."),

    ("원작은 리스크 OS, 윈도우, 에이콘 8비트 컴퓨터에서 실행되었습니다. 이 아희 에디션은 "
     "적절한 아희 인터프리터 또는 컴파일러가 있는 모든 컴퓨터에서 실행될 수 있습니다."),

    ("이 버전을 원작에 최대한 가깝게 변환하려 노력했습니다. 아희 에디션의 해법은 원작과 "
     "약간 다를 수 있습니다. 방 설명과 일부 메시지가 변경되었으며 2.8Kb 크기 제한 없이 "
     "새로운 기능이 추가되었습니다."),

    ("짧은 방 설명 모드와 긴 방 설명 모드 두 가지를 제공합니다. 짧은 모드가 원작에 가장 "
     "가깝습니다. 긴 방 설명 버전은 특별히 강화되었으며 본질적으로 별도의 게임입니다. "
     "두 버전의 해법은 서로 다릅니다."),

    ("이 게임은 아마도 아희로 작성된 최초의 진정한 인터랙티브 픽션입니다. 아마도 아희로 "
     "작성된 가장 큰 프로그램일 것입니다."),

    ("잃어버린 왕국을 플레이하려면 아희 인터프리터가 필요합니다. 고도로 이식 가능한 최적화 "
     "인터프리터의 소스 코드가 bftools 디렉토리에 포함되어 있습니다. 인터프리터 'bf'는 "
     "리스크 OS, 윈도우, DOS, 리눅스, 솔라리스, 맥 OS X에서 동작하는 것이 확인되었습니다. "
     "대부분의 시스템에서 동작할 것입니다. 인터프리터를 컴파일하려면 C 컴파일러가 필요합니다."),

    ("제공된 인터프리터를 사용할 것을 강력히 권장합니다. 그렇지 않으면 게임 경험이 "
     "최상의 성능을 발휘하지 못할 수 있습니다."),

    ("윈도우용 인터프리터 버전 'bf.exe'가 제공됩니다. 윈도우를 사용하는 경우 구글리 눈을 "
     "가진 'LostKng.exe'를 더블 클릭하여 게임을 실행할 수 있습니다."),

    ("게임 내에 백스토리와 플레이 방법에 대한 정보가 포함된 전체 문서가 함께 제공됩니다."),

    ("파서는 다소 제한적이지만 매우 기능적입니다. 더 나은 파서는 먼 미래에 구현될 수 있으며, "
     "아마도 향후 프로젝트에서 실현될 것입니다. 이것은 첫 번째 릴리스에는 계획되지 않았는데, "
     "아희에서 적절한 파서를 코딩하는 것이 쉽지 않기 때문입니다."),

    ("이 게임에 대한 리뷰를 작성하신다면 사본을 보내주시면 감사하겠습니다. 허락하신다면 "
     "웹사이트에 포함시키겠습니다. 모든 댓글, 제안, 건설적인 비평을 환영합니다."),

    ("이 게임을 플레이한 모든 분의 소식을 듣고 싶습니다."),
]

CREDITS_BLOCK = (
    "크레딧\n\n"
    "다음 분들께 감사드립니다:\n"
    "  김영희 (http://hangul-lang.kr)\n"
    "  이민준 (http://aheui.github.io)\n"
    "  박서연 (웹사이트 없음)\n"
    "  최도윤 aka 워리어 (http://nostalgia8.org)\n\n"
    "특별 감사:\n"
    "  이 프로젝트 없이는 훨씬 빈약했을 분께\n"
    "  아희 없이는 불가능했을 분께"
)


def wrap(text, fnt_obj, max_w, draw):
    lines = []
    for para in text.split('\n'):
        words = para.split()
        if not words:
            lines.append('')
            continue
        line = ''
        for w in words:
            test = (line + ' ' + w).strip()
            bb = draw.textbbox((0, 0), test, font=fnt_obj)
            if bb[2] - bb[0] <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
    return lines


def generate(out_path):
    im = Image.new('RGB', (W, H), BG)
    d  = ImageDraw.Draw(im)

    # ── header bar ───────────────────────────────────────────────────────────
    d.rectangle([(0, 0), (W, 44)], fill=HDR_BG)
    d.line([(0, 44), (W, 44)], fill=BORDER, width=1)
    d.text((14, 10), "김철수닷컴", font=f_site, fill=NAV_HEAD)

    # ── sidebar ──────────────────────────────────────────────────────────────
    d.rectangle([(0, 45), (SIDEBAR_W, H - 22)], fill=SIDEBAR_BG)
    d.line([(SIDEBAR_W, 45), (SIDEBAR_W, H - 22)], fill=BORDER, width=1)

    sy = 58
    for group, items in NAV:
        d.text((8, sy), group, font=f_nav_h, fill=NAV_HEAD)
        sy += 20
        for item in items:
            d.text((18, sy), item, font=f_nav, fill=LINK)
            sy += 17
        sy += 8

    # ── content ──────────────────────────────────────────────────────────────
    cy = 62

    # title + subheading
    d.text((CX, cy), "잃어버린 왕국 아희 에디션", font=f_title, fill=HEADING)
    cy += 38
    d.text((CX, cy),
           "v0.11  2025년 1월 (115k)  *** 세계 최초 아희 텍스트 어드벤처 ***",
           font=f_sub, fill=BODY_COL)
    cy += 22
    d.line([(CX, cy), (W - 18, cy)], fill=RULE, width=1)
    cy += 14

    # monospace header block
    d.rectangle([(CX - 4, cy - 2), (W - 18, cy + 50)], fill=CODE_BG)
    for line in HEADER_BLOCK.split('\n'):
        d.text((CX, cy), line, font=f_mono, fill=BODY_COL)
        cy += 15
    cy += 12

    # body paragraphs
    for para in PARAS:
        for line in wrap(para, f_body, CW, d):
            d.text((CX, cy), line, font=f_body, fill=BODY_COL)
            cy += 19
        cy += 8

    # credits block
    cy += 4
    d.rectangle([(CX - 4, cy - 2), (W - 18, cy + 130)], fill=CODE_BG)
    for line in CREDITS_BLOCK.split('\n'):
        d.text((CX, cy), line, font=f_mono, fill=BODY_COL)
        cy += 15

    # ── footer ───────────────────────────────────────────────────────────────
    d.line([(0, H - 22), (W, H - 22)], fill=BORDER, width=1)
    d.text((8, H - 18), "© 김철수닷컴 2004-2025", font=f_small, fill=FOOTER_COL)

    im.save(out_path)
    print(f"saved {out_path}  {W}×{H}  capacity={W*H*3:,} bytes")
    return im


if __name__ == '__main__':
    generate('/home/claude/korean_lk_full.png')
