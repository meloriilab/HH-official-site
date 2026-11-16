import re
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

# キャラ性を表すタグ（管理サイトの「サイト用タグ」から、2026-11-15 に取り込み）。無い人は「未確定」で、タグの段を出さない
TAGS = {"trt01": ["ストイックなカワセミ", "釣った命は美味しくいただく", "21:00就寝、05:00起床"],
        "trt02": ["ムードメーカーなメジロ", "ファンレター募集中！！", "初恋がまだ来ません"],
        "trt03": ["風まかせな旅ツバメ", "いいや違うべったら派", "温泉ソムリエです"],
        "nct01": ["孤高のハヤブサ", "ブラコン（本人は否定）", "兄さんの恋人募集中"],
        "nct02": ["みんなのお兄ちゃんフクロウ", "カカオ中毒", "私服はちょいダサ"],
        "prs01": ["自然派のサンコウチョウ", "古民家暮らし", "トリートメントは使ってません"],
        "prs02": ["陽キャなワカケホンセイインコ", "人類皆兄弟！", "巷で評判のチャラ兄"],
        "blc01": ["カリスマカラス", "意外と常識人", "こだわりのバスローブ"],
        "blc02": ["面倒見のいいカササギ", "隼瞳さんとツーリング希望", "セインはジム友"],
        "blc03": ["天才肌なカケス", "省エネ主義", "積みゲー消化中"],
        "orb01": ["エスコート上手なベニマシコ", "アイドルに憧れて", "僕はみんなのもの"],
        "orb02": ["元気っ子なキクイタダキ", "基本的に見切り発車", "日曜の夕方は笑点一択"],
        "orb03": ["しっかり者のルリビタキ", "モーニングルーティーンがある", "どう考えても僕が兄"],
        "orb04": ["大ざっぱなジョウビタキ", "弟の小言はスルー", "そうだ、亀飼おう！"]}


UNIT = {u: dict(no=no, name=n, kana=kana, tag=tg, c=c) for no, u, code, n, kana, tg, c, cnt in T.UNITS}
CH = {c[1]: c for c in T.CHARS}
esc = html.escape

# モチーフの野鳥の中身（2026-11-16。Kさんの監修で決定）。キャラの一言とオスメスはキャラの口調、中の人メモは K さんの文
B = json.load(open(os.path.join(HERE, "birds.json"), encoding="utf-8"))
BNAME = {"blc01": "ハシボソガラス"}   # 種名をはっきりさせる（Kさんの回答 2026-11-16：カラス＝ハシボソガラス）
REG = (("hk", "北海道"), ("hs", "本州・四国"), ("ky", "九州"))
REAL_BIRD = {"01-1", "01-2", "01-3", "02-1", "02-2", "03-1", "03-2", "04-1", "04-2", "04-3"}   # 本物の絵がある鳥（make_bird_placeholders.py と同じ）
def bname(cid): return BNAME.get(cid, CD[cid]["motif"])
LV = {3: "近所で会える", 2: "ちょっと探す", 1: "狙って行く"}   # ★の段階の名前（仮。未確定）
def lum(h):
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)
def scol(cid):
    """★の色：キャラのメインカラー（Kさんの指示 2026-11-16）。白地で見えにくい明るい色には、細いふちを付ける"""
    h = CD[cid]["colors"]["main"]
    return h, (" lt" if 1.05 / (lum(h) + .05) < 2.5 else "")
def stars(n, cid):
    """見つけやすさ：四つ角の星（Kさんが選択 2026-11-16）が多いほど見つけやすい。足りない分は薄い灰色"""
    h, lt = scol(cid)
    return f'<span class="st{lt}" style="--sc:{h}" role="img" aria-label="見つけやすさ 3段階中{n}"><b>{"✦" * n}</b><i>{"✦" * (3 - n)}</i></span>'
def br(t): return "<br>".join(esc(x) for x in t.split("\n"))
def months(b):
    """会える時期：地方ごとに12か月の帯。中身が同じ地方は1行にまとめる（Kさんの回答 v2q2）。地方の補足は帯の右端に置く"""
    rows = []
    for k, l in REG:
        v = (tuple(b[k]["m"]), b[k]["note"])
        if rows and rows[-1][1] == v: rows[-1][0].append(l)
        else: rows.append(([l], v))
    lab = lambda ls: {3: "全国"}.get(len(ls)) or ("本州〜九州" if ls == ["本州・四国", "九州"] else "〜".join([ls[0], ls[-1]]) if len(ls) > 1 else ls[0])
    def said(ms):
        if not ms: return "いない"
        if len(ms) == 12: return "1年中"
        return "・".join(map(str, ms)) + "月"
    out = ""
    for ls, (ms, note) in rows:
        cells = "".join(f'<i data-m="{m}"{" class=on" if m in ms else ""}></i>' for m in range(1, 13))
        out += f'<div class="mo-r"><span class="mo-l">{lab(ls)}</span><span class="mo-c" role="img" aria-label="{lab(ls)}：{said(ms)}">{cells}</span><span class="mo-n">{esc(note)}</span></div>'
    # カレンダーだと一目で分かるよう、帯の上に季節と月の数字を置く（Kさんの指示 2026-11-16：春3〜5月・夏6〜8月・秋9〜11月・冬12〜2月）
    se = "".join(f'<b class="s{k}" style="grid-column:{a}/{z}">{t}</b>' for k, a, z, t in ((1, 1, 3, "冬"), (2, 3, 6, "春"), (3, 6, 9, "夏"), (4, 9, 12, "秋"), (1, 12, 13, "冬")))
    axis = "".join(f'<b data-m="{m}">{m}</b>' for m in range(1, 13))
    head = (f'<div class="mo-r mo-se" aria-hidden="true"><span class="mo-l"></span><span class="mo-c">{se}</span><span class="mo-n"></span></div>'
            f'<div class="mo-r mo-a" aria-hidden="true"><span class="mo-l"></span><span class="mo-c">{axis}</span><span class="mo-n">月</span></div>')
    return f'<div class="mo">{head}{out}</div>'


def phrases(line):
    """キャッチコピーを文節で区切る。スマホではKさんの改行を使わず、区切り目（「、」の後と、助詞の後ろに漢字・カタカナが続くところ）でだけ折り返す。2026-11-15"""
    out, cur = [], ""
    for i, ch in enumerate(line):
        cur += ch
        nxt = line[i + 1] if i + 1 < len(line) else ""
        if ch == "、" or (ch in "をにとがのはへで" and nxt and not ("\u3041" <= nxt <= "\u309f") and nxt not in "、。！ "):
            out.append(cur); cur = ""
    if cur: out.append(cur)
    return out

def kana_wrap(s):
    """ユニットの読みがなを「・」の所でだけ折る（2026-11-15。以前は「ハ／ーモニック」のように言葉の途中で折れていた）"""
    return "・<wbr>".join(f'<span class="nw">{esc(p)}</span>' for p in s.split("・"))

def ruby_text(s):
    """[[名前|よみ]] をふりがな付きに、[[名前]] をそのままの名前にする"""
    s = esc(s)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", lambda m: T.rb(m.group(1), m.group(2)), s)
    return re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)

def h2(en, jp, i, n, pc=None):
    # i, n, pc は以前の「01 /04」の番号用。2026-11-15 に番号を外した（区切りは順番に読むものではないため）
    return f'<h2><span>{en}</span><small>{jp}</small></h2>'

def face(cid, speed=".0"):
    c = CH[cid]
    return f'<a class="mem" href="{T.mhref(c, PRE)}"><span class="ph"><img src="{PRE}images/face/{T.fid(c)}.webp" alt=""></span><span>{T.name(c)}</span></a>'

def rels_of(u): return [r for r in T.RELS if r[1] == u]

# ユニットの絵の中で、各メンバーが立っている位置（左端からの％）。ピルをその人の足もとに置く（Kさんの指示 2026-11-15）
ART_X = {"trt01": 17, "trt02": 46, "trt03": 81, "nct02": 31, "nct01": 69, "blc02": 20, "blc01": 50, "blc03": 83}

def unit_page(u):
    d, m = UD[u], UNIT[u]
    no = m["no"]
    # 紹介文とキャッチコピーが無いユニットは、旧サイトの短い紹介文を出し、キャッチコピーの行は出さない（文は作らない）
    intro = "".join(f"<p>{ruby_text(p)}</p>" for p in d.get("intro") or [d["blurb"]])
    catch = f'<p class="uh-c">{"<br class=\"br-w\">".join("".join(f'<span class="nw">{esc(x)}</span>' for x in phrases(l)) for l in d["catch"].split(chr(10)))}</p>' if d.get("catch") else ""
    kv = u in T.KV   # 集合絵が無いユニットは、絵の場所に紋章を大きく出す
    mems = "".join(face(i.lower(), s) for i, s in zip(d["members"], [".0", "-.1", ".06", "-.04"]))
    more = f'<p class="row more"><a class="btn" href="{PRE}songs.html?u={T.SLUG[u]}">Songs</a></p>' if rels_of(u) else ""
    rels = "".join(f'''
      <article class="rel"><a class="ph" href="{T.MV.get(n, T.YT_CH)}"><img src="{PRE}images/jacket/{T.JK[n]}.webp" alt="{t} のジャケット">{T.jo(n)}</a>
        <h3>{T.rb(t, k)}</h3><p class="by">{T.kn(un)}</p>{T.lk(n)}{T.ep_btn(n, PRE)}</article>''' for n, ru, t, k, un in T.RELS if ru == u)
    # 2026-11-15 Kさんの指示：ユニットページは1画面にまとめる（Members・Release・Unitsの一覧は外す）。
    # 絵の下側にメンバーのピル（メンバーカラー＋名前→キャラページ）、About は重ねて開く画面、Songs は曲一覧をこのユニットで絞った状態で開く。
    # 左右の丸ボタンでユニットを切り替える（キャラページの左右ボタンと同じ形）。
    order = [o for o in UNIT if o in T.PAGES]
    i = order.index(u)
    pv, nx = order[i - 1], order[(i + 1) % len(order)]
    def pill(cid):
        c = CH[cid]; col = c[6]
        x = f";--x:{ART_X[cid]}%" if kv and cid in ART_X else ""
        return f'<a class="uv-m" href="{T.mhref(c, PRE)}" style="--mc:{col};--mt:{"#141414" if T._lum(col) > .6 else "#fff"}{x}">{c[2]}{c[3]}<i aria-hidden="true"></i></a>'
    ids = [i2.lower() for i2 in d["members"]]
    if kv: ids.sort(key=lambda x: ART_X.get(x, 0))   # 絵の左から順に並べる（読み上げの順も、見た目の順と同じにする）
    pills = "".join(pill(x) for x in ids)
    art = (f'<img src="{PRE}images/unit/{no}.webp" alt="{m["name"]}">' if kv else f'<img class="em" src="{PRE}images/emblem/{no}.webp" alt="">')
    songs = f'<a class="btn" href="{PRE}songs.html?u={T.SLUG[u]}">Songs</a>' if rels_of(u) else ""
    about = f'<dialog class="pop" id="pop-about" aria-label="{m["name"]} について"><div class="pop-h"><b>About</b><button class="pop-x" type="button" aria-label="閉じる"></button></div><div class="pop-b prose">{intro}</div></dialog>'
    inner = f'''{T.header(PRE, top=False)}
<main>
<section class="uv">
  <div class="uv-pic{" e" if not kv else ""}">{art}<nav class="uv-ms{" at" if kv else ""}" aria-label="メンバー">{pills}</nav><a class="uv-ar pv" href="{T.uhref(pv, PRE)}" aria-label="前のユニット：{UNIT[pv]["name"]}"></a><a class="uv-ar nx" href="{T.uhref(nx, PRE)}" aria-label="次のユニット：{UNIT[nx]["name"]}"></a></div>
  <div class="uv-t">
    <div class="uv-n">{f'<img class="uv-em" src="{PRE}images/emblem/{no}.webp" alt="">' if kv else ""}<h1>{T.kn(m["name"])}{f"<small>{m[chr(107)+chr(97)+chr(110)+chr(97)]}</small>" if m["kana"] else ""}</h1></div>
    <p class="uh-tag">{esc(d["tagline"])}</p>{catch}
    <div class="uv-bar pop-w"><p class="row"><button class="btn" type="button" data-pop="about">About</button>{songs}</p>{about}</div>
  </div>
</section>
</main>
{T.footer(PRE)}'''
    return T.page(f'{m["name"]} | Humming Hearts', esc(d.get("catch") or d["blurb"]), PRE, inner, css=("page.css",), attrs=f' data-u="{T.SLUG[u]}"')

def songs_page():
    """楽曲ページ：全曲のジャケットを並べ、気分（Mood）とユニット（Unit）の2段で絞り込む。聴き比べる場所なので、動かさず同じ大きさで並べる"""
    pre = ""
    def row(k, lbl, aria, items):
        ps = f'<button class="md on" type="button" data-k="{k}" data-v="" aria-pressed="true">すべて</button>' + "".join(
            f'<button class="md" type="button" data-k="{k}" data-v="{esc(v)}" aria-pressed="false">{esc(t)}</button>' for v, t in items)
        # スマホは同じ中身を、押すと下に開く一覧で出す（Kさんの指示 2026-11-14：丸いボタンだと窮屈。端末まかせの選択画面は使わず、ユニットのピルの下に出るメンバー名と同じ見た目にする）
        # PCは丸いボタンのまま。どちらも同じ一覧から作るので手間は増えない
        sel = (f'<div class="dd" data-k="{k}"><button class="dd-b" type="button" aria-haspopup="listbox" aria-expanded="false" aria-label="{aria}"><i>{lbl}</i><span>すべて</span></button><span class="dd-m" role="listbox" aria-label="{aria}">'
               + '<button type="button" role="option" data-v="" aria-selected="true">すべて</button>' + "".join(f'<button type="button" role="option" data-v="{esc(v)}" aria-selected="false">{esc(t)}</button>' for v, t in items) + '</span></div>')
        return f'<div class="flt"><p class="lbl">{lbl}</p><div class="moods" role="group" aria-label="{aria}">{ps}</div>{sel}</div>'
    units = [(T.SLUG[u], UNIT[u]["name"]) for u in UNIT if any(r[1] == u for r in T.RELS)]   # 曲があるユニットだけ
    rows = row("m", "Mood", "気分で選ぶ", [(m, m) for m in T.used_moods()]) + row("u", "Unit", "ユニットで選ぶ", units)
    cards = "".join(f'''
      <article class="rel" data-m="{esc("|".join(T.MOOD.get(n, [])))}" data-u="{T.SLUG[ru]}"><a class="ph" href="{T.MV.get(n, T.YT_CH)}"><img src="{pre}images/jacket/{T.JK[n]}.webp" alt="{t} のジャケット">{T.jo(n)}</a>
        <h3>{T.rb(t, k)}</h3><p class="by">{T.kn(un)}</p><p class="sg-m">{"".join(f'<button class="tg" type="button" data-v="{esc(m)}">{esc(m)}</button>' for m in T.MOOD.get(n, []))}</p>
        {T.lk(n)}{T.ep_btn(n, pre)}</article>''' for n, ru, t, k, un in T.RELS)
    inner = f'''{T.header(pre, top=False)}
<main>
<section class="sec sg" id="songs"><h2><span>Songs</span><small>楽曲</small></h2>
  <div class="flts">{rows}</div>
  <div class="rels sgs">{cards}</div>
</section>
</main>
{T.footer()}<script>{SGJS}</script>'''
    return T.page("楽曲 | Humming Hearts", "Humming Hearts の楽曲一覧。気分とユニットで選べます。", pre, inner, css=("page.css",))

SGJS = """(function(){var ps=[].slice.call(document.querySelectorAll('.sg .md')),cs=[].slice.call(document.querySelectorAll('.sgs .rel')),ss=[].slice.call(document.querySelectorAll('.sg .dd')),st={m:'',u:''};
function ok(c,m,u){return(!m||c.dataset.m.split('|').indexOf(m)>=0)&&(!u||c.dataset.u===u)}
function draw(){ps.forEach(function(p){var k=p.dataset.k,v=p.dataset.v,on=st[k]===v;p.classList.toggle('on',on);p.setAttribute('aria-pressed',on?'true':'false');
/* a word that would leave no song with the other row's choice is dimmed and cannot be pressed = never an empty page */
p.disabled=!on&&!cs.some(function(c){return k==='m'?ok(c,v,st.u):ok(c,st.m,v)})});
ss.forEach(function(s){var k=s.dataset.k;[].forEach.call(s.querySelectorAll('[role=option]'),function(o){var v=o.dataset.v,on=st[k]===v;o.setAttribute('aria-selected',on?'true':'false');if(on)s.querySelector('.dd-b span').textContent=o.textContent;o.disabled=!on&&!cs.some(function(c){return k==='m'?ok(c,v,st.u):ok(c,st.m,v)})})});
/* reorder motion: each jacket slides from where it was to where it goes, so the eye can follow which songs stayed */
var mv=!matchMedia('(prefers-reduced-motion: reduce)').matches&&!!document.body.animate,old=new Map();
if(mv)cs.forEach(function(c){if(!c.hidden)old.set(c,c.getBoundingClientRect())});
cs.forEach(function(c){c.hidden=!ok(c,st.m,st.u)});
if(mv)cs.forEach(function(c){if(c.hidden)return;var n=c.getBoundingClientRect(),o=old.get(c);
if(o){var dx=o.left-n.left,dy=o.top-n.top;if(dx||dy)c.animate([{transform:'translate('+dx+'px,'+dy+'px)'},{transform:'none'}],{duration:480,easing:'cubic-bezier(.2,.7,.2,1)'})}
else c.animate([{opacity:0,transform:'translateY(16px)'},{opacity:1,transform:'none'}],{duration:420,delay:120,easing:'ease-out',fill:'backwards'})})}
function put(){try{var q=[];if(st.m)q.push('m='+encodeURIComponent(st.m));if(st.u)q.push('u='+encodeURIComponent(st.u));history.replaceState(null,'',q.length?'?'+q.join('&'):location.pathname)}catch(e){}}
ps.forEach(function(p){p.addEventListener('click',function(){st[p.dataset.k]=p.dataset.v;draw();put()})});
function shut(x){ss.forEach(function(s){if(s!==x){s.classList.remove('open');s.querySelector('.dd-b').setAttribute('aria-expanded','false')}})}
ss.forEach(function(s){var b=s.querySelector('.dd-b');b.addEventListener('click',function(){shut(s);b.setAttribute('aria-expanded',s.classList.toggle('open')?'true':'false')});
[].forEach.call(s.querySelectorAll('[role=option]'),function(o){o.addEventListener('click',function(){st[s.dataset.k]=o.dataset.v;shut();draw();put();b.focus()})})});
document.addEventListener('click',function(e){if(!e.target.closest('.dd'))shut()});document.addEventListener('keydown',function(e){if(e.key==='Escape')shut()});
[].forEach.call(document.querySelectorAll('.sgs .tg'),function(t){t.addEventListener('click',function(){st.m=t.dataset.v;if(!cs.some(function(c){return ok(c,st.m,st.u)}))st.u='';draw()})});
try{var sp=new URLSearchParams(location.search);['m','u'].forEach(function(k){var v=sp.get(k)||'';if(v&&ps.some(function(p){return p.dataset.k===k&&p.dataset.v===v}))st[k]=v})}catch(e){}
if(st.m&&st.u&&!cs.some(function(c){return ok(c,st.m,st.u)}))st.u='';
draw()})();"""

# 開いた直後にも帯が伸びる動きを見せるため、最初の1コマを描いてから「準備できた」の印を付ける
# 【お試し】タグの形の案を見比べるための切り替え（アドレスの最後に ?tag=1 / 2 / 4）。形が決まったら消す
RDY = "requestAnimationFrame(function(){requestAnimationFrame(function(){document.documentElement.classList.add('rdy')})})"
ORDER = [c[1] for c in T.CHARS if c[1] in T.MSLUG]   # 前へ・次への並び

QCUT = {"でもそれ以上にワクワクしてるッス！": 7}   # 帯を分ける位置の指定（行の文 → 何字目の後ろで分けるか）。律：Kさんの指定（2026-11-13）。文は変えない
QMAX, QLOW = 17, 14   # せりふの帯1本の字数の上限／下げる帯がこの字数以上なら上下を入れ替える

def guideline_page():
    """ガイドライン：ファンが「これはやっていい？」を確かめに来る場所。読むためのページなので、絵も動きも足さず、番号と見出しで探しやすくする。
    文は旧サイトのファンガイドラインがもと（Kさんの指示 2026-11-15：このサイトに合わせた言葉遣いにする。決まりごとの中身は変えない）"""
    items = [
        ("二次創作", "<p>イラスト、漫画、小説、音楽、コスプレなど、ファンによる非営利の二次創作を歓迎します。</p><p>公式とは関係のない創作だと分かる形で楽しんでください。原作の雰囲気やキャラクターのイメージを大切にしてもらえると嬉しいです。</p>"),
        ("収益化", "<p>同人誌やグッズなど、個人や少人数のサークルの範囲での頒布は問題ありません。</p><p>大量生産しての販売、公式と間違われる商品化、ブランドや第三者のライセンスを侵害する利用はご遠慮ください。</p>"),
        ("AIの利用", "<p>Humming Hearts は生成AIを活用して制作しています。そのため、二次創作にAIを使うこと自体は禁止しておりません。</p><p>公式の画像や音源をそのまま学習データとして使用すること、再配布すること、公式になりすます利用はお控えください。</p>"),
        ("禁止事項", "<ul><li>公式・公認であるかのような誤認を招く表現</li><li>過度に暴力的・差別的な内容、特定の個人や団体を誹謗中傷する内容</li><li>政治・宗教・反社会的活動への利用</li><li>ロゴ・エンブレムなどの公式素材の無断使用、改変しての配布</li></ul>"),
        ("お問い合わせ", f'<p>Humming Hearts は現在、お問い合わせの窓口を設けておりません。個別のご質問やご連絡にはお返事できませんので、あらかじめご了承ください。</p><p>最新のお知らせは、公式の <a href="{T.XURL}">X</a> と <a href="{T.YT_CH}">YouTube</a> でご確認ください。</p>'),
    ]
    def tail(h):   # 段落・箇条書きの終わりの5文字は途中で折り返さない（「す。」だけが次の行に落ちるのを防ぐ。Kさんの指摘 2026-11-15）
        return re.sub(r"([^<>]{5})(</p>|</li>)", r'<span class="nb">\1</span>\2', h)
    items = [(t, tail(b)) for t, b in items]
    lead = tail("<p class=\"gl-l\">Humming Hearts（ハミングハーツ）のキャラクターや世界を使った創作や、歌ってみた動画などは大歓迎です！みんなが気持ちよく楽しめるように、以下をご一読いただければと思います。</p>")
    note = tail('<p class="gl-x">ガイドラインの内容は予告なく変わることがあります。</p>')   # いちばん下の注意書き（Kさんの指示 2026-11-15。「草案です」の一文は外す）
    rows = "".join(f'<div class="gl-i"><p class="gl-n" aria-hidden="true">{i:02d}</p><h3>{t}</h3><div class="gl-b">{b}</div></div>' for i, (t, b) in enumerate(items, 1))
    inner = f'''{T.header("", top=False)}
<main>
<section class="sec gl" id="guideline"><h2><span>Guideline</span><small>ガイドライン</small></h2>
  {lead}
  <div class="gl-s">{rows}</div>
  {note}
</section>
</main>
{T.footer()}'''
    return T.page("ガイドライン | Humming Hearts", "Humming Hearts の二次創作についてのお願いをまとめています。", "", inner, css=("page.css",))

def birds_page():
    """Birds：鳥が目当てで来た人の入口。マナー → 見つけやすさで絞り込み → 14羽の一覧。行を押すと、そのメンバーのページが鳥の側で開く（Kさんの了承 2026-11-16）
    紹介の1行・マナーの文・★の段階の名前は、たたき台（未確定。Kさんの確認待ち）"""
    lead = "メンバーのモチーフになった野鳥たち。会える季節と場所を、メンバーが案内します"
    manners = ["近づきすぎない。追いかけない", "巣やヒナには近づかない。撮影もひかえる", "えさをあげない", "田畑や私有地に入らない。めずらしい鳥の場所はSNSに書かない"]
    rows = "".join(f'<li data-s="{B[cid]["star"]}"><a class="bl-i" href="{T.mhref(CH[cid])}#bird"><img src="images/face/{T.fid(CH[cid])}.webp" alt=""><span class="bl-t"><b>{esc(bname(cid))}</b><small>{T.name(CH[cid])}</small></span><span class="bl-s">{stars(B[cid]["star"], cid)}<small>{LV[B[cid]["star"]]}</small></span></a></li>' for cid in ORDER)
    # 絞り込み：すべて＋3段階。札は4つとも同じ幅（Moodの札と同じ形）。星は黒（どのメンバーの色でもないため）
    chips = '<button class="md on" type="button" data-v="" aria-pressed="true">すべて</button>' + "".join(
        f'<button class="md" type="button" data-v="{n}" aria-pressed="false" aria-label="{t}"><span class="st">{"✦" * n}</span></button>' for n, t in sorted(LV.items(), reverse=True))
    legend = "".join(f'<span><b class="st">{"✦" * n}</b>{t}</span>' for n, t in sorted(LV.items(), reverse=True))
    inner = f'''{T.header("", top=False)}
<main>
<section class="sec bp" id="birds"><h2><span>Birds</span><small>野鳥</small></h2>
  <p class="bp-l">{lead}</p>
  <div class="bp-m"><p class="bp-k">観察のマナー</p><ul>{"".join(f"<li>{esc(x)}</li>" for x in manners)}</ul></div>
  <p class="bp-k bp-kk">見つけやすさで選ぶ</p>
  <div class="bp-f" role="group" aria-label="見つけやすさで選ぶ">{chips}</div>
  <p class="bp-lg">{legend}</p>
  <ul class="bl">{rows}</ul>
</section>
</main>
{T.footer()}<script>{BFJS}</script>'''
    return T.page("Birds | Humming Hearts", "Humming Hearts のメンバーのモチーフになった野鳥の、会える季節・場所・見つけやすさ。", "", inner, css=("page.css",))

# Birds の絞り込み：押した段階の鳥だけ残す。もう一度押すか「すべて」で全部に戻る
BFJS = """(function(){var bs=[].slice.call(document.querySelectorAll('.bp-f .md')),li=[].slice.call(document.querySelectorAll('.bl li'));
bs.forEach(function(b){b.addEventListener('click',function(){var v=b.classList.contains('on')&&b.dataset.v?'':b.dataset.v;
 bs.forEach(function(x){var on=x.dataset.v===v;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on?'true':'false')});
 li.forEach(function(l){l.hidden=!!v&&l.dataset.s!==v})})})})();"""

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
    # 値は「、」の後でだけ折り返す（趣味などが2行になっても、ことばの途中で切れない。2026-11-15）
    dl = "".join(f"<div><dt>{k}</dt><dd>{''.join(f'<span class=nw>{esc(x)}</span>' for x in phrases(str(v)) if x)}</dd></div>" for k, v in rows)
    tags = ('<ul class="tags">' + "".join(f"<li>#{esc(t)}</li>" for t in TAGS[cid]) + "</ul>") if cid in TAGS else ""
    # タブレット幅では、タグを立ち絵の上にメインカラーの帯で縦に並べる。帯が明るい色の人は、白ではなく黒の文字にして読めるようにする
    r, g, b = (int(col["main"][i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = sum(w * (v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4) for w, v in zip((.2126, .7152, .0722), (r, g, b)))
    tags_a = tags.replace('class="tags"', f'class="tags-a" style="--tc:{"#141414" if lum > .36 else "#fff"}"') if tags else ""
    tags_a = tags_a.replace("<li>", "<li><span>").replace("</li>", "</span></li>")
    # モチーフの鳥の絵（ある人だけ）。モチーフの段の背景に置き、スクロールでゆっくりずれる
    bp = os.path.join(HERE, "..", "public", "images", "bird", T.aid(c) + ".webp")
    tall = ""
    if os.path.exists(bp):   # 縦長の絵（フクロウなど）は、幅を狭くして高さをほかの鳥とそろえる
        from PIL import Image
        bw, bh = Image.open(bp).size; tall = " tall" if bh > bw else ""
    bird = f'<img class="mt-b{tall}" src="{PRE}images/bird/{T.aid(c)}.webp" alt="" data-speed=".08">' if os.path.exists(bp) else ""
    mates = "".join(face(i.lower(), s) for i, s in zip([x for x in UD[u]["members"] if x.lower() != cid], [".0", "-.1", ".06"]))
    i = ORDER.index(cid); pv, nx = CH[ORDER[i - 1]], CH[ORDER[(i + 1) % len(ORDER)]]
    # 前後のメンバーへ移る丸いボタン（名前の段の右上。ページのいちばん下の Prev / Next と同じ行き先）
    nav = (f'<p class="ch-nv"><a class="pv" href="{T.mhref(pv, PRE)}" aria-label="前のメンバー：{pv[2]}{pv[3]}"></a>'
           f'<a class="nx" href="{T.mhref(nx, PRE)}" aria-label="次のメンバー：{nx[2]}{nx[3]}"></a></p>')
    # PC では、プロフィールを最初の画面の右側にまとめて出す（スマホは下の Profile の段のまま）
    # モチーフは重ねて開く小さな画面（背景に鳥の絵、上に文）。同じユニットのメンバーは小さな丸い顔で詰めて並べる（Kさんの指示 2026-11-15）
    mm = "".join(f'<a class="mm-i" href="{T.mhref(CH[x.lower()], PRE)}"><img src="{PRE}images/face/{T.fid(CH[x.lower()])}.webp" alt=""><span>{T.name(CH[x.lower()])}</span></a>' for x in UD[u]["members"] if x.lower() != cid)
    # 鳥の側（Kさんの指示 2026-11-16：小窓をやめ、「Character／Motif Bird」の切り替えでページの中身ごと入れ替える。
    # キャラがその鳥を紹介する形。データは吹き出しの間に置き、豆知識・中の人メモはキャラの声と分けて下にまとめる）
    b = B[cid]; fc = f'<img class="bv-f" src="{PRE}images/face/{T.fid(c)}.webp" alt="">'
    # 紹介とデータ・会える時期は出したまま、その先は押すと開く（Kさんの指示 2026-11-16：情報を垂れ流さない。Note は見たい人だけ）
    note = lambda en, jp, t, cls="": f'<details class="bx{cls}"><summary><span class="bx-k">{en}<small>{jp}</small></span></summary><div class="bx-in"><p>{t}</p></div></details>' if t else ""
    birdx = (f'<div class="cp-b{scol(cid)[1]}" style="--cm:{col["main"]}">'
             f'<div class="bv">{fc}<div class="bv-b"><p>{br(b["line"])}</p></div></div>'
             f'<div class="bf"><dl class="bf-g"><div><dt>区分</dt><dd>{esc(b["kind"])}</dd></div><div><dt>地域</dt><dd>{esc(b["region"])}</dd></div><div class="w"><dt>いる場所</dt><dd>{esc(b["place"])}</dd></div></dl>'
             f'<div class="bf-s"><p class="bf-k">見つけやすさ</p>{stars(b["star"], cid)}<p class="bf-l">{LV[b["star"]]}</p></div></div>'
             f'<div class="bm"><p class="bm-h"><span>会える時期</span><span class="bm-now">今月も会える</span></p>{months(b)}</div>'
             f'<div class="bxs"><details class="bx"><summary><span class="bx-k">Male / Female<small>オスとメスの見分け方</small></span></summary><div class="bx-in"><div class="bv">{fc}<div class="bv-b"><p>{br(b["sex"])}</p></div></div></div></details>{note("Tips", "見分けのヒント", br(b["tips"]))}{note("Trivia", "豆知識", br(b["trivia"]))}{note("Note", "中の人メモ", br(b["memo"]), " memo")}</div>'
             f'<p class="row bd-go"><a class="btn" href="{PRE}birds.html">More Birds</a></p></div>')
    # 切り替え（名前は仮）。PC は右側の幅いっぱいで名前の上、スマホは絵のすぐ下（Kさんが選択 2026-11-16）
    tabs = ('<div class="ch-tab" role="tablist" aria-label="表示の切り替え"><i class="ch-ind" aria-hidden="true"></i><button type="button" role="tab" aria-selected="true" data-v="c">Character</button>'
            '<button type="button" role="tab" aria-selected="false" data-v="b">Motif Bird</button></div>'
            "<script>if(location.hash==='#bird')document.documentElement.classList.add('bird')</script>")
    bart = f'<span class="ch-bd"><img src="{PRE}images/bird/{T.aid(c)}.webp" alt="{esc(bname(cid))}"><span class="vq bq"><span class="col">{esc(bname(cid))}</span></span><span class="ch-ben">{esc(b["en"])}</span></span>'
    mmx = f'<div class="ch-mm"><p class="lbl">Member</p><div class="mm">{mm}</div></div>'
    prof = f'<div class="ch-p"><div class="cp-c"><p>{esc(d["bio"])}</p><dl class="pf">{dl}</dl>{mmx}</div>{birdx}</div>'
    # そのメンバーが歌っている曲（＝ユニットの曲）。ページのいちばん最後に、小さいジャケットの1行ずつの一覧で出す
    # （Kさんの指示 2026-11-14：キャラのページは縦に長くしない。曲は今後増えるので小さくまとめる。ほかのページのカードの並べ方は使い回さない）
    songs = "".join(f'''
      <li class="sl-i"><a class="sl-j" href="{T.MV.get(n, T.YT_CH)}"><img src="{PRE}images/jacket/{T.JK[n]}.webp" alt="{t} のジャケット" loading="lazy"></a>
        <h3>{T.rb(t, k)}</h3>{T.lk(n)}{T.ep_btn(n, PRE)}</li>''' for n, ru, t, k, un in T.RELS if ru == u)
    k = 1 if songs else 0   # 曲の段がある人は、段の数が1つ増える
    songs_sec = f'''<section class="sec sl-s" id="songs">{h2("Songs", "参加曲", 4, 4, (3, 3))}<ul class="sl">{songs}</ul><p class="row more"><a class="btn" href="{PRE}songs.html?u={T.SLUG[u]}">Songs</a></p></section>''' if songs else ""
    inner = f'''{T.header(PRE, top=False)}
<main>
<section class="fv ch" style="--cm:{col["main"]};--cs:{col["sub"]};--ca:{col["accent"]}">
  <div class="ch-art"><i class="bg-main"></i><i class="bg-dia"></i><i class="bg-line"></i><button class="ch-sw" type="button" aria-label="立ち絵の見え方を切り替える（アップ・全身）" aria-pressed="false"><i></i><i></i></button><p class="vq" aria-label="{esc(" ".join(d["tagline"].split()))}">{quote}</p><span class="ch-img"><img src="{PRE}images/chara/{T.aid(c)}.webp" alt="{c[2]}{c[3]}" data-speed=".05"></span>{tags_a}{bart}<i class="bg-deco"></i></div>
  <div class="ch-t">{tabs}<div class="ch-in">{nav}<p class="ch-u"><a href="{T.uhref(u, PRE)}"><img src="{PRE}images/emblem/{m["no"]}.webp" alt="">{T.kn(m["name"])}</a></p><h1>{T.name(c)}</h1><p class="ch-r">{esc(d["roma"].title())}</p></div>{prof}</div>
  <p class="hint ch-hint" aria-hidden="true">Scroll</p>
</section>
<section class="sec" id="profile"><div class="cp-c">{h2("Profile", "プロフィール", 1, 1 + k)}<div class="prose"><p>{esc(d["bio"])}</p></div><dl class="pf">{dl}</dl>{mmx}</div><div class="cp-bw">{h2("Motif Bird", esc(bname(cid)), 1, 1)}{birdx}</div></section>
{songs_sec}
</main>
{T.footer(PRE)}<script>{SWJS}</script><script>{TABJS}</script><script>{RDY}</script>'''
    return T.page(f'{c[2]}{c[3]} | Humming Hearts', esc(d["bio"]), PRE, inner, css=("page.css",), attrs=f' data-u="{T.SLUG[u]}" data-ch', share=f'{c[2]}{c[3]}（{m["name"]}） | Humming Hearts')   # 共有の文面のたたき台（Kさんの確認待ち）

# キャラ／鳥の切り替え。#bird で鳥の側を開いた状態にする（Birds ページ・TOP から来たとき）。会える時期の帯に今月の印を付ける
TABJS = """(function(){var h=document.documentElement,bs=[].slice.call(document.querySelectorAll('.ch-tab button'));
var t=document.querySelector('.ch-tab'),ind=t&&t.querySelector('.ch-ind');
if(ind)ind.addEventListener('transitionend',function(e){if(e.target===ind)t.classList.remove('mv')});
function set(b){if(t&&b!==h.classList.contains('bird')&&!matchMedia('(prefers-reduced-motion:reduce)').matches)t.classList.add('mv');h.classList.toggle('bird',b);bs.forEach(function(x){x.setAttribute('aria-selected',(x.dataset.v==='b')===b?'true':'false')});
 history.replaceState(null,'',location.pathname+location.search+(b?'#bird':''))}
bs.forEach(function(x){x.addEventListener('click',function(){set(x.dataset.v==='b')})});set(h.classList.contains('bird'));
var m=new Date().getMonth()+1;[].forEach.call(document.querySelectorAll('[data-m="'+m+'"]'),function(i){i.classList.add('now')});
[].forEach.call(document.querySelectorAll('.bm'),function(b){if(b.querySelector('i.on.now'))b.classList.add('now')})})();"""

# 立ち絵の切り替え（アップ ⇄ 全身）。いったん左へ消えて、右から入り直す
SWJS = """(function(){var b=document.querySelector('.ch-sw'),w=document.querySelector('.ch-img');if(!b||!w)return;
b.addEventListener('click',function(){w.classList.add('out');setTimeout(function(){var f=w.classList.toggle('full');b.setAttribute('aria-pressed',f?'true':'false');w.classList.remove('out')},160)})})();"""

CSS = """
/* songs page: same-size jackets in a plain grid (no drift, no stagger) = easy to compare */
.sg{padding-bottom:96px}
/* two rows of words, each with a small name on the left: Mood = by feeling, Unit = by who sings */
.flts{display:grid;gap:18px;margin-bottom:40px}.flt{display:grid;gap:10px}
.md:disabled{opacity:.3;cursor:default;background:none;color:inherit}
/* phone: the same choices as two lists that open under a pill (same look as the member names under the unit pills) = no cramped rows of pills, no ragged gaps */
.dd{display:none;position:relative}
.dd-b{appearance:none;width:100%;min-height:46px;margin:0;padding:0 44px 0 20px;text-align:left;border:1px solid var(--ink);border-radius:999px;color:var(--ink);font:500 15px/1 var(--jp);letter-spacing:.06em;cursor:pointer;background-color:transparent;background-image:linear-gradient(45deg,transparent 50%,var(--ink) 50%),linear-gradient(135deg,var(--ink) 50%,transparent 50%);background-repeat:no-repeat;background-size:6px 6px,6px 6px;background-position:right 24px center,right 18px center;transition:background-color .25s,color .25s}
.dd.open .dd-b{background-color:var(--ink);color:var(--bg);background-image:linear-gradient(45deg,transparent 50%,var(--bg) 50%),linear-gradient(135deg,var(--bg) 50%,transparent 50%)}
.dd-m{display:none;position:absolute;z-index:20;left:0;right:0;top:100%;padding-top:5px}.dd.open .dd-m{display:block}
.dd-m button{appearance:none;display:block;width:100%;margin:0;min-height:44px;padding:9px 20px;text-align:left;background:var(--bg);color:var(--ink);border:1px solid var(--ink);border-top:0;border-radius:0;font:500 14px/1.4 var(--min);letter-spacing:.06em;cursor:pointer}
.dd-m button:first-child{border-top:1px solid var(--ink);border-radius:12px 12px 0 0}.dd-m button:last-child{border-radius:0 0 12px 12px}
.dd-m button[aria-selected="true"]{background:var(--ink);color:var(--bg)}.dd-m button:disabled{color:var(--line);cursor:default}
/* 2つを1段に並べる（Kさんの指示 2026-11-15：場所を取らない）。名前（Mood / Unit）は枠の中に小さく入れ、開く一覧は2つ分の幅いっぱいに出す */
@media(max-width:699px){.flts{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}.flt{display:block}.flt>.lbl,.flt .moods{display:none}.dd{display:block}.dd-m{right:auto;min-width:100%;width:max-content;max-width:calc(100vw - 32px)}.flt+.flt .dd-m{left:auto;right:0}
 .dd-b{display:flex;align-items:center;gap:6px;padding:0 26px 0 12px;font-size:13px;background-position:right 17px center,right 12px center}.dd-b i{flex:none;font:italic 500 15px/1 var(--en);letter-spacing:.02em;opacity:.6}.dd-b span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.sgs{padding-bottom:0;row-gap:0}.sgs .rel{padding-bottom:40px}   /* 2026-11-15 曲どうしの縦の間は、各曲の下の余白で取る（並びの間隔で取ると、曲の中の段ごとにも同じ間隔が入って、タグの上下が空きすぎていた） */.sgs .rel{margin-top:0!important}.sgs .rel[hidden]{display:none}
/* 2026-11-15: 隣の曲と、曲名・札・ボタンの高さをそろえる（曲名が2行になってもボタンがずれない）。札とボタンの間は少し広げて、丸い札（選ぶもの）と四角いボタン（開くもの）を別のかたまりに見せる */
.sgs .rel{display:grid;grid-template-rows:subgrid;grid-row:span 6;row-gap:0;align-content:start}.sgs .rel .lk{margin-top:18px}

/* ユニットページ（1画面。2026-11-15）
   スマホ：上に絵（少し小さく）、下半分に紋章・名前・キャッチ・ボタン。左右のユニット切り替えは、親指の届く一番下の列に About・Songs と並べる */
.uv{padding:147px 0 28px;display:flex;flex-direction:column}
.uv-pic{position:relative;height:clamp(230px,38svh,380px);overflow:hidden}
.uv-pic>img{width:100%;height:100%;object-fit:cover;object-position:50% 30%}
.uv-pic.e{background:var(--faint)}.uv-pic.e>img{object-fit:contain;padding:28px 0 64px}
.uv-ms{position:absolute;left:var(--gx);right:var(--gx);bottom:12px;display:flex;flex-wrap:wrap;gap:6px}
.uv-m{min-height:32px;padding:0 11px 0 14px;display:inline-flex;align-items:center;gap:7px;border-radius:999px;background:var(--mc);color:var(--mt);font:500 13px/1 var(--jp);letter-spacing:.06em;white-space:nowrap;box-shadow:0 1px 6px rgba(0,0,0,.18);transition:opacity .25s}
.uv-m:hover{opacity:.8}
.uv-ms.at{left:0;right:0}.uv-ms.at .uv-m{position:absolute;bottom:0;left:var(--x);translate:-50% 0}
@media(max-width:359px){.uv-m{font-size:12px;padding:0 9px 0 11px;gap:5px}}
.uv-m i{width:6px;height:6px;margin-left:2px;border-top:1.5px solid currentColor;border-right:1.5px solid currentColor;rotate:45deg}
.uv-t{padding:20px var(--gx) 0}
.uv-n{display:flex;align-items:center;gap:12px}
.uv-em{flex:none;width:56px;height:56px;object-fit:contain}
.uv h1{margin:0;font:500 34px/1.1 var(--en);letter-spacing:-.01em;word-break:keep-all}
.uv h1 small{display:block;margin-top:6px;font:400 11px/1 var(--jp);letter-spacing:.06em;color:var(--sub)}
.uv .uh-tag{margin-top:16px}.uv .uh-c{font-size:19px}
.uv-bar{display:flex;align-items:center;gap:12px;margin-top:20px}
.uv-bar .row{flex:1}
/* ユニットの切り替え：絵の左右の端（About・Songs と離して、別の操作だとわかるように） */
.uv-ar{position:absolute;top:calc(50% - 23px);width:44px;height:44px;border:1px solid var(--ink);border-radius:50%;background:rgba(250,250,248,.88);color:var(--ink);transition:background .25s,color .25s}.uv-ar.pv{left:10px}.uv-ar.nx{right:10px}
.uv-ar:hover{background:var(--ink);color:var(--bg)}
.uv-ar::before{content:"";position:absolute;left:13px;top:21px;width:18px;height:1px;background:currentColor}
.uv-ar::after{content:"";position:absolute;top:18px;width:6px;height:6px;border-top:1px solid currentColor;border-right:1px solid currentColor}
.uv-ar.nx::after{right:13px;rotate:45deg}.uv-ar.pv::after{left:13px;rotate:-135deg}
/* About：重ねて開く画面。スマホは下から、PCは真ん中に */
html.pop-on{overflow:hidden}
.pop-w{position:relative}
.pop{border:0;padding:0;margin:auto auto 0;width:100%;max-width:none;max-height:36svh;background:var(--bg);color:var(--ink);border-top:1px solid var(--ink)}
.pop::backdrop{background:rgba(20,20,20,.45)}
.pop[open]{display:flex;flex-direction:column}
.pop-h{flex:none;display:flex;align-items:center;justify-content:space-between;padding:2px 4px 2px var(--gx);border-bottom:1px solid var(--line)}
.pop-h b{font:500 19px/1 var(--en);letter-spacing:.02em}
.pop-x{appearance:none;background:none;border:0;padding:0;cursor:pointer;color:inherit;position:relative;width:44px;height:44px}
.pop-x::before,.pop-x::after{content:"";position:absolute;left:11px;top:50%;width:22px;height:1px;background:currentColor;rotate:45deg}.pop-x::after{rotate:-45deg}
.pop-b{overflow-y:auto;overscroll-behavior:contain;padding:14px var(--gx) 24px}
.pop-b.prose p{margin:0;font-size:13px;line-height:1.95;letter-spacing:.04em}.pop-b.prose p+p{margin-top:.8em}.pop-b rt{font-size:8px}
@media(min-width:700px){.pop{position:absolute;z-index:30;inset:auto auto calc(100% + 10px) 0;margin:0;width:min(460px,calc(100vw - 2 * var(--gx)));max-height:min(60svh,420px);border:1px solid var(--ink);box-shadow:0 10px 30px rgba(0,0,0,.12)}.pop-h{padding-left:24px}.pop-b{padding:16px 24px 24px}.pop-b.prose p{font-size:14px}}
/* 縦長のタブレット：スマホと同じ縦の並びのまま、大きくする（横に並べると、上下が大きく空くため） */
@media(min-width:700px) and (orientation:portrait){.uv{padding-top:150px}.uv-pic{height:min(52svh,100vw)}.uv-t{padding-top:32px}.uv-em{width:80px;height:80px}.uv h1{font-size:52px}.uv .uh-tag{font-size:14px}.uv .uh-c{font-size:24px}.uv-bar{margin-top:28px;max-width:520px}.uv-ms{bottom:16px;gap:8px}.uv-m{min-height:34px;font-size:14px;padding:0 16px}}
/* 横長の画面（PC・横持ちのタブレット）：左に絵、右に文字。1画面に収める */
@media(min-width:700px) and (orientation:landscape){
 .uv{padding:100px var(--gx) 40px;min-height:100svh;box-sizing:border-box;display:grid;grid-template-columns:auto 1fr;align-items:center;column-gap:clamp(32px,5vw,72px)}
 .uv-pic{height:auto;width:min(44vw,calc(100svh - 160px),640px);aspect-ratio:1}
 .uv-pic.e>img{padding:48px 48px 80px}
 .uv-ms{left:16px;right:16px;bottom:16px;gap:8px}.uv-ms.at{left:0;right:0}.uv-m{min-height:34px;font-size:14px;padding:0 13px 0 16px}
 .uv-t{padding:0}
 .uv-n{display:block}.uv-em{width:clamp(72px,9vw,120px);height:clamp(72px,9vw,120px);margin:0 0 16px -6px}
 .uv h1{font-size:clamp(36px,5vw,72px)}.uv h1 small{font-size:12px;margin-top:10px}
 .uv .uh-tag{margin-top:24px;font-size:14px}.uv .uh-c{font-size:clamp(18px,2.1vw,26px)}
 .uv-bar{margin-top:32px;max-width:420px}
}
@media(min-width:700px) and (max-width:899px) and (orientation:landscape){.uv{padding-top:150px}}
/* モチーフ（キャラページ）：小さく重ねて開く。背景に鳥の絵、上に文（白いふちどりで読みやすく） */
/* キャラ／鳥の切り替え（2026-11-16。名前は仮）。PC は右側の幅いっぱいで名前の上、スマホは絵のすぐ下。2つとも同じ幅 */
.ch-tab{position:relative;display:grid;grid-template-columns:1fr 1fr;margin:0 0 26px;background:var(--faint);border-radius:99px}
.ch-tab button{appearance:none;position:relative;z-index:1;border:0;margin:0;background:none;color:var(--sub);height:46px;border-radius:99px;font:500 18px/1 var(--en);letter-spacing:.02em;cursor:pointer;transition:color .3s}
.ch-tab button:hover{color:var(--ink)}
/* 選んでいる側：黒い札と、下向きの小さな三角（この下の中身が切り替わったことを示す。Kさんの参考画像 2026-11-16） */
/* 黒い札は1枚だけで、押した側へ滑って移る。止まってから三角が下に出る（Kさんの指示 2026-11-16） */
.ch-tab button[aria-selected=true]{color:var(--bg)}
.ch-ind{position:absolute;left:0;top:0;width:50%;height:100%;border-radius:99px;background:var(--ink);transition:translate .38s cubic-bezier(.65,0,.35,1)}
html.bird .ch-ind{translate:100% 0}
.ch-ind::after{content:"";position:absolute;left:50%;bottom:-7px;translate:-50% 0;border:7px solid transparent;border-bottom:0;border-top-color:var(--ink);transition:opacity .2s,translate .2s}
.ch-tab.mv .ch-ind::after{opacity:0;translate:-50% -6px;transition:none}
@media(prefers-reduced-motion:reduce){.ch-ind,.ch-tab button{transition:none}}
/* PC は名前の下（切り替わるのはそこから下なので。Kさんの指示 2026-11-16）。スマホは絵のすぐ下のまま */
@media(min-width:900px){.ch-t{display:flex;flex-direction:column}.ch-in{order:1}.ch-tab{order:2;margin:26px 0 0}.ch-p{order:3}}
.ch-in{position:relative}.ch-in .ch-nv{right:0;top:0}
.cp-b,.cp-bw,.ch-bd{display:none}
html.bird .cp-c{display:none}html.bird .cp-b,html.bird .cp-bw{display:block}
/* 鳥の側の絵：立ち絵の代わりに鳥。メンバーの色を薄く敷き、鳥の足もとに丸い面を置いて浮いて見えないようにする。鳥の名前はセリフと同じ縦の帯で */
html.bird .ch-img,html.bird .ch-art>.vq,html.bird .tags-a,html.bird .ch-sw{display:none}
html.bird .bg-main,html.bird .bg-dia{opacity:0}html.bird .bg-line{z-index:3}
.ch-bd{position:absolute;inset:0;z-index:2;background:color-mix(in oklab,var(--cm) 14%,var(--bg))}
html.bird .ch-bd{display:block;animation:pFade .35s ease both}
.ch-bd::before{content:"";position:absolute;left:52%;top:52%;width:min(82%,540px);aspect-ratio:1;translate:-50% -50%;border-radius:50%;background:var(--cm);opacity:.16}
.ch-bd>img{position:absolute;left:10%;top:18%;width:84%;height:64%;object-fit:contain}
.ch-ben{position:absolute;left:26px;bottom:52px;font:italic 500 18px/1 var(--en);letter-spacing:.02em;color:color-mix(in oklab,var(--cm) 60%,#141414)}
/* 鳥の紹介：キャラが話す吹き出し → データ → 会える時期 → 見分け方の吹き出し → 豆知識・中の人メモ（声と分ける） */
.cp-b{max-width:640px}
.cp-b .bv{display:grid;grid-template-columns:48px minmax(0,1fr);gap:12px;align-items:start}
.cp-b .bv+*{margin-top:20px}.cp-b *+.bv{margin-top:24px}
/* 顔：四角い絵を丸く切り抜く。枠は付けない（Kさんの指示 2026-11-16：枠がうるさく、キャラが見えにくい） */
.bv-f{width:48px;height:48px;border-radius:50%;object-fit:cover;background:var(--faint)}
.cp-b .bv-b{padding:13px 18px 14px;background:color-mix(in oklab,var(--cm) 11%,var(--bg));border-radius:4px 18px 18px 18px}
.cp-b .bv-b p{margin:0;font:400 14px/1.9 var(--jp);letter-spacing:.04em}
.cp-b .bv-b .bv-k{margin:0 0 2px;font-size:11px;line-height:1.6;color:var(--sub)}
/* データ：左に 区分・地域（上段2マス）といる場所（下段）、右に見つけやすさ。マスの境に細い線を引いて、どこからどこまでが1項目か分かるように（Kさんの指示 2026-11-16） */
.cp-b .bf{display:grid;grid-template-columns:minmax(0,1fr) 104px;border-top:1px solid var(--ink);border-bottom:1px solid var(--ink)}
/* 縦の線は上下の線に付けず、少し離す（Kさんの指示 2026-11-16） */
.bf-g{position:relative;margin:0;display:grid;grid-template-columns:1fr 1fr}
.bf-g::after,.bf-g>div:nth-child(2)::before{content:"";position:absolute;top:10px;bottom:10px;width:1px;background:var(--line)}
.bf-g::after{right:0}
.bf-g>div{padding:11px 12px 12px 0}.bf-g>div:nth-child(2){position:relative;padding-left:14px}.bf-g>div:nth-child(2)::before{left:0}
.bf-g .w{grid-column:1/-1;border-top:1px solid var(--line)}
.cp-b .bf-g dt,.cp-b .bf-k,.cp-b .bm-h{margin:0;font:500 11px/1.6 var(--jp);letter-spacing:.06em;color:var(--sub)}
.cp-b .bf-g dd{margin:3px 0 0;font:500 16px/1.5 var(--jp);letter-spacing:.04em}
.bf-s{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:12px 0 12px 8px;text-align:center}
.bf-s .st{display:block;font-size:24px;line-height:1;letter-spacing:4px}.cp-b .bf-l{margin:0;font:500 12px/1.4 var(--jp)}
.cp-b .bm{margin-top:16px}.cp-b .bm-h{margin-bottom:8px;display:flex;justify-content:space-between}
.bm-now{display:none;color:color-mix(in oklab,var(--cm) 60%,#141414);font-weight:500}.bm-now::before{content:"";display:inline-block;width:7px;height:7px;margin-right:6px;border-radius:50%;background:currentColor;vertical-align:1px}
.bm.now .bm-now{display:inline}
/* 会える時期：地方ごとに12か月の帯。いる月をメンバーの色で塗り、今月に印。補足は右端 */
.mo{display:grid;gap:5px}
.mo-r{display:grid;grid-template-columns:62px minmax(0,1fr) 56px;align-items:center;column-gap:8px}
.mo-l{font:500 11px/1.3 var(--jp);letter-spacing:.02em}
.mo-c{display:grid;grid-template-columns:repeat(12,1fr);gap:2px}
.mo-c i{height:16px;background:var(--faint);border-radius:3px}.mo-c i.on{background:var(--cm)}.cp-b.lt .mo-c i.on{box-shadow:inset 0 0 0 1px rgba(20,20,20,.4)}
.mo-c i.now{outline:1.5px solid var(--ink);outline-offset:1px}
.mo-n{font:400 10px/1.3 var(--jp);color:var(--sub)}
.mo-se .mo-c b{padding-bottom:3px;border-bottom:1px solid var(--line);font:500 11px/1.2 var(--jp);text-align:center;color:var(--sub)}
.mo-a{margin-bottom:1px}.mo-a .mo-c b{font:500 14px/1 var(--en);font-variant-numeric:lining-nums;text-align:center;color:var(--sub)}.mo-a .mo-c b.now{color:var(--ink);font-weight:700}.mo-a .mo-n{font-size:10px}
/* 押すと開く欄：見出しの行だけ並べ、右の＋が開くと−になる。中の人メモだけ灰色の面で、キャラの声と分ける */
.cp-b .bxs{margin-top:28px;border-bottom:1px solid var(--line)}
.cp-b .bx{border-top:1px solid var(--line)}
.cp-b .bx summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:52px;cursor:pointer}
.cp-b .bx summary::-webkit-details-marker{display:none}
.cp-b .bx summary::after{content:"";flex:none;width:12px;height:12px;background:linear-gradient(var(--ink),var(--ink)) center/12px 1.5px no-repeat,linear-gradient(var(--ink),var(--ink)) center/1.5px 12px no-repeat;transition:rotate .25s}
.cp-b .bx[open] summary::after{background:linear-gradient(var(--ink),var(--ink)) center/12px 1.5px no-repeat;rotate:180deg}
.cp-b .bx summary:hover .bx-k{color:var(--sub)}
.cp-b .bx-k{font:italic 500 18px/1 var(--en)}.bx-k small{margin-left:10px;font:400 11px var(--jp);font-style:normal;color:var(--sub)}
.cp-b .bx-in{padding:0 0 18px;animation:pFade .3s ease both}
.cp-b .bx-in>p{margin:0;font:400 14px/1.95 var(--jp);letter-spacing:.04em}
.cp-b .bx.memo .bx-in{margin-bottom:16px;padding:14px 16px 16px;background:var(--faint)}
@media(prefers-reduced-motion:reduce){.cp-b .bx-in{animation:none}.cp-b .bx summary::after{transition:none}}
.cp-b .bd-go{margin-top:32px;width:fit-content}.bd-go .btn{min-width:180px}
/* PC の鳥の側：右が長くなるので上でそろえ、絵は画面に残す。Scroll の合図は文字に重なるので出さない */
@media(min-width:900px){section.ch{align-items:start}.ch>.ch-t{padding-top:39px}html.bird .ch-art{position:sticky;top:0}html.bird .ch-hint{display:none}}
@media(min-width:700px){.cp-b .bf,.cp-b .bm{margin-left:60px}.mo-r{grid-template-columns:76px minmax(0,1fr) 64px}.mo-l{font-size:12px}.mo-c i{height:20px}.mo-a .mo-c b{font-size:16px}.mo-n{font-size:11px}.cp-b .bxs{margin-left:60px}.cp-b .bd-go{margin-left:60px}.cp-b .bv-b p{font-size:15px}}
/* 見つけやすさ：四つ角の星。キャラの色（明るい色には細いふち）。足りない分は薄い灰色 */
.st{white-space:nowrap;letter-spacing:.12em}.st b{font-weight:400;color:var(--sc,var(--ink))}.st i{font-style:normal;color:#E2E2DE}.st.lt b{-webkit-text-stroke:.9px rgba(20,20,20,.6)}
/* Birds ページ：マナー → 見つけやすさで選ぶ → 14羽の一覧（1羽1行、Songs の一覧と同じく縦に短く） */
.bp{padding-bottom:32px}
.bp-l{margin:0 0 32px;max-width:40em;font-size:15px;line-height:2.1}
.bp-m{max-width:40em;padding:4px 20px 18px;border:1px solid var(--ink)}
.bp .bp-k{margin:14px 0 6px;font:500 11px/1.6 var(--jp);letter-spacing:.08em;color:var(--sub)}.bp .bp-kk{margin:32px 0 10px}
.bp-m ul{margin:0;padding:0;list-style:none;font-size:14px;line-height:1.9}.bp-m li{position:relative;padding-left:18px}.bp-m li+li{margin-top:4px}
.bp-m li::before{content:"";position:absolute;left:0;top:.95em;width:9px;height:1px;background:var(--ink)}
.bp-f{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;max-width:520px}.bp-f .md{min-height:44px;padding:0 6px;justify-content:center;font-size:13px}.bp-f .st{font-size:15px;letter-spacing:.18em}
.bp-lg{margin:12px 0 20px;display:flex;flex-wrap:wrap;gap:4px 20px;font-size:12px;color:var(--sub)}.bp-lg b{margin-right:8px;font-weight:400;color:var(--ink)}
.bl{list-style:none;margin:0;padding:0;border-top:1px solid var(--ink)}.bl li[hidden]{display:none}
.bl-i{display:grid;grid-template-columns:48px minmax(0,1fr) auto;gap:14px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line);transition:opacity .25s}.bl-i:hover{opacity:.7}
.bl-i img{width:48px;height:48px;border-radius:50%;object-fit:cover}
.bl-t b{display:block;font:500 17px/1.4 var(--min);letter-spacing:.06em}.bl-t small{display:block;margin-top:2px;font:400 12px/1.5 var(--jp);color:var(--sub)}.bl-t rt{font-size:7px}
.bl-s{display:flex;flex-direction:column;align-items:flex-end;gap:2px}.bl-s .st{font-size:17px}.bl-s small{font-size:10px;color:var(--sub)}
@media(min-width:900px){.bp-l{font-size:16px}.bl{display:grid;grid-template-columns:1fr 1fr;column-gap:48px}.bl-i{grid-template-columns:56px minmax(0,1fr) auto}.bl-i img{width:56px;height:56px}}
.ch-x{margin-top:24px}.ch-x .row{width:fit-content}.ch-x .btn{min-width:168px;padding-inline:24px}
.ch-mm{margin-top:28px}.ch-mm .lbl{margin:0 0 12px}
.mm{display:flex;flex-wrap:wrap;gap:14px 22px}
.mm-i{display:flex;flex-direction:column;align-items:center;gap:6px;font:500 12px/1.5 var(--min);letter-spacing:.04em;text-align:center;transition:opacity .25s}.mm-i:hover{opacity:.7}
.mm-i img{width:64px;height:64px;border-radius:50%;object-fit:cover}
.sl-s .more{margin-top:20px}
/* PCのキャラページ：最初の画面だけで完結して見えるので、下に参加曲があることをトップと同じ「Scroll」で知らせる（画面の下端の少し上に置く） */
@media(min-width:900px){.ch-hint{top:calc(100svh - 130px);bottom:auto}}
/* スマホのキャラページのプロフィール：項目を2列にして、見出しと上の空きも小さくする（2026-11-15） */
@media(max-width:899px){#profile{padding-top:56px}
 #profile .pf{margin-top:20px;display:grid;grid-template-columns:1fr 1fr;column-gap:20px}#profile .pf div{display:block;padding:7px 0}
 #profile .pf dt{line-height:1.6}#profile .pf dd{font-size:14px;line-height:1.7}#profile .ch-x{margin-top:20px}#profile .ch-mm{margin-top:20px}#profile .prose p{font-size:14px;line-height:1.95}}
.nw{white-space:nowrap}@media(max-width:699px){.br-w{display:none}}
/* mood tags on each song: small pills; pressing one picks that mood above */
.sg-m{margin:8px 0 0;display:flex;flex-wrap:wrap;gap:6px;align-items:flex-start;align-content:flex-start}   /* 2026-11-15 隣の曲のタグが2段になると、1つだけの札が縦に伸びて楕円になっていた */
.tg{appearance:none;background:none;margin:0;cursor:pointer;min-height:24px;padding:0 10px;border:1px solid var(--line);border-radius:999px;font:500 11px/1 var(--jp);letter-spacing:.06em;color:var(--sub);white-space:nowrap;transition:border-color .25s,color .25s}
.tg:hover{border-color:var(--ink);color:var(--ink)}
.lk button{font:inherit;letter-spacing:inherit}
@media(min-width:900px){.sgs{grid-template-columns:repeat(3,1fr);gap:0 48px}.sgs .rel{padding-bottom:56px}.flts{margin-bottom:64px}.flt{grid-template-columns:64px 1fr;align-items:center;gap:20px}}

/* 個別ページ（ユニット・メンバー）だけの見た目。色・文字・見出し・線の約束は style.css と同じ */
.prose{max-width:640px}
.prose p{margin:0 0 1.6em;font-size:15px;line-height:2.2}
.rels.solo{grid-template-columns:minmax(0,300px)}
/* member page songs: one thin row per song (small jacket, title, the three buttons) = stays short as songs are added */
.sl{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.sl-i{display:grid;grid-template-columns:56px minmax(0,1fr);column-gap:14px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)}
.sl-j{grid-row:1/span 3;align-self:start;display:block}.sl-j img{display:block;width:56px;height:56px;object-fit:cover}
.sl-i h3{margin:0;font:500 17px/1.4 var(--min);letter-spacing:.04em}
.sl-i .lk{margin:8px 0 0}.sl-i .ep-in{margin:8px 0 0}
.uh-tag{margin:22px 0 0;font:500 13px/1.6 var(--jp);letter-spacing:.06em;color:var(--sub)}
.uh-c{margin:6px 0 0;font:500 21px/1.7 var(--min);letter-spacing:.06em}
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
.ch-t{position:relative;padding:30px var(--gx) 0}
.ch-p,.n-pc{display:none}
/* motif bird: below the text on phones, beside the text on wide screens; it never sits under the words */
/* モチーフの鳥: 下から2番目の層（薄い大きな見出し文字のすぐ上、文章の下）に大きく薄く置く。文章と少し重なってよい。段の外へは出さない（切らない） */
.has-b{padding-bottom:110px;min-height:calc(66vw + 330px)}.has-b .mt-p{position:relative;z-index:1}
.mt-b{position:absolute;z-index:0;left:3vw;top:230px;width:94vw;max-width:none;height:auto;opacity:.42;pointer-events:none}
.mt-b.tall{width:60vw;left:20vw}.has-b.tall{min-height:calc(96vw + 330px)}
/* phone: a smaller bird (the text over it stays easy to read) and no spare room kept under it (K 2026-11-14) */
@media(max-width:699px){.has-b{padding-bottom:32px;min-height:calc(48vw + 262px)}.mt-b{width:72vw;left:14vw}.mt-b.tall{width:46vw;left:27vw}.has-b.tall{min-height:calc(74vw + 262px)}}
@media(min-width:700px){.mt-b.tall{width:min(26vw,330px);left:auto}.has-b.tall{min-height:calc(min(26vw,330px)*1.6 + 380px)}}
@media(min-width:700px){.has-b{padding-bottom:150px;min-height:calc(min(62vw,760px)*.68 + 380px)}.mt-b{left:auto;right:var(--gx);top:250px;width:min(62vw,760px)}}
/* 縦長の鳥（フクロウ、サンコウチョウ）は、PCでは見出しの線より下から始める（段の番号の数字に頭が重ならないように） */
@media(min-width:700px){.mt-b.tall{top:340px}.has-b.tall{min-height:calc(min(26vw,330px)*1.62 + 470px)}}
@media(min-width:700px) and (max-width:899px){.ch-art{height:600px}.ch-img img{height:190%}.vq{top:18%}}
/* タグ：どの幅でも、立ち絵の右下に右寄せの横帯で出す（Kさんの指示 2026-11-15：タブレットもPCもスマホとそろえる。左にはセリフの帯があるので右へ）。形は両端の丸い帯（Kさんが案4に決定 2026-11-15） */
.tags-a{position:absolute;z-index:4;right:18px;bottom:44px;margin:0;padding:0;list-style:none;display:grid;gap:8px;justify-items:end}
.tags-a li{padding:5px 18px;border-radius:99px;background:var(--cm);color:var(--tc);font:500 13px/1.5 var(--jp);letter-spacing:.06em}
/* 帯の出入り: 絵が画面の真ん中に来たら、右の端から帯が1本ずつ伸び、文字があとから追いつく。離れると右へ戻る（絵と同じ合図で動かす） */
.js .tags-a li{clip-path:inset(0 0 0 100% round 99px);transition:clip-path .45s cubic-bezier(.7,0,.84,0)}
.js .tags-a li span{display:inline-block;opacity:0;transform:translateX(18px);transition:opacity .2s ease,transform .3s ease}
.js .tags-a li:nth-child(2){transition-delay:.07s}.js .tags-a li:nth-child(1){transition-delay:.14s}
.rdy .fv.lit .tags-a li{clip-path:inset(0 round 99px);transition:clip-path .75s cubic-bezier(.16,1,.3,1) .45s}
.rdy .fv.lit .tags-a li:nth-child(2){transition-delay:.57s}.rdy .fv.lit .tags-a li:nth-child(3){transition-delay:.69s}
.rdy .fv.lit .tags-a li span{opacity:1;transform:none;transition:opacity .5s ease .7s,transform .7s cubic-bezier(.16,1,.3,1) .7s}
.rdy .fv.lit .tags-a li:nth-child(2) span{transition-delay:.82s}.rdy .fv.lit .tags-a li:nth-child(3) span{transition-delay:.94s}
@media(min-width:700px){.tags-a{bottom:52px;gap:8px}.tags-a li{font-size:15px;padding:7px 18px}}
@media(prefers-reduced-motion:reduce){.js .tags-a li,.js .tags-a li span{clip-path:none;opacity:1;transform:none;transition:none}}
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
.pf div{display:grid;grid-template-columns:104px 1fr;gap:12px;padding:8px 0;border-bottom:1px solid var(--line)}
.pf dt{font:500 12px/2.1 var(--jp);letter-spacing:.06em;color:var(--sub)}.pf dd{margin:0;font-size:15px}
.mt{margin:0 0 16px;font:500 26px/1.4 var(--min);letter-spacing:.08em;display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.mt small{font:italic 500 17px var(--en);letter-spacing:.02em;color:var(--sub)}
.un{margin:0 0 36px}.un a{display:inline-flex;align-items:baseline;gap:14px;min-height:44px;font:italic 500 34px/1.1 var(--en);border-bottom:1px solid var(--ink);padding-bottom:6px}
.un small{font:500 12px/1 var(--jp);font-style:normal;color:var(--sub);letter-spacing:.06em}
/* スマホ：立ち絵の段を画面の高さに合わせて少し低くし、1画面に名前まで入れる（Kさんの指示 2026-11-15）。上のピルはたたんであるので、上の余白も詰める */
@media(max-width:699px){.ch{padding-top:84px}.ch-art{height:clamp(340px,calc(100svh - 270px),470px)}}
/* 幅のとても狭いスマホ（360px未満）は、低くするとセリフの帯とタグの帯が重なるので、立ち絵の段の高さは変えない */
@media(max-width:359px){.ch-art{height:470px}}
@media(min-width:900px){
 .prose p{font-size:16px}
 .rels.solo{grid-template-columns:340px}
 .sl-i{grid-template-columns:64px minmax(0,1fr) 252px 150px;column-gap:24px;padding:10px 0}.sl-j{grid-row:auto}.sl-j img{width:64px;height:64px}.sl-i h3{font-size:20px}.sl-i .lk{margin:0;width:252px}.sl-i .ep-in{margin:0}
 .ch{padding-top:96px;display:grid;grid-template-columns:1fr 1fr;align-items:center;padding-inline:max(0px,calc(50% - 640px))}
 .ch-art{height:760px}.bg-dia{width:580px;top:-40px;right:-238px}.bg-line{width:24px}.bg-deco{height:42px}
 .ch-img img{height:165%;margin:40px 0 0 8%}.ch-em{left:14px;top:14px;width:84px;height:84px}.ch-sw{right:40px;top:16px}.ch-img.full img{margin:0 0 42px}.tags{font-size:16px;margin-top:32px;padding-top:26px}
 .vq{left:64px;top:16%;gap:11px}.vq .col{font-size:19px;letter-spacing:.14em;line-height:1.7;padding:18px 10px}.vq .col.low{margin-top:74px}
 .ch-t{box-sizing:border-box;padding:0 32px 0 72px;max-width:684px}.ch-in .ch-nv{top:10px}.ch h1{font-size:54px}.ch-nv{right:32px;top:10px}.ch-u{font-size:22px;margin-bottom:14px}.ch-u img{width:72px;height:72px;margin-left:-6px}
 .ch-p{display:block;margin-top:26px}.ch-p p{margin:0;font-size:15px;line-height:2}
 .ch-p .pf{margin-top:22px;display:grid;grid-template-columns:1fr 1fr;column-gap:32px}.ch-p .pf div{grid-template-columns:84px 1fr;gap:8px;padding:6px 0}.ch-p .pf dd{font-size:14px;line-height:1.9}
 @media(max-width:1099px){.ch-t{padding-left:44px}.ch h1{font-size:46px}.ch-p .pf{column-gap:20px}.ch-p .pf div{grid-template-columns:76px 1fr}}
 .tags-a{bottom:76px}.tags-a li{font-size:15px;padding:8px 18px}
 #profile,.n-sp{display:none}.n-pc{display:inline}.ch .tags{margin-top:22px;padding-top:18px;font-size:15px}
 .pf div{grid-template-columns:160px 1fr}
}
@media(prefers-reduced-motion:reduce){.ch-art{filter:none}}
/* ガイドライン：読むためのページ。1行を40字ほどに収め、番号と見出しで目当ての項目を探せるようにする。PCは左に見出し・右に本文 */
.gl{padding-bottom:16px}
.gl-l{margin:0 0 48px;max-width:40em;font-size:15px;line-height:2.1}
.gl-s{border-top:1px solid var(--ink)}
.gl-i{display:grid;grid-template-columns:40px 1fr;column-gap:12px;row-gap:14px;align-items:baseline;padding:28px 0 30px;border-bottom:1px solid var(--line)}
.gl-n{margin:0;font:italic 500 22px/1 var(--en);color:var(--sub)}
.gl-i h3{margin:0;font:500 19px/1.5 var(--min);letter-spacing:.08em}
.gl-b{grid-column:1/-1;max-width:40em;font-size:15px;line-height:2.1}
.gl-b p{margin:0}.gl-b p+p{margin-top:.9em}
.gl-b ul{margin:0;padding:0;list-style:none}.gl-b li{position:relative;padding-left:20px}.gl-b li+li{margin-top:.5em}
.gl-b li::before{content:"";position:absolute;left:0;top:1.05em;width:10px;height:1px;background:var(--ink)}
.gl-x{margin:32px 0 0;max-width:40em;font-size:13px;line-height:2;color:var(--sub)}
.gl-b a{border-bottom:1px solid var(--ink)}.gl .nb{white-space:nowrap}
@media(min-width:900px){.gl{padding-bottom:32px}.gl-l{margin-bottom:48px;font-size:16px}
 .gl-i{grid-template-columns:64px 236px minmax(0,1fr);column-gap:0;padding:40px 0 44px}.gl-n{font-size:26px}.gl-i h3{font-size:22px}.gl-b{grid-column:auto;font-size:16px}.gl-x{margin-left:300px}}
"""

def main():
    out = [(f"units/{T.SLUG[u]}.html", unit_page(u)) for u in UNIT if u in T.PAGES]
    out += [(f"members/{T.MSLUG[c]}.html", char_page(c)) for c in ORDER]
    out.append(("songs.html", songs_page()))
    out.append(("guideline.html", guideline_page()))
    out.append(("birds.html", birds_page()))
    out.append(("css/page.css", CSS.lstrip("\n")))
    for path, text in out:
        full = os.path.join(T.ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f: f.write(text)
        print("ok", path)

if __name__ == "__main__":
    main()
