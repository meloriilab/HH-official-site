/* Listen: one press opens the bar at the bottom and starts the song (Spotify's own player API). If that API cannot be loaded, the plain player is shown and the visitor presses play there. */
(function(){var d,ctl,api,wait;
function mark(b){[].forEach.call(document.querySelectorAll('[data-try]'),function(x){var on=x===b;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on?'true':'false')})}
function shut(){if(d){try{ctl&&ctl.destroy()}catch(e){}ctl=null;d.parentNode.removeChild(d);d=null;document.documentElement.classList.remove('has-dock');mark(null)}}
function plain(id){var h=d&&d.querySelector('.dock-p');if(h)h.innerHTML='<iframe title="Spotify" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" src="https://open.spotify.com/embed/track/'+encodeURIComponent(id)+'"></iframe>'}
function start(id){var h=d&&d.querySelector('.dock-p');if(!h)return;
if(ctl){try{ctl.loadUri('spotify:track:'+id);ctl.play();return}catch(e){ctl=null}}
h.innerHTML='<div></div>';
try{api.createController(h.firstChild,{uri:'spotify:track:'+id,width:'100%',height:80},function(c){ctl=c;var go=function(){try{c.play()}catch(e){}};c.addListener('ready',go);go()})}catch(e){plain(id)}}
function load(id){if(api){start(id);return}
window.onSpotifyIframeApiReady=function(a){api=a;clearTimeout(wait);if(d&&d.dataset.id)start(d.dataset.id)};
if(!document.getElementById('sp-api')){var s=document.createElement('script');s.id='sp-api';s.async=true;s.src='https://open.spotify.com/embed/iframe-api/v1';s.onerror=function(){clearTimeout(wait);if(d)plain(d.dataset.id)};document.head.appendChild(s)}
clearTimeout(wait);wait=setTimeout(function(){if(!api&&d)plain(d.dataset.id)},4000)}
document.addEventListener('click',function(e){var b=e.target.closest('[data-try]');if(!b)return;var was=b.classList.contains('on');if(was||!b.dataset.try){shut();return}
if(!d){d=document.createElement('div');d.className='dock';d.setAttribute('role','region');d.setAttribute('aria-label','Spotify');
d.innerHTML='<div class="dock-p"></div><button type="button">閉じる</button>';d.querySelector('button').addEventListener('click',shut);document.body.appendChild(d);document.documentElement.classList.add('has-dock')}
d.dataset.id=b.dataset.try;mark(b);load(b.dataset.try)})})();
/* Mood: five jackets picked at random; a mood word picks again among the songs of that mood (fewer than five = all of them) */
(function(){var w=document.querySelector('.mds');if(!w)return;var cs=[].slice.call(w.children),ps=[].slice.call(document.querySelectorAll('.mood-s .md')),more=document.querySelector('.mood-s .more a'),
mv=!matchMedia('(prefers-reduced-motion: reduce)').matches&&!!w.animate;
function sh(a){for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a}
function draw(m,an){var pk=sh(cs.filter(function(c){return!m||c.dataset.m.split('|').indexOf(m)>=0})).slice(0,5);
cs.forEach(function(c){c.hidden=pk.indexOf(c)<0});for(var i=pk.length-1;i>=0;i--)w.insertBefore(pk[i],w.firstChild);
w.classList.toggle('ev',pk.length%2===0);
ps.forEach(function(p){var on=p.dataset.v===m;p.classList.toggle('on',on);p.setAttribute('aria-pressed',on?'true':'false')});
if(more)more.href='songs.html'+(m?'?m='+encodeURIComponent(m):'');
if(an&&mv)pk.forEach(function(c,i){c.animate([{opacity:0,transform:'translateY(16px)'},{opacity:1,transform:'none'}],{duration:420,delay:i*60,easing:'ease-out',fill:'backwards'})})}
ps.forEach(function(p){p.addEventListener('click',function(){draw(p.dataset.v,true)})});draw('',false)})();
(function(){var b=document.querySelector('.burger'),m=document.getElementById('menu');if(!b||!m)return;
function set(o){m.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false');document.documentElement.style.overflow=o?'hidden':'';document.documentElement.classList.toggle('menu-open',o)}
b.addEventListener('click',function(){set(m.hidden)});m.addEventListener('click',function(e){if(e.target.closest('a'))set(false)});
addEventListener('keydown',function(e){if(e.key==='Escape')set(false)})})();
(function(){if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;
/* colour only in the middle band of the screen */
document.documentElement.classList.add('js');if(/[?&]flag=1/.test(location.search))document.documentElement.classList.add('fl1');
var ho=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');ho.unobserve(e.target)}})},{threshold:.6});
[].forEach.call(document.querySelectorAll('h2'),function(el){ho.observe(el)});
var pg=document.querySelector('.prog');
var pill={};[].forEach.call(document.querySelectorAll('.up-a'),function(a){pill[a.dataset.u]=a});
if(!matchMedia('(hover:hover)').matches)document.addEventListener('click',function(e){var a=e.target.closest('.up-a'),u=a&&a.parentNode,o=document.querySelector('.up.open');if(o&&o!==u)o.classList.remove('open');if(!a||!u.querySelector('.up-m')||u.classList.contains('open'))return;e.preventDefault();u.classList.add('open')});
function mark(){var fs=[].slice.call(document.querySelectorAll('.flag.lit')),cur=document.body.dataset.u||(fs.length?fs[fs.length-1].dataset.u:'');for(var k in pill)pill[k].classList.toggle('on',k===cur)}
var io=new IntersectionObserver(function(es){es.forEach(function(e){e.target.classList.toggle('lit',e.isIntersecting)});mark()},{rootMargin:'-30% 0px -30% 0px'});
[].forEach.call(document.querySelectorAll('.rel,.flag,.mem,.fv,.pu-fr'),function(el){io.observe(el)});
/* layers move at their own speed */
var px=[].slice.call(document.querySelectorAll('[data-speed],[data-speedx]')).map(function(el){return{el:el,s:parseFloat(el.dataset.speed)||0,x:parseFloat(el.dataset.speedx)||0,h:el.closest('.flag,.rel,section')||el.parentNode}}),tk=false;
var pu=document.querySelector('.pu-fr'),us=document.getElementById('units'),fl=document.querySelector('.flags');
function fr(){tk=false;var vh=innerHeight;if(us&&fl)document.documentElement.classList.toggle('in-units',us.getBoundingClientRect().top<vh*.55&&fl.getBoundingClientRect().bottom>vh*.35);if(pu){var q=pu.getBoundingClientRect(),o=1.25-Math.abs(q.top+q.height/2-vh/2)/(vh*.42);o=Math.max(0,Math.min(1,o));pu.style.setProperty('--o',(o*o*(3-2*o)).toFixed(3))}pg.style.setProperty('--p',(scrollY/Math.max(1,document.documentElement.scrollHeight-vh)).toFixed(4));px.forEach(function(p){var r=p.h.getBoundingClientRect();if(r.bottom<-500||r.top>vh+500)return;
 var d=(r.top+r.height/2)-vh/2;p.el.style.translate=(-d*p.x).toFixed(1)+'px '+(-d*p.s).toFixed(1)+'px'})}
addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(fr)}},{passive:true});addEventListener('resize',fr);fr();})();
/* Episode: opens the chat over the page; lines appear one by one (Skip shows all). #episode-<song> opens it directly. */
(function(){var tm=0;
function rows(d){return d.querySelectorAll('.ep-log>*')}
function noty(d){[].forEach.call(d.querySelectorAll('.ep-ty'),function(x){x.remove()})}
function all(d){clearTimeout(tm);noty(d);[].forEach.call(rows(d),function(x){x.classList.add('in')});d.querySelector('.ep-sk').hidden=true}
/* before each line, the speaker's side shows moving dots ("typing") for a moment, then the line takes their place */
function play(d){var r=[].slice.call(rows(d)),i=0,log=d.querySelector('.ep-log');log.scrollTop=0;
 function down(){log.scrollTo({top:log.scrollHeight,behavior:'smooth'})}
 function show(x){noty(d);x.classList.add('in');i++;down();tm=setTimeout(step,Math.min(1700,450+x.textContent.length*45))}
 function step(){if(!d.open)return;if(i>=r.length){d.querySelector('.ep-sk').hidden=true;return}
  var x=r[i];if(!x.classList.contains('ep-r')){show(x);return}
  var t=document.createElement('div');t.className='ep-r ep-ty in'+(x.classList.contains('me')?' me':'');t.setAttribute('aria-hidden','true');
  t.innerHTML='<img class="ep-av" src="'+x.querySelector('.ep-av').getAttribute('src')+'" alt=""><div><p><i></i><i></i><i></i></p></div>';
  log.insertBefore(t,x);down();tm=setTimeout(function(){show(x)},520+Math.min(900,x.textContent.length*28))}
 step()}
function open(s){var d=document.getElementById('ep-'+s);if(!d||!d.showModal||d.open)return;
 noty(d);[].forEach.call(rows(d),function(x){x.classList.remove('in')});d.querySelector('.ep-sk').hidden=false;
 d.showModal();document.documentElement.classList.add('ep-on');history.replaceState(null,'','#episode-'+s);
 if(matchMedia('(prefers-reduced-motion:reduce)').matches)all(d);else tm=setTimeout(function(){play(d)},380)}
document.addEventListener('click',function(e){var b=e.target.closest('[data-ep]');if(b){open(b.dataset.ep);return}
 var d=e.target.closest('dialog.ep');if(!d)return;
 if(e.target===d||e.target.closest('.ep-x'))d.close();else if(e.target.closest('.ep-ph'))e.target.closest('.ep-ph').classList.toggle('big');else if(e.target.closest('.ep-sk')){all(d);d.querySelector('.ep-log').scrollTop=0}});
[].forEach.call(document.querySelectorAll('dialog.ep'),function(d){d.addEventListener('close',function(){clearTimeout(tm);noty(d);document.documentElement.classList.remove('ep-on');
 if(/^#episode-/.test(location.hash))history.replaceState(null,'',location.pathname+location.search)})});
var m=location.hash.match(/^#episode-([a-z-]+)$/);if(m)open(m[1])})();

/* Share: 上の帯の Share。スマホは端末の共有の画面を開く。使えない端末（PCなど）では、すぐ下に X と Copy を出す。送る一言は各ページの <meta name="share"> */
(function(){var b=document.querySelector('.sh');if(!b)return;var pop=null;
function shut(){if(pop){pop.remove();pop=null;b.setAttribute('aria-expanded','false')}}
b.addEventListener('click',function(e){e.stopPropagation();var m=document.querySelector('meta[name="share"]'),t=(m&&m.content)||document.title,u=location.href;
 if(navigator.share&&matchMedia('(pointer:coarse)').matches){navigator.share({title:document.title,text:t,url:u}).catch(function(){});return}
 if(pop){shut();return}
 pop=document.createElement('p');pop.className='sh-p';
 var x=document.createElement('a');x.className='btn';x.textContent='X';x.target='_blank';x.rel='noopener';x.href='https://x.com/intent/post?text='+encodeURIComponent(t)+'&url='+encodeURIComponent(u);
 var c=document.createElement('button');c.type='button';c.className='btn';c.textContent='Copy';
 c.addEventListener('click',function(ev){ev.stopPropagation();var done=function(){c.textContent='Copied';setTimeout(shut,900)};
  if(navigator.clipboard)navigator.clipboard.writeText(u).then(done,function(){prompt('',u)});else prompt('',u)});
 pop.appendChild(x);pop.appendChild(c);document.body.appendChild(pop);
 var r=b.getBoundingClientRect();pop.style.margin='0';pop.style.top=(r.bottom+scrollY+4)+'px';pop.style.left=Math.max(8,Math.min(r.right-216,innerWidth-224))+'px';b.setAttribute('aria-expanded','true')});
addEventListener('click',shut);addEventListener('keydown',function(e){if(e.key==='Escape')shut()});addEventListener('resize',shut)})();

