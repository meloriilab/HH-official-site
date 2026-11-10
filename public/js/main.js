/* Humming Hearts 公式サイト トップページ
   中身は data/content.json から読み込みます。ここは「並べ方」と「動き」だけを書いています。 */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var PLAY_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';

  /* ---------- 小さな通知 ---------- */
  var toastTimer;
  function toast(msg) {
    var t = $('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('show'); }, 2400);
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-soon]');
    if (a) { e.preventDefault(); toast('このページは準備中です'); }
  });

  /* ---------- メニュー ---------- */
  var menuBtn = $('menuBtn'), menu = $('menu');
  function setMenu(open) {
    menu.hidden = !open;
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
  }
  menuBtn.addEventListener('click', function () { setMenu(menu.hidden); });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });

  /* ---------- 動画プレーヤー ---------- */
  function youtubeId(url) {
    if (!url) return '';
    var m = url.match(/youtu\.be\/([\w-]{11})/) || url.match(/[?&]v=([\w-]{11})/) || url.match(/\/(?:embed|shorts|live)\/([\w-]{11})/);
    return m ? m[1] : '';
  }
  function toSeconds(t) {
    if (!t) return 0;
    var p = String(t).split(':').map(Number);
    return p.length === 2 ? p[0] * 60 + p[1] : (p[0] || 0);
  }
  var lastFocus;
  function play(url, start) {
    var id = youtubeId(url);
    if (!id) { toast('この曲の動画は準備中です'); return; }
    lastFocus = document.activeElement;
    var src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&playsinline=1&rel=0' + (start ? '&start=' + start : '');
    $('playerFrame').innerHTML = '<iframe src="' + src + '" title="YouTube 動画" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    $('player').hidden = false;
    $('playerClose').focus();
  }
  function closePlayer() {
    $('player').hidden = true;
    $('playerFrame').innerHTML = '';
    if (lastFocus) lastFocus.focus();
  }
  $('playerClose').addEventListener('click', closePlayer);
  $('player').addEventListener('click', function (e) { if (e.target === $('player')) closePlayer(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { if (!$('player').hidden) closePlayer(); if (!menu.hidden) setMenu(false); }
  });

  /* ---------- 画像か「（仮）」の枠か ---------- */
  var glowDefault = ['#4A4772', '#24233D'];
  function setGlow(el, m) {
    var g = (m && m.glow && m.glow.length === 2) ? m.glow : glowDefault;
    el.style.setProperty('--c1', g[0]);
    el.style.setProperty('--c2', g[1]);
  }
  function figure(el, src, alt, label) {
    if (src) {
      el.classList.remove('ph');
      el.innerHTML = '<img src="' + esc(src) + '" alt="' + esc(alt) + '" loading="lazy" decoding="async">';
    } else {
      el.classList.add('ph');
      el.textContent = label;
    }
  }

  /* ---------- 色の計算（ユニット色を背景に混ぜる） ---------- */
  function hex(c) { c = c.replace('#', ''); return [0, 2, 4].map(function (i) { return parseInt(c.substr(i, 2), 16); }); }
  function mix(a, b, r) {
    var x = hex(a), y = hex(b);
    return 'rgb(' + x.map(function (v, i) { return Math.round(v * r + y[i] * (1 - r)); }).join(',') + ')';
  }

  /* ---------- データを読み込んで並べる ---------- */
  fetch('data/content.json', { cache: 'no-cache' })
    .then(function (r) { return r.json(); })
    .then(build)
    .catch(function () { toast('データを読み込めませんでした'); });

  function build(d) {
    if (d.glowDefault) glowDefault = d.glowDefault;
    var unitBy = {}, memberBy = {}, moodBy = {};
    d.units.forEach(function (u) { unitBy[u.no] = u; });
    d.members.forEach(function (m) { memberBy[m.id] = m; });
    d.moods.forEach(function (m) { moodBy[m.id] = m.label; });
    var unitLabel = function (no) { var u = unitBy[no]; return u ? "UNIT " + u.no + " ／ " + u.name : "ユニット名（未確定）"; };

    /* ファーストビュー */
    var fv = d.firstView || {};
    [['fvLeft', fv.left, '立ち絵（仮）'], ['fvCenter', fv.center, 'センターの立ち絵（仮）'], ['fvRight', fv.right, '立ち絵（仮）']].forEach(function (x) {
      var m = memberBy[x[1]];
      figure($(x[0]), m && m.image, m ? m.name : '', x[2]);
      if (m && m.image) setGlow($(x[0]), m);
    });
    var latest = d.songs.filter(function (s) { return s.id === d.latestSong; })[0] || d.songs[0];
    if (latest) {
      $('relTitle').textContent = latest.title;
      $('relUnit').textContent = unitLabel(latest.unit);
      $('relPlay').addEventListener('click', function () { play(latest.youtube, 0); });
      $('relUnitLink').addEventListener('click', function () { focusUnit(latest.unit); });
    }

    /* 楽曲 */
    var current = 'all';
    function renderSongs() {
      var list = d.songs.filter(function (s) { return current === 'all' || s.mood === current; });
      $('songs').innerHTML = list.length ? list.map(function (s, i) {
        var u = unitBy[s.unit];
        var jacket = s.jacket ? 'background-image:url(' + esc(s.jacket) + ');' : '';
        return '<div class="song reveal" style="transition-delay:' + (i * 0.08) + 's">' +
          '<div class="jacket" style="background-color:' + esc(s.color || (u && u.color) || '#ECE8F6') + ';' + jacket + '"></div>' +
          '<div class="song-info"><span class="song-title">' + esc(s.title) + '</span>' +
          '<span class="song-sub">' + esc(u ? u.name : '未確定') + ' ・ ' + esc(moodBy[s.mood] || '未確定') + '</span>' +
          '<span class="song-sub">' + (s.chorus ? 'サビ ' + esc(s.chorus) + '〜' : 'サビ 未確定') + '</span></div>' +
          '<button class="play-sm" data-song="' + esc(s.id) + '" aria-label="' + esc(s.title) + 'を試聴する">' + PLAY_ICON + '</button></div>';
      }).join('') : '<p class="empty">この雰囲気の曲は、まだありません。</p>';
      observeReveal($('songs'));
    }
    if (d.showMoodFilter !== false) {
      var moods = [{ id: 'all', label: 'すべて' }].concat(d.moods);
      $('moods').innerHTML = moods.map(function (m) {
        return '<button class="mood" data-mood="' + esc(m.id) + '" aria-pressed="' + (m.id === current) + '">' + esc(m.label) + '</button>';
      }).join('');
      $('moods').addEventListener('click', function (e) {
        var b = e.target.closest('.mood'); if (!b) return;
        current = b.dataset.mood;
        [].forEach.call($('moods').children, function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        renderSongs();
      });
    } else {
      $('moods').hidden = true;
    }
    $('songs').addEventListener('click', function (e) {
      var b = e.target.closest('[data-song]'); if (!b) return;
      var s = d.songs.filter(function (x) { return x.id === b.dataset.song; })[0];
      if (s) play(s.youtube, toSeconds(s.chorus));
    });
    renderSongs();

    /* ユニット */
    $('unitsCount').textContent = d.units.length + (d.units.length === 1 ? ' unit' : ' units');
    $('unitScroller').innerHTML = d.units.map(function (u) {
      var names = u.members.map(function (id) { return memberBy[id] ? memberBy[id].name : ''; }).filter(Boolean);
      return '<div class="unit-card" data-unit="' + esc(u.no) + '">' +
        '<div class="unit-top" style="background:' + esc(u.color) + ';color:' + esc(u.text) + '">' +
        '<span class="unit-no">' + esc(u.no) + '</span><span class="unit-label">UNIT</span></div>' +
        '<div class="unit-body"><span class="unit-name">' + esc(u.name) + '</span>' +
        '<span class="unit-concept">' + esc(u.concept) + '</span>' +
        '<span class="unit-members">メンバー：' + esc(names.length ? names.join('・') : '未確定') + '</span>' +
        '<a href="#" data-soon>詳しく見る →</a></div></div>';
    }).join('');
    var scroller = $('unitScroller'), unitsSec = $('units'), activeUnit = '';
    function updateUnitColor() {
      var cards = scroller.children, best = null, bestDist = 1e9, left = scroller.getBoundingClientRect().left + 20;
      for (var i = 0; i < cards.length; i++) {
        var dist = Math.abs(cards[i].getBoundingClientRect().left - left);
        if (dist < bestDist) { bestDist = dist; best = cards[i]; }
      }
      if (!best || best.dataset.unit === activeUnit) return;
      activeUnit = best.dataset.unit;
      unitsSec.style.backgroundColor = mix(unitBy[activeUnit].color, '#ECE8F6', 0.22);
    }
    var unitTick = false;
    scroller.addEventListener('scroll', function () {
      if (unitTick) return; unitTick = true;
      requestAnimationFrame(function () { unitTick = false; updateUnitColor(); });
    }, { passive: true });
    updateUnitColor();
    function focusUnit(no) {
      var card = scroller.querySelector('[data-unit="' + no + '"]');
      if (card) scroller.scrollTo({ left: card.offsetLeft - 20, behavior: reduceMotion.matches ? 'auto' : 'smooth' });
    }

    /* 今日のさえずり（日付で入れ替わる） */
    var chirps = d.chirps || [];
    var day = Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);
    var ci = chirps.length ? day % chirps.length : 0;
    function renderChirp() {
      var c = chirps[ci]; if (!c) return;
      var m = memberBy[c.member], u = m && unitBy[m.unit];
      $('chirpText').textContent = c.text;
      $('chirpWho').textContent = (m ? m.name : 'メンバー名（未確定）') + '・UNIT ' + (u ? u.no : '未確定');
      $('chirpCount').textContent = (ci + 1) + ' / ' + chirps.length;
      var face = $('chirpFace');
      if (u) face.style.borderColor = u.color;
      if (m && (m.face || m.image)) face.innerHTML = '<img src="' + esc(m.face || m.image) + '" alt="">';
      else face.textContent = '顔（仮）';
    }
    renderChirp();
    $('chirpNext').addEventListener('click', function () { ci = (ci + 1) % chirps.length; renderChirp(); });
    $('chirpShare').addEventListener('click', function () {
      var c = chirps[ci]; if (!c) return;
      var m = memberBy[c.member];
      var text = '【今日のさえずり】' + (m ? m.name + '「' : '「') + c.text + '」 #HummingHearts';
      var url = location.href.split('#')[0];
      if (navigator.share) { navigator.share({ text: text, url: url }).catch(function () {}); }
      else { window.open('https://x.com/intent/post?text=' + encodeURIComponent(text) + '&url=' + encodeURIComponent(url), '_blank', 'noopener'); }
    });

    /* 注目のメンバー */
    var p = memberBy[d.pickupMember] || d.members[0];
    if (p) {
      var pu = unitBy[p.unit];
      figure($('pickupImg'), p.image, p.name, '立ち絵・大（仮）');
      if (p.image) setGlow($('pickupImg'), p);
      $('pickupName').textContent = p.name;
      $('pickupUnit').textContent = 'UNIT ' + (pu ? pu.no : '未確定');
      if (pu) {
        $('pickupUnit').style.background = pu.color; $('pickupUnit').style.color = pu.text;
        $('pickupCircle').style.background = pu.color;
      }
      var bd = p.birthday ? p.birthday.replace(/^(\d+)-(\d+)$/, function (_, a, b) { return Number(a) + '月' + Number(b) + '日'; }) : '未確定';
      $('pickupFacts').innerHTML = [['モチーフ', p.motif], ['パート', p.part], ['声のタイプ', p.voice], ['誕生日', bd]].map(function (f) {
        return '<div class="fact"><span class="fact-k">' + f[0] + '</span><span class="fact-v">' + esc(f[1] || '未確定') + '</span></div>';
      }).join('');
      $('pickupOshi').innerHTML = (p.oshi || []).slice(0, 3).map(function (o, i) {
        return '<div class="oshi-row"><span class="oshi-no">' + (i + 1) + '</span><span>' + esc(o) + '</span></div>';
      }).join('');
      $('pickupBird').innerHTML = (p.birdNote || []).map(esc).join('<br>');
    }

    /* 最新情報（X） */
    var L = d.links || {};
    $('xAccount').textContent = L.xAccount || '@アカウント名（未確定）';
    if (L.x) $('xFollow').href = L.x; else $('xFollow').setAttribute('data-soon', '');
    if (L.xPinnedPost) {
      var box = $('xEmbed');
      box.innerHTML = '<a href="' + esc(L.xPinnedPost) + '" target="_blank" rel="noopener">Xで固定ポストを見る</a>';
      var bq = document.createElement('blockquote');
      bq.className = 'twitter-tweet'; bq.setAttribute('data-dnt', 'true'); bq.setAttribute('data-lang', 'ja');
      bq.innerHTML = '<a href="' + esc(L.xPinnedPost.replace('x.com', 'twitter.com')) + '"></a>';
      var holder = document.createElement('div'); holder.style.width = '100%';
      holder.appendChild(bq); box.appendChild(holder);
      var s = document.createElement('script');
      s.src = 'https://platform.twitter.com/widgets.js'; s.async = true;
      s.onload = function () {
        if (window.twttr && twttr.events) twttr.events.bind('rendered', function () {
          box.classList.add('loaded'); var a = box.querySelector(':scope > a'); if (a) a.remove();
        });
      };
      document.body.appendChild(s);
    }

    /* 今月のバースデー（いない月は欄ごと出さない） */
    var month = new Date().getMonth() + 1;
    var bdays = d.members.filter(function (m) { return m.birthday && Number(m.birthday.split('-')[0]) === month; })
      .sort(function (a, b) { return Number(a.birthday.split('-')[1]) - Number(b.birthday.split('-')[1]); });
    if (bdays.length) {
      $('bdayList').innerHTML = bdays.map(function (m) {
        var u = unitBy[m.unit], pt = m.birthday.split('-');
        return '<div class="bday"><div class="bday-face" style="border-color:' + esc(u ? u.color : '#ECE8F6') + '">' +
          (m.face || m.image ? '<img src="' + esc(m.face || m.image) + '" alt="">' : '') + '</div>' +
          '<div class="bday-text"><span class="bday-date">' + pt[0].padStart(2, '0') + '/' + pt[1].padStart(2, '0') + '</span>' +
          '<span class="bday-name">' + esc(m.name) + '</span></div></div>';
      }).join('');
      $('birthday').hidden = false;
    }

    /* フッター */
    $('sns').innerHTML = [['YouTube', L.youtube], ['TikTok', L.tiktok], ['Instagram', L.instagram], ['X', L.x]].map(function (s) {
      return s[1] ? '<a href="' + esc(s[1]) + '" target="_blank" rel="noopener">' + s[0] + '</a>'
                  : '<a href="#" class="off" data-soon>' + s[0] + '</a>';
    }).join('');

    observeReveal(document);
  }

  /* ---------- 画面に入ったら下からふわっと出る ---------- */
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -10% 0px' }) : null;
  function observeReveal(root) {
    [].forEach.call(root.querySelectorAll('.reveal:not(.in)'), function (el) {
      if (!io || reduceMotion.matches) el.classList.add('in'); else io.observe(el);
    });
  }

  /* ---------- 奥行き（視差） ---------- */
  var layers = [].slice.call(document.querySelectorAll('.fv [data-speed]'));
  var pickupImg = $('pickupImg');
  var ticking = false;
  function parallax() {
    ticking = false;
    if (reduceMotion.matches) {
      layers.forEach(function (l) { l.style.transform = ''; });
      pickupImg.style.transform = '';
      return;
    }
    var y = window.scrollY;
    if (y < 900) layers.forEach(function (l) { l.style.transform = 'translate3d(0,' + (y * Number(l.dataset.speed)) + 'px,0)'; });
    var r = pickupImg.getBoundingClientRect(), vh = window.innerHeight;
    if (r.bottom > 0 && r.top < vh) {
      var off = (r.top + r.height / 2 - vh / 2) * Number(pickupImg.dataset.lag);
      pickupImg.style.transform = 'translate3d(0,' + off.toFixed(1) + 'px,0)';
    }
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(parallax); } }, { passive: true });
  if (reduceMotion.addEventListener) reduceMotion.addEventListener('change', parallax);
  parallax();

  /* ---------- 固定ナビ：いま見ている場所に印をつける ---------- */
  var navLinks = [].slice.call(document.querySelectorAll('.bottom-nav a'));
  var spots = ['fv', 'music', 'units', 'latest'].map(function (id) { return $(id); });
  if (io) {
    var navIo = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var i = spots.indexOf(e.target);
        navLinks.forEach(function (a, j) { a.classList.toggle('on', j === i); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    spots.forEach(function (s) { navIo.observe(s); });
  }
})();
