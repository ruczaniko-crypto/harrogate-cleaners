#!/usr/bin/env python3
"""Builds the Harrogate Cleaners static site.

Change DOMAIN and HOURS below, then run:  python3 build.py
Outputs:
  out/deploy/   full site ready to upload to any web host
  out/artifact/ same site, with index.html in the preview format
"""
import json, os, shutil, html

DOMAIN = "https://harrogatecleaner.co.uk"
NAME = "Harrogate Cleaners"
PHONE = "01423 508568"
PHONE_INTL = "+441423508568"
STREET = "34 Cold Bath Road"
TOWN = "Harrogate"
POSTCODE = "HG2 0NA"
WHATSAPP = "https://wa.me/441423508568?text=Hello%20Harrogate%20Cleaners%2C%20"
# Paste the review link from Google Business Profile ("Ask for reviews" > copy link) here.
# Until then the buttons open the Google Maps search for the shop.
GOOGLE_REVIEW = "https://share.google/WVhCBlfNNvHvr8HG9"
MAPS = "https://www.google.com/maps/search/?api=1&query=Harrogate+Cleaners+34+Cold+Bath+Road+Harrogate+HG2+0NA"
TODAY = "2026-10-23"
MAP_EMBED = "https://www.google.com/maps?q=Harrogate+Cleaners,+34+Cold+Bath+Road,+Harrogate+HG2+0NA&z=16&output=embed"
PREVIEW = False   # set automatically for the Claude preview, where embedded maps can't load

# Paste the Zoho Desk chat widget code here (Zoho Desk > Setup > Channels > ASAP > Web > install code).
# It is added just before </body> on every page.
CHAT_SNIPPET = ""

# Fill these in. Format for schema: ("Monday", "08:30", "17:30"); use None to mark closed.
HOURS = [
    ("Monday", "09:00", "17:30"),
    ("Tuesday", "09:00", "17:30"),
    ("Wednesday", "09:00", "17:30"),
    ("Thursday", "09:00", "17:30"),
    ("Friday", "09:00", "17:30"),
    ("Saturday", "09:00", "17:00"),
    ("Sunday", None, None),
]
HOURS_SHORT = "Mon–Fri 9am–5:30pm, Sat 9am–5pm"
TURNAROUND = "2 days"
EXPRESS = "We also offer a 24-hour express service. How quickly we can turn an item around depends on the garment and its fabric, so just ask and we will do our best."


IMAGES = {
    "suit": ("images/blue-suit-tailoring.jpg", "Navy suit jacket and red tie, freshly pressed"),
    "shirts": ("images/shirts-on-rail.jpg", "Pressed shirts hanging on a rail"),
    "lace": ("images/lace-wedding-dress.jpg", "Detail of a beaded lace wedding dress and veil"),
    "inspect": ("images/wedding-dress-inspection.jpg", "A wedding dress being checked on its hanger"),
    "weddingcare": ("images/wedding-dress-care.jpg", "Seamstress holding a lace wedding dress on a hanger"),
    "linen": ("images/folded-bed-linen.jpg", "Freshly laundered bed linen, folded and rolled"),
    "laundry": ("images/laundry-basket-machines.jpg", "Basket of laundry in front of commercial washing machines"),
    "alterations": ("images/alterations-tools.jpg", "Tape measure, thread, thimbles and tailor's scissors on fabric"),
    "shopfront": ("images/harrogate-dry-cleaners-shopfront-cold-bath-road.jpg", "The blue shopfront of Harrogate Cleaners at 34 Cold Bath Road, established 1986"),
    "interior": ("images/harrogate-dry-cleaners-shop-interior.jpg", "Inside the shop: the counter and freshly cleaned garments on the rail, each with its ticket"),
    "shopside": ("images/harrogate-cleaners-shop-cold-bath-road.jpg", "Harrogate Cleaners on Cold Bath Road, with the Est. 1986 window sign"),
    "plaque": ("images/cold-bath-plaque-harrogate.jpg", "Harrogate Civic Society plaque for the Cold Bath spring"),
}
def img(key, cls="", eager=False):
    src, alt = IMAGES[key]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{src}" alt="{alt}" class="{cls}" {load} decoding="async">'

SCRIPT = r"""
(function(){
  // Always open a new page at the top (unless a link points to a section)
  try { if ('scrollRestoration' in history) history.scrollRestoration = 'manual'; } catch(e){}
  function toTop(){ if (!location.hash) { document.documentElement.style.scrollBehavior = 'auto'; window.scrollTo(0, 0); document.documentElement.style.scrollBehavior = ''; } }
  toTop(); addEventListener('load', toTop); addEventListener('pageshow', toTop);

  // Live open/closed status (UK time). Edit the hours here too if they change.
  var H = {1:[9,17.5],2:[9,17.5],3:[9,17.5],4:[9,17.5],5:[9,17.5],6:[9,17]};
  var names = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  function fmt(h){ var hr = Math.floor(h), m = Math.round((h - hr) * 60); return (hr % 12 || 12) + (m ? ':' + (m < 10 ? '0' : '') + m : '') + (hr < 12 ? 'am' : 'pm'); }
  function update(){
    var el = document.querySelector('[data-status]'); if(!el) return;
    var parts = new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',weekday:'short',hour:'numeric',minute:'numeric',hour12:false}).formatToParts(new Date());
    var get = function(t){ var p = parts.find(function(x){return x.type===t}); return p ? p.value : ''; };
    var day = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].indexOf(get('weekday'));
    var now = parseInt(get('hour'),10) + parseInt(get('minute'),10)/60;
    var t = H[day], txt;
    if (t && now >= t[0] && now < t[1]) { el.className='status open'; txt = 'Open now · closes ' + fmt(t[1]); }
    else {
      el.className='status closed';
      if (t && now < t[0]) txt = 'Closed · opens today at ' + fmt(t[0]);
      else { var d = day; for (var i=1;i<=7;i++){ d=(day+i)%7; if(H[d]) break; } txt = 'Closed · opens ' + (i===1?'tomorrow':names[d]) + ' at ' + fmt(H[d][0]); }
    }
    el.querySelector('[data-status-text]').textContent = txt;
  }
  update(); setInterval(update, 60000);

  // Gentle reveal on scroll (content is visible without it)
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.remove('pending'); io.unobserve(e.target);} }); }, {rootMargin:'0px 0px -60px 0px'});
    document.querySelectorAll('main section:not(.hero) .card, main section:not(.hero) .post-card, .feature .copy, .feature .pic').forEach(function(el){
      var r = el.getBoundingClientRect(); if (r.top > innerHeight) { el.classList.add('reveal','pending'); io.observe(el); }
    });
  }

  // Mobile menu
  var mb = document.querySelector('.menu-btn'), nav = document.getElementById('mainnav');
  if (mb && nav) mb.addEventListener('click', function(){ var o = nav.classList.toggle('open'); mb.setAttribute('aria-expanded', o ? 'true' : 'false'); });

  // Back to top
  var tt = document.querySelector('.totop');
  if (tt) { addEventListener('scroll', function(){ tt.hidden = scrollY < 900; }, {passive:true}); tt.addEventListener('click', function(){ scrollTo({top:0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'}); }); }

  // Stain first aid
  var chips = document.querySelectorAll('.chip[data-stain]');
  chips.forEach(function(c){ c.addEventListener('click', function(){
    chips.forEach(function(x){ x.setAttribute('aria-pressed', x===c ? 'true' : 'false'); });
    document.querySelectorAll('.tip[data-tip]').forEach(function(t){ t.hidden = t.getAttribute('data-tip') !== c.getAttribute('data-stain'); });
  }); });

  // Price list search
  var q = document.getElementById('price-q');
  if (q) {
    var rows = Array.prototype.slice.call(document.querySelectorAll('.price-group tr'));
    rows.forEach(function(r){ r.dataset.label = r.cells[0].textContent; });
    q.addEventListener('input', function(){
      var v = q.value.trim().toLowerCase(), shown = 0;
      rows.forEach(function(r){
        var label = r.dataset.label, i = label.toLowerCase().indexOf(v), hit = !v || i > -1;
        r.hidden = !hit; if (hit) shown++;
        r.cells[0].innerHTML = '';
        if (v && i > -1) { r.cells[0].append(label.slice(0,i)); var m=document.createElement('mark'); m.textContent=label.slice(i,i+v.length); r.cells[0].append(m, label.slice(i+v.length)); }
        else r.cells[0].textContent = label;
      });
      document.querySelectorAll('.price-group').forEach(function(g){ g.hidden = !!v && !g.querySelector('tr:not([hidden])'); });
      document.getElementById('no-match').hidden = shown > 0;
    });
  }

  // Copy address
  document.querySelectorAll('[data-copy]').forEach(function(b){ b.addEventListener('click', function(){
    var text = b.getAttribute('data-copy'), done = function(){ var o=b.textContent; b.textContent='Copied'; setTimeout(function(){ b.textContent=o; }, 1800); };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function(){});
  }); });
})();
"""

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")

CSS = r"""
/* Refined "Spa Water": calm mineral green, big readable type, phone and hours always in view. Single light theme by choice. */
:root{
  --ground:#F2F6F3; --paper:#FFFFFF; --spa:#0F3D35; --spa-deep:#0A2B25; --mist:#D9E8E1;
  --ink:#14302B; --ink-soft:#2E4A44; --line:#B7CEC6; --brass:#E7C38A;
  --copper:#B4472A; --copper-deep:#93391F; --copper-soft:#F6E1D8;
  --display:'DM Serif Display', Georgia, 'Times New Roman', serif;
  --body:'Work Sans', 'Segoe UI', Arial, sans-serif;
  color-scheme: light;
}
*{box-sizing:border-box}
html{font-size:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);font-size:1.1875rem;line-height:1.65}
img{max-width:100%;height:auto}
a{color:var(--spa);text-underline-offset:3px}
a:hover{color:var(--spa-deep)}
:focus-visible{outline:3px solid var(--brass);outline-offset:3px;border-radius:4px}
h1,h2,h3{font-family:var(--display);font-weight:400;color:var(--spa);line-height:1.1;text-wrap:balance;margin:0}
h1{font-size:clamp(2.6rem,6vw,4.6rem)}
h2{font-size:clamp(2rem,4vw,3.1rem)}
h3{font-size:1.6rem}
p{margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(20px, env(safe-area-inset-left, 0px));padding-right:max(20px, env(safe-area-inset-right, 0px))}
.prose{max-width:68ch}
.stack{display:flex;flex-direction:column;gap:20px}
.skip{position:absolute;left:-999px;top:0;background:var(--paper);padding:12px 16px;z-index:50}
.skip:focus{left:16px}
.eyebrow{font-size:.95rem;letter-spacing:.14em;text-transform:uppercase;font-weight:600;color:#3A6359}

/* Top bar */
.topbar{background:var(--spa-deep);color:#E6F0EC;font-size:1.05rem}
.topbar .wrap{display:flex;flex-wrap:wrap;gap:8px 28px;justify-content:space-between;padding-block:10px}
.topbar a{color:#FFFFFF;font-weight:600;text-decoration:none}
.topbar a:hover{text-decoration:underline}

/* Header */
header.site{background:var(--spa);color:#FFFFFF}
header.site .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:18px 32px;padding-block:20px}
.brand{text-decoration:none;color:#FFFFFF;display:flex;flex-direction:column;gap:2px}
.brand b{font-family:var(--display);font-weight:400;font-size:1.9rem;line-height:1}
.brand span{font-size:.85rem;letter-spacing:.16em;text-transform:uppercase;color:#B8DACD}
nav.main ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px 26px}
nav.main a{color:#FFFFFF;text-decoration:none;font-size:1.1rem;font-weight:500;padding:6px 0;display:inline-block;border-bottom:2px solid transparent}
nav.main a:hover,nav.main a[aria-current="page"]{border-bottom-color:var(--brass);color:#FFFFFF}

/* Buttons */
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:54px;padding:0 28px;border-radius:999px;font-weight:600;font-size:1.1rem;text-decoration:none;border:2px solid var(--spa)}
.btn.solid{background:var(--copper);border-color:var(--copper);color:#FFFFFF;box-shadow:0 6px 18px rgba(180,71,42,.25)}
.btn.solid:hover{background:var(--copper-deep);border-color:var(--copper-deep);color:#FFFFFF}
.btn.line{background:transparent;color:var(--spa)}
.btn.line:hover{background:var(--mist)}
.btn.brass{background:var(--brass);border-color:var(--brass);color:var(--spa-deep)}
.btns{display:flex;flex-wrap:wrap;gap:14px}

/* Sections */
section{padding-block:80px}
.band{background:var(--paper)}
.band-dark{background:var(--spa);color:#E6F0EC}
.band-dark h2,.band-dark h3{color:#FFFFFF}
.band-dark a{color:#FFFFFF}
.section-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:16px 40px;margin-bottom:40px}
.section-head p{max-width:46ch;color:var(--ink-soft)}

/* Hero */
.hero{padding-block:72px 64px}
.hero .wrap{display:flex;flex-wrap:wrap;gap:48px;align-items:center}
.hero-copy{flex:1 1 520px;min-width:0;display:flex;flex-direction:column;gap:26px}
.hero-copy .lead{font-size:1.3rem;color:var(--ink-soft);max-width:34ch}
.hero-art{flex:1 1 360px;display:flex;justify-content:center}
.arch{position:relative;width:100%;max-width:400px;aspect-ratio:4/5;background:var(--spa);border-radius:200px 200px 14px 14px;overflow:hidden;display:flex;align-items:flex-end;padding:34px}
.arch svg{position:absolute;inset:18% 0 auto 0;width:100%;opacity:.5}
.arch p{position:relative;color:#E6F0EC;font-family:var(--display);font-size:1.5rem;line-height:1.2}
.ticket{position:absolute;left:-10px;bottom:-22px;background:var(--paper);border-radius:12px;padding:16px 22px;box-shadow:0 18px 40px rgba(15,61,53,.2);display:flex;flex-direction:column;gap:2px}
.hero-art .holder{position:relative;width:100%;max-width:400px}
.ticket small{font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:#3A6359}
.ticket strong{font-family:var(--display);font-weight:400;font-size:1.5rem;color:var(--spa)}

/* Photo hero */
.hero-bg{position:relative;overflow:hidden;background:var(--spa-deep);padding-block:0}
.hero-bg .hero-photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center top;animation:fadeIn 1s ease both}
.hero-bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg, rgba(15,61,53,.55) 0%, rgba(15,61,53,.6) 30%, rgba(10,43,37,.86) 50%, rgba(10,43,37,.97) 100%)}
.hero-inner{position:relative;z-index:1;display:flex;flex-wrap:wrap;gap:32px;align-items:flex-end;justify-content:space-between;padding-block:300px 64px;min-height:800px}
.hero-panel{flex:0 1 620px;min-width:0;display:flex;flex-direction:column;gap:24px;color:#FFFFFF}
.hero-panel .eyebrow{color:var(--brass)}
.hero-panel h1{color:#FFFFFF;font-size:clamp(2.8rem,6.5vw,5rem)}
.hero-panel .lead{font-size:1.35rem;color:#E1EEE9;max-width:32ch}
.btn.light{background:transparent;color:#FFFFFF;border-color:#FFFFFF}
.btn.light:hover{background:rgba(255,255,255,.12);color:#FFFFFF}
.hours-chip{background:var(--paper);color:var(--ink);border-radius:16px;padding:20px 24px;display:flex;flex-direction:column;gap:2px;box-shadow:0 20px 44px rgba(0,0,0,.28);border-top:5px solid var(--copper)}
.hours-chip small{font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:#3A6359;font-weight:600}
.hours-chip strong{font-family:var(--display);font-weight:400;font-size:1.45rem;color:var(--spa)}
.hours-chip span{color:var(--ink-soft)}
.hero-panel > *{animation:rise .8s ease both}
.hero-panel > *:nth-child(2){animation-delay:.1s}.hero-panel > *:nth-child(3){animation-delay:.2s}.hero-panel > *:nth-child(4){animation-delay:.3s}
.hours-chip{animation:rise .8s .45s ease both}
@keyframes fadeIn{from{opacity:.4}to{opacity:1}}
@keyframes rise{from{transform:translateY(16px)}to{transform:none}}
@media (max-width: 720px){.hero-bg .hero-photo{position:relative;inset:auto;height:auto;aspect-ratio:4/3;display:block}.hero-bg::after{inset:0 0 auto 0;aspect-ratio:4/3;height:auto;background:linear-gradient(180deg, rgba(15,61,53,.5) 0%, rgba(15,61,53,.58) 60%, rgba(10,43,37,1) 100%)}.hero-inner{min-height:0;padding-block:28px 40px}.hero-panel .lead{font-size:1.15rem}.hours-chip{width:100%}}
@media (prefers-reduced-motion: reduce){.hero-bg .hero-photo{animation:none}.hero-panel > *,.hours-chip{animation:none}}

/* Reviews */
.review-band{background:var(--copper-soft)}
.review-inner{display:flex;flex-wrap:wrap;align-items:center;gap:24px 40px;padding-block:56px}
.review-copy{flex:1 1 420px;min-width:0;display:flex;flex-direction:column;gap:10px}
.review-copy p{color:var(--ink-soft);max-width:56ch}
.stars{display:inline-flex;gap:4px;flex:0 0 auto}
.stars svg{width:34px;height:34px;fill:var(--copper)}

/* Strap line */
.strap{background:var(--paper);border-bottom:1px solid var(--mist)}
.strap p{padding-block:22px;text-align:center;font-family:var(--display);font-size:clamp(1.3rem,2.6vw,1.8rem);color:var(--spa)}
.strap strong{font-weight:400}

/* Service icons */
.svc-head{display:flex;align-items:center;gap:14px}
.svc-icon{flex:0 0 auto;width:52px;height:52px;border-radius:14px;background:var(--copper-soft);color:var(--copper);display:inline-flex;align-items:center;justify-content:center;transition:background-color .2s ease,color .2s ease}
.svc-icon svg{width:28px;height:28px}
a.card:hover .svc-icon{background:var(--copper);color:#FFFFFF}

/* Answer box */
.answer{background:var(--paper);border:2px solid var(--mist);border-radius:18px;padding:28px 32px;display:flex;flex-wrap:wrap;gap:12px 40px;align-items:baseline}
.answer .eyebrow{flex:0 0 auto}
.answer p{flex:1 1 520px;min-width:0;font-size:1.25rem}

/* Cards */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:22px}
.card{background:var(--ground);border-radius:16px;padding:28px;display:flex;flex-direction:column;gap:12px;text-decoration:none;color:var(--ink)}
.band .card{background:var(--ground)}
a.card:hover{background:var(--mist);color:var(--ink)}
.card h3{font-size:1.65rem}
.card p{color:var(--ink-soft);flex-grow:1}
.card .more{font-weight:600;color:var(--spa)}

/* Feature */
.feature .wrap{display:flex;flex-wrap:wrap;gap:56px;align-items:center}
.feature .pic{flex:1 1 380px;aspect-ratio:1/1;max-width:100%;border-radius:14px 14px 200px 200px;background:var(--mist);display:flex;align-items:center;justify-content:center;text-align:center;padding:32px;font-family:var(--display);font-size:1.5rem;color:var(--spa)}
.feature .copy{flex:1 1 460px;min-width:0;display:flex;flex-direction:column;gap:20px}

/* Posts */
.post-card{display:flex;flex-direction:column;gap:12px;text-decoration:none;color:#E6F0EC}
.post-card .thumb{aspect-ratio:16/10;max-width:100%;border-radius:14px;background:#1C5248;display:flex;align-items:flex-end;padding:16px;font-size:.85rem;letter-spacing:.14em;text-transform:uppercase;color:#D6EBE3}
.post-card h3{font-size:1.55rem}
.post-card p{color:#CFE3DB}
.post-card:hover h3{text-decoration:underline}
.band .post-card,.plain .post-card{color:var(--ink)}
.band .post-card .thumb,.plain .post-card .thumb{background:var(--mist);color:var(--spa)}
.band .post-card p,.plain .post-card p{color:var(--ink-soft)}

/* FAQ */
.faq{max-width:860px}
.faq details{border-top:1px solid var(--line);padding-block:18px}
.faq details:last-child{border-bottom:1px solid var(--line)}
.faq summary{cursor:pointer;font-weight:600;font-size:1.25rem;color:var(--spa);list-style:none;display:flex;justify-content:space-between;gap:16px;min-height:44px;align-items:center}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-size:1.6rem;line-height:1}
.faq details[open] summary::after{content:"−"}
.faq details p{margin-top:10px;color:var(--ink-soft);max-width:68ch}

/* Prices */
.price-groups{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:28px}
.price-group{background:var(--paper);border-radius:16px;padding:28px}
.price-group h2{font-size:1.8rem;margin-bottom:12px}
.price-group table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
.price-group td{padding:12px 0;border-bottom:1px solid var(--mist);vertical-align:top}
.price-group td:last-child{text-align:right;font-weight:600;white-space:nowrap;padding-left:16px}

/* Article */
.article-head{padding-block:64px 32px}
.article-head .stack{max-width:780px}
.meta{color:#3A6359;font-size:1rem}
article.body{padding-block:16px 80px}
article.body .prose{display:flex;flex-direction:column;gap:22px}
article.body h2{font-size:2rem;margin-top:18px}
article.body ul,article.body ol{margin:0;padding-left:1.3em;display:flex;flex-direction:column;gap:8px}
.callout{background:var(--paper);border-radius:16px;padding:24px 28px;display:flex;flex-direction:column;gap:12px}
.breadcrumb{font-size:1rem;color:#3A6359}
.breadcrumb a{color:#3A6359}

/* Hours */
.hours{border-collapse:collapse;font-variant-numeric:tabular-nums;width:100%;max-width:420px}
.hours td{padding:8px 0;border-bottom:1px solid var(--line)}
.hours td:last-child{text-align:right}
.band-dark .hours td{border-color:#2D5E54}

/* Footer */
footer.site{background:var(--spa-deep);color:#DCEAE5}
footer.site .wrap{padding-block:64px 40px;display:flex;flex-direction:column;gap:40px}
.map{position:relative;width:100%;height:340px;border-radius:18px;overflow:hidden;background:#164036;display:flex;align-items:center;justify-content:center;text-align:center;padding:24px}
.map iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.map .map-fallback{display:flex;flex-direction:column;gap:12px;align-items:center;color:#DCEAE5}
.foot-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:36px}
footer.site h2{font-size:1.5rem;color:#FFFFFF;margin-bottom:12px}
footer.site a{color:#FFFFFF}
footer.site ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.legal{font-size:.95rem;color:#A9C7BD;border-top:1px solid #23493F;padding-top:20px}

/* Photos */
.arch.photo{padding:0}
.arch.photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.pic.photo{padding:0;overflow:hidden}
.pic.photo img{width:100%;height:100%;object-fit:cover;display:block}
.pic.plaque{aspect-ratio:3/4;border-radius:14px}
.card-img{width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:12px;display:block}
.post-card .thumb.photo{padding:0;overflow:hidden;position:relative}
.post-card .thumb.photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.post-card .thumb.photo span{position:relative;margin:14px;background:var(--paper);color:var(--spa);padding:5px 12px;border-radius:999px;font-weight:600;letter-spacing:.08em}
.article-img{width:100%;max-width:1000px;aspect-ratio:16/9;object-fit:cover;border-radius:16px;display:block}
figcaption{font-size:.95rem;color:#3A6359;margin-top:8px}

/* Interactions */
.btn{transition:transform .15s ease, background-color .15s ease, box-shadow .15s ease}
.btn:hover{transform:translateY(-2px)}
a.card,.post-card{transition:transform .2s ease, box-shadow .2s ease, background-color .2s ease}
a.card:hover{transform:translateY(-4px);box-shadow:0 14px 30px rgba(15,61,53,.12)}
.card-img,.post-card .thumb.photo img,.arch.photo img{transition:transform .6s ease}
.card:hover .card-img,.post-card:hover .thumb.photo img{transform:scale(1.04)}
.post-card:hover{transform:translateY(-4px)}
.header-call{display:inline-flex;align-items:center;min-height:48px;padding:0 22px;border-radius:999px;background:var(--copper);color:#FFFFFF;font-weight:600;text-decoration:none}
.header-call:hover{background:var(--copper-deep);color:#FFFFFF}
.status{display:inline-flex;align-items:center;gap:8px;font-weight:600}
.status i{width:10px;height:10px;border-radius:50%;background:#9AA9A4;display:inline-block}
.status.open i{background:#5BD08F;box-shadow:0 0 0 4px rgba(91,208,143,.25)}
.status.closed i{background:#E8A089}
.reveal{transition:opacity .6s ease, transform .6s ease}
.reveal.pending{transform:translateY(18px)}
.sos{display:flex;flex-wrap:wrap;gap:40px;align-items:flex-start}
.sos .intro{flex:1 1 320px;min-width:0;display:flex;flex-direction:column;gap:16px}
.sos .tool{flex:2 1 480px;min-width:0;background:var(--paper);border-radius:18px;padding:28px;display:flex;flex-direction:column;gap:20px}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{font:inherit;font-size:1.05rem;font-weight:600;min-height:48px;padding:0 20px;border-radius:999px;border:2px solid var(--line);background:var(--ground);color:var(--spa);cursor:pointer;transition:background-color .15s ease,border-color .15s ease,color .15s ease}
.chip:hover{border-color:var(--copper)}
.chip[aria-pressed="true"]{background:var(--copper);border-color:var(--copper);color:#FFFFFF}
.tip{border-top:2px solid var(--mist);padding-top:18px;display:flex;flex-direction:column;gap:10px;min-height:150px}
.tip h3{font-size:1.5rem}
.tip ol{margin:0;padding-left:1.3em;display:flex;flex-direction:column;gap:6px}
.price-search{display:flex;flex-direction:column;gap:8px;max-width:520px;margin-bottom:28px}
.price-search label{font-weight:600}
.price-search input{font:inherit;font-size:1.15rem;min-height:56px;padding:0 18px;border-radius:14px;border:2px solid var(--line);background:var(--paper);color:var(--ink)}
.price-search input:focus{border-color:var(--copper);outline:none;box-shadow:0 0 0 4px var(--copper-soft)}
.no-match{background:var(--copper-soft);border-radius:14px;padding:18px 22px}
mark{background:var(--copper-soft);color:var(--ink);border-radius:3px}
.totop{position:fixed;right:calc(18px + env(safe-area-inset-right, 0px));bottom:calc(18px + env(safe-area-inset-bottom, 0px));width:52px;height:52px;border-radius:50%;border:0;background:var(--spa);color:#FFFFFF;font-size:1.4rem;cursor:pointer;box-shadow:0 8px 20px rgba(15,61,53,.25);z-index:15}
.totop:hover{background:var(--copper)}
.copy-btn{font:inherit;font-weight:600;min-height:48px;padding:0 18px;border-radius:999px;border:2px solid var(--spa);background:transparent;color:var(--spa);cursor:pointer}
.copy-btn:hover{background:var(--mist)}
@media (prefers-reduced-motion: reduce){*{transition:none !important}.reveal.pending{opacity:1;transform:none}}

/* WhatsApp */
.wa-float{position:fixed;left:calc(18px + env(safe-area-inset-left, 0px));bottom:calc(18px + env(safe-area-inset-bottom, 0px));z-index:15;display:inline-flex;align-items:center;gap:10px;min-height:56px;padding:0 22px 0 16px;border-radius:999px;background:#1B7A43;color:#FFFFFF;font-weight:600;text-decoration:none;box-shadow:0 10px 24px rgba(0,0,0,.2);transition:transform .15s ease, background-color .15s ease}
.wa-float:hover{background:#14613A;color:#FFFFFF;transform:translateY(-2px)}

/* Mobile menu */
.menu-btn{display:none}

/* Mobile call bar */
.callbar{display:none}
@media (max-width: 720px){
  body{font-size:1.125rem;padding-bottom:calc(74px + env(safe-area-inset-bottom, 0px))}
  section{padding-block:56px}
  .callbar{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:20;gap:10px;background:var(--spa-deep);padding:10px max(14px, env(safe-area-inset-right, 0px)) calc(10px + env(safe-area-inset-bottom, 0px)) max(14px, env(safe-area-inset-left, 0px))}
  .callbar a{flex:1;min-height:52px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:600;text-decoration:none}
  .callbar .c1{background:var(--copper);color:#FFFFFF}
  .callbar .c2{background:#1C5248;color:#FFFFFF}
  .ticket{left:8px}
  .totop{bottom:calc(86px + env(safe-area-inset-bottom, 0px))}
  .header-call{display:none}
  .topbar .addr,.topbar .topcall{display:none}
  header.site .wrap{flex-wrap:wrap;padding-block:14px}
  .brand b{font-size:1.6rem}
  .menu-btn{display:inline-flex;align-items:center;gap:10px;font:inherit;font-weight:600;font-size:1.05rem;min-height:48px;padding:0 18px;border-radius:12px;border:2px solid rgba(255,255,255,.5);background:transparent;color:#FFFFFF;cursor:pointer}
  .menu-btn .bars,.menu-btn .bars::before,.menu-btn .bars::after{display:block;width:20px;height:2px;background:currentColor;border-radius:2px;position:relative}
  .menu-btn .bars::before,.menu-btn .bars::after{content:"";position:absolute;left:0}
  .menu-btn .bars::before{top:-6px}.menu-btn .bars::after{top:6px}
  nav.main{display:none;flex-basis:100%}
  nav.main.open{display:block}
  nav.main ul{flex-direction:column;gap:0;border-top:1px solid rgba(255,255,255,.2);padding-top:6px}
  nav.main a{display:flex;align-items:center;min-height:52px;font-size:1.2rem;border-bottom:1px solid rgba(255,255,255,.12)}
  .section-head{margin-bottom:28px}
  .card{padding:22px}
  .feature .wrap{gap:32px}
  .faq summary{font-size:1.15rem}
  .map{height:260px}
  .wa-float{display:none}
  .callbar .c3{background:#1B7A43;color:#FFFFFF}
}
"""

NAV = [("index.html", "Home"), ("services.html", "Services"), ("prices.html", "Get a price"),
       ("wedding-dress-cleaning.html", "Wedding dresses"), ("journal.html", "Care journal"), ("find-us.html", "Find us")]

def esc(s): return html.escape(s, quote=True)

def business_schema():
    spec = []
    for day, o, c in HOURS:
        if o: spec.append({"@type": "OpeningHoursSpecification", "dayOfWeek": day, "opens": o, "closes": c})
    return {
        "@context": "https://schema.org", "@type": "DryCleaningOrLaundry", "@id": DOMAIN + "/#business",
        "name": NAME, "url": DOMAIN + "/", "telephone": PHONE_INTL,
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": TOWN,
                    "addressRegion": "North Yorkshire", "postalCode": POSTCODE, "addressCountry": "GB"},
        "areaServed": ["Harrogate", "Knaresborough", "Pannal", "Killinghall", "Starbeck"],
        "foundingDate": "1986", "sameAs": ["https://share.google/WVhCBlfNNvHvr8HG9"], "alternateName": ["Harrogate Dry Cleaners", "Harrogate Cleaners & Intrim"], "hasMap": MAPS, "image": DOMAIN + "/images/blue-suit-tailoring.jpg", "openingHoursSpecification": spec,
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}} for s in
                       ["Dry cleaning", "Laundry and service wash", "Shirt laundering", "Alterations and repairs",
                        "Wedding dress cleaning and preservation", "Duvet and curtain cleaning"]],
    }

def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"

def faq_html(faqs, heading="Questions people ask us", hid="faq"):
    items = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs)
    return f'<div class="faq stack"><h2 id="{hid}">{esc(heading)}</h2><div>{items}</div></div>'

def hours_table():
    def nice(t):
        h, m = int(t[:2]), t[3:]
        return f"{h % 12 or 12}{'' if m == '00' else ':' + m}{'am' if h < 12 else 'pm'}"
    rows = "".join(f"<tr><td>{d}</td><td>{(nice(o) + '–' + nice(c)) if o else 'Closed'}</td></tr>" for d, o, c in HOURS)
    return f'<table class="hours"><tbody>{rows}</tbody></table>'

def head(title, desc, path, extra_ld):
    canon = DOMAIN + "/" + ("" if path == "index.html" else path)
    return f"""<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="en_GB">
<meta property="og:image" content="{DOMAIN}/images/blue-suit-tailoring.jpg">
<meta name="geo.region" content="GB-NYK">
<meta name="geo.placename" content="Harrogate">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&amp;family=Work+Sans:wght@400;500;600&amp;display=swap">
<style>{CSS}</style>
{ld(business_schema())}
{"".join(ld(x) for x in extra_ld)}"""

def chrome_top(path):
    cur = ' aria-current="page"'
    links = "".join(f'<li><a href="{h}"{cur if h == path else ""}>{t}</a></li>' for h, t in NAV)
    return f"""<a class="skip" href="#content">Skip to content</a>
<div class="topbar"><div class="wrap"><span><span class="status" data-status><i aria-hidden="true"></i><span data-status-text>{HOURS_SHORT}</span></span><span class="addr"> · {STREET}, {POSTCODE}</span></span><span class="topcall">Call us: <a href="tel:{PHONE_INTL}">{PHONE}</a></span></div></div>
<header class="site"><div class="wrap">
<a class="brand" href="index.html"><b>{NAME}</b><span>Est. 1986 · Cold Bath Road</span></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="mainnav"><span class="bars" aria-hidden="true"></span>Menu</button>
<nav class="main" id="mainnav" aria-label="Main"><ul>{links}</ul></nav>
</div></header>
<main id="content">"""

def review_url():
    return GOOGLE_REVIEW or MAPS

STARS = '<span class="stars" aria-hidden="true">' + ''.join('<svg viewBox="0 0 24 24"><path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z"/></svg>' for _ in range(5)) + '</span>'

def review_band():
    return f"""<section class="review-band"><div class="wrap review-inner">
{STARS}
<div class="review-copy"><h2>Happy with your cleaning?</h2><p>Please leave us a review on Google. It takes a minute, and it helps other people in Harrogate find a dry cleaner they can trust.</p></div>
<a class="btn solid" href="{review_url()}" rel="noopener">Leave us a Google review</a>
</div></section>"""

def map_html():
    fallback = f'<div class="map-fallback"><strong style="font-size:1.3rem;color:#FFFFFF">{NAME}</strong><span>{STREET}, {TOWN} {POSTCODE}</span><a class="btn solid" href="{MAPS}" rel="noopener">Open in Google Maps</a></div>'
    if PREVIEW:
        return fallback
    return fallback + f'<iframe src="{MAP_EMBED}" title="Map showing {NAME} on Cold Bath Road, Harrogate" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>'

def chrome_bottom():
    links = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    return f"""</main>
<footer class="site"><div class="wrap">
<div class="map">{map_html()}</div>
<div class="foot-grid">
<div><h2>{NAME}</h2><p>{STREET}<br>{TOWN} {POSTCODE}</p><p style="margin-top:10px">Phone: <a href="tel:{PHONE_INTL}">{PHONE}</a></p><p style="margin-top:6px"><a href="{WHATSAPP}" rel="noopener">Message us on WhatsApp</a></p><p style="margin-top:6px"><a href="{review_url()}" rel="noopener">Leave us a Google review</a></p><p style="margin-top:10px"><a href="{MAPS}" rel="noopener">Open in Google Maps</a></p></div>
<div><h2>Opening times</h2>{hours_table()}</div>
<div><h2>Pages</h2><ul>{links}</ul></div>
</div>
<p class="legal">© 2026 {NAME} · <a href="privacy.html">Privacy notice</a> · <a href="terms.html">Terms &amp; conditions</a></p>
</div></footer>
<a class="wa-float" href="{WHATSAPP}" rel="noopener"><svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20.5l1.6-5.2A8.5 8.5 0 1 1 21 11.5z"/><path d="M9 9.5c.3 2 1.8 3.8 4 4.6l1.2-1.1 1.8.8"/></svg><span>WhatsApp us</span></a>
<button class="totop" type="button" aria-label="Back to top" hidden>↑</button>
<script>{SCRIPT}</script>
<nav class="callbar" aria-label="Quick contact"><a class="c1" href="tel:{PHONE_INTL}">Call</a><a class="c3" href="{WHATSAPP}" rel="noopener">WhatsApp</a><a class="c2" href="find-us.html">Find us</a></nav>"""

def page(path, title, desc, body, extra_ld=(), artifact=False):
    h = head(title, desc, path, extra_ld)
    b = chrome_top(path) + body + chrome_bottom()
    if artifact:
        return h + "\n" + b
    return ('<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + h + '\n</head>\n<body>\n' + b + '\n' + CHAT_SNIPPET + '\n</body>\n</html>\n')

# ---------- Content ----------
def icon(d):
    return f'<span class="svc-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{d}</svg></span>'

ICONS = {
    "dry-cleaning": '<path d="M12 7.5a2.2 2.2 0 1 1 2.2-2.2"/><path d="M12 7.5v1.2L3.4 15.2a1.3 1.3 0 0 0 .8 2.3h15.6a1.3 1.3 0 0 0 .8-2.3L12 8.7"/>',
    "laundry": '<rect x="4" y="3" width="16" height="18" rx="2"/><circle cx="12" cy="13.5" r="4.5"/><path d="M7.5 6.5h.01M10.5 6.5h3"/>',
    "shirts": '<path d="M8 3.5 12 6l4-2.5 4.5 3-2.3 4.2H16V21H8V10.7H5.8L3.5 6.5z"/><path d="M12 6v4"/>',
    "alterations": '<circle cx="6" cy="6" r="2.8"/><circle cx="6" cy="18" r="2.8"/><path d="M20 4 8.2 15.8M14.6 14.6 20 20M8.2 8.2 11.5 11.5"/>',
    "wedding": '<path d="M9.5 3h5l-1 4.5L19 21H5l5.5-13.5z"/><path d="M10.5 7.5h3"/>',
    "household": '<path d="M3 18v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6"/><path d="M3 18h18M3 21v-3M21 21v-3"/><path d="M6.5 10V7.5a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1V10"/>',
}

SERVICES = [
    ("dry-cleaning", "Dry cleaning", "Suits, coats, dresses, knitwear, silk and delicates. Every item is checked for stains and loose buttons, cleaned with the right process for its fabric, then pressed and finished by hand.",
     ["Suits, jackets and trousers", "Winter coats and macs", "Dresses, skirts and blouses", "Wool, cashmere and silk", "Ties and scarves"]),
    ("laundry", "Laundry & service wash", "Bring a bag of everyday washing and we will wash, dry and fold it for you. Ideal if you are busy, have no space to dry clothes, or are staying in Harrogate on holiday.",
     ["Everyday clothes", "Towels and bed linen", "Ironing only, if you prefer to wash at home"]),
    ("shirts", "Shirts", "Shirts laundered and pressed, returned on a hanger or folded and boxed. A good choice for office shirts week after week.",
     ["Cotton and cotton-blend shirts", "Blouses", "Starch to your liking"]),
    ("alterations", "Alterations & repairs", "Hems taken up or let down, zips replaced, garments taken in or let out, and small repairs. Tell us how you want it to fit and we will pin it with you.",
     ["Trouser and skirt hems", "Zip replacement", "Taking in and letting out", "Buttons and small repairs"]),
    ("wedding", "Wedding & occasion wear", "Wedding dresses pressed before the day, then cleaned and boxed afterwards so they keep. We also look after bridesmaid dresses, prom dresses and christening gowns.",
     ["Wedding dresses", "Bridesmaid and prom dresses", "Christening gowns", "Morning suits"]),
    ("household", "Duvets, curtains & bedding", "Large items that will not fit, or should not go, in a home washing machine. Feather and down duvets are cleaned and dried thoroughly so the filling stays even.",
     ["Feather, down and synthetic duvets", "Pillows", "Lined and unlined curtains", "Throws, blankets and table linen"]),
]

HOME_FAQS = [
    ("Where is Harrogate Cleaners?", f"We are at {STREET}, {TOWN} {POSTCODE}, in the blue shopfront with the Harrogate Cleaners sign. You can call us on {PHONE} or message us on WhatsApp."),
    ("How much does dry cleaning cost?", "Every item is priced individually, because the fabric, size and finish all make a difference. Send us a photo on WhatsApp, call us or pop into the shop and we will give you a price straight away."),
    ("How long has Harrogate Cleaners been open?", "We were established in 1986 and have been cleaning for Harrogate ever since."),
    ("How long does dry cleaning take?", f"Most items are ready in {TURNAROUND}. {EXPRESS}"),
    ("Do you offer same-day or express dry cleaning?", "We offer a 24-hour express service for many items. Some garments and fabrics need longer, so ask in the shop or call us and we will turn it around as quickly as we can."),
    ("Can you clean my wedding dress?", "Yes. We clean wedding dresses, including silk, lace and beaded gowns, and can box them in acid-free tissue for long-term storage."),
    ("Do you clean duvets and curtains?", "Yes. We clean feather, down and synthetic duvets of every size, as well as pillows, throws and curtains."),
    ("Do you do alterations and repairs?", "Yes. We do hems, zips, taking in and letting out, and small repairs."),
    ("Do I need an appointment?", "No. Just bring your items to the shop during opening hours. For a wedding dress fitting or large curtain order, a quick call first is helpful."),
]

POSTS = [
    {"slug": "how-to-clean-and-store-a-wedding-dress.html", "tag": "Weddings", "img": "inspect",
     "title": "How to clean and store a wedding dress after the big day",
     "dek": "What to do in the weeks after your wedding so the dress stays white for years.",
     "desc": "A practical guide to cleaning and storing a wedding dress, from a Harrogate dry cleaner. When to clean it, how to store it, and what to avoid.",
     "body": """
<p>Most wedding dresses come home from the reception looking fine. A little dust on the hem, perhaps a splash of champagne. It is tempting to hang it in the wardrobe and deal with it later. Here is why it is worth acting within the first few weeks, and how to store the dress once it is clean.</p>
<h2>Why sooner is better</h2>
<p>Some of the most damaging marks on a wedding dress are invisible on the day. Champagne, white wine, sweat and sugary drinks dry clear. Over months, the sugars in them oxidise and turn yellow or brown, much like a cut apple. By the time you can see the mark it is far harder to remove, and on silk it may be permanent.</p>
<p>Cleaning within a few weeks of the wedding gives the best chance of a clean, even result.</p>
<h2>What to do before you bring it in</h2>
<ul>
<li>Do not try to scrub stains at home. Rubbing can spread the mark and damage delicate fabric or beading.</li>
<li>Hang the dress by its inner loops, not the shoulders, so the weight does not pull the fabric out of shape.</li>
<li>Make a note of anything you know was spilled, such as red wine, lipstick or grass. It helps us choose the right treatment.</li>
<li>Bring any detachable parts, such as a belt, sash or train loop, so everything can be cleaned together.</li>
</ul>
<h2>How we clean a wedding dress</h2>
<p>Every dress is inspected first, seam by seam. Beading, sequins and lace are checked for loose threads, and the hem is examined for ground-in dirt from the dance floor. Stains are treated individually before the dress is cleaned using a process chosen for its fabric. It is then pressed and finished by hand.</p>
<h2>How to store it afterwards</h2>
<ul>
<li><strong>Acid-free tissue and box.</strong> Ordinary tissue and cardboard contain acids that can yellow fabric over time.</li>
<li><strong>No plastic.</strong> Plastic covers trap moisture, which can lead to mildew and yellowing.</li>
<li><strong>Cool, dark and dry.</strong> A wardrobe shelf or under a bed is better than a loft or garage, where temperature and damp change through the year.</li>
<li><strong>Check it once a year.</strong> Open the box, look it over and refold it along different lines to avoid permanent creases.</li>
</ul>
<div class="callout"><h3>Bring it to Cold Bath Road</h3><p>We clean and box wedding dresses for brides across Harrogate and the surrounding area. <a href="wedding-dress-cleaning.html">See our wedding dress service</a> or call us on """ + PHONE + """.</p></div>
"""},
    {"slug": "what-affects-dry-cleaning-cost.html", "tag": "Good to know", "img": "shirts",
     "title": "What affects the cost of dry cleaning?",
     "dek": "What affects the price of cleaning a garment, and how to get the most for your money.",
     "desc": "A plain-English guide from a Harrogate dry cleaner: what affects the cost of cleaning suits, dresses, coats and duvets, and how to get a price.",
     "body": """
<p>It is a fair question, and one we are asked at the counter every week. Because every garment is different, we price each item individually. This guide explains why two items that look similar can cost different amounts, and how to keep your cleaning bill down.</p>
<h2>What affects the price</h2>
<ul>
<li><strong>Fabric.</strong> Silk, velvet, suede and some wools need a gentler process and more careful hand finishing than cotton or polyester.</li>
<li><strong>Construction.</strong> A lined, structured jacket takes longer to press than an unlined shirt. Pleats, ruffles and gathers all add finishing time.</li>
<li><strong>Embellishment.</strong> Beads, sequins and lace are checked and sometimes protected before cleaning.</li>
<li><strong>Size.</strong> A king-size duvet or a long pair of lined curtains uses more space and drying time than a single item of clothing.</li>
<li><strong>Stains.</strong> Most stain removal is included. A heavily marked item may need extra treatment, and we will always tell you first.</li>
<li><strong>Speed.</strong> Most items are ready in """ + TURNAROUND + """. Our 24-hour express service is available for many garments, depending on the fabric.</li>
</ul>
<h2>Is dry cleaning worth it?</h2>
<p>For a good suit or coat, regular professional cleaning usually extends its life. Home washing a "dry clean only" garment risks shrinkage, colour loss and a jacket that never hangs the same way again. Replacing a suit costs far more than cleaning it a few times a year.</p>
<h2>Five ways to spend less</h2>
<ol>
<li>Clean suit jackets and trousers together so they wear and fade evenly, and you are not paying to fix a mismatch later.</li>
<li>Air garments between wears. A suit worn for a few hours often needs a hang and a brush, not a clean.</li>
<li>Bring stains in quickly. Fresh marks come out more easily, which saves treatment time.</li>
<li>Have winter coats and duvets cleaned before you put them away for summer, so stains do not set while they are stored.</li>
<li>Ask about bundles for shirts and household items.</li>
</ol>
<div class="callout"><h3>Get a price</h3><p>Send us a photo on WhatsApp, call """ + PHONE + """, or bring the item into the shop at """ + STREET + """ and we will give you a price on the spot.</p><p><a class="btn solid" href=\"""" + WHATSAPP + """\" rel=\"noopener\">WhatsApp us a photo</a></p></div>
"""},
    {"slug": "duvet-and-curtain-cleaning-guide.html", "tag": "Household", "img": "linen",
     "title": "Can you wash a duvet or curtains at home?",
     "dek": "When home washing works, when it goes wrong, and when to bring them to us.",
     "desc": "Can you wash a feather duvet or lined curtains at home? A Harrogate dry cleaner explains when it works, the common problems, and when to use a professional.",
     "body": """
<p>Duvets and curtains are among the largest things in a home, and among the least often cleaned. Here is an honest guide to doing it yourself, and when it makes sense to bring them in.</p>
<h2>Duvets</h2>
<p>Start with the care label. Many synthetic duvets are machine washable, and a single or double often fits a large domestic drum. The trouble starts with bigger sizes and natural fillings.</p>
<ul>
<li><strong>Drum size.</strong> A duvet needs room to move. Crammed into a small drum it will not rinse properly, and the machine can be strained by the weight of a wet duvet.</li>
<li><strong>Drying.</strong> Feather and down must be dried completely, right through to the centre. Filling that stays damp can clump and develop a musty smell or mildew.</li>
<li><strong>Clumping.</strong> Even when dry, feathers can bunch at one end. Professional drying keeps the filling moving so it stays even.</li>
</ul>
<p>As a rule, most people are happy washing a synthetic single at home, and bring feather, down and king-size duvets to us.</p>
<h2>Curtains</h2>
<p>Curtains look simple, but they are often a mix of fabrics. A cotton face with a different lining can shrink at different rates, leaving a puckered edge. Many curtains are also faded on the side that faces the window, and washing can make that more obvious.</p>
<ul>
<li>Check the label. If it says dry clean only, it usually means it.</li>
<li>Measure the drop and width before cleaning, so any change can be spotted.</li>
<li>Remove all hooks, weights and fixings before bringing them in.</li>
<li>Vacuum curtains gently on low suction every few months to keep dust down between cleans.</li>
</ul>
<h2>How often should they be cleaned?</h2>
<p>Most households have duvets cleaned once or twice a year, often at the change of season. Curtains usually need cleaning every one to two years, or sooner in a kitchen or a smoker's home.</p>
<div class="callout"><h3>Too big for your machine?</h3><p>We clean duvets, pillows, throws and curtains of every size. WhatsApp us a photo for a price, or call us on """ + PHONE + """.</p></div>
"""},
]

STAINS = [
    ("wine", "Red wine", ["Blot straight away with a clean white cloth. Do not rub.", "Rinse from the back of the fabric with cold water.", "Avoid salt and hot water, which can set the stain.", "Bring it in within a day or two and tell us it was wine."]),
    ("coffee", "Tea or coffee", ["Blot off as much as you can.", "Rinse with cold water from the back of the fabric.", "If it had milk in it, keep heat away from it.", "Bring it in soon. Old tea and coffee marks turn brown."]),
    ("grease", "Grease or oil", ["Do not use water. It spreads oil.", "Blot gently with kitchen paper.", "Dust with a little cornflour or talc to soak it up, then brush off.", "Bring it in. Grease needs a solvent to lift properly."]),
    ("makeup", "Make-up or fake tan", ["Lift off any excess with the edge of a card.", "Do not rub, especially on collars.", "Keep it away from heat, including hairdryers and irons.", "Bring it in and tell us the product if you know it."]),
    ("mud", "Mud or grass", ["Let mud dry completely, then brush off what you can.", "For grass, do not wash it at a high temperature.", "Bring it in. Grass marks are a dye and need specialist treatment."]),
    ("blood", "Blood", ["Use cold water only. Hot water sets blood for good.", "Blot from the back of the fabric.", "Bring it in as soon as possible."]),
]

def stain_sos():
    chips = "".join(f'<button class="chip" type="button" data-stain="{k}" aria-pressed="{"true" if i == 0 else "false"}">{n}</button>' for i, (k, n, _) in enumerate(STAINS))
    tips = "".join(f'<div class="tip" data-tip="{k}"{"" if i == 0 else " hidden"}><h3>{n}: first aid</h3><ol>' + "".join(f"<li>{esc(x)}</li>" for x in steps) + "</ol></div>" for i, (k, n, steps) in enumerate(STAINS))
    return f"""<section><div class="wrap sos">
<div class="intro"><p class="eyebrow">Stain first aid</p><h2>Spilled something?</h2><p style="color:var(--ink-soft)">Pick what it is to see what to do right now. Then bring it to us, the sooner the better.</p><div class="btns"><a class="btn solid" href="{WHATSAPP}" rel="noopener">WhatsApp us a photo</a><a class="btn line" href="tel:{PHONE_INTL}">Call for advice</a></div></div>
<div class="tool"><div class="chips" role="group" aria-label="Type of stain">{chips}</div>{tips}</div>
</div></section>
"""

def post_cards(n=3):
    out = ""
    for p in POSTS[:n]:
        thumb = f'<div class="thumb photo">{img(p["img"])}<span>{p["tag"]}</span></div>' if p.get("img") else f'<div class="thumb">{p["tag"]}</div>'
        out += f'<a class="post-card" href="{p["slug"]}">{thumb}<h3>{esc(p["title"])}</h3><p>{esc(p["dek"])}</p></a>'
    return out

WAVES = '<svg aria-hidden="true" viewBox="0 0 340 200"><path d="M0 40 Q42 20 85 40 T170 40 T255 40 T340 40" fill="none" stroke="#7FB8A8" stroke-width="2"/><path d="M0 80 Q42 60 85 80 T170 80 T255 80 T340 80" fill="none" stroke="#7FB8A8" stroke-width="2"/><path d="M0 120 Q42 100 85 120 T170 120 T255 120 T340 120" fill="none" stroke="#7FB8A8" stroke-width="2"/><path d="M0 160 Q42 140 85 160 T170 160 T255 160 T340 160" fill="none" stroke="#7FB8A8" stroke-width="2"/></svg>'

def home():
    cards = "".join(f'<a class="card" href="services.html#{sid}"><div class="svc-head">{icon(ICONS[sid])}<h3>{name}</h3></div><p>{esc(text.split(". ")[0])}.</p><span class="more">More about {name.lower()}</span></a>' for sid, name, text, _ in SERVICES)
    body = f"""
<section class="hero-bg">
{img("shopfront", "hero-photo", eager=True)}
<div class="wrap hero-inner">
<div class="hero-panel">
<p class="eyebrow">Specialist cleaners on Cold Bath Road since 1986</p>
<h1>Spa town care for <em>everything</em> you wear.</h1>
<p class="lead">Suits, dresses, coats, wedding dresses, duvets and curtains, cleaned and pressed by hand.</p>
<div class="btns"><a class="btn solid" href="{WHATSAPP}" rel="noopener">WhatsApp us for a price</a><a class="btn light" href="find-us.html">Opening times &amp; map</a></div>
</div>
<div class="hours-chip"><small>Opening hours</small><strong>Mon–Fri 9am–5:30pm</strong><strong>Sat 9am–5pm</strong><span>Sunday closed</span></div>
</div>
</section>

<div class="strap"><div class="wrap"><p><strong>{NAME}</strong><span aria-hidden="true"> · </span><span>Dry cleaning, laundry &amp; alterations</span></p></div></div>

<section><div class="wrap">
<div class="section-head"><h2>What we look after</h2><p>Every item is checked, tagged and treated by hand. You get it back pressed, on a hanger and ready to wear.</p></div>
<div class="grid">{cards}</div>
</div></section>

<section class="feature"><div class="wrap">
<div class="copy">
<p class="eyebrow">Established 1986</p>
<h2>Specialist cleaners on Cold Bath Road for nearly 40 years.</h2>
<p>Every item that comes over our counter is checked, tagged with its own ticket and treated by hand. It comes back pressed, on a hanger and in a protective cover, ready to wear.</p>
<p>Before you leave, we ask you to check your items with us, so you go home happy.</p>
<div class="btns"><a class="btn solid" href="services.html">See our services</a><a class="btn line" href="{WHATSAPP}" rel="noopener">Ask us on WhatsApp</a></div>
</div>
<figure class="pic photo" style="margin:0;aspect-ratio:4/3;border-radius:14px">{img("interior")}</figure>
</div></section>

<section class="feature band"><div class="wrap">
<figure class="pic photo plaque" style="margin:0">{img("plaque")}</figure>
<div class="copy">
<p class="eyebrow">Named after the Cold Bath spring</p>
<h2>Harrogate was built on water. We still treat it with respect.</h2>
<p>Our road takes its name from the Cold Bath, a spring of unusually cold, clear water. In the 18th century people bathed in it, and some came to soothe sore eyes. The Great Award of 1778 made it a common watering place, and a bathing house stood on the spot from 1837 until 1974.</p>
<p>The bath house has gone, but the street still washes things properly.</p>
<p><a class="btn line" href="find-us.html">Visit us on Cold Bath Road</a></p>
</div></div></section>

<section class="feature"><div class="wrap">
<div class="copy">
<p class="eyebrow">Wedding &amp; occasion wear</p>
<h2>The dress, cleaned and kept for the next generation.</h2>
<p>Wedding dresses, christening gowns, silk and lace are checked by hand, cleaned with care and boxed in acid-free tissue so they stay white for years.</p>
<p><a class="btn solid" href="wedding-dress-cleaning.html">Wedding dress cleaning</a></p>
</div>
<figure class="pic photo" style="margin:0;border-radius:200px 200px 14px 14px">{img("weddingcare")}</figure>
</div></section>

{stain_sos()}
<section class="band-dark"><div class="wrap">
<div class="section-head"><h2>The Care Journal</h2><a href="journal.html">All articles</a></div>
<div class="grid">{post_cards()}</div>
</div></section>

{review_band()}
<section><div class="wrap">{faq_html(HOME_FAQS)}</div></section>

<section class="feature band"><div class="wrap">
<figure class="pic photo" style="margin:0;aspect-ratio:3/4;max-height:640px;border-radius:14px">{img("shopside")}</figure>
<div class="copy"><h2>Visit us</h2><p><strong>{STREET}, {TOWN} {POSTCODE}</strong><br>Look for the blue shopfront with the Harrogate Cleaners sign.</p><p>Phone: <a href="tel:{PHONE_INTL}">{PHONE}</a></p>{hours_table()}<div class="btns"><a class="btn solid" href="{MAPS}" rel="noopener">Directions in Google Maps</a><a class="btn line" href="{WHATSAPP}" rel="noopener">WhatsApp us</a></div></div>
</div></section>
"""
    return page("index.html", f"{NAME} | Dry Cleaning & Laundry, Cold Bath Road",
                f"Dry cleaning, laundry, alterations, wedding dress and duvet cleaning at {STREET}, {TOWN} {POSTCODE}. Call {PHONE}.",
                body, [faq_schema(HOME_FAQS)])

def services():
    secs = ""
    simg = {"dry-cleaning": "suit", "shirts": "shirts", "wedding": "weddingcare", "household": "linen", "laundry": "laundry", "alterations": "alterations"}
    for sid, name, text, items in SERVICES:
        pic = img(simg[sid], "card-img") if sid in simg else ""
        li = "".join(f"<li>{esc(i)}</li>" for i in items)
        secs += f'<div class="card" id="{sid}" style="scroll-margin-top:20px">{pic}<div class="svc-head">{icon(ICONS[sid])}<h2>{name}</h2></div><p>{esc(text)}</p><ul style="margin:0;padding-left:1.2em">{li}</ul><span class="more"><a href="{WHATSAPP}" rel="noopener">Ask for a price on WhatsApp</a></span></div>'
    faqs = [("Do you clean leather and suede?", "[YES / NO: confirm with the shop. If yes, add typical turnaround.]"),
            ("Will you tell me if a stain cannot be removed?", "Yes. We check every item when you hand it in and will tell you honestly if a stain may not come out completely."),
            ("Can I drop off and collect at different times?", "Yes. You will get a ticket when you drop off, and you can collect any time during opening hours once your items are ready.")]
    body = f"""
<section class="article-head"><div class="wrap stack"><p class="breadcrumb"><a href="index.html">Home</a> / Services</p><h1>Our services</h1>
<p class="prose" style="font-size:1.25rem;color:var(--ink-soft)">Everything we clean, press and repair at {STREET}. Most items are ready in {TURNAROUND}, and a 24-hour express service is available for many garments.</p></div></section>
<section style="padding-top:0"><div class="wrap"><div class="grid" style="background:transparent">{secs}</div></div></section>
<section class="band"><div class="wrap">{faq_html(faqs, "Service questions", "faq-s")}</div></section>
"""
    return page("services.html", f"Dry Cleaning, Laundry & Alterations in Harrogate | {NAME}",
                f"Dry cleaning, laundry, shirts, alterations, wedding dresses, duvets and curtains at {STREET}, Harrogate. Most items ready in {TURNAROUND}, 24-hour express available.",
                body, [faq_schema(faqs)])

def prices():
    body = f"""
<section class="article-head"><div class="wrap stack"><p class="breadcrumb"><a href="index.html">Home</a> / Get a price</p><h1>Get a price</h1>
<p class="prose" style="font-size:1.25rem;color:var(--ink-soft)">Every garment is different. Fabric, size, trims and stains all make a difference, so we price each item individually. Getting a price is quick and there is no obligation.</p></div></section>
<section style="padding-top:0"><div class="wrap">
<div class="grid">
<div class="card"><h2>WhatsApp us a photo</h2><p>The quickest way. Send a photo of the item, and of any stain, to {PHONE} and we will reply with a price.</p><div class="btns"><a class="btn solid" href="{WHATSAPP}" rel="noopener">WhatsApp us</a></div></div>
<div class="card"><h2>Call us</h2><p>Tell us what you have and we will give you a price over the phone.</p><p style="font-size:1.5rem;color:var(--ink)"><strong>{PHONE}</strong></p><div class="btns"><a class="btn line" href="tel:{PHONE_INTL}">Call now</a></div></div>
<div class="card"><h2>Pop into the shop</h2><p>Bring it to {STREET}. We will look at it with you and price it on the spot. Open {HOURS_SHORT}.</p><div class="btns"><a class="btn line" href="find-us.html">Find us</a></div></div>
</div>
<div class="answer" style="margin-top:28px"><span class="eyebrow">Turnaround</span><p>Most items are ready in {TURNAROUND}. Need it sooner? Our 24-hour express service covers many garments, depending on the fabric. Just ask and we will do our best.</p></div>
</div></section>
<section class="band"><div class="wrap stack"><h2>What we can price for you</h2>
<p class="prose" style="color:var(--ink-soft)">Suits and jackets, dresses and coats, shirts and blouses, knitwear, everyday laundry, duvets, pillows and curtains, wedding and occasion wear, and alterations and repairs. <a href="services.html">See all our services</a>.</p></div></section>
"""
    return page("prices.html", f"Get a Dry Cleaning Price in Harrogate | {NAME}",
                f"Get a price for dry cleaning, laundry, alterations, duvets and wedding dresses at {NAME}, {STREET}. WhatsApp us a photo or call {PHONE}.", body)

def wedding():
    faqs = [("When should I have my wedding dress cleaned?", "Ideally within a few weeks of the wedding. Sugary drinks and perspiration dry clear but turn yellow or brown over time."),
            ("Can you press my dress before the wedding?", "Yes. Bring it in [X] days before the wedding and we will press and steam it ready for the day."),
            ("What does preservation include?", "After cleaning, the dress is folded in acid-free tissue and placed in a storage box designed to protect it from light and dust."),
            ("Can you clean beaded or lace dresses?", "Yes. Beading and lace are checked and protected before cleaning, and any loose beads are noted with you.")]
    body = f"""
<section class="hero"><div class="wrap">
<div class="hero-copy"><p class="breadcrumb"><a href="index.html">Home</a> / Wedding dresses</p>
<h1>Wedding dress cleaning &amp; preservation in Harrogate</h1>
<p class="lead">Pressed before the day. Cleaned and boxed after it, so the dress stays white for the next generation.</p>
<div class="btns"><a class="btn solid" href="tel:{PHONE_INTL}">Call {PHONE}</a><a class="btn line" href="{WHATSAPP}" rel="noopener">Ask for a price</a></div></div>
<div class="hero-art"><div class="holder"><div class="arch photo">{img("lace", eager=True)}</div></div></div>
</div></section>
<section class="band"><div class="wrap"><div class="grid">
<div class="card"><h3>Before the wedding</h3><p>Steaming and pressing so the dress hangs perfectly, including trains and layered skirts.</p></div>
<div class="card"><h3>After the wedding</h3><p>Every stain treated, including the hidden ones from champagne and perspiration, then cleaned by a process chosen for the fabric.</p></div>
<div class="card"><h3>Preservation box</h3><p>Folded in acid-free tissue and boxed to protect it from light, dust and yellowing.</p></div>
</div></div></section>
<section><div class="wrap">{faq_html(faqs, "Wedding dress questions", "faq-w")}
<p style="margin-top:28px">Read our guide: <a href="{POSTS[0]['slug']}">{esc(POSTS[0]['title'])}</a></p></div></section>
"""
    svc = {"@context": "https://schema.org", "@type": "Service", "name": "Wedding dress cleaning and preservation",
           "provider": {"@id": DOMAIN + "/#business"}, "areaServed": "Harrogate"}
    return page("wedding-dress-cleaning.html", f"Wedding Dress Cleaning & Preservation Harrogate | {NAME}",
                f"Wedding dress pressing, cleaning and preservation boxing on Cold Bath Road, Harrogate. Call {PHONE}.",
                body, [faq_schema(faqs), svc])

def find_us():
    body = f"""
<section class="article-head"><div class="wrap stack"><p class="breadcrumb"><a href="index.html">Home</a> / Find us</p><h1>Find us on Cold Bath Road</h1><p class="prose" style="font-size:1.25rem;color:var(--ink-soft)">Look for the blue shopfront with the Harrogate Cleaners sign.</p></div></section>
<section style="padding-block:0 40px"><div class="wrap"><figure style="margin:0">{img("shopfront", "article-img", eager=True)}</figure></div></section>
<section style="padding-top:0"><div class="wrap"><div class="grid">
<div class="card"><h2>Address</h2><p style="font-size:1.3rem;color:var(--ink)"><strong>{NAME}</strong><br>{STREET}<br>{TOWN}<br>{POSTCODE}</p><div class="btns"><a class="btn solid" href="{MAPS}" rel="noopener">Directions in Google Maps</a><button class="copy-btn" type="button" data-copy="{NAME}, {STREET}, {TOWN} {POSTCODE}">Copy address</button></div></div>
<div class="card"><h2>Opening times</h2>{hours_table()}</div>
<div class="card"><h2>Phone &amp; WhatsApp</h2><p style="font-size:1.6rem;color:var(--ink)"><strong>{PHONE}</strong></p><p>Call or WhatsApp us on the same number to check if your items are ready, ask about a price or send a photo of a stain.</p><div class="btns"><a class="btn line" href="{WHATSAPP}" rel="noopener">WhatsApp us</a></div></div>
<div class="card"><h2>Parking &amp; getting here</h2><p>[Parking details: nearest car park, on-street parking rules, bus routes, and how long it takes to walk from the town centre.]</p></div>
</div></div></section>
"""
    return page("find-us.html", f"Find Us | {NAME}, {STREET}, {POSTCODE}",
                f"Address, opening times, phone number and parking for {NAME}, {STREET}, {TOWN} {POSTCODE}.", body)

def journal():
    body = f"""
<section class="article-head"><div class="wrap stack"><p class="breadcrumb"><a href="index.html">Home</a> / Care journal</p><h1>The Care Journal</h1>
<p class="prose" style="font-size:1.25rem;color:var(--ink-soft)">Practical advice on looking after your clothes and household textiles, from the counter on Cold Bath Road.</p></div></section>
<section class="plain" style="padding-top:0"><div class="wrap"><div class="grid">{post_cards()}</div></div></section>
"""
    blog = {"@context": "https://schema.org", "@type": "Blog", "name": "The Care Journal", "url": DOMAIN + "/journal.html",
            "publisher": {"@id": DOMAIN + "/#business"}}
    return page("journal.html", f"Clothes Care Tips & Guides | {NAME}",
                "Advice on stains, wedding dress care, duvets, curtains and dry cleaning costs from a Harrogate dry cleaner.", body, [blog])

def post(p):
    others = "".join(f'<li><a href="{o["slug"]}">{esc(o["title"])}</a></li>' for o in POSTS if o is not p)
    body = f"""
<section class="article-head"><div class="wrap stack"><p class="breadcrumb"><a href="index.html">Home</a> / <a href="journal.html">Care journal</a></p>
<p class="eyebrow">{p['tag']}</p><h1>{esc(p['title'])}</h1><p class="meta">By the team at {NAME} · <time datetime="{TODAY}">23 October 2026</time></p></div></section>
<article class="body"><div class="wrap">{('<figure style="margin:0 0 36px">' + img(p["img"], "article-img", eager=True) + '</figure>') if p.get("img") else ""}<div class="prose">{p['body']}
<h2>More from the journal</h2><ul>{others}</ul></div></div></article>
"""
    bp = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["desc"],
          "datePublished": TODAY, "dateModified": TODAY, "author": {"@type": "Organization", "name": NAME},
          "publisher": {"@id": DOMAIN + "/#business"}, "mainEntityOfPage": DOMAIN + "/" + p["slug"]}
    if p.get("img"): bp["image"] = DOMAIN + "/" + IMAGES[p["img"]][0]
    return page(p["slug"], f"{p['title']} | {NAME}", p["desc"], body, [bp])

def legal_page(path, title, desc, h1, inner):
    body = f"""<section class="article-head"><div class="wrap stack"><p class="breadcrumb"><a href="index.html">Home</a> / {h1}</p><h1>{h1}</h1><p class="meta">Last updated <time datetime="{TODAY}">23 October 2026</time></p></div></section>
<article class="body"><div class="wrap"><div class="prose">{inner}</div></div></article>"""
    return page(path, title, desc, body)

def privacy():
    inner = f"""
<p>This notice explains what personal information {NAME} collects, why we collect it and how we look after it. We keep it simple: we only ask for what we need to look after your order.</p>
<h2>Who we are</h2>
<p>{NAME}, {STREET}, {TOWN} {POSTCODE}. Phone {PHONE}. We are the data controller for the personal information described here. We are registered with the Information Commissioner's Office (ICO) and handle personal data in line with the UK General Data Protection Regulation (UK GDPR) and the Data Protection Act 2018.</p>
<h2>What we collect</h2>
<p>We only collect personal details when you use our collection and delivery service. These are:</p>
<ul><li>your name</li><li>your collection and delivery address</li><li>your phone number and, if you give it, your email address</li><li>any instructions you give us about access or timing</li></ul>
<p>If you phone us, email us, message us on WhatsApp or use the chat on this website, we will also see the details you choose to share so we can reply. We do not collect any other personal information, and we do not hold special category data.</p>
<h2>Why we use it</h2>
<ul>
<li>To arrange, collect and return your items. Our lawful basis is that it is needed to carry out our agreement with you.</li>
<li>To contact you about your order, for example if an item needs extra care or your delivery time changes.</li>
<li>To answer questions you send us.</li>
</ul>
<p>We do not use your details for marketing, we do not sell or share them for marketing, and we do not use them for automated decision-making or profiling.</p>
<h2>How long we keep it</h2>
<p>We keep your details only for as long as we need them to complete your order and deal with any follow-up questions. After that they are securely deleted. The only exception is where the law requires us to keep a record, for example basic sales records for tax purposes.</p>
<h2>Who can see it</h2>
<p>Only our staff, and only when they need it to handle your order. We may use trusted service providers to run this website and our customer messages, such as our website host, WhatsApp (provided by Meta) and our customer support and chat system. They act only on our instructions and must keep your information secure. We never sell your information.</p>
<h2>Cookies and third-party features</h2>
<p>This website does not use advertising or tracking cookies of its own. The Google map on our pages and the chat window are provided by third parties, who may set their own cookies when you use them. You can control cookies in your browser settings.</p>
<h2>How we keep it safe</h2>
<p>We take sensible steps to protect your information, including limiting who can access it and keeping paper records out of public view.</p>
<h2>Your rights</h2>
<p>Under UK data protection law you have the right to:</p>
<ul><li>ask for a copy of the information we hold about you</li><li>ask us to correct anything that is wrong</li><li>ask us to delete your information</li><li>ask us to restrict or stop using it</li><li>ask for it in a portable format</li></ul>
<p>To use any of these rights, call us on {PHONE} or speak to us in the shop. We will respond within one month.</p>
<h2>Complaints</h2>
<p>If you are unhappy with how we have handled your information, please tell us first so we can put it right. You also have the right to complain to the Information Commissioner's Office at <a href="https://ico.org.uk/make-a-complaint/" rel="noopener">ico.org.uk</a> or on 0303 123 1113.</p>
<h2>Changes to this notice</h2>
<p>We may update this notice from time to time. The latest version will always be on this page.</p>
"""
    return legal_page("privacy.html", f"Privacy Notice | {NAME}", f"How {NAME} collects and uses personal information under UK GDPR.", "Privacy notice", inner)

def terms():
    inner = f"""
<p>These terms apply to all items left with {NAME}, {STREET}, {TOWN} {POSTCODE}, whether handed in at the shop or collected by us. By leaving items with us you agree to these terms. Nothing in them affects your statutory rights under the Consumer Rights Act 2015.</p>
<h2>1. Our service</h2>
<p>We clean, launder, press and repair every item with reasonable care and skill, following the care label and the standards of the dry cleaning trade.</p>
<h2>2. When you hand items in</h2>
<ul>
<li>Please empty all pockets. We cannot accept responsibility for money, jewellery, keys, pens or other items left in garments, or for damage they cause to your items or other customers' items.</li>
<li>Please point out any stains, damage or special features, and tell us what caused a stain if you know. This helps us choose the right treatment.</li>
<li>We check each item when it is handed in. If we think there is a risk in cleaning it, we will tell you before we go ahead.</li>
<li>You will be given a ticket. Please keep it, as it is needed to collect your items.</li>
</ul>
<h2>3. Care labels and fabrics</h2>
<p>We follow the manufacturer's care label. We are not responsible for damage that results from following a correct label where the fault lies in the garment itself, or from an incorrect or missing label. This can include shrinkage, colour loss or bleeding, weak or worn fabric, or trims, glues and linings that are not suitable for the recommended process.</p>
<p>Where an item has no care label, we will only clean it if you ask us to, and at your own risk.</p>
<h2>4. Stains</h2>
<p>We do our best to remove every stain. Some stains, especially older ones or those that have been treated at home or exposed to heat, cannot be removed without risking the fabric. In those cases we will stop rather than damage the item.</p>
<h2>5. Buttons, trims and decoration</h2>
<p>Where possible we protect or remove delicate buttons, sequins, beads and trims before cleaning. We cannot be responsible for decoration that is not designed to withstand cleaning.</p>
<h2>6. Turnaround</h2>
<p>Most items are ready in {TURNAROUND}. Our 24-hour express service is available for many items, depending on the garment and fabric. Ready times are estimates, and we will let you know if your order needs longer.</p>
<h2>7. Collection and delivery</h2>
<ul>
<li>Please make sure someone is available at the agreed time, or give us clear instructions for a safe place to leave items.</li>
<li>Items left in a safe place at your request are left at your own risk.</li>
<li>Please check your items when they are delivered. The 24-hour rule in section 9 starts from delivery.</li>
</ul>
<h2>8. Payment</h2>
<p>Every item is priced individually, and we will always tell you the price before we start. Payment is due when you collect your items, or on delivery. Special items are priced when you hand them in, and we will always tell you before any extra charge.</p>
<h2>9. Check your items when you collect them</h2>
<p>Please check your items carefully when you collect them, before you leave the shop. If anything is not right, tell us straight away so we can look at it with you.</p>
<p>If you notice a problem after you have left, you must let us know within 24 hours of collection or delivery, by phone or in the shop, and bring the item back with your ticket. After 24 hours we cannot accept responsibility, because we can no longer be sure the problem happened while the item was with us.</p>
<h2>10. If we are responsible</h2>
<p>If we are responsible for loss of or damage to an item, we will first try to put it right by recleaning or repairing it. If that is not possible, we will pay fair compensation based on the item's value at the time, taking into account its age, condition and wear, and not its price when new. Proof of purchase helps.</p>
<p>Where an item needs an independent opinion, we may send it for testing to an independent textile testing service.</p>
<h2>11. Uncollected items</h2>
<p>Please collect your items within 2 months. We will try to contact you before then using the details we hold. Items not collected after 2 months will be given to a charity shop of our choice, and any money owed for the work will no longer be charged. This is in line with the Torts (Interference with Goods) Act 1977.</p>
<h2>12. Contact</h2>
<p>Questions about these terms? Call {PHONE} or speak to us in the shop.</p>
"""
    return legal_page("terms.html", f"Terms & Conditions | {NAME}", f"Terms and conditions for dry cleaning, laundry, alterations and collection and delivery at {NAME}.", "Terms &amp; conditions", inner)

def extras():
    pages = ["", "services.html", "prices.html", "wedding-dress-cleaning.html", "find-us.html", "journal.html", "privacy.html", "terms.html"] + [p["slug"] for p in POSTS]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"  <url><loc>{DOMAIN}/{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in pages) + "</urlset>\n"
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"
    svc_lines = "\n".join(f"- {name}: {text.split('. ')[0]}." for _, name, text, _ in SERVICES)
    llms = f"""# {NAME}

> {NAME} is a dry cleaning, laundry and alterations shop at {STREET}, {TOWN}, North Yorkshire {POSTCODE}, England, established in 1986. Phone {PHONE}. Open {HOURS_SHORT}. Most items are ready in {TURNAROUND}. A 24-hour express service is available for many items, depending on the garment and fabric.

## Services
{svc_lines}

## Key pages
- [Services]({DOMAIN}/services.html): everything we clean and repair
- [Get a price]({DOMAIN}/prices.html): how to get a price by WhatsApp, phone or in the shop
- [Wedding dress cleaning]({DOMAIN}/wedding-dress-cleaning.html): pressing, cleaning and preservation
- [Find us]({DOMAIN}/find-us.html): address, opening times, parking

## Guides
""" + "\n".join(f"- [{p['title']}]({DOMAIN}/{p['slug']}): {p['dek']}" for p in POSTS) + "\n"
    return {"sitemap.xml": sitemap, "robots.txt": robots, "llms.txt": llms}

def build(artifact):
    global PREVIEW
    PREVIEW = artifact
    d = os.path.join(OUT, "artifact" if artifact else "deploy")
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    files = {"services.html": services(), "prices.html": prices(), "wedding-dress-cleaning.html": wedding(),
             "find-us.html": find_us(), "journal.html": journal(), "privacy.html": privacy(), "terms.html": terms()}
    for p in POSTS: files[p["slug"]] = post(p)
    files["index.html"] = home() if not artifact else None
    for k, v in files.items():
        if v is None: continue
        open(os.path.join(d, k), "w", encoding="utf-8").write(v)
    if artifact:
        # index in preview format: no doctype/html/head/body wrapper
        global page
        orig = page
        def apage(*a, **k): return orig(*a, artifact=True, **k)
        page = apage
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(home())
        page = orig
    os.makedirs(os.path.join(d, "images"), exist_ok=True)
    for src, _ in IMAGES.values():
        shutil.copy(os.path.join(ROOT, "img", os.path.basename(src)), os.path.join(d, src))
    for k, v in extras().items():
        open(os.path.join(d, k), "w", encoding="utf-8").write(v)
    return d

if __name__ == "__main__":
    print(build(False)); print(build(True))
