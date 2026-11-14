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
        "trt03": ["風まかせな旅ツバメ", "三味線", "写真好き"],
        # ここから下は Kさんが 2026-11-13 に決めたもの（/mnt/project-files/plan/member-tags-final.md）
        "nct01": ["孤高のハヤブサ", "ブラコン（本人は否定）", "実は下戸"],
        "nct02": ["みんなのお兄ちゃんフクロウ", "カカオ中毒", "私服はちょいダサ"],
        "prs01": ["自然派のサンコウチョウ", "古民家暮らし", "トリートメントは使ってません"],
        "prs02": ["陽キャなワカケホンセイインコ", "人類皆兄弟！", "巷で評判のチャラ兄"],
        "blc01": ["カリスマカラス", "意外と常識人", "こだわりのバスローブ"],
        "blc02": ["面倒見のいいカササギ", "脳みそは筋肉です", "セインはジム友"],
        "blc03": ["天才肌なカケス", "省エネ主義", "積みゲー消化中"],
        "orb01": ["エスコート上手なベニマシコ", "アイドルに憧れて", "僕はみんなのもの"],
        "orb02": ["元気っ子なキクイタダキ", "基本的に見切り発車", "日曜の夕方は笑点一択"],
        "orb03": ["しっかり者のルリビタキ", "モーニングルーティーンがある", "どう考えても僕が兄"],
        "orb04": ["大ざっぱなジョウビタキ", "弟の小言はスルー", "そうだ、亀飼おう！"]}


UNIT = {u: dict(no=no, name=n, kana=kana, tag=tg, c=c) for no, u, code, n, kana, tg, c, cnt in T.UNITS}
CH = {c[1]: c for c in T.CHARS}
esc = html.escape

def ruby_text(s):
    """[[名前|よみ]] をふりがな付きに、[[名前]] をそのままの名前にする"""
    s = esc(s)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", lambda m: T.rb(m.group(1), m.group(2)), s)
    return re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)

def h2(en, jp, i, n, pc=None):
    num = lambda a, b: f'{a:02d}<b>/{b:02d}</b>'
    idx = num(i, n) if pc is None else f'<span class="n-sp">{num(i, n)}</span><span class="n-pc">{num(*pc)}</span>'
    return f'<h2><span>{en}</span><small>{jp}</small><i class="idx" aria-hidden="true">{idx}</i></h2>'

def face(cid, speed=".0"):
    c = CH[cid]
    return f'<a class="mem" href="{T.mhref(c, PRE)}" data-speed="{speed}"><span class="ph"><img src="{PRE}images/face/{T.fid(c)}.webp" alt=""></span><span>{T.name(c)}</span></a>'

def rels_of(u): return [r for r in T.RELS if r[1] == u]

def unit_page(u):
    d, m = UD[u], UNIT[u]
    no = m["no"]
    # 紹介文とキャッチコピーが無いユニットは、旧サイトの短い紹介文を出し、キャッチコピーの行は出さない（文は作らない）
    intro = "".join(f"<p>{ruby_text(p)}</p>" for p in d.get("intro") or [d["blurb"]])
    catch = f'<p class="uh-c">{esc(d["catch"])}</p>' if d.get("catch") else ""
    kv = u in T.KV   # 集合絵が無いユニットは、絵の場所に紋章を大きく出す
    mems = "".join(face(i.lower(), s) for i, s in zip(d["members"], [".0", "-.1", ".06", "-.04"]))
    more = f'<p class="row more"><a class="btn" href="{PRE}songs.html?u={T.SLUG[u]}">Songs</a></p>' if rels_of(u) else ""
    rels = "".join(f'''
      <article class="rel"><a class="ph" href="{T.MV.get(n, T.YT_CH)}"><img src="{PRE}images/jacket/{T.JK[n]}.webp" alt="{t} のジャケット">{T.jo(n)}</a>
        <h3>{T.rb(t, k)}</h3><p class="by">{T.kn(un)}</p>{T.lk(n)}{T.ep_btn(n, PRE)}</article>''' for n, ru, t, k, un in T.RELS if ru == u)
    others = "".join(f'<a href="{T.uhref(o, PRE)}">{T.kn(UNIT[o]["name"])}<small>{UNIT[o]["kana"]}</small></a>' for o in UNIT if o != u and o in T.PAGES)
    inner = f'''{T.header(PRE, top=False)}
<main>
<section class="fv uh">
  <div class="uh-t">{f'<img class="uh-em" src="{PRE}images/emblem/{no}.webp" alt="">' if kv else ""}<h1>{T.kn(m["name"])}{f"<small>{m[chr(107)+chr(97)+chr(110)+chr(97)]}</small>" if m["kana"] else ""}</h1><p class="uh-tag">{esc(d["tagline"])}</p>{catch}</div>
  {f'<div class="uh-pic ph"><img src="{PRE}images/kv/{no}.webp" alt="{m["name"]}" data-speed=".08"></div>' if kv else f'<div class="uh-pic em"><img src="{PRE}images/emblem/{no}.webp" alt="" data-speed=".08"></div>'}
</section>
<section class="sec" id="about"><p class="ghost" aria-hidden="true" data-speedx="-.35">About</p>{h2("About", "紹介", 1, 3)}<div class="prose">{intro}</div></section>
<section class="sec" id="members"><p class="ghost" aria-hidden="true" data-speedx=".35">Members</p>{h2("Members", "メンバー", 2, 3)}<div class="mems big">{mems}</div></section>
<section class="sec" id="release"><p class="ghost" aria-hidden="true" data-speedx="-.35">Release</p>{h2("Release", "楽曲", 3, 3)}<div class="rels solo">{rels}</div>{more}</section>
<nav class="sec others" aria-label="ほかのユニット"><p class="lbl">Units</p><div class="m-nav">{others}</div></nav>
</main>
{T.footer()}'''
    return T.page(f'{m["name"]} | Humming Hearts', esc(d.get("catch") or d["blurb"]), PRE, inner, css=("page.css",), attrs=f' data-u="{T.SLUG[u]}"')

def songs_page():
    """楽曲ページ：全曲のジャケットを並べ、気分（Mood）とユニット（Unit）の2段で絞り込む。聴き比べる場所なので、動かさず同じ大きさで並べる"""
    pre = ""
    def row(k, lbl, aria, items):
        ps = f'<button class="md on" type="button" data-k="{k}" data-v="" aria-pressed="true">すべて</button>' + "".join(
            f'<button class="md" type="button" data-k="{k}" data-v="{esc(v)}" aria-pressed="false">{esc(t)}</button>' for v, t in items)
        return f'<div class="flt"><p class="lbl">{lbl}</p><div class="moods" role="group" aria-label="{aria}">{ps}</div></div>'
    units = [(T.SLUG[u], UNIT[u]["name"]) for u in UNIT if any(r[1] == u for r in T.RELS)]   # 曲があるユニットだけ
    rows = row("m", "Mood", "気分で選ぶ", [(m, m) for m in T.used_moods()]) + row("u", "Unit", "ユニットで選ぶ", units)
    cards = "".join(f'''
      <article class="rel" data-m="{esc("|".join(T.MOOD.get(n, [])))}" data-u="{T.SLUG[ru]}"><a class="ph" href="{T.MV.get(n, T.YT_CH)}"><img src="{pre}images/jacket/{T.JK[n]}.webp" alt="{t} のジャケット">{T.jo(n)}</a>
        <h3>{T.rb(t, k)}</h3><p class="by">{T.kn(un)}</p><p class="sg-m">{"".join(f'<button class="tg" type="button" data-v="{esc(m)}">{esc(m)}</button>' for m in T.MOOD.get(n, []))}</p>
        {T.lk(n)}{T.ep_btn(n, pre)}</article>''' for n, ru, t, k, un in T.RELS)
    inner = f'''{T.header(pre, top=False)}
<main>
<section class="sec sg" id="songs"><p class="ghost" aria-hidden="true" data-speedx=".35">Songs</p><h2><span>Songs</span><small>楽曲</small></h2>
  <div class="flts">{rows}</div>
  <div class="rels sgs">{cards}</div>
</section>
</main>
{T.footer()}<script>{SGJS}</script>'''
    return T.page("楽曲 | Humming Hearts", "Humming Hearts の楽曲一覧。気分とユニットで選べます。", pre, inner, css=("page.css",))

SGJS = """(function(){var ps=[].slice.call(document.querySelectorAll('.sg .md')),cs=[].slice.call(document.querySelectorAll('.sgs .rel')),st={m:'',u:''};
function ok(c,m,u){return(!m||c.dataset.m.split('|').indexOf(m)>=0)&&(!u||c.dataset.u===u)}
function draw(){ps.forEach(function(p){var k=p.dataset.k,v=p.dataset.v,on=st[k]===v;p.classList.toggle('on',on);p.setAttribute('aria-pressed',on?'true':'false');
/* a word that would leave no song with the other row's choice is dimmed and cannot be pressed = never an empty page */
p.disabled=!on&&!cs.some(function(c){return k==='m'?ok(c,v,st.u):ok(c,st.m,v)})});
/* reorder motion: each jacket slides from where it was to where it goes, so the eye can follow which songs stayed */
var mv=!matchMedia('(prefers-reduced-motion: reduce)').matches&&!!document.body.animate,old=new Map();
if(mv)cs.forEach(function(c){if(!c.hidden)old.set(c,c.getBoundingClientRect())});
cs.forEach(function(c){c.hidden=!ok(c,st.m,st.u)});
if(mv)cs.forEach(function(c){if(c.hidden)return;var n=c.getBoundingClientRect(),o=old.get(c);
if(o){var dx=o.left-n.left,dy=o.top-n.top;if(dx||dy)c.animate([{transform:'translate('+dx+'px,'+dy+'px)'},{transform:'none'}],{duration:480,easing:'cubic-bezier(.2,.7,.2,1)'})}
else c.animate([{opacity:0,transform:'translateY(16px)'},{opacity:1,transform:'none'}],{duration:420,delay:120,easing:'ease-out',fill:'backwards'})})}
ps.forEach(function(p){p.addEventListener('click',function(){st[p.dataset.k]=p.dataset.v;draw();
try{var q=[];if(st.m)q.push('m='+encodeURIComponent(st.m));if(st.u)q.push('u='+encodeURIComponent(st.u));history.replaceState(null,'',q.length?'?'+q.join('&'):location.pathname)}catch(e){}})});
[].forEach.call(document.querySelectorAll('.sgs .tg'),function(t){t.addEventListener('click',function(){st.m=t.dataset.v;if(!cs.some(function(c){return ok(c,st.m,st.u)}))st.u='';draw()})});
try{var sp=new URLSearchParams(location.search);['m','u'].forEach(function(k){var v=sp.get(k)||'';if(v&&ps.some(function(p){return p.dataset.k===k&&p.dataset.v===v}))st[k]=v})}catch(e){}
if(st.m&&st.u&&!cs.some(function(c){return ok(c,st.m,st.u)}))st.u='';
draw()})();"""

# 開いた直後にも帯が伸びる動きを見せるため、最初の1コマを描いてから「準備できた」の印を付ける
# 【お試し】タグの形の案を見比べるための切り替え（アドレスの最後に ?tag=1 / 2 / 4）。形が決まったら消す
TGV = "(function(){var m=location.search.match(/[?&]tag=([124])/);if(!m)return;document.documentElement.classList.add('tg'+m[1]);document.querySelectorAll('.ch-nv a').forEach(function(a){a.href+='?tag='+m[1]})})();"
RDY = "requestAnimationFrame(function(){requestAnimationFrame(function(){document.documentElement.classList.add('rdy')})})"
ORDER = [c[1] for c in T.CHARS if c[1] in T.MSLUG]   # 前へ・次への並び

QCUT = {"でもそれ以上にワクワクしてるッス！": 7}   # 帯を分ける位置の指定（行の文 → 何字目の後ろで分けるか）。律：Kさんの指定（2026-11-13）。文は変えない
QMAX, QLOW = 17, 14   # せりふの帯1本の字数の上限／下げる帯がこの字数以上なら上下を入れ替える

def char_page(cid):
    d, c = CD[cid], CH[cid]
    u = cid[:3]; m = UNIT[u]
    col = d["colors"]
    # せりふは旧サイトと同じく、立ち絵の肩に縦書きの2本で出す（行末の句読点は付けない）
    lines = [x.rstrip("。、") for x in d["tagline"].split("\n")]
    # 帯の長さの決まり（下のタグの帯に重ならないため。2026-11-13）：
    #  1) 1本は QMAX 字まで。超える行は、真ん中にいちばん近い「、」で2本に分ける（文は変えない。帯の切れ目になるだけ）
    #  2) 一段下げるのは2行目。ただし下げる帯が QLOW 字以上のときは、1行目のほうを下げる（長い帯を上から始める）
    cols = []
    for k, x in enumerate(lines):
        if x in QCUT:   # Kさんが切れ目を指定した行
            cols += [(x[:QCUT[x]], k), (x[QCUT[x]:], k)]
        elif len(x) > QMAX:
            cut = min((i for i, ch in enumerate(x) if ch == "、"), key=lambda i: abs(i - len(x) / 2), default=None)
            assert cut is not None, f"せりふの行が長すぎて分けられない（「、」が無い）: {x}"
            cols += [(x[:cut], k), (x[cut + 1:], k)]
        else:
            cols.append((x, k))
    assert all(len(x) <= QMAX for x, _ in cols), cols
    if any(k and len(x) >= QLOW for x, k in cols):
        cols = [(x, 0 if k else 1) for x, k in cols]
    quote = "".join(f'<span class="col{" low" if k else ""}">{esc(x)}</span>' for x, k in reversed(cols))
    rows = [("誕生日", d["birthday"]), ("身長", f'{d["height"]}cm'), ("年齢", f'{d["age"]}歳'),
            ("趣味", "、".join(d["hobby"])), ("好きなもの", d["like"]), ("苦手なもの", d["dislike"])]
    dl = "".join(f"<div><dt>{k}</dt><dd>{esc(str(v))}</dd></div>" for k, v in rows)
    tags = ('<ul class="tags">' + "".join(f"<li>#{esc(t)}</li>" for t in TAGS[cid]) + "</ul>") if cid in TAGS else ""
    # タブレット幅では、タグを立ち絵の上にメインカラーの帯で縦に並べる。帯が明るい色の人は、白ではなく黒の文字にして読めるようにする
    r, g, b = (int(col["main"][i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = sum(w * (v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4) for w, v in zip((.2126, .7152, .0722), (r, g, b)))
    tags_a = tags.replace('class="tags"', f'class="tags-a" style="--tc:{"#141414" if lum > .36 else "#fff"}"') if tags else ""
    tags_a = tags_a.replace("<li>", "<li><span>").replace("</li>", "</span></li>")
    # モチーフの鳥の絵（ある人だけ）。モチーフの段の背景に置き、スクロールでゆっくりずれる
    bird = f'<img class="mt-b" src="{PRE}images/bird/{T.aid(c)}.webp" alt="" data-speed=".08">' if os.path.exists(os.path.join(HERE, "..", "public", "images", "bird", T.aid(c) + ".webp")) else ""
    mates = "".join(face(i.lower(), s) for i, s in zip([x for x in UD[u]["members"] if x.lower() != cid], [".0", "-.1", ".06"]))
    i = ORDER.index(cid); pv, nx = CH[ORDER[i - 1]], CH[ORDER[(i + 1) % len(ORDER)]]
    # 前後のメンバーへ移る丸いボタン（名前の段の右上。ページのいちばん下の Prev / Next と同じ行き先）
    nav = (f'<p class="ch-nv"><a class="pv" href="{T.mhref(pv, PRE)}" aria-label="前のメンバー：{pv[2]}{pv[3]}"></a>'
           f'<a class="nx" href="{T.mhref(nx, PRE)}" aria-label="次のメンバー：{nx[2]}{nx[3]}"></a></p>')
    # PC では、プロフィールを最初の画面の右側にまとめて出す（スマホは下の Profile の段のまま）
    prof = f'<div class="ch-p"><p>{esc(d["bio"])}</p><dl class="pf">{dl}</dl></div>'
    # そのメンバーが歌っている曲（＝ユニットの曲）。カードはユニットのページと同じもの（Kさんの回答 2026-11-14）
    songs = "".join(f'''
      <article class="rel"><a class="ph" href="{T.MV.get(n, T.YT_CH)}"><img src="{PRE}images/jacket/{T.JK[n]}.webp" alt="{t} のジャケット">{T.jo(n)}</a>
        <h3>{T.rb(t, k)}</h3><p class="by">{T.kn(un)}</p>{T.lk(n)}{T.ep_btn(n, PRE)}</article>''' for n, ru, t, k, un in T.RELS if ru == u)
    k = 1 if songs else 0   # 曲の段がある人は、後ろの段の番号が1つずつ増える
    songs_sec = f'''<section class="sec" id="songs"><p class="ghost" aria-hidden="true" data-speedx=".35">Songs</p>{h2("Songs", "楽曲", 2, 4, (1, 3))}<div class="rels solo">{songs}</div><p class="row more"><a class="btn" href="{PRE}songs.html?u={T.SLUG[u]}">Songs</a></p></section>''' if songs else ""
    inner = f'''{T.header(PRE, top=False)}
<main>
<section class="fv ch" style="--cm:{col["main"]};--cs:{col["sub"]};--ca:{col["accent"]}">
  <div class="ch-art"><i class="bg-main"></i><i class="bg-dia"></i><i class="bg-line"></i><button class="ch-sw" type="button" aria-label="立ち絵の見え方を切り替える（アップ・全身）" aria-pressed="false"><i></i><i></i></button><p class="vq" aria-label="{esc(" ".join(d["tagline"].split()))}">{quote}</p><span class="ch-img"><img src="{PRE}images/chara/{T.aid(c)}.webp" alt="{c[2]}{c[3]}" data-speed=".05"></span>{tags_a}<i class="bg-deco"></i></div>
  <div class="ch-t">{nav}<p class="ch-u"><a href="{T.uhref(u, PRE)}"><img src="{PRE}images/emblem/{m["no"]}.webp" alt="">{T.kn(m["name"])}</a></p><h1>{T.name(c)}</h1><p class="ch-r">{esc(d["roma"].title())}</p>{tags}{prof}</div>
</section>
<section class="sec" id="profile"><p class="ghost" aria-hidden="true" data-speedx="-.35">Profile</p>{h2("Profile", "プロフィール", 1, 3 + k)}<div class="prose"><p>{esc(d["bio"])}</p></div><dl class="pf">{dl}</dl></section>
{songs_sec}
<section class="sec{" has-b" if bird else ""}" id="motif"><p class="ghost" aria-hidden="true" data-speedx=".35">Motif</p>{h2("Motif", "モチーフ", 2 + k, 3 + k, (1 + k, 2 + k))}{bird}<div class="prose mt-p"><h3 class="mt">{esc(d["motif"])}<small>{esc(d["motifEn"])}</small></h3><p>{esc(d["trivia"])}</p></div></section>
<section class="sec" id="unit"><p class="ghost" aria-hidden="true" data-speedx="-.35">Unit</p>{h2("Unit", "ユニット", 3 + k, 3 + k, (2 + k, 2 + k))}<p class="un"><a href="{T.uhref(u, PRE)}">{T.kn(m["name"])}<small>{m["kana"]}</small></a></p><div class="mems big">{mates}</div></section>
<nav class="sec pn" aria-label="前後のメンバー"><a href="{T.mhref(pv, PRE)}"><small>Prev</small><span>{T.name(pv)}</span></a><a href="{T.mhref(nx, PRE)}"><small>Next</small><span>{T.name(nx)}</span></a></nav>
</main>
{T.footer()}<script>{SWJS}</script><script>{TGV}{RDY}</script>'''
    return T.page(f'{c[2]}{c[3]} | Humming Hearts', esc(d["bio"]), PRE, inner, css=("page.css",), attrs=f' data-u="{T.SLUG[u]}"', share=f'{c[2]}{c[3]}（{m["name"]}） | Humming Hearts')   # 共有の文面のたたき台（Kさんの確認待ち）

# 立ち絵の切り替え（アップ ⇄ 全身）。いったん左へ消えて、右から入り直す
SWJS = """(function(){var b=document.querySelector('.ch-sw'),w=document.querySelector('.ch-img');if(!b||!w)return;
b.addEventListener('click',function(){w.classList.add('out');setTimeout(function(){var f=w.classList.toggle('full');b.setAttribute('aria-pressed',f?'true':'false');w.classList.remove('out')},160)})})();"""

CSS = """
/* songs page: same-size jackets in a plain grid (no drift, no stagger) = easy to compare */
.sg{padding-bottom:96px}
/* two rows of words, each with a small name on the left: Mood = by feeling, Unit = by who sings */
.flts{display:grid;gap:18px;margin-bottom:40px}.flt{display:grid;gap:10px}
.md:disabled{opacity:.3;cursor:default;background:none;color:inherit}
.sgs{padding-bottom:0}.sgs .rel{margin-top:0!important}.sgs .rel[hidden]{display:none}
/* mood tags on each song: small pills; pressing one picks that mood above */
.sg-m{margin:8px 0 0;display:flex;flex-wrap:wrap;gap:6px}
.tg{appearance:none;background:none;margin:0;cursor:pointer;min-height:24px;padding:0 10px;border:1px solid var(--line);border-radius:999px;font:500 11px/1 var(--jp);letter-spacing:.06em;color:var(--sub);white-space:nowrap;transition:border-color .25s,color .25s}
.tg:hover{border-color:var(--ink);color:var(--ink)}
.lk button{font:inherit;letter-spacing:inherit}
@media(min-width:900px){.sgs{grid-template-columns:repeat(3,1fr);gap:56px 48px}.flts{margin-bottom:64px}.flt{grid-template-columns:64px 1fr;align-items:center;gap:20px}}

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
.uh-pic.em{aspect-ratio:1;max-width:420px;margin-inline:auto;padding-inline:24px}.uh-pic.em img{object-fit:contain;scale:1}
.more{margin:28px auto 0;width:fit-content}.more .btn{min-width:180px}
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
.ch-t{position:relative;padding:30px 24px 0}
.ch-p,.n-pc,.tags-a{display:none}
/* motif bird: below the text on phones, beside the text on wide screens; it never sits under the words */
/* モチーフの鳥: 下から2番目の層（薄い大きな見出し文字のすぐ上、文章の下）に大きく薄く置く。文章と少し重なってよい。段の外へは出さない（切らない） */
.has-b{padding-bottom:110px;min-height:calc(66vw + 330px)}.has-b .mt-p{position:relative;z-index:1}
.mt-b{position:absolute;z-index:0;left:3vw;top:230px;width:94vw;max-width:none;height:auto;opacity:.42;pointer-events:none}
@media(min-width:700px){.has-b{padding-bottom:150px;min-height:calc(min(62vw,760px)*.68 + 380px)}.mt-b{left:auto;right:max(32px,calc(50% - 540px));top:250px;width:min(62vw,760px)}}
@media(min-width:700px) and (max-width:899px){.ch-art{height:600px}.ch-img img{height:190%}.vq{top:18%}}
@media(min-width:700px){
 .tags-a{position:absolute;z-index:4;left:0;bottom:52px;margin:0;padding:0;list-style:none;display:grid;gap:8px;justify-items:start}
 .tags-a li{padding:7px 16px 7px 26px;background:var(--cm);color:var(--tc);font:500 15px/1.5 var(--jp);letter-spacing:.06em}
 /* タグの帯の出入り: 絵が画面の真ん中に来たら、左の端から帯が1本ずつ伸び、文字があとから追いつく。離れると下の帯から順に左へ戻る（絵と同じ合図で動かす） */
 .js .tags-a li{clip-path:inset(0 100% 0 0);transition:clip-path .45s cubic-bezier(.7,0,.84,0)}
 .js .tags-a li span{display:inline-block;opacity:0;transform:translateX(-18px);transition:opacity .2s ease,transform .3s ease}
 .js .tags-a li:nth-child(2){transition-delay:.07s}.js .tags-a li:nth-child(1){transition-delay:.14s}
 .rdy .fv.lit .tags-a li{clip-path:inset(0);transition:clip-path .75s cubic-bezier(.16,1,.3,1) .45s}
 .rdy .fv.lit .tags-a li:nth-child(2){transition-delay:.57s}.rdy .fv.lit .tags-a li:nth-child(3){transition-delay:.69s}
 .rdy .fv.lit .tags-a li span{opacity:1;transform:none;transition:opacity .5s ease .7s,transform .7s cubic-bezier(.16,1,.3,1) .7s}
 .rdy .fv.lit .tags-a li:nth-child(2) span{transition-delay:.82s}.rdy .fv.lit .tags-a li:nth-child(3) span{transition-delay:.94s}
 @media(prefers-reduced-motion:reduce){.js .tags-a li,.js .tags-a li span{clip-path:none;opacity:1;transform:none;transition:none}}
 /* 【お試し】案1：右端をななめに切る */
 .tg1 .tags-a li{padding-right:36px}
 .tg1.js .tags-a li{clip-path:polygon(0 0,0 0,0 100%,0 100%)}
 .tg1.rdy .fv.lit .tags-a li{clip-path:polygon(0 0,100% 0,calc(100% - 18px) 100%,0 100%)}
 /* 【お試し】案2：帯をやめて細い線 */
 .tg2 .tags-a{gap:12px}
 .tg2 .tags-a li{position:relative;background:none;color:#141414;padding:4px 6px 7px 26px}
 .tg2.js .tags-a li,.tg2.rdy .fv.lit .tags-a li{clip-path:none}
 .tg2 .tags-a li::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:#141414;transform-origin:left;transition:transform .45s cubic-bezier(.7,0,.84,0)}
 .tg2.js .tags-a li::after{transform:scaleX(0)}
 .tg2.js .tags-a li:nth-child(2)::after{transition-delay:.07s}.tg2.js .tags-a li:nth-child(1)::after{transition-delay:.14s}
 .tg2.rdy .fv.lit .tags-a li::after{transform:none;transition:transform .75s cubic-bezier(.16,1,.3,1) .45s}
 .tg2.rdy .fv.lit .tags-a li:nth-child(2)::after{transition-delay:.57s}.tg2.rdy .fv.lit .tags-a li:nth-child(3)::after{transition-delay:.69s}
 /* 【お試し】案4：両端を丸くする */
 .tg4 .tags-a{left:26px;gap:10px}
 .tg4 .tags-a li{padding-inline:22px}
 .tg4.js .tags-a li{clip-path:inset(0 100% 0 0 round 99px)}
 .tg4.rdy .fv.lit .tags-a li{clip-path:inset(0 round 99px)}
 @media(prefers-reduced-motion:reduce){.tg1.js .tags-a li{clip-path:polygon(0 0,100% 0,calc(100% - 18px) 100%,0 100%)}.tg4.js .tags-a li{clip-path:inset(0 round 99px)}.tg2.js .tags-a li::after{transform:none;transition:none}}
 .ch-t .tags{display:none}
}
.ch-nv{position:absolute;right:24px;top:30px;margin:0;display:flex;gap:10px}
.ch-nv a{position:relative;width:44px;height:44px;border:1px solid var(--ink);border-radius:50%;transition:background .25s,color .25s}
.ch-nv a:hover{background:var(--ink);color:var(--bg)}
.ch-nv a::before{content:"";position:absolute;left:13px;top:21px;width:18px;height:1px;background:currentColor}
.ch-nv a::after{content:"";position:absolute;top:18px;width:6px;height:6px;border-top:1px solid currentColor;border-right:1px solid currentColor}
.ch-nv .nx::after{right:13px;rotate:45deg}.ch-nv .pv::after{left:13px;rotate:-135deg}
.ch-u{margin:0 0 10px;font:italic 500 18px/1 var(--en)}.ch-u a{display:inline-flex;min-height:44px;align-items:center;gap:12px}.ch-u img{width:52px;height:52px;object-fit:contain;margin-left:-4px}
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
 .ch{padding-top:96px;display:grid;grid-template-columns:1fr 1fr;align-items:center;padding-inline:max(0px,calc(50% - 640px))}
 .ch-art{height:760px}.bg-dia{width:580px;top:-40px;right:-238px}.bg-line{width:24px}.bg-deco{height:42px}
 .ch-img img{height:165%;margin:40px 0 0 8%}.ch-em{left:14px;top:14px;width:84px;height:84px}.ch-sw{right:40px;top:16px}.ch-img.full img{margin:0 0 42px}.tags{font-size:16px;margin-top:32px;padding-top:26px}
 .vq{left:64px;top:16%;gap:11px}.vq .col{font-size:19px;letter-spacing:.14em;line-height:1.7;padding:18px 10px}.vq .col.low{margin-top:74px}
 .ch-t{box-sizing:border-box;padding:0 32px 0 72px;max-width:684px}.ch h1{font-size:54px}.ch-nv{right:32px;top:10px}.ch-u{font-size:22px;margin-bottom:14px}.ch-u img{width:72px;height:72px;margin-left:-6px}
 .ch-p{display:block;margin-top:26px}.ch-p p{margin:0;font-size:15px;line-height:2}
 .ch-p .pf{margin-top:22px;display:grid;grid-template-columns:1fr 1fr;column-gap:32px}.ch-p .pf div{grid-template-columns:84px 1fr;gap:8px;padding:9px 0}.ch-p .pf dd{font-size:14px;line-height:2.1}
 @media(max-width:1099px){.ch-t{padding-left:44px}.ch h1{font-size:46px}.ch-p .pf{column-gap:20px}.ch-p .pf div{grid-template-columns:76px 1fr}}
 .tags-a{bottom:76px}.tags-a li{font-size:15px;padding:8px 16px 8px 24px}
 @media(max-width:1279px){.tags-a{display:none}.ch-t .tags{display:flex}}
 #profile,.n-sp{display:none}.n-pc{display:inline}.ch .tags{margin-top:22px;padding-top:18px;font-size:15px}
 .pf div{grid-template-columns:160px 1fr}
 .pn{padding-top:160px}.pn a{font-size:20px;padding:26px 24px}
}
@media(prefers-reduced-motion:reduce){.ch-art{filter:none}}
"""

def main():
    out = [(f"units/{T.SLUG[u]}.html", unit_page(u)) for u in UNIT if u in T.PAGES]
    out += [(f"members/{T.MSLUG[c]}.html", char_page(c)) for c in ORDER]
    out.append(("songs.html", songs_page()))
    out.append(("css/page.css", CSS.lstrip("\n")))
    for path, text in out:
        full = os.path.join(T.ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f: f.write(text)
        print("ok", path)

if __name__ == "__main__":
    main()
