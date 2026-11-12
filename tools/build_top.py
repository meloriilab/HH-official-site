# -*- coding: utf-8 -*-
"""トップページを組み立てる道具。

使い方:  python3 tools/build_top.py
書き出すもの:  public/index.html / public/css/style.css / public/js/main.js

中身（曲・ユニット・メンバー・お知らせ・リンク）は、このファイルの「中身」の欄だけを書きかえて、
もう一度実行する。public/ の3つのファイルは直接書きかえない（次の実行で上書きされる）。
"""
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")

# ───────── 中身 ─────────
YT_CH = "https://www.youtube.com/channel/UCV7MPR0MRoOkYt-dht88Gww"
YT_MV = "https://youtu.be/IlpEetoUMso"
XURL = "https://x.com/humminghearts_x"
def rb(b, r): return f"<ruby>{b}<rt>{r}</rt></ruby>" if r else b

CHARS = [("TRT01","trt01","川瀬","帝翔","かわせ","みこと","#23989E"),("TRT02","trt02","目代","煎之介","めじろ","せんのすけ","#8E9334"),("TRT03","trt03","燕谷","航","つばめや","わたる","#C9432E"),
         ("NCT01","nct01","月嶺","隼瞳","つきみね","はやと","#9C8E5E"),("NCT02","nct02","月嶺","有智","つきみね","あると","#835E41"),
         ("PRS01","prs01","三条","羽響","さんじょう","うきょう","#0D86C8"),("PRS02","prs02","若本","セイン","わかもと","","#C9A21E"),
         ("BLC01","blc01","烏丸","蓮司","からすま","れんじ","#473548"),("BLC02","blc02","笠木","涼佑","かさぎ","りょうすけ","#2B83AA"),("BLC03","blc03","筧","傑","かけい","すぐる","#1E9BD0"),
         ("ORB01","orb01","紅","ましろ","くれない","","#E3426A"),("ORB02","orb02","菊井","律","きくい","ただし","#B8A51F"),("ORB03","orb03","日滝","ルイ","ひたき","","#2A79C3"),("ORB04","orb04","日滝","ジョウ","ひたき","","#E28126")]
UNITS = [("01","trt","TRT","Triattique","トリアティーク","日本の身近な野鳥 × 和ロック","#23989E",3),
         ("02","nct","NCT","NocturnalFizz","ノクターナルフィズ","猛禽兄弟 × ジャズ","#B08A3E",2),
         ("03","prs","PRS","Prisméa","プリスメア","シティポップ・デュオ","#0D86C8",2),
         ("04","blc","BLC","Blackveil Harmonic","ブラックヴェイル・ハーモニック","カラスたちの宴 × ロック","#5B4560",3),
         ("05","orb","ORB","ORYBIA","オリビア","14歳、地元アイドル四人組","#E3426A",4),
         ("06","wgo","WGO","Winged Oath","ウィングド・オウス","誓いの五人組","#3C5A7A",5)]
RELS = [("003","blc","Rule The Darkness","","Blackveil Harmonic"),("002","nct","宵の翼","よいのつばさ","NocturnalFizz"),("001","trt","薄紅梅","うすこうばい","Triattique")]

# お知らせ（新しいものを上に）: (日付, 札, 本文)。札は MV / MUSIC / INFO のどれか
NEWS = [("2026.07.07","MV","ミュージックビデオを公開しました"),("2026.07.07","MUSIC","楽曲の配信を開始しました"),("2026.07.07","INFO","Humming Hearts 公式サイトを公開しました")]
# ピックアップ曲（RELS の先頭の番号で選ぶ）と、その公開日。扉の紋章・ユニット名は、選んだ曲のユニットに自動で変わる
# (ユニット, 曲名, ふりがな, 公開日, MVのアドレス)。わからない欄は空（空なら画面に出さない）
PICK = ("prs", "月日の奏", "つきひのかなで", "", YT_MV)
# 曲ごとのMVのアドレス。わかっているものだけ（無い曲は YouTube のチャンネルへ送り、ボタンの名前も YouTube にする）
MV = {}
# Spotify のアドレス。未確定のあいだは空にしておく（空ならボタンを出さない）
SPOT = ""
# ピックアップ曲の絵（YouTube のサムネイル。読めないときは手元の絵を出す）
YT_THUMB = "https://i.ytimg.com/vi/IlpEetoUMso/hq720.jpg"   # 横長（16:9）で、上下の黒い帯が無い絵
YT_THUMB2 = "https://i.ytimg.com/vi/IlpEetoUMso/mqdefault.jpg"   # 上が読めないときの小さい絵
# 旗に大きな絵を出すユニット（絵がそろっているものだけ。ほかは紋章を出す）
KV = {"trt","nct","blc"}
FONT = "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Shippori+Mincho+B1:wght@500&family=Zen+Kaku+Gothic+New:wght@400;500&display=swap"
DESC = "鳥のアイドル事務所 Humming Hearts の公式サイト。楽曲とユニット、メンバーを紹介しています。"

# ───────── ここから下は組み立て ─────────
# 画像のファイル名とページ内の行き先には、制作用の記号（TRT など）を使わない
NO = {u: no for no, u, *_ in UNITS}
SLUG = {u: n.lower().replace(" ", "-").replace("é", "e") for no, u, code, n, *_ in UNITS}
def members_of(u): return [c for c in CHARS if c[1].startswith(u)]
def name(c): return rb(c[2], c[4]) + rb(c[3], c[5])
def fid(c): return f"{NO[c[1][:3]]}-{int(c[1][3:])}"
# 個別ページがあるユニットと、メンバーのページの名前（ローマ字。制作用の記号は使わない）
PAGES = {"trt","nct","blc"}
MSLUG = {"trt01":"mikoto-kawase","trt02":"sennosuke-mejiro","trt03":"wataru-tsubameya","nct01":"hayato-tsukimine","nct02":"aruto-tsukimine",
         "blc01":"renji-karasuma","blc02":"ryosuke-kasagi","blc03":"suguru-kakei"}
def uhref(u, pre=""): return f"{pre}units/{SLUG[u]}.html" if u in PAGES else f"{pre or './'}#{SLUG[u]}"
def mhref(c, pre=""): return f"{pre}members/{MSLUG[c[1]]}.html" if c[1] in MSLUG else ""
def chan(): return f'<p class="row"><a class="btn" href="{YT_CH}">YouTube</a>{spot("btn")}<a class="btn" href="{XURL}">X</a></p>'
def header(pre="", top=True):
    """上の帯とメニュー。pre はトップページへ戻る道（個別ページでは "../"）"""
    home = "#" if top else pre
    sec = lambda k: f"#{k}" if top else f"{pre}#{k}"
    # 丸いボタン：押すとユニットのページへ。カーソルを載せると、そのユニットのメンバー名が下に出る
    def pill(u, n):
        ms = members_of(u)
        rows = "".join(
            f'<a href="{mhref(c,pre)}">{c[2]} {c[3]}</a>' if mhref(c) else f'<span>{c[2]} {c[3]}</span>' for c in ms)
        drop = f'<span class="up-m">{rows}</span>' if ms else ""
        return f'<span class="up"><a class="up-a" href="{uhref(u,pre)}" data-u="{SLUG[u]}">{n}</a>{drop}</span>'
    upills="".join(pill(u,n) for no,u,code,n,*_ in UNITS)
    return f'''
<div class="prog" aria-hidden="true"><i></i></div>
<header class="hd"><a class="logo" href="{home}">Humming Hearts</a><nav class="upills" aria-label="ユニット">{upills}</nav><nav class="gnav"><a href="{sec("release")}">Release</a><a href="{sec("units")}">Units</a><a href="{sec("members")}">Members</a><a href="{sec("news")}">News</a></nav><a class="yt" href="{YT_CH}">YouTube</a><button class="burger" type="button" aria-label="メニュー" aria-expanded="false" aria-controls="menu"><i></i><i></i></button></header>
<div class="menu" id="menu" hidden><nav class="m-nav"><a href="{sec("release")}">Release<small>楽曲</small></a><a href="{sec("units")}">Units<small>ユニット</small></a><a href="{sec("members")}">Members<small>メンバー</small></a><a href="{sec("news")}">News<small>お知らせ</small></a></nav>{chan()}</div>'''
def footer():
    return f'''<footer class="ft"><p class="logo">Humming Hearts</p>{chan()}<p class="note">キャラクター・楽曲・映像の制作に生成AIを活用しています。</p><p class="note">© melorii lab</p></footer>'''
def page(title, desc, pre, inner, css=(), attrs=""):
    links="".join(f'<link rel="stylesheet" href="{pre}css/{c}">' for c in ("style.css",)+tuple(css))
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#FAFAF8">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONT}">
{links}</head><body{attrs}>{inner}<script src="{pre}js/main.js"></script></body></html>
'''
def spot(cls): return f'<a class="{cls}" href="{SPOT}">Spotify</a>' if SPOT else ""

def body():
    rels="".join(f'''
      <article class="rel" data-speed="{sp}"><a class="ph" href="{MV.get(n,YT_CH)}"><img src="images/jacket/{NO[u]}.webp" alt="{t} のジャケット" data-speed=".1"></a>
        <h3>{rb(t,k)}</h3><p class="by">{un}</p><p class="lk">{f'<a href="{MV[n]}">MV</a>' if n in MV else f'<a href="{YT_CH}">YouTube</a>'}{spot("")}</p></article>''' for (n,u,t,k,un),sp in zip(RELS,[".1","-.14",".04"]))
    INK={"nct":"#1B1712"}
    def unit(i,no,u,n,kana,tg,c):
        art=f'<img class="f-art" src="images/kv/{NO[u]}.webp" alt="" data-speed=".12">' if u in KV else f'<img class="f-em" src="images/emblem/{NO[u]}.webp" alt="" data-speed=".12">'
        names="".join(f'<li>{name(m)}</li>' for m in members_of(u)) 
        tag,end,go=(f'a href="{uhref(u)}"',"a",'<span class="f-go">プロフィール</span>') if u in PAGES else ("div","div","")
        return f'''
      <{tag} class="flag" id="{SLUG[u]}" data-u="{SLUG[u]}" style="--c:{c};--tx:{INK.get(u,"#fff")}">
        <span class="f-txt"><img class="f-mark" src="images/emblem/{NO[u]}.webp" alt=""><span class="f-name">{n}</span><span class="f-kana">{kana}</span><span class="f-tag">{tg}</span><ul class="f-mem">{names}</ul>{go}</span>
        <span class="f-pic">{art}</span></{end}>'''
    units="".join(unit(i,no,u,n,kana,tg,c) for i,(no,u,code,n,kana,tg,c,cnt) in enumerate(UNITS))
    def face(c):
        tag,end=(f'a href="{mhref(c)}"',"a") if mhref(c) else ("div","div")
        return f'<{tag} class="mem" data-speed="{[".0","-.12",".08"][CHARS.index(c)%3]}"><span class="ph"><img src="images/face/{fid(c)}.webp" alt=""></span><span>{name(c)}</span></{end}>'
    mem="".join(face(c) for c in CHARS)
    news="".join(f'<li><time>{d}</time><span class="tag">{t}</span><span class="n-t">{x}</span></li>' for d,t,x in NEWS)
    order={"01":CHARS[0:3],"02":CHARS[3:5],"03":CHARS[5:7],"04":CHARS[7:10],"05":CHARS[10:14]}
    def alt(k):
        u,i=k.split("-"); cs=order.get(u)
        return name(cs[int(i)-1]) if cs else ""
    # (file, x%, size, bottom as a share of H, layer, scroll speed)
    FIG=[("05-1",39,.70,.44,1,".26"),("05-2",46,.74,.50,1,".26"),("05-3",56,.72,.46,1,".26"),("05-4",65,.70,.51,1,".26"),
         ("03-1",13,.82,.34,1,".22"),("03-2",24,.78,.40,1,".22"),("07-1",76,.76,.50,1,".22"),("07-2",91,.80,.46,1,".22"),
         ("04-2",74,.98,.08,2,".14"),("04-1",85,1.04,.04,2,".14"),("04-3",96,.96,.10,2,".14"),
         ("02-1",8,1.12,-.24,2,".12"),("02-2",22,1.06,-.2,2,".12"),
         ("01-2",37,1.26,-.42,3,".04"),("01-3",63,1.24,-.4,3,".04"),("01-1",50,1.34,-.44,4,".04")]
    lineup="".join(f'<img style="left:{x}%;--s:{sz};--y:{y};z-index:{z}" src="images/chara/{k}.webp" alt="{alt(k)}" data-speed="{sp}">' for k,x,sz,y,z,sp in FIG)
    chan=globals()['chan']()
    pu_u,PT,PK,PD,PMV=PICK; PN=NO[pu_u]; PUN=next(n for no,u,code,n,*_ in UNITS if u==pu_u)   # ピックアップ曲。扉の紋章はこの曲のユニットのもの
    return f'''{header()}
<main>
<section class="fv">
  <p class="word w1" aria-hidden="true" data-speed=".55">Humming</p><p class="word w2" aria-hidden="true" data-speed=".3" data-speedx="-.15">Hearts</p>
  <div class="trio">{lineup}</div>
  <h1 class="catch"><span>本能のまま、</span><span>歌う。</span></h1>
  <p class="hint" aria-hidden="true">Scroll</p>
</section>
<section class="sec pu" id="pickup"><p class="ghost" aria-hidden="true" data-speedx="-.35">Pick Up</p><h2><span>Pick Up</span><small>ピックアップ曲</small><i class="idx" aria-hidden="true">01<b>/05</b></i></h2>
<div class="pu-g">
  <a class="pu-fr" href="{PMV}"><span class="pu-w"><span class="pu-c ph"><img src="{YT_THUMB}" onerror="this.onerror=null;this.src='{YT_THUMB2}'" alt="{PT} のミュージックビデオ"></span><i class="dr dl" aria-hidden="true"><b class="d-a">Pick Up</b><img src="images/emblem/{PN}.webp" alt=""><b class="d-b">{PUN}</b></i><i class="dr drr" aria-hidden="true"><b class="d-a">MV</b><img src="images/emblem/{PN}.webp" alt=""><b class="d-b">{PD}</b></i></span><span class="pu-t">{rb(PT,PK)}<small>{PUN}</small></span></a>
  <div class="pu-s"><p class="lbl">New Release</p><p class="row"><a class="btn on" href="{PMV}">MV</a>{spot("btn")}</p>{chan}</div>
</div></section>
<section class="sec" id="release"><p class="ghost" aria-hidden="true" data-speedx=".35">Release</p><h2><span>Release</span><small>楽曲</small><i class="idx" aria-hidden="true">02<b>/05</b></i></h2><div class="rels">{rels}</div></section>
<section class="sec" id="units"><p class="ghost" aria-hidden="true" data-speedx="-.35">Units</p><h2><span>Units</span><small>ユニット</small><i class="idx" aria-hidden="true">03<b>/05</b></i></h2></section>
<div class="flags">{units}</div>
<section class="sec" id="members"><p class="ghost" aria-hidden="true" data-speedx=".35">Members</p><h2><span>Members</span><small>メンバー</small><i class="idx" aria-hidden="true">04<b>/05</b></i></h2><div class="mems">{mem}</div></section>
<section class="sec" id="news"><p class="ghost" aria-hidden="true" data-speedx="-.35">News</p><h2><span>News</span><small>お知らせ</small><i class="idx" aria-hidden="true">05<b>/05</b></i></h2><ul class="news">{news}</ul><p class="row one"><a class="btn" href="{XURL}">X</a></p></section>
</main>
{footer()}'''
CSS="""
:root{--bg:#FAFAF8;--ink:#141414;--sub:#6E6E6E;--faint:#E9E9E6;--line:#CFCFCB;
--en:"Cormorant Garamond","Cormorant",Georgia,serif;--min:"Shippori Mincho B1","Yu Mincho",serif;--jp:"Zen Kaku Gothic New","Hiragino Sans",sans-serif}
*{box-sizing:border-box}html,body{overflow-x:clip}
body{margin:0;background:var(--bg);color:var(--ink);font:400 14px/2 var(--jp)}
img{display:block;max-width:100%}a{color:inherit;text-decoration:none}
ruby rt{font:400 .4em/1 var(--jp);letter-spacing:.1em}
/* pictures are grey until they reach the middle of the screen */
.ph img,.trio img{filter:grayscale(1) contrast(1.05);transition:filter .8s ease}
.lit .ph img,.ph.lit img,.fv.lit .trio img,a:hover .ph img{filter:none}
.sec{isolation:isolate}
.hd,.sec,.nr,.ft{padding-inline:24px}
.hd{position:absolute;inset:0 0 auto;z-index:10;display:flex;justify-content:space-between;align-items:center;padding-block:20px}
.logo{margin:0;font:500 22px/1 var(--en);letter-spacing:.02em}
.hd .gnav{display:none}
.hd{flex-wrap:wrap;gap:14px}
/* unit pills: jump straight to a unit from anywhere at the top; the one on screen is filled */
.upills{order:3;flex:1 0 100%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:5px;margin-inline:-8px}
.up{position:relative;display:block;min-width:0}
.up-a{min-height:24px;padding-inline:9px;display:flex;align-items:center;justify-content:center;text-align:center;border:1px solid var(--ink);border-radius:999px;font:500 11px/1 var(--en);letter-spacing:.02em;white-space:nowrap;background:rgba(250,250,248,.8);transition:background .25s,color .25s}
.up-a:hover,.up-a.on,.up:hover .up-a{background:var(--ink);color:var(--bg)}
.row{display:flex;gap:0;margin:0;border:1px solid var(--ink)}
.btn{flex:1 1 0;min-height:46px;display:inline-flex;align-items:center;justify-content:center;font:500 18px/1 var(--en);letter-spacing:.04em;transition:background .25s,color .25s}
.btn+.btn{border-left:1px solid var(--ink)}
.btn:hover,.btn.on{background:var(--ink);color:var(--bg)}
.yt{margin-left:auto;font:500 17px/1 var(--en);letter-spacing:.04em;min-height:44px;display:flex;align-items:center;border-bottom:0}
.burger{position:relative;z-index:31;width:44px;height:44px;margin-right:-10px;padding:0;border:0;background:none;color:inherit;cursor:pointer}
.burger i{position:absolute;left:10px;right:10px;height:1px;background:currentColor;transition:transform .3s,top .3s}
.burger i:first-child{top:18px}.burger i:last-child{top:26px}
.burger[aria-expanded=true]{position:fixed;top:20px;right:24px}
.burger[aria-expanded=true] i{top:22px}.burger[aria-expanded=true] i:first-child{transform:rotate(45deg)}.burger[aria-expanded=true] i:last-child{transform:rotate(-45deg)}
.menu{position:fixed;inset:0;z-index:30;background:var(--bg);padding:96px 24px 32px;display:flex;flex-direction:column;justify-content:space-between;overflow:auto;animation:menuIn .3s ease}
.menu[hidden]{display:none}
/* member names under a unit pill: only where a cursor can rest on it (no touch screens) */
.up-m{display:none;position:absolute;z-index:20;left:0;top:100%;min-width:100%;padding-top:5px}
.up-m a,.up-m span{display:block;padding:9px 14px;background:var(--bg);border:1px solid var(--ink);border-top:0;font:500 13px/1.4 var(--min);letter-spacing:.06em;white-space:nowrap;transition:background .2s,color .2s}
.up-m>:first-child{border-top:1px solid var(--ink);border-radius:12px 12px 0 0}.up-m>:last-child{border-radius:0 0 12px 12px}.up-m>:only-child{border-radius:12px}
.up-m a:hover{background:var(--ink);color:var(--bg)}.up-m span{color:var(--sub)}
@media(hover:hover){.up:hover .up-m,.up:focus-within .up-m{display:block}}
.menu-open .hd{z-index:40}.menu-open .upills,.menu-open .yt{visibility:hidden}
@keyframes menuIn{from{opacity:0}to{opacity:1}}
.m-nav{display:grid}
.m-nav a{display:flex;align-items:baseline;gap:14px;padding:16px 0;border-bottom:1px solid var(--line);font:italic 500 38px/1.1 var(--en)}
.m-nav small{font:500 12px/1 var(--jp);color:var(--sub);letter-spacing:.2em}
.menu .row{margin:32px 0 0}
.fv{position:relative;height:730px;overflow:hidden}
.word{position:absolute;margin:0;font:500 112px/1 var(--en);color:var(--faint);white-space:nowrap;letter-spacing:-.02em}
.w1{left:-10px;top:150px}.w2{right:-14px;top:330px}
.trio{position:absolute;inset:auto 3% 0;height:560px}
.trio img{position:absolute;bottom:0;max-width:none}
.trio{--H:340px}.trio img{transform:translateX(-50%);width:auto;height:calc(var(--H)*var(--s));bottom:calc(var(--H)*var(--y))!important}
.catch{position:absolute;z-index:3;right:22px;top:150px;margin:0;writing-mode:vertical-rl;font:500 21px/1.6 var(--min);letter-spacing:.3em}
.catch span{display:block;white-space:nowrap}.catch span+span{padding-top:4em}
.pu{padding-top:72px}
h2 span,h2 small{white-space:nowrap}.pu h2{gap:10px}.pu h2 small{letter-spacing:.1em}
.pu-g{display:grid;gap:28px}
/* pick up: the picture stays whole. two ink doors stand in front of it and slide apart as the frame
   comes to the middle of the screen, like a stage curtain; they close again as it leaves.
   job: the opening marks "this is the song to watch now". --o is how far open (0 shut, 1 open) */
/* the frame keeps the video's own 16:9 shape at every width, so nothing in the picture is cut off */
.pu-fr{position:relative;display:block;margin-inline:-24px}
.pu-w{position:relative;display:block;aspect-ratio:16/9;overflow:hidden}
.pu-c{position:absolute;inset:0;display:block}
.pu-c img{width:100%;height:100%;object-fit:cover;transition:filter .8s ease}
.dr{position:absolute;top:0;bottom:0;width:50%;background:var(--ink);color:var(--bg);overflow:hidden;will-change:transform;--e:104px;--in:9px}
.dl{left:0;transform:translateX(calc(var(--o,1)*-101%))}
.drr{right:0;transform:translateX(calc(var(--o,1)*101%))}
/* on the doors, each with a job:
   thin frame line, open on the seam side = the two halves read as one pair of doors
   the unit's emblem in one colour (the doors are black), half on each door = whose song is behind the doors; it parts when they open
   four small words in the corners = what this is (Pick Up / MV), who (unit) and when (release date) */
.dr::before{content:"";position:absolute;inset:var(--in);border:1px solid rgba(250,250,248,.55)}
.dl::before{right:0;border-right:0}.drr::before{left:0;border-left:0}
.dr img{position:absolute;top:50%;width:var(--e);height:var(--e);max-width:none;margin-top:calc(var(--e)/-2);filter:grayscale(1) contrast(1.1)}
.dl img{right:calc(var(--e)/-2)}.drr img{left:calc(var(--e)/-2)}
.dr b{position:absolute;font:italic 500 14px/1 var(--en);letter-spacing:.04em;white-space:nowrap}
.d-a{top:calc(var(--in) + 9px)}.d-b{bottom:calc(var(--in) + 9px)}
.dl b{left:calc(var(--in) + 10px)}.drr b{right:calc(var(--in) + 10px)}
.pu-t{margin:14px 24px 0;font:500 30px/1.3 var(--min);letter-spacing:.08em;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.pu-t small{font:italic 500 16px var(--en);letter-spacing:.02em;color:var(--sub)}
.pu-s{display:grid;gap:14px}
.lbl{margin:0;font:italic 500 17px/1 var(--en);color:var(--sub)}
.nr-t{margin:0 0 6px;font:500 32px/1.3 var(--min);letter-spacing:.08em;display:flex;align-items:baseline;gap:14px}.nr-t small{font:italic 500 17px var(--en);color:var(--sub)}
.sec{position:relative;padding-top:128px;overflow:clip}
h2{margin:0 0 44px;display:flex;align-items:baseline;gap:14px;font-weight:500;border-bottom:1px solid var(--ink);padding-bottom:14px}
h2 span{font:500 56px/1 var(--en);letter-spacing:-.01em}h2 small{font:500 12px var(--min);letter-spacing:.3em;color:var(--sub)}
.rels{display:grid;grid-template-columns:1fr 1fr;gap:40px 18px}
.rel:nth-child(2){margin-top:64px}
.rel .ph img{width:100%;aspect-ratio:1;object-fit:cover}
.rel h3{margin:12px 0 0;font:500 17px/1.4 var(--min);letter-spacing:.04em}.by{margin:0;font:italic 500 15px var(--en);color:var(--sub)}
.lk{margin:8px 0 0;display:flex;gap:18px;font:500 16px var(--en)}.lk a{border-bottom:1px solid var(--ink);padding-bottom:1px;min-width:44px;text-align:center}
/* restrained decoration, each with a job:
   .idx   small section number at the end of the heading rule = where you are among the four sections
   h2 rule draws itself from the left when the section arrives = marks the start of a section
   .prog  1px line that fills with scroll = how far down the page you are
   .hint  small word + falling line at the bottom of the first screen = there is more below
   .f-mark the unit's own emblem beside its name = repeats each unit's mark so the flag reads as theirs */
h2{position:relative;border-bottom:0!important}
h2::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--ink);transform-origin:left}
.js h2::after{transform:scaleX(0);transition:transform 1.1s cubic-bezier(.7,0,.2,1)}
.js h2.in::after{transform:none}
.idx{margin-left:auto;font:italic 500 20px/1 var(--en);font-style:italic;letter-spacing:.04em}
.idx b{font-weight:500;color:var(--sub);font-size:13px;margin-left:3px}
.prog{position:fixed;z-index:40;left:0;top:0;width:100%;height:2px;pointer-events:none}
.prog i{display:block;height:100%;background:var(--ink);transform-origin:left;transform:scaleX(var(--p,0))}
.hint{display:none;position:absolute;z-index:3;left:24px;bottom:0;margin:0;padding-bottom:54px;font:italic 500 14px/1 var(--en);letter-spacing:.08em;writing-mode:vertical-rl}
.hint::after{content:"";position:absolute;left:50%;bottom:0;width:1px;height:44px;background:var(--ink);transform-origin:top;animation:fall 2.4s cubic-bezier(.7,0,.2,1) infinite}
@keyframes fall{0%{transform:scaleY(0);transform-origin:top}50%{transform:scaleY(1);transform-origin:top}51%{transform-origin:bottom}100%{transform:scaleY(0);transform-origin:bottom}}
.f-go{display:inline-flex;align-items:center;justify-content:center;min-width:140px;min-height:44px;margin-top:22px;border:1px solid currentColor;font:500 13px/1 var(--min);letter-spacing:.3em;transition:background .25s,color .25s}
a.flag:hover .f-go{background:var(--tx);color:var(--c)}
.f-mark{width:48px;height:48px;margin-bottom:14px}
.ghost{position:absolute;left:0;top:40px;margin:0;font:500 150px/1 var(--en);color:var(--faint);white-space:nowrap;z-index:-1;letter-spacing:-.02em}
.rel .ph{display:block;overflow:hidden;aspect-ratio:1}.rel .ph img{scale:1.22}
/* unit flags: full-width, stack over the previous one; grey until they take the screen */
.flags{margin-top:8px}
.flag{position:sticky;top:0;display:grid;min-height:100svh;background:var(--c);color:var(--tx);grid-template-rows:auto 1fr;overflow:hidden;filter:grayscale(1);transition:filter .9s ease}
.flag.lit{filter:none}
.f-txt{display:block;padding:72px 24px 24px}
.f-name{display:block;font:500 58px/.95 var(--en);letter-spacing:-.01em}
.f-kana{display:block;margin-top:10px;font-size:12px;letter-spacing:.16em;opacity:.85}
.f-tag{display:block;margin-top:14px;font:500 18px/1.6 var(--min)}
.f-mem{list-style:none;margin:18px 0 0;padding:14px 0 0;border-top:1px solid currentColor;display:grid;grid-template-columns:1fr 1fr;gap:6px 12px;font:500 15px/1.7 var(--min)}
.f-mem .tbd{font:400 12px var(--jp);grid-column:1/-1}
.f-pic{position:relative;display:block;min-height:260px;overflow:hidden}
.f-art{position:absolute;left:0;top:-15%;width:100%;height:130%;object-fit:cover;object-position:50% 20%}
.f-em{position:absolute;height:80%;left:50%;top:10%;margin-left:-40%;width:80%;object-fit:contain}
.mems{display:grid;grid-template-columns:repeat(3,1fr);gap:32px 12px}
.mem{display:flex;flex-direction:column;align-items:center;text-align:center;font:500 12px/1.5 var(--min);letter-spacing:.04em}
.mem .ph{display:block;width:84px;height:84px;border-radius:50%;overflow:hidden;margin-bottom:10px}
.news{list-style:none;margin:0 0 28px;padding:0}
.news li{display:grid;grid-template-columns:auto 1fr;gap:2px 14px;align-items:center;padding:18px 0;border-bottom:1px solid var(--line)}
.news time{font:500 19px var(--en)}.tag{justify-self:start;width:64px;text-align:center;border:1px solid var(--ink);font:500 10px/20px var(--jp);letter-spacing:.14em}
.news .n-t{grid-column:1/-1}
.one{width:140px}
.ft{margin-top:128px;padding-block:56px 40px;border-top:1px solid var(--ink);display:grid;gap:20px}.ft .logo{font-size:34px}.note{margin:0;font-size:12px;color:var(--sub)}
:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
[data-speed]{will-change:translate}
@media(min-width:900px){
 .hd,.sec,.nr,.ft{padding-inline:max(32px,calc(50% - 540px))}
 .hd .gnav{display:flex;gap:30px;font:500 19px var(--en);margin-left:auto}.yt{margin-left:0;font-size:19px}.burger{display:none}
 .hd{flex-wrap:nowrap;gap:28px;justify-content:flex-start}
 .upills{order:0;flex:0 0 auto;display:inline-grid;grid-template-columns:repeat(3,1fr);margin-inline:0}.up-a{min-height:24px;font-size:13px;padding-inline:14px}
 .fv{height:900px}.word{font-size:300px}.w1{left:calc(50% - 600px);top:70px}.w2{right:calc(50% - 600px);top:420px}
 .trio{height:780px;width:960px;left:50%;right:auto;margin-left:-560px;--H:500px}
 .catch{right:max(32px,calc(50% - 540px));top:150px;font-size:30px}
 .pu{padding-top:120px}.pu-g{grid-template-columns:1fr 720px;align-items:end;column-gap:80px}.pu-fr{order:2;margin:0}.dr{--e:230px;--in:18px}.dr b{font-size:24px}.pu-t{position:absolute;z-index:2;left:0;bottom:0;margin:0;max-width:71.6%;background:var(--bg);font-size:44px;padding:16px 26px 0 0}
 .sec{padding-top:200px}h2 span{font-size:110px}h2{margin-bottom:72px}
 .rels{grid-template-columns:repeat(3,1fr);gap:48px}.rel:nth-child(2){margin-top:120px}.rel h3{font-size:21px}
 .ghost{font-size:380px;top:60px}
 .idx{font-size:26px}.idx b{font-size:15px}.f-mark{width:64px;height:64px;margin-bottom:20px}
 .hint{display:block;left:auto;right:max(32px,calc(50% - 540px))}
 .prog{width:2px;height:100%;left:auto;right:0}.prog i{width:100%;transform-origin:top;transform:scaleY(var(--p,0))}
 .flag{grid-template-rows:none;grid-template-columns:1fr 1fr}
 .f-txt{padding:120px 60px 60px max(32px,calc(50vw - 540px));align-self:center}.f-name{font-size:76px}.f-tag{font-size:24px}.f-mem{font-size:18px;max-width:440px}
 .mems{grid-template-columns:repeat(7,1fr);gap:48px 20px}.mem .ph{width:116px;height:116px}.mem{font-size:13px}
 .news li{grid-template-columns:150px 84px 1fr}.news .n-t{grid-column:auto}
 .ft{grid-template-columns:1fr 420px;align-items:end}.ft .note{grid-column:1/-1}
}
/* narrow PC and tablets held sideways (900 to 1139px): same layout, with the menu button instead of the word links */
@media(min-width:900px) and (max-width:1139px){
 .hd .gnav{display:none}.burger{display:block}.yt{margin-left:auto}
 .trio{left:0;margin-left:0;width:88%}
 .pu-g{grid-template-columns:1fr 62%;column-gap:40px}
 h2 span{font-size:88px}
}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}.ph img,.trio img{filter:none}}
"""
JS="""(function(){var b=document.querySelector('.burger'),m=document.getElementById('menu');if(!b||!m)return;
function set(o){m.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false');document.documentElement.style.overflow=o?'hidden':'';document.documentElement.classList.toggle('menu-open',o)}
b.addEventListener('click',function(){set(m.hidden)});m.addEventListener('click',function(e){if(e.target.closest('a'))set(false)});
addEventListener('keydown',function(e){if(e.key==='Escape')set(false)})})();
(function(){if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;
/* colour only in the middle band of the screen */
document.documentElement.classList.add('js');
var ho=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');ho.unobserve(e.target)}})},{threshold:.6});
[].forEach.call(document.querySelectorAll('h2'),function(el){ho.observe(el)});
var pg=document.querySelector('.prog');
var pill={};[].forEach.call(document.querySelectorAll('.up-a'),function(a){pill[a.dataset.u]=a});
function mark(){var fs=[].slice.call(document.querySelectorAll('.flag.lit')),cur=document.body.dataset.u||(fs.length?fs[fs.length-1].dataset.u:'');for(var k in pill)pill[k].classList.toggle('on',k===cur)}
var io=new IntersectionObserver(function(es){es.forEach(function(e){e.target.classList.toggle('lit',e.isIntersecting)});mark()},{rootMargin:'-30% 0px -30% 0px'});
[].forEach.call(document.querySelectorAll('.rel,.flag,.mem,.fv,.pu-fr'),function(el){io.observe(el)});
/* layers move at their own speed */
var px=[].slice.call(document.querySelectorAll('[data-speed],[data-speedx]')).map(function(el){return{el:el,s:parseFloat(el.dataset.speed)||0,x:parseFloat(el.dataset.speedx)||0,h:el.closest('.flag,.rel,section')||el.parentNode}}),tk=false;
var pu=document.querySelector('.pu-fr');
function fr(){tk=false;var vh=innerHeight;if(pu){var q=pu.getBoundingClientRect(),o=1.25-Math.abs(q.top+q.height/2-vh/2)/(vh*.42);o=Math.max(0,Math.min(1,o));pu.style.setProperty('--o',(o*o*(3-2*o)).toFixed(3))}pg.style.setProperty('--p',(scrollY/Math.max(1,document.documentElement.scrollHeight-vh)).toFixed(4));px.forEach(function(p){var r=p.h.getBoundingClientRect();if(r.bottom<-500||r.top>vh+500)return;
 var d=(r.top+r.height/2)-vh/2;p.el.style.translate=(-d*p.x).toFixed(1)+'px '+(-d*p.s).toFixed(1)+'px'})}
addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(fr)}},{passive:true});addEventListener('resize',fr);fr();})();"""

def main():
    html = page("Humming Hearts OFFICIAL SITE", DESC, "", body())
    for path, text in (("index.html", html), ("css/style.css", CSS.lstrip("\n")), ("js/main.js", JS + "\n")):
        with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f: f.write(text)
        print("ok", path)

if __name__ == "__main__":
    main()
