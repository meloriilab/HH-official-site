"""スタッフツールの窓口（/api/read/catalog）から、サイトに出す中身を取り込む。
- 野鳥のテキスト → tools/birds.json（2026-11-16、航のスレッドと合意）
- 鳥の和名・年齢・身長・誕生日・趣味・好きなもの・苦手なもの・#タグ → tools/pages_data.json
  （2026-11-17 Kさんの回答：食い違いはスタッフツールが正しい。今後はスタッフツールから自動で取り込む）
メンバーの色（"pill"）は、スタッフツールの色が変わった人だけ、pill_color の決め方で選び直す（2026-11-17 Kさんの回答 Q9：今の色のままでよい）。
今の色は、この決め方ができる前に1人ずつ選んだもので、決め方と少し違う人もいる（菊井律はメインの灰色のまま、など）。変わっていない人は触らない。
窓口で空の欄は、今のサイトの中身を残す。
使い方：python3 tools/sync_staff.py  →  そのあと build_top.py / build_pages.py"""
import json, os, re, subprocess
HERE = os.path.dirname(__file__)
UNIT = {"BVH": "blc"}   # スタッフツールのユニット記号と、サイトの記号が違うもの
raw = subprocess.run(["curl", "-sSf", "https://staff.humming-hearts.com/api/read/catalog"], capture_output=True, text=True, check=True).stdout
cat = json.loads(raw)

def key(c):
    m = re.fullmatch(r"([A-Z]+)-(\d+)", str(c.get("id", "")))
    return f'{UNIT.get(m[1], m[1].lower())}{int(m[2]):02d}' if m else None

def bday(s):   # 「3/31」→「3月31日」（サイトの書き方）
    m = re.fullmatch(r"\s*(\d{1,2})\s*/\s*(\d{1,2})\s*", str(s or ""))
    return f"{int(m[1])}月{int(m[2])}日" if m else None


def _lin(x): return x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4
def _gam(x): return 12.92 * x if x <= .0031308 else 1.055 * x ** (1 / 2.4) - .055
def oklch(h):
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l = (.4122214708 * r + .5363325363 * g + .0514459929 * b) ** (1 / 3); m = (.2119034982 * r + .6806995451 * g + .1073969566 * b) ** (1 / 3); q = (.0883024619 * r + .2817188376 * g + .6299787005 * b) ** (1 / 3)
    L = .2104542553 * l + .7936177850 * m - .0040720468 * q; A = 1.9779984951 * l - 2.4285922050 * m + .4505937099 * q; B = .0259040371 * l + .7827717662 * m - .8086757660 * q
    return L, A, B
def to_hex(L, A, B):
    l = (L + .3963377774 * A + .2158037573 * B) ** 3; m = (L - .1055613458 * A - .0638541728 * B) ** 3; q = (L - .0894841775 * A - 1.2914855480 * B) ** 3
    rgb = (4.0767416621 * l - 3.3077115913 * m + .2309699292 * q, -1.2684380046 * l + 2.6097574011 * m - .3413193965 * q, -.0041960863 * l - .7034186147 * m + 1.7076147010 * q)
    return "#" + "".join(f"{round(min(1, max(0, _gam(min(1, max(0, v))))) * 255):02X}" for v in rgb)
def pill_color(main, sub, accent):
    """名前の札の色の決め方（2026-11-17）。
    1. スタッフツールのメインカラーを使う
    2. メインが黒・灰色に近い（色みが 0.05 未満）なら、黒い札が並んで見分けられなくなるので、サブとアクセントのうち色みが強い方を使う（メインより色みがあるときだけ）
    3. 明るすぎて白い文字が読めない色（明るさ 0.72〜0.9）は、色みを保ったまま明るさ 0.62 まで暗くする。とても明るい色（0.9 以上）は、そのまま黒い文字にする"""
    def C(h): L, A, B = oklch(h); return (A * A + B * B) ** .5
    pick = main
    if C(main) < .05:
        alt = max((sub, accent), key=C)
        if C(alt) > C(main): pick = alt
    L, A, B = oklch(pick)
    return to_hex(.62, A, B) if .72 < L < .9 else pick.upper()

changed = []
# 野鳥のテキスト
PB = os.path.join(HERE, "birds.json"); B = json.load(open(PB))
for c in cat.get("characters", []):
    k, sb = key(c), c.get("siteBird") or {}
    if not k or not sb or k not in B: continue   # サイトにページが無いキャラは飛ばす
    if B[k] != sb: changed.append(f"{k}の鳥")
    B[k] = sb
json.dump(B, open(PB, "w"), ensure_ascii=False, indent=1)

# プロフィール
PD = os.path.join(HERE, "pages_data.json"); D = json.load(open(PD))
S = {key(c): c for c in cat.get("characters", []) if key(c)}
for c in D["chars"]:
    s = S.get(c["id"].lower())
    if not s: continue
    new = {"motif": s.get("bird") or None,
           "age": s.get("age") if isinstance(s.get("age"), int) else None,
           "height": s.get("height") if isinstance(s.get("height"), int) else None,
           "birthday": bday(s.get("bday")),
           "hobby": [h.strip() for h in s["hobby"] if h.strip()] if isinstance(s.get("hobby"), list) and s["hobby"] else None,
           "like": (s.get("fav") or "").strip() or None,
           "dislike": (s.get("weak") or "").strip() or None,
           "tags": [t.strip().lstrip("#") for t in s["siteTags"] if t.strip()] if s.get("siteTags") else None}
    for f, v in new.items():
        if v is None or c.get(f) == v: continue
        changed.append(f'{c["id"]}の{f} {c.get(f)}→{v}'); c[f] = v
    cols = {"main": (s.get("mainColor") or "").lower(), "sub": (s.get("subColor") or "").lower(), "accent": (s.get("accentColor") or "").lower()}
    if all(cols.values()) and c.get("pillFrom") != cols:   # スタッフツールで色が変わった人だけ選び直す
        new_pill = pill_color(cols["main"], cols["sub"], cols["accent"])
        changed.append(f'{c["id"]}の色 {c.get("pill")}→{new_pill}（スタッフツールの色が変わったため。画面で確かめること）')
        c["pill"], c["pillFrom"] = new_pill, cols
json.dump(D, open(PD, "w"), ensure_ascii=False, indent=1)
print("updated:", "\n ".join(changed) or "なし")
