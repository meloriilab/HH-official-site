(function(){var b=document.querySelector('.burger'),m=document.getElementById('menu');if(!b||!m)return;
function set(o){m.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false');document.documentElement.style.overflow=o?'hidden':'';document.documentElement.classList.toggle('menu-open',o)}
b.addEventListener('click',function(){set(m.hidden)});m.addEventListener('click',function(e){if(e.target.closest('a'))set(false)});
addEventListener('keydown',function(e){if(e.key==='Escape')set(false)})})();
(function(){if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;
/* colour only in the middle band of the screen */
document.documentElement.classList.add('js');
var ho=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');ho.unobserve(e.target)}})},{threshold:.6});
[].forEach.call(document.querySelectorAll('h2'),function(el){ho.observe(el)});
var pg=document.querySelector('.prog');
var pill={};[].forEach.call(document.querySelectorAll('.upills a'),function(a){pill[a.dataset.u]=a});
function mark(){var fs=[].slice.call(document.querySelectorAll('.flag.lit')),cur=fs.length?fs[fs.length-1].dataset.u:'';for(var k in pill)pill[k].classList.toggle('on',k===cur)}
var io=new IntersectionObserver(function(es){es.forEach(function(e){e.target.classList.toggle('lit',e.isIntersecting)});mark()},{rootMargin:'-30% 0px -30% 0px'});
[].forEach.call(document.querySelectorAll('.rel,.flag,.mem,.fv,.pu-fr'),function(el){io.observe(el)});
/* layers move at their own speed */
var px=[].slice.call(document.querySelectorAll('[data-speed],[data-speedx]')).map(function(el){return{el:el,s:parseFloat(el.dataset.speed)||0,x:parseFloat(el.dataset.speedx)||0,h:el.closest('.flag,.rel,section')||el.parentNode}}),tk=false;
function fr(){tk=false;var vh=innerHeight;pg.style.setProperty('--p',(scrollY/Math.max(1,document.documentElement.scrollHeight-vh)).toFixed(4));px.forEach(function(p){var r=p.h.getBoundingClientRect();if(r.bottom<-500||r.top>vh+500)return;
 var d=(r.top+r.height/2)-vh/2;p.el.style.translate=(-d*p.x).toFixed(1)+'px '+(-d*p.s).toFixed(1)+'px'})}
addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(fr)}},{passive:true});addEventListener('resize',fr);fr();})();
