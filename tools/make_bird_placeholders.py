"""モチーフの鳥の「仮の絵」を作る。本物の絵がまだ無いメンバーの分だけ、枠と鳥の名前を書いた置き絵を images/bird に出す。
本物の絵が届いたら、同じ名前（ユニット番号-メンバー番号.webp）で上書きし、下の REAL に番号を足す（足した番号は仮の絵で上書きされない）。
使い方: python3 tools/make_bird_placeholders.py"""
import os
from PIL import Image, ImageDraw, ImageFont
import build_top as T
import build_pages as P

REAL = {"01-1"}   # 本物の絵がある番号
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "images", "bird")
W, H = 1352, 918   # 本物の絵（カワセミ）と同じ縦横比

def make(name, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([40, 40, W - 40, H - 40], outline=(70, 70, 70, 255), width=5)
    big, small = ImageFont.truetype(FONT, 150), ImageFont.truetype(FONT, 64)
    while d.textlength(name, font=big) > W - 240: big = ImageFont.truetype(FONT, big.size - 8)
    d.text((W / 2, H / 2 - 40), name, font=big, fill=(70, 70, 70, 255), anchor="mm")
    d.text((W / 2, H / 2 + 110), "仮の絵", font=small, fill=(70, 70, 70, 255), anchor="mm")
    im.save(path, quality=80, method=6)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for cid in P.ORDER:
        n = T.aid(P.CH[cid])
        if n in REAL: continue
        make(P.CD[cid]["motif"], os.path.join(OUT, n + ".webp")); print("仮の絵", n, P.CD[cid]["motif"])
