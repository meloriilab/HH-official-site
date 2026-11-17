/*
 サイトのチェック役（2026-11-17 Kさんの指示：区切りごとにチェックを通し、通ったものだけを見せる）
 使い方：  node tools/check/check_site.js            … 全部（数分かかる）
           node tools/check/check_site.js --quick    … 幅を4通りに減らす
 結果：    最後に「合格」か「不合格」と、見つかった問題の一覧を出す。不合格なら終了コード 1。
 前提：    playwright（require('playwright') で読めること）。public/ を自分で配信して開く。外のサイトへは通信しない。

 調べること
  1. リンク：サイトの中のリンクの行き先（ファイル）があるか。# 付きなら、行き先のページにその id があるか。
             上の帯・メニュー・ユニットの札を実際に押して、着いたページと場所が合っているか。
  2. はみ出し：全ページを、スマホ〜大きなPC・横向きの幅で開き、画面の外にはみ出す文字や部品がないか。
  3. 重なり：ユニットのページの名前の札どうし、札と左右の矢印が重なっていないか。
  4. 動き：Units ボタン（スマホ）・About・Episode・絞り込みが、動きを減らす設定でも働くか。
  5. エラー：ページを開いたときのエラー。
  6. 決まりごと：制作用の記号（TRT01 など）が画面に出ていない／外のサイトへのリンクは新しいタブ／
                画像が全部読める／ページの名前（タブに出る名前）がある。
*/
const {chromium} = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../public');
const QUICK = process.argv.includes('--quick');
const problems = [];
const bad = (kind, where, what) => problems.push(`[${kind}] ${where}：${what}`);

const TYPES = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.json':'application/json','.ico':'image/x-icon'};
function serve() {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      let u = decodeURIComponent(q.url.split('?')[0].split('#')[0]);
      if (u.endsWith('/')) u += 'index.html';
      const f = path.join(ROOT, u);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); r.end('not found'); return; }
      r.writeHead(200, {'content-type': TYPES[path.extname(f)] || 'application/octet-stream'}); fs.createReadStream(f).pipe(r);
    });
    s.listen(0, '127.0.0.1', () => res(s));
  });
}

function pages() {
  const out = ['index.html', 'songs.html', 'birds.html', 'guideline.html'];
  for (const d of ['units', 'members']) for (const f of fs.readdirSync(path.join(ROOT, d)).sort()) if (f.endsWith('.html')) out.push(`${d}/${f}`);
  return out;
}

// 1. リンク（ファイルを読むだけで分かるもの）
function staticLinks(list) {
  const ids = {};
  const html = {};
  for (const p of list) { html[p] = fs.readFileSync(path.join(ROOT, p), 'utf8'); ids[p] = new Set([...html[p].matchAll(/\sid="([^"]+)"/g)].map(m => m[1])); }
  for (const p of list) {
    const h = html[p];
    for (const m of h.matchAll(/<a\b([^>]*)>/g)) {
      const attrs = m[1], href = (attrs.match(/\shref="([^"]*)"/) || [])[1];
      if (href === undefined) continue;
      if (/^https?:\/\//.test(href)) { if (!/target="_blank"/.test(attrs)) bad('決まり', p, `外のサイトへのリンクが新しいタブで開かない：${href}`); continue; }
      if (/^(mailto:|tel:|javascript:)/.test(href)) continue;
      if (href === '') { bad('リンク', p, 'href が空（今のページを開き直すだけ）'); continue; }
      const [file, hash] = href.split('#');
      let target = file ? path.posix.normalize(path.posix.join(path.posix.dirname(p), file.split('?')[0])) : p;
      if (target.endsWith('/') || target === '.') target = path.posix.join(target, 'index.html');
      if (!fs.existsSync(path.join(ROOT, target))) { bad('リンク', p, `行き先のファイルがない：${href}`); continue; }
      if (hash && !hash.startsWith('episode-') && hash !== 'bird') {
        if (!ids[target]) { const t = fs.readFileSync(path.join(ROOT, target), 'utf8'); ids[target] = new Set([...t.matchAll(/\sid="([^"]+)"/g)].map(m => m[1])); }
        if (!ids[target].has(hash)) bad('リンク', p, `行き先（${target}）に #${hash} がない：${href}`);
      }
    }
    for (const m of h.matchAll(/<img\b[^>]*\ssrc="([^"]+)"/g)) {
      const src = m[1].split('?')[0]; if (/^(https?:|data:)/.test(src)) continue;
      if (!fs.existsSync(path.join(ROOT, path.posix.normalize(path.posix.join(path.posix.dirname(p), src))))) bad('画像', p, `画像がない：${m[1]}`);
    }
    if (!/<title>[^<]+<\/title>/.test(h)) bad('決まり', p, 'ページの名前（title）がない');
  }
}

// はみ出しの検査（飾りとして画面の外へ出しているものは除く）
const OVERFLOW = () => {
  const iw = document.documentElement.clientWidth, out = [];
  for (const e of document.querySelectorAll('main *, header *, footer *')) {
    if (e.closest('[aria-hidden=true],[data-speed],.word,.trio,[hidden],dialog:not([open]),.menu,.up-m,.dd-m,[class^="bg-"]')) continue;
    const s = getComputedStyle(e); if (s.display === 'none' || s.visibility === 'hidden' || s.position === 'fixed') continue;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
    if (r.right > iw + 1 || r.left < -1) out.push(((typeof e.className === 'string' && e.className) ? '.' + e.className.split(' ')[0] : e.tagName) + '「' + (e.textContent || '').trim().slice(0, 12) + '」');
  }
  return [...new Set(out)].slice(0, 4);
};
const CODES = () => { const t = document.body.innerText; const m = t.match(/\b(TRT|NCT|PRS|BLC|BVH|ORB|WGO)[-_]?\d{1,3}\b/); return m ? m[0] : ''; };
const PILLS = () => {
  const ps = [...document.querySelectorAll('.uv-m')].map(e => e.getBoundingClientRect()), o = [];
  const pic = document.querySelector('.uv-pic'); if (!pic) return o; const pr = pic.getBoundingClientRect();
  for (let i = 0; i < ps.length; i++) {
    for (let j = i + 1; j < ps.length; j++) { const a = ps[i], c = ps[j]; if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) o.push(`札${i + 1}と札${j + 1}が重なる`); }
    if (ps[i].left < pr.left - 1 || ps[i].right > pr.right + 1) o.push(`札${i + 1}が絵からはみ出す`);
    for (const a of document.querySelectorAll('.uv-ar')) { const r = a.getBoundingClientRect(), c = ps[i]; if (r.left < c.right && c.left < r.right && r.top < c.bottom && c.top < r.bottom) o.push(`札${i + 1}と矢印が重なる`); }
  }
  return o;
};

(async () => {
  const server = await serve(), BASE = `http://127.0.0.1:${server.address().port}/`;
  const list = pages();
  staticLinks(list);
  const b = await chromium.launch();
  const SIZES = QUICK ? [[320, 640], [390, 844], [1024, 768], [1440, 900]]
    : [[320, 640], [360, 740], [390, 844], [430, 932], [600, 900], [700, 1000], [768, 1024], [820, 1180], [899, 1000], [900, 1000], [1024, 768], [1100, 800], [1180, 820], [1280, 800], [1366, 768], [1440, 900], [1920, 1080], [1280, 600], [844, 390], [932, 430]];

  // 2・3・5・6 はみ出し・重なり・エラー・記号
  for (const [w, h] of SIZES) {
    const ctx = await b.newContext({viewport: {width: w, height: h}, hasTouch: w < 900 || h < 500});
    await ctx.route(u => !u.href.startsWith(BASE), r => r.abort());
    const pg = await ctx.newPage(); const errs = [];
    pg.on('pageerror', e => errs.push(e.message));
    for (const p of [...list, ...list.filter(x => x.startsWith('members/')).map(x => x + '#bird')]) {
      errs.length = 0;
      await pg.goto(BASE + p, {waitUntil: 'load'}); await pg.waitForTimeout(150);
      const o = await pg.evaluate(OVERFLOW); if (o.length) bad('はみ出し', `${w}×${h} ${p}`, o.join('、'));
      if (p.startsWith('units/')) { const q = await pg.evaluate(PILLS); if (q.length) bad('重なり', `${w}×${h} ${p}`, q.join('、')); }
      if (w === 390 || w === 1440) { const c = await pg.evaluate(CODES); if (c) bad('決まり', p, `制作用の記号が画面に出ている：${c}`); }
      if (errs.length) bad('エラー', `${w}×${h} ${p}`, errs.join(' / '));
    }
    await ctx.close();
  }

  // 1. リンクの意味：全ページの、名前のついたリンクが、その名前どおりの所を指しているか
  //    （ロゴ→TOP、Songs→曲のページ、ユニットの札→そのユニット、メンバー名→そのメンバーのページ、など。2026-11-17 チェック役の指摘で追加）
  {
    const ctx = await b.newContext({viewport: {width: 1440, height: 900}});
    await ctx.route(u => !u.href.startsWith(BASE), r => r.abort());
    const pg = await ctx.newPage();
    const who = {};   // メンバー名 → ページ
    for (const p of list.filter(x => x.startsWith('members/'))) { const t = fs.readFileSync(path.join(ROOT, p), 'utf8').match(/<title>([^|<]+)/); if (t) who[t[1].replace(/\s/g, '')] = p; }
    const unitName = {};   // ユニット名 → ページ
    for (const p of list.filter(x => x.startsWith('units/'))) unitName[p.slice(6, -5)] = p;
    const SEC = {units: 1, members: 1, news: 1, mood: 1, pickup: 1};
    for (const p of list) {
      await pg.goto(BASE + p, {waitUntil: 'domcontentloaded'});
      const links = await pg.evaluate(() => [...document.querySelectorAll('a[href]')].filter(a => !a.target).map(a => {
        const c = a.cloneNode(true); c.querySelectorAll('rt,rp,i,small').forEach(x => x.remove());
        return {txt: c.textContent.replace(/\s/g, ''), cls: a.className, u: a.dataset.u || '', href: a.getAttribute('href'), url: a.href,
                area: a.closest('.gnav') ? 'gnav' : a.closest('.m-nav') ? 'menu' : a.closest('.ft-l') ? 'foot' : a.closest('.up-m') ? 'upm' : ''};
      }));
      for (const l of links) {
        const u = new URL(l.url), file = u.pathname.replace(/^\//, '') || 'index.html', hash = u.hash.slice(1), say = `「${l.txt || l.cls}」（${l.href}）`;
        const want = (f, h) => { if (file !== f || (h !== undefined && hash !== h)) bad('リンク', p, `${say} が ${file}${u.hash} を指している（${f}${h ? '#' + h : ''} のはず）`); };
        if (/\blogo\b/.test(l.cls)) { if (!(file === 'index.html' && (hash === '' || p === 'index.html'))) want('index.html', ''); continue; }
        if (l.area === 'gnav' || l.area === 'menu' || l.area === 'foot') {
          const k = l.txt.toLowerCase().replace(/[^a-z]/g, '').replace(/^(songs|units|members|birds|news|guideline).*/, '$1');
          if (k === 'songs') want('songs.html'); else if (k === 'birds') want('birds.html'); else if (k === 'guideline') want('guideline.html');
          else if (SEC[k]) want('index.html', k);
          continue;
        }
        if (/\bup-a\b/.test(l.cls) && l.u) { if (unitName[l.u]) want(unitName[l.u]); else want('index.html', l.u); continue; }
        const member = who[l.txt];
        if (member && (l.area === 'upm' || /\b(uv-m|mem|bl-i|bd-i)\b/.test(l.cls))) { if (file !== member) want(member); continue; }
      }
    }
    await ctx.close();
  }

  // 1. 押して着く場所（上の帯・メニュー・ユニットの札）
  const WHERE = () => { const el = document.elementFromPoint(innerWidth / 2, innerHeight * 0.4); const s = el && el.closest('[id]'); return {file: location.pathname.split('/').pop() || 'index.html', hash: location.hash, at: s ? s.id : ''}; };
  for (const [w, h, touch] of [[390, 844, true], [1440, 900, false]]) {
    const ctx = await b.newContext({viewport: {width: w, height: h}, hasTouch: touch});
    await ctx.route(u => !u.href.startsWith(BASE), r => r.abort());
    const pg = await ctx.newPage();
    for (const from of ['index.html', 'songs.html', 'birds.html', 'guideline.html', 'units/orybia.html', 'members/jo-hitaki.html']) {
      const sel = touch ? '.menu a' : '.gnav a';
      await pg.goto(BASE + from);
      const links = await pg.$$eval(sel, a => a.map(x => ({t: x.textContent.trim().split(/\s/)[0], href: x.getAttribute('href'), ext: !!x.getAttribute('target')})));
      for (let i = 0; i < links.length; i++) {
        if (links[i].ext) continue;
        await pg.goto(BASE + from); await pg.waitForTimeout(300);
        if (touch) { await pg.click('.burger'); await pg.waitForTimeout(250); }
        await (await pg.$$(sel))[i].click(); await pg.waitForLoadState('load').catch(() => {}); await pg.waitForTimeout(1800);
        const r = await pg.evaluate(WHERE), name = links[i].t.replace(/[^A-Za-z]/g, '').toLowerCase();
        const wantFile = {songs: 'songs.html', birds: 'birds.html'}[name] || 'index.html';
        if (r.file !== wantFile) bad('リンク', `${w}px ${from}`, `メニューの「${links[i].t}」で ${r.file} に着いた（${wantFile} のはず）`);
        else if (wantFile === 'index.html') { const ok = name === 'units' ? /^(units|triattique|nocturnalfizz|prismea|blackveil-harmonic|orybia)$/.test(r.at) : r.at === name; if (!ok) bad('リンク', `${w}px ${from}`, `メニューの「${links[i].t}」で ${r.at || '不明'} の場所に着いた（${name} のはず）`); }
      }
      // ユニットの札（スマホのユニット・メンバーのページは Units ボタンで開いてから）
      const n = await pg.$$eval('.up-a', a => a.length);
      for (let i = 0; i < n; i++) {
        await pg.goto(BASE + from); await pg.waitForTimeout(300);
        const uf = await pg.$('.uf'); if (touch && uf && await uf.isVisible()) { await uf.click(); await pg.waitForTimeout(200); }
        const a = (await pg.$$('.up-a'))[i]; if (!await a.isVisible()) continue;
        if (await a.evaluate(e => e.getBoundingClientRect().bottom <= 0)) continue;   // 画面の上に隠してある札（ユニットの段に来るまで出さない作り）は押せなくて正しい
        const slug = await a.getAttribute('data-u'), nm = (await a.textContent()).trim();
        try { await a.click({timeout: 4000}); } catch (e) { bad('リンク', `${w}px ${from}`, `ユニットの札「${nm}」が押せない（ほかの部品の下に隠れている）`); continue; }
        await pg.waitForTimeout(400); await pg.waitForLoadState('load').catch(() => {});
        if (await pg.$('.up.open .up-m').catch(() => null)) { const m = await pg.$('.up.open .up-m a'); if (!m) continue; try { await a.click({timeout: 4000}); } catch (e) { bad('リンク', `${w}px ${from}`, `ユニットの札「${nm}」の2回目が押せない`); continue; } }   // タッチは1回目でメンバー名が開く。2回目で移る
        await pg.waitForLoadState('load').catch(() => {}); await pg.waitForTimeout(1500);
        const r = await pg.evaluate(WHERE);
        const okHere = r.file === `${slug}.html` || (r.file === 'index.html' && r.at === slug);
        if (!okHere && !(from === `units/${slug}.html`)) bad('リンク', `${w}px ${from}`, `ユニットの札「${nm}」で ${r.file}${r.hash} に着いた`);
      }
    }
    await ctx.close();
  }

  // 4. 動きを減らす設定でも働くか
  {
    const ctx = await b.newContext({viewport: {width: 390, height: 844}, hasTouch: true, reducedMotion: 'reduce'});
    await ctx.route(u => !u.href.startsWith(BASE), r => r.abort());
    const pg = await ctx.newPage();
    for (const p of ['members/jo-hitaki.html', 'units/triattique.html']) {
      await pg.goto(BASE + p); await pg.click('.uf'); await pg.waitForTimeout(250);
      if (await pg.evaluate(() => getComputedStyle(document.querySelector('.upills')).display) === 'none') bad('動き', p, '動きを減らす設定で Units ボタンが開かない');
    }
    await pg.goto(BASE + 'units/orybia.html'); await pg.click('[data-pop=about]'); await pg.waitForTimeout(250);
    if (!await pg.$eval('#pop-about', d => d.open)) bad('動き', 'units/orybia.html', 'About が開かない');
    await pg.goto(BASE + 'songs.html?u=prismea'); await pg.waitForTimeout(300);
    if (await pg.$$eval('.sgs .rel', a => a.filter(x => !x.hidden).length) === 0) bad('動き', 'songs.html?u=prismea', 'ユニットで絞ると曲が1つも出ない');
    await ctx.close();
  }

  await b.close(); server.close();
  if (problems.length) { console.log(`不合格：${problems.length}件\n` + problems.map(x => '- ' + x).join('\n')); process.exit(1); }
  console.log(`合格：${list.length}ページ・${SIZES.length}通りの幅で問題なし`);
})().catch(e => { console.error('チェックが途中で止まった：', e); process.exit(2); });
