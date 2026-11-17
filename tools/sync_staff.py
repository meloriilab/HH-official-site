"""スタッフツールの窓口（/api/read/catalog）から、サイトに出す中身を取り込む。
- 野鳥のテキスト → tools/birds.json（2026-11-16、航のスレッドと合意）
- 鳥の和名・年齢・身長・誕生日・趣味・好きなもの・苦手なもの・#タグ → tools/pages_data.json
  （2026-11-17 Kさんの回答：食い違いはスタッフツールが正しい。今後はスタッフツールから自動で取り込む）
色は取り込まない（名前の札の色をどうするかは、Kさんが見本を見て決める。2026-11-17 時点で未確定）。
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
json.dump(D, open(PD, "w"), ensure_ascii=False, indent=1)
print("updated:", "\n ".join(changed) or "なし")
