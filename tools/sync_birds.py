"""スタッフツールの窓口（/api/read/catalog）から野鳥のテキストを取り込み、tools/birds.json を作り直す。
Kさんがスタッフツールで直した内容をサイトに反映するときに実行する（2026-11-16、航のスレッドと合意）。
窓口にまだ入っていないキャラ（siteBird が空）は、今の birds.json の中身を残す。
使い方：python3 tools/sync_birds.py  →  そのあと build_top.py / build_pages.py"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(__file__)
P = os.path.join(HERE, "birds.json")
UNIT = {"BVH": "blc"}   # スタッフツールのユニット記号と、サイトの記号が違うもの
raw = subprocess.run(["curl", "-sSf", "https://staff.humming-hearts.com/api/read/catalog"], capture_output=True, text=True, check=True).stdout
cat = json.loads(raw)
B = json.load(open(P))
changed = []
for c in cat.get("characters", []):
    m = re.fullmatch(r"([A-Z]+)-(\d+)", str(c.get("id", "")))
    sb = c.get("siteBird") or {}
    if not m or not sb: continue
    key = f'{UNIT.get(m[1], m[1].lower())}{int(m[2]):02d}'
    if key not in B: continue   # サイトにページが無いキャラは飛ばす
    if B[key] != sb: changed.append(key)
    B[key] = sb
json.dump(B, open(P, "w"), ensure_ascii=False, indent=1)
print("updated:", ", ".join(changed) or "なし")
