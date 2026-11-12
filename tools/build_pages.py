# -*- coding: utf-8 -*-
"""ユニットとメンバーの個別ページを組み立てる道具。

使い方:  python3 tools/build_pages.py
書き出すもの:  public/units/<ユニット名>.html / public/members/<名前>.html / public/css/page.css

文章（紹介文・せりふ・プロフィール）は tools/pages_data.json に入っている（旧サイトの文章そのまま）。
文章を直すときは pages_data.json を書きかえて、もう一度実行する。
上の帯・下の帯・リンク先・ユニットやメンバーの並びは build_top.py の「中身」の欄と共通。
"""
import os, re, json, html
import build_top as T

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "pages_data.json"), encoding="utf-8"))
UD = {u["id"].lower(): u for u in D["units"]}
CD = {c["id"].lower(): c for c in D["chars"]}
PRE = "../"

# キャラ性を表すタグ（K さんが決めた言葉そのまま）。無い人は「未確定」で、タグの段を出さない
TAGS = {"trt01": ["ストイックなカワセミ", "渓流釣り", "魚は骨だけ残す職人芸"],
        "trt02": ["ムードメーカーなメジロ", "実は茶道家三男坊", "スイーツラブ"],
        "trt03": ["フッ軽なツバメ", "三味線", "写真好き"]}


UNIT = {u: dict(no=no, name=n, kana=kana, tag=tg, c=c) for no, u, code, n, kana, tg, c, cnt in T.UNITS}
CH = {c[1]: c for c in T.CHARS}
esc = html.escape

def ruby_text(s):
    """[[名前|よみ]] をふりがな付きに、[[名前]] をそのままの名前にする"""
    s = esc(s)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", lambda m: T.rb(m.group(1), m.group(2)), s)
    return re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)

def h2(en, jp, i, n):
    return f'<h2><span>{en}</span><small>{jp}</small><i class="idx" aria-hidden="true">{i:02d}<b>/{n:02d}</b></i></h2>'

def face(cid, speed=".0"):
    c = CH[cid]
    return f'<a class="mem" href="{T.mhref(c, PRE)}" data-speed="{speed}"><span class="ph"><img src="{PRE}images/face/{T.fid(c)}.webp" alt=""></span><span>{T.name(c)}</span></a>'

def unit_page(u):
    d, m = UD[u], UNIT[u]
    no = m["no"]
    intro = "".join(f"<p>{ruby_text(p)}</p>" for p in d["intro"])
    mems = "".join(face(i.lower(), s) for i, s in zip(d["members"], [".0", "-.1", ".06"]))
    rels = "".join(f'''
      <article class="rel"><a class="ph" href="{T.MV.get(n, T.YT_CH)}"><img src="{PRE}images/jacket/{T.JK[n]}.webp" alt="{t} のジャケット"></a>
        <h3>{T.rb(t, k)}</h3><p class="by">{un}</p><p class="lk"><a href="{T.MV.get(n, T.YT_CH)}">MV</a>{T.spot("", T.SPT.get(n, ""))}</p></article>''' for n, ru, t, k, un in T.RELS if ru == u)
    others = "".join(f'<a href="{T.uhref(o, PRE)}">{UNIT[o]["name"]}<small>{UNIT[o]["kana"]}</small></a>' for o in UNIT if o != u and o in T.PAGES)
    inner = f'''{T.header(PRE, top=False)}
<main>
<section class="fv uh">
  <div class="uh-t"><img class="uh-em" src="{PRE}images/emblem/{no}.webp" alt=""><h1>{m["name"]}<small>{m["kana"]}</small></h1><p class="uh-tag">{esc(d["tagline"])}</p><p class="uh-c">{esc(d["catch"])}</p></div>
  <div class="uh-pic ph"><img src="{PRE}images/kv/{no}.webp" alt="{m["name"]}" data-speed=".08"></div>
</section>
<section class="sec" id="about"><p class="ghost" aria-hidden="true" data-speedx="-.35">About</p>{h2("About", "紹介", 1, 3)}<div class="prose">{intro}</div></section>
<section class="sec" id="members"><p class="ghost" aria-hidden="true" data-speedx=".35">Members</p>{h2("Members", "メンバー", 2, 3)}<div class="mems big">{mems}</div></section>
<section class="sec" id="release"><p class="ghost" aria-hidden="true" data-speedx="-.35">Release</p>{h2("Release", "楽曲", 3, 3)}<div class="rels solo">{rels}</div></section>
<nav class="sec others" aria-label="ほかのユニット"><p class="lbl">Units</p><div class="m-nav">{others}</div></nav>
</main>
{T.footer()}'''
    return T.page(f'{m["name"]} | Humming Hearts', esc(d["catch"]), PRE, inner, css=("page.css",), attrs=f' data-u="{T.SLUG[u]}"')

ORDER = [c[1] for c in T.CHARS if c[1] in T.MSLUG]   # 前へ・次への並び

def char_page(cid):
    d, c = CD[cid], CH[cid]
    u = cid[:3]; m = UNIT[u]
    col = d["colors"]
    # せりふは旧サイトと同じく、立ち絵の肩に縦書きの2本で出す（行末の句読点は付けない）
    lines = [x.rstrip("。、") for x in d["tagline"].split("\n")]
    quote = "".join(f'<span class="col{" low" if k else ""}">{esc(x)}</span>' for k, x in reversed(list(enumerate(lines))))
    rows = [("誕生日", d["birthday"]), ("身長", f'{d["height"]}cm'), ("年齢", f'{d["age"]}歳'),
            ("趣味", "、".join(d["hobby"])), ("好きなもの", d["like"]), ("苦手なもの", d["dislike"])]
    dl = "".join(f"<div><dt>{k}</dt><dd>{esc(str(v))}</dd></div>" for k, v in rows)
    tags = ('<ul class="tags">' + "".join(f"<li>#{esc(t)}</li>" for t in TAGS[cid]) + "</ul>") if cid in TAGS else ""
    mates = "".join(face(i.lower(), s) for i, s in zip([x for x in UD[u]["members"] if x.lower() != cid], [".0", "-.1"]))
    i = ORDER.index(cid); pv, nx = CH[ORDER[i - 1]], CH[ORDER[(i + 1) % len(ORDER)]]
    inner = f'''{T.header(PRE, top=False)}
<main>
<section class="fv ch" style="--cm:{col["main"]};--cs:{col["sub"]};--ca:{col["accent"]}">
  <div class="ch-art"><i class="bg-main"></i><i class="bg-dia"></i><i class="bg-line"></i><a class="ch-em" href="{T.uhref(u, PRE)}" aria-label="{m["name"]}"><img src="{PRE}images/emblem/{m["no"]}.webp" alt=""></a><button class="ch-sw" type="button" aria-label="立ち絵の見え方を切り替える（アップ・全身）" aria-pressed="false"><i></i><i></i></button><p class="vq" aria-label="{esc(" ".join(d["tagline"].split()))}">{quote}</p><span class="ch-img"><img src="{PRE}images/chara/{T.fid(c)}.webp" alt="{c[2]}{c[3]}" data-speed=".05"></span><i class="bg-deco"></i></div>
  <div class="ch-t"><p class="ch-u"><a href="{T.uhref(u, PRE)}">{m["name"]}</a></p><h1>{T.name(c)}</h1><p class="ch-r">{esc(d["roma"].title())}</p>{tags}</div>
</section>
<section class="sec" id="profile"><p class="ghost" aria-hidden="true" data-speedx="-.35">Profile</p>{h2("Profile", "プロフィール", 1, 3)}<div class="prose"><p>{esc(d["bio"])}</p></div><dl class="pf">{dl}</dl></section>
<section class="sec" id="motif"><p class="ghost" aria-hidden="true" data-speedx=".35">Motif</p>{h2("Motif", "モチーフ", 2, 3)}<div class="prose"><h3 class="mt">{esc(d["motif"])}<small>{esc(d["motifEn"])}</small></h3><p>{esc(d["trivia"])}</p></div></section>
<section class="sec" id="unit"><p class="ghost" aria-hidden="true" data-speedx="-.35">Unit</p>{h2("Unit", "ユニット", 3, 3)}<p class="un"><a href="{T.uhref(u, PRE)}">{m["name"]}<small>{m["kana"]}</small></a></p><div class="mems big">{mates}</div></section>
<nav class="sec pn" aria-label="前後のメンバー"><a href="{T.mhref(pv, PRE)}"><small>Prev</small><span>{T.name(pv)}</span></a><a href="{T.mhref(nx, PRE)}"><small>Next</small><span>{T.name(nx)}</span></a></nav>
</main>
{T.footer()}<script>{SWJS}</script>'''
    return T.page(f'{c[2]}{c[3]} | Humming Hearts', esc(d["bio"]), PRE, inner, css=("page.css",), attrs=f' data-u="{T.SLUG[u]}"')

# 立ち絵の切り替え（アップ ⇄ 全身）。いったん左へ消えて、右から入り直す
SWJS = """(function(){var b=document.querySelector('.ch-sw'),w=document.querySelector('.ch-img');if(!b||!w)return;
b.addEventListener('click',function(){w.classList.add('out');setTimeout(function(){var f=w.classList.toggle('full');b.setAttribute('aria-pressed',f?'true':'false');w.classList.remove('out')},160)})})();"""

CSS = """
/* 個別ページ（ユニット・メンバー）だけの見た目。色・文字・見出し・線の約束は style.css と同じ */
.prose{max-width:640px}
.prose p{margin:0 0 1.6em;font-size:15px;line-height:2.2}
.mems.big{grid-template-columns:repeat(3,1fr);gap:28px 10px;max-width:640px}.mems.big .ph{width:104px;height:104px}.mems.big .mem{font-size:14px}
.rels.solo{grid-template-columns:minmax(0,300px)}
.others{padding-top:96px}.others .lbl{margin-bottom:8px}
.others .m-nav a{font-size:30px;flex-wrap:wrap;gap:6px 14px}.others .m-nav small{white-space:nowrap;letter-spacing:.12em}
/* unit first screen */
.uh{height:auto;overflow:clip;padding-top:150px}
/* the unit's emblem, large: on its own page the mark is the first thing seen */
.uh-em{width:176px;height:176px;margin:0 0 18px -10px}
.uh-t{position:relative;z-index:2;padding-inline:24px}
.uh h1{margin:0;font:500 50px/1 var(--en);letter-spacing:-.01em}
.uh h1 small{display:block;margin-top:12px;font:400 12px/1 var(--jp);letter-spacing:.16em;color:var(--sub)}
.uh-tag{margin:22px 0 0;font:500 13px/1.6 var(--jp);letter-spacing:.12em;color:var(--sub)}
.uh-c{margin:6px 0 0;font:500 21px/1.7 var(--min);letter-spacing:.06em}
.uh-pic{display:block;margin-top:36px;aspect-ratio:4/3;overflow:hidden}
.uh-pic img{width:100%;height:100%;object-fit:cover;scale:1.16}
/* member first screen, as on the old site: the member's main colour slides in as a panel, a square in the
   sub colour turns into place, the accent line grows down the edge, a slanted two-colour strip closes the foot,
   then the figure rises, the unit emblem appears and the member's line is unrolled beside the shoulder.
   job: the member's own three colours become their backdrop, and their voice is the first thing read */
.ch{height:auto;overflow:clip;padding-top:136px}
.ch-art{position:relative;display:block;height:470px;overflow:hidden;background:var(--faint);filter:grayscale(1);transition:filter .8s ease}
.fv.lit .ch-art{filter:none}
.bg-main{position:absolute;left:0;top:0;width:100%;height:62%;background:linear-gradient(165deg,color-mix(in oklab,var(--cm) 82%,#fff) 0%,var(--cm) 70%);animation:pSlide .3s cubic-bezier(.3,.6,.3,1) both}
.bg-main::after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(135deg,rgba(255,255,255,.035) 0 6px,transparent 6px 13px)}
.bg-dia{position:absolute;top:-12%;right:-8%;width:80%;aspect-ratio:1;background:linear-gradient(135deg,color-mix(in oklab,var(--cs) 84%,#fff) 0%,var(--cs) 75%);rotate:45deg;animation:pDia .3s ease-out .12s both}
.bg-line{position:absolute;right:0;top:0;bottom:0;width:13px;background:var(--ca);z-index:1;transform-origin:top;animation:pBar .25s cubic-bezier(.3,.6,.3,1) .2s both}
.bg-deco{position:absolute;left:0;right:0;bottom:0;z-index:3;height:30px;pointer-events:none;animation:pSlide .28s cubic-bezier(.3,.6,.3,1) .28s both}
.bg-deco::before{content:"";position:absolute;inset:0;background:linear-gradient(135deg,color-mix(in oklab,var(--cs) 80%,#fff),var(--cs));clip-path:polygon(0 38%,100% 0,100% 100%,0 100%)}
.bg-deco::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in oklab,var(--ca) 78%,#000) 0%,var(--ca) 100%);clip-path:polygon(0 52%,100% 14%,100% 100%,0 100%)}
.ch-img{position:absolute;inset:0;z-index:2;display:flex;justify-content:center;align-items:flex-start;animation:pUp .38s cubic-bezier(.22,.68,.3,1) .34s both}
.ch-img img{height:205%;width:auto;max-width:none;margin:14px 0 0 14%}
.ch-img img{transition:opacity .16s ease,transform .16s ease}
.ch-img.out img{opacity:0;transform:translateX(-18px)}
.ch-img.full{align-items:flex-end}.ch-img.full img{height:94%;margin:0 0 30px}
/* switch between close-up and full figure: two arrows pointing opposite ways */
.ch-sw{position:absolute;z-index:5;right:25px;top:12px;width:44px;height:44px;padding:0;border:1px solid var(--ink);border-radius:50%;background:var(--bg);color:var(--ink);cursor:pointer;animation:pFade .3s ease .5s both;transition:background .25s,color .25s}
.ch-sw:hover,.ch-sw[aria-pressed=true]{background:var(--ink);color:var(--bg)}
.ch-sw i{position:absolute;left:12px;width:18px;height:1px;background:currentColor}
.ch-sw i:first-child{top:17px}.ch-sw i:last-child{top:25px}
.ch-sw i::after{content:"";position:absolute;top:-3px;width:6px;height:6px;border-top:1px solid currentColor;border-right:1px solid currentColor}
.ch-sw i:first-child::after{right:0;rotate:45deg}.ch-sw i:last-child::after{left:0;rotate:-135deg}
.tags{list-style:none;margin:22px 0 0;padding:18px 0 0;border-top:1px solid var(--line);display:flex;flex-wrap:wrap;gap:6px 18px;font:500 14px/1.8 var(--jp);letter-spacing:.06em}
.ch-em{position:absolute;z-index:4;left:12px;top:12px;width:64px;height:64px;animation:pFade .3s ease .5s both}
.ch-em img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 0 2px rgba(255,255,255,.6))}
.vq{position:absolute;z-index:4;left:26px;top:26%;margin:0;display:flex;gap:7px;align-items:flex-start}
.vq .col{writing-mode:vertical-rl;white-space:nowrap;padding:12px 7px;background:rgba(20,20,20,.86);color:#fff;font:500 14px/1.5 var(--min);letter-spacing:.1em;animation:pRoll .8s cubic-bezier(.3,.6,.3,1) .6s both}
.vq .col.low{margin-top:28px;animation-delay:.75s}
@keyframes pSlide{from{transform:translateX(-101%)}to{transform:none}}
@keyframes pDia{from{opacity:0;rotate:49deg;scale:.97}to{opacity:1;rotate:45deg;scale:1}}
@keyframes pFade{from{opacity:0}to{opacity:1}}
@keyframes pBar{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes pRoll{from{clip-path:inset(0 0 100% 0)}to{clip-path:inset(0 0 0 0)}}
.ch-t{padding:30px 24px 0}
.ch-u{margin:0 0 10px;font:italic 500 18px/1 var(--en)}.ch-u a{border-bottom:1px solid var(--ink);padding-bottom:2px;display:inline-flex;min-height:44px;align-items:center}
.ch h1{margin:0;font:500 40px/1.5 var(--min);letter-spacing:.1em}
.ch-r{margin:2px 0 0;font:italic 500 18px/1 var(--en);letter-spacing:.04em;color:var(--sub)}
.pf{margin:36px 0 0;max-width:640px;border-top:1px solid var(--ink)}
.pf div{display:grid;grid-template-columns:104px 1fr;gap:12px;padding:14px 0;border-bottom:1px solid var(--line)}
.pf dt{font:500 12px/2.4 var(--jp);letter-spacing:.14em;color:var(--sub)}.pf dd{margin:0;font-size:15px}
.mt{margin:0 0 16px;font:500 26px/1.4 var(--min);letter-spacing:.08em;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.mt small{font:italic 500 17px var(--en);letter-spacing:.02em;color:var(--sub)}
.un{margin:0 0 36px}.un a{display:inline-flex;align-items:baseline;gap:14px;min-height:44px;font:italic 500 34px/1.1 var(--en);border-bottom:1px solid var(--ink);padding-bottom:6px}
.un small{font:500 12px/1 var(--jp);font-style:normal;color:var(--sub);letter-spacing:.2em}
.pn{padding-top:96px;display:grid;grid-template-columns:1fr 1fr}
.pn a{display:grid;gap:4px;padding:18px 0;border-block:1px solid var(--ink);font:500 16px/1.6 var(--min);letter-spacing:.06em;transition:background .25s,color .25s}
.pn a+a{text-align:right;border-left:1px solid var(--ink)}
.pn a:first-child{padding-left:14px}.pn a+a{padding-right:14px}
.pn small{font:italic 500 16px/1 var(--en);color:var(--sub)}
.pn a:hover{background:var(--ink);color:var(--bg)}.pn a:hover small{color:inherit}
@media(min-width:900px){
 .prose p{font-size:16px}
 .mems.big{grid-template-columns:repeat(3,200px);gap:48px}.mems.big .ph{width:180px;height:180px;margin-bottom:16px}.mems.big .mem{font-size:17px}
 .rels.solo{grid-template-columns:340px}
 .others{padding-top:160px}.others .m-nav a{font-size:44px}
 .uh{padding-top:190px;display:grid;grid-template-columns:1fr 1fr;align-items:center;column-gap:60px;padding-inline:max(32px,calc(50% - 540px))}
 .uh-em{width:300px;height:300px;margin:0 0 20px -18px}
 .uh-t{padding:0}.uh h1{font-size:84px}.uh-tag{font-size:14px;margin-top:32px}.uh-c{font-size:28px}
 .uh-pic{margin-top:0}
 .ch{padding-top:96px;display:grid;grid-template-columns:1fr 1fr;align-items:center}
 .ch-art{height:760px}.bg-dia{width:580px;top:-40px;right:-238px}.bg-line{width:24px}.bg-deco{height:42px}
 .ch-img img{height:165%;margin:40px 0 0 8%}.ch-em{left:14px;top:14px;width:84px;height:84px}.ch-sw{right:40px;top:16px}.ch-img.full img{margin:0 0 42px}.tags{font-size:16px;margin-top:32px;padding-top:26px}
 .vq{left:64px;top:18%;gap:11px}.vq .col{font-size:19px;letter-spacing:.14em;line-height:1.7;padding:18px 10px}.vq .col.low{margin-top:74px}
 .ch-t{padding:0 0 0 72px;max-width:540px}.ch h1{font-size:58px}
 .pf div{grid-template-columns:160px 1fr}
 .pn{padding-top:160px}.pn a{font-size:20px;padding:26px 24px}
}
@media(prefers-reduced-motion:reduce){.ch-art{filter:none}}
"""

def main():
    out = [(f"units/{T.SLUG[u]}.html", unit_page(u)) for u in UNIT if u in T.PAGES]
    out += [(f"members/{T.MSLUG[c]}.html", char_page(c)) for c in ORDER]
    out.append(("css/page.css", CSS.lstrip("\n")))
    for path, text in out:
        full = os.path.join(T.ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f: f.write(text)
        print("ok", path)

if __name__ == "__main__":
    main()
