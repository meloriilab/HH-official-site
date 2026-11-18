"""鳥の顔の丸いアイコン（TOP の Birds と Birds ページの一覧用。Kさんの指示 2026-11-18）。
public/images/bird/<番号>.webp から、顔のまわりを正方形に切り抜いて public/images/bird/face/<番号>.webp に書き出す。
丸くするのは CSS（border-radius）。絵を差し替えたら、FACE の位置を見直して、もう一度走らせる。
FACE の値：(顔の中心の横の位置, 縦の位置, 切り抜く一辺) どれも絵の幅に対する割合（縦の位置だけ高さに対する割合）"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "public", "images", "bird")
OUT = os.path.join(SRC, "face")
SIZE = 240
FACE = {
    "01-1": (.71, .40, .33),   # カワセミ
    "01-2": (.72, .19, .32),   # メジロ
    "01-3": (.71, .42, .20),   # ツバメ
    "02-1": (.485, .565, .145),   # ハヤブサ
    "02-2": (.54, .22, .62),   # フクロウ
    "03-1": (.79, .09, .36),   # サンコウチョウ
    "03-2": (.85, .29, .27),   # ワカケホンセイインコ
    "04-1": (.71, .21, .25),   # ハシボソガラス
    "04-2": (.62, .45, .19),   # カササギ
    "04-3": (.82, .25, .26),   # カケス
    "05-1": (.74, .10, .44),   # ジョウビタキ
    "05-2": (.14, .33, .34),   # ルリビタキ
    "05-3": (.63, .31, .18),   # ベニマシコ
    "05-4": (.68, .22, .36),   # キクイタダキ
}

def main():
    os.makedirs(OUT, exist_ok=True)
    for k, (fx, fy, fs) in FACE.items():
        im = Image.open(os.path.join(SRC, f"{k}.webp")).convert("RGBA")
        w, h = im.size
        side = fs * w
        cx, cy = fx * w, fy * h
        box = (cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2)
        # 絵の外にはみ出す分は、透明のまま（背景の色は CSS で敷く）
        crop = Image.new("RGBA", (round(side), round(side)), (0, 0, 0, 0))
        src = im.crop(tuple(round(v) for v in box))
        crop.alpha_composite(src.convert("RGBA"))
        crop.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, f"{k}.webp"), quality=88)
    print(f"{len(FACE)} 枚を書き出しました")

if __name__ == "__main__":
    main()
