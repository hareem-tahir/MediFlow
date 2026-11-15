"""Static front-end assets (CSS, SVG symbols, JavaScript) for the MediFlow city views.

Everything here is plain text that cityview.py fills with *real* data computed by the
Python algorithms. The JavaScript only plays back that data (it never invents results).
"""

CSS = """
:root{--bg:#0b1220;--panel:#111a2e;--panel2:#16213b;--line:#22304d;--txt:#e2e8f0;--mut:#8aa0c0;
--red:#ef4444;--blue:#3b82f6;--green:#22c55e;--amber:#f59e0b}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--txt);
font:13px/1.35 'Segoe UI',system-ui,-apple-system,Roboto,sans-serif;overflow:hidden}
.app{display:flex;gap:10px;height:100%;padding:2px}
.mapcol{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px}
.mapwrap{position:relative;flex:1;min-height:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;
background:#0a1020;box-shadow:inset 0 0 60px rgba(0,0,0,.45)}
.mapwrap svg.city{width:100%;height:100%;display:block}
.panel{width:330px;flex:none;overflow-y:auto;display:flex;flex-direction:column;gap:8px;padding-right:2px}
.panel::-webkit-scrollbar{width:6px}.panel::-webkit-scrollbar-thumb{background:#2a3a5e;border-radius:4px}
.box{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:9px 11px}
.box h4{margin:0 0 6px;font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut)}
/* HUD + legend overlays */
.hud{position:absolute;left:12px;top:12px;display:flex;align-items:center;gap:10px;padding:8px 14px 8px 10px;
border-radius:12px;background:rgba(10,16,32,.88);border:1px solid var(--line);backdrop-filter:blur(3px)}
.hud b{font-size:13px;letter-spacing:.06em}.hud small{display:block;color:var(--mut);font-size:11px}
.hud.active{animation:hudflash .8s infinite}
@keyframes hudflash{0%,45%{border-color:#ef4444;box-shadow:0 0 18px rgba(239,68,68,.55)}
50%,95%{border-color:#3b82f6;box-shadow:0 0 18px rgba(59,130,246,.55)}100%{border-color:#ef4444}}
.beacon{position:relative;width:34px;height:20px;border-radius:10px 10px 4px 4px;background:#1e293b;display:flex;overflow:hidden;
border:1px solid #334155}
.beacon i{flex:1;opacity:.28}.beacon i.r{background:#ef4444}.beacon i.b{background:#3b82f6}
.hud.active .beacon i.r{animation:blinkA .8s infinite}.hud.active .beacon i.b{animation:blinkB .8s infinite}
@keyframes blinkA{0%,45%{opacity:1}50%,100%{opacity:.18}}@keyframes blinkB{0%,45%{opacity:.18}50%,95%{opacity:1}100%{opacity:.18}}
.clock{position:absolute;right:12px;top:12px;padding:8px 14px;border-radius:12px;background:rgba(10,16,32,.88);
border:1px solid var(--line);font-variant-numeric:tabular-nums;text-align:right}
.clock b{font-size:18px;letter-spacing:.04em}.clock small{display:block;color:var(--mut);font-size:10px}
.legend{position:absolute;left:50%;transform:translateX(-50%);bottom:8px;padding:6px 14px;border-radius:12px;background:rgba(10,16,32,.92);
border:1px solid var(--line);font-size:10.5px;display:grid;grid-template-columns:repeat(4,auto);gap:3px 20px;color:#b6c4dc}
.legend span{display:flex;align-items:center;gap:7px;white-space:nowrap}
.sw{display:inline-block;width:22px;height:6px;border-radius:3px}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%}
/* toolbar */
.bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
button,select{font:inherit;color:var(--txt);background:#18253f;border:1px solid #2c3d63;border-radius:9px;padding:7px 12px;cursor:pointer}
button:hover{background:#1f3156;border-color:#41588c}
button.go{background:linear-gradient(180deg,#ef4444,#b91c1c);border-color:#f87171;font-weight:700;letter-spacing:.03em}
button.go:hover{background:linear-gradient(180deg,#f25a5a,#c42323)}
input[type=range]{flex:1;min-width:120px;accent-color:#ef4444}
label.tg{display:flex;align-items:center;gap:6px;color:var(--mut);cursor:pointer}
/* ambulance cards */
.card{display:grid;grid-template-columns:62px 1fr;gap:2px 8px;padding:8px;border-radius:11px;background:var(--panel2);
border:1px solid var(--line);margin-bottom:7px;cursor:pointer;border-left:4px solid var(--c,#475569)}
.card.sel{outline:2px solid #60a5fa}.card .ic{grid-row:1/4;align-self:center}
.card .hd{display:flex;justify-content:space-between;align-items:center}
.badge{font-size:10px;font-weight:700;letter-spacing:.06em;padding:2px 7px;border-radius:20px;border:1px solid transparent}
.b-ok{background:#052e16;color:#86efac;border-color:#15803d}.b-amber{background:#451a03;color:#fcd34d;border-color:#b45309}
.b-red{background:#450a0a;color:#fecaca;border-color:#dc2626}.b-off{background:#1e293b;color:#94a3b8;border-color:#475569}
.b-red.flash{animation:badgeflash .8s infinite}
@keyframes badgeflash{0%,45%{box-shadow:0 0 10px #ef4444}50%,95%{box-shadow:0 0 10px #3b82f6;border-color:#3b82f6}}
.chips{display:flex;gap:4px;flex-wrap:wrap}.chip{font-size:10px;padding:1px 6px;border-radius:5px;background:#1d2b4a;color:#a9bde0}
.kv{font-size:11.5px;color:#c3d0e6;display:flex;gap:6px}.kv i{font-style:normal;color:var(--mut);min-width:54px}
.feed{max-height:190px;overflow-y:auto;font-size:12px}.feed div{padding:3px 0;border-bottom:1px solid #1b2842}
.feed time{color:#7aa2ff;margin-right:6px;font-variant-numeric:tabular-nums}
/* svg parts */
.road-body{stroke:#34435f;stroke-width:21;stroke-linecap:round}.road-case{stroke:#050913;stroke-width:28;stroke-linecap:round}
.road-line{stroke:#6a7c9c;stroke-width:1.6;stroke-dasharray:9 10;stroke-linecap:butt;opacity:.8}
.road-traffic{stroke-width:21;stroke-linecap:round;opacity:.92}
.traffic-flow{stroke:#fff;stroke-width:2.4;stroke-dasharray:3 14;stroke-linecap:round;opacity:.55;animation:flow 1s linear infinite}
@keyframes flow{to{stroke-dashoffset:-34}}
.nd{fill:#0e1730;stroke:#7f93b5;stroke-width:2.5}
.nlabel{font-size:12px;font-weight:600;fill:#d5e0f5;paint-order:stroke;stroke:#0a1020;stroke-width:5px;stroke-linejoin:round}
.tag{font-size:10.5px;font-weight:700;paint-order:stroke;stroke:#0a1020;stroke-width:4px}
.lt-r{fill:#7f1d1d}.lt-b{fill:#1e3a8a}.glow{opacity:0}
.amb.siren .lt-r{fill:#ff3b3b;animation:blinkA .8s infinite}.amb.siren .lt-b{fill:#4f8dff;animation:blinkB .8s infinite}
.amb.siren .gr{animation:blinkA .8s infinite}.amb.siren .gb{animation:blinkB .8s infinite}
.amb.off{filter:grayscale(1) brightness(.6)}.amb{cursor:pointer}
.ripple{transform-box:fill-box;transform-origin:center;animation:ripple 1.8s ease-out infinite}
@keyframes ripple{0%{transform:scale(.8);opacity:.9}100%{transform:scale(2.6);opacity:0}}
.inc-g.calm .ripple{animation:none;opacity:0}
.rlabel{font-size:10.5px;font-weight:700;paint-order:stroke;stroke:#08101f;stroke-width:5px;stroke-linejoin:round}
.route.dim{opacity:.12}.route{transition:opacity .25s}
.altl{display:none}.altg.f .altl{display:block}.pulse{animation:pls 1.2s ease-in-out infinite}@keyframes pls{50%{opacity:.45}}
"""

# Reusable SVG definitions: ambulance sprite, gradients, hatch pattern, glow filter.
DEFS = """
<defs>
<g id="amb-g">
  <ellipse cx="4" cy="17" rx="27" ry="4.5" fill="#000" opacity=".35"/>
  <circle class="glow gr" cx="-2" cy="-14" r="30" fill="url(#glR)"/>
  <circle class="glow gb" cx="9" cy="-14" r="30" fill="url(#glB)"/>
  <rect x="-24" y="-12" width="34" height="24" rx="5" fill="#f8fafc" stroke="#0f172a" stroke-width="1.6"/>
  <path d="M10,-12 h10 q6,0 9,7 l3,7 v10 h-22 z" fill="#eef2f7" stroke="#0f172a" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M15,-8 h5 q3,0 5.5,5 h-10.5z" fill="#7dd3fc" stroke="#0f172a" stroke-width="1.2"/>
  <rect x="-23.2" y="3.5" width="54" height="4" fill="#ef4444"/>
  <rect x="-14" y="-9.5" width="5" height="14" rx="1" fill="#ef4444"/><rect x="-18.5" y="-5" width="14" height="5" rx="1" fill="#ef4444"/>
  <rect x="-8" y="-18" width="24" height="7" rx="2.5" fill="#0f172a"/>
  <rect class="lt-r" x="-7" y="-17" width="10" height="5" rx="1.8"/><rect class="lt-b" x="4" y="-17" width="10" height="5" rx="1.8"/>
  <circle cx="-13" cy="13" r="5.2" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
  <circle cx="20" cy="13" r="5.2" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<radialGradient id="glR"><stop offset="0" stop-color="#ff2a2a" stop-opacity=".95"/><stop offset="1" stop-color="#ff2a2a" stop-opacity="0"/></radialGradient>
<radialGradient id="glB"><stop offset="0" stop-color="#2f7bff" stop-opacity=".95"/><stop offset="1" stop-color="#2f7bff" stop-opacity="0"/></radialGradient>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c3a5e"/><stop offset="1" stop-color="#071a33"/></linearGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
<pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="9" height="9" fill="#7f1d1d"/><rect width="4.5" height="9" fill="#ef4444"/></pattern>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
</defs>
"""

# ------------------------------------------------------------------ dispatch map
DISPATCH_JS = r"""
(function(){
const D=JSON.parse(document.getElementById('data').textContent);
const NS="http://www.w3.org/2000/svg",$=id=>document.getElementById(id);
const el=(t,a,p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;};
const SEV={5:'#ef4444',4:'#f97316',3:'#eab308',2:'#84cc16',1:'#22c55e'};
const IDLE=[42,-34],PARK=[64,26],clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const L={alt:$('l-alt'),route:$('l-route'),inc:$('l-inc'),amb:$('l-amb')};
let t=0,running=false,started=false,speed=1,focus=-1,last=null,lastFeed=-1;
const M=D.missions;
function sprite(parent){const g=document.getElementById('amb-g').cloneNode(true);g.removeAttribute('id');parent.appendChild(g);return g;}
document.querySelectorAll('svg.ic').forEach(s=>sprite(s));

function polyLen(p){let s=0;for(let i=1;i<p.length;i++)s+=Math.hypot(p[i][0]-p[i-1][0],p[i][1]-p[i-1][1]);return s;}
function midPoint(p){const h=polyLen(p)/2;let s=0;for(let i=1;i<p.length;i++){const d=Math.hypot(p[i][0]-p[i-1][0],p[i][1]-p[i-1][1]);
 if(s+d>=h){const f=(h-s)/d;return[p[i-1][0]+f*(p[i][0]-p[i-1][0]),p[i-1][1]+f*(p[i][1]-p[i-1][1])];}s+=d;}return p[0];}
const pstr=p=>p.map(q=>q[0]+','+q[1]).join(' ');

/* ---- routes (selected = solid glowing, patient leg = dashed, alternatives = grey dotted) ---- */
const routeEls=[];
M.forEach((m,i)=>{
  const leg1=m.pts.slice(0,m.scene_idx+1),leg2=m.pts.slice(m.scene_idx);
  const g=el('g',{class:'route','data-m':i},L.route);
  el('polyline',{points:pstr(m.pts),fill:'none',stroke:m.color,'stroke-width':16,opacity:.2,'stroke-linecap':'round','stroke-linejoin':'round',filter:'url(#soft)'},g);
  el('polyline',{points:pstr(leg1),fill:'none',stroke:m.color,'stroke-width':5,'stroke-linecap':'round','stroke-linejoin':'round'},g);
  el('polyline',{points:pstr(leg2),fill:'none',stroke:m.color,'stroke-width':5,'stroke-dasharray':'11 8','stroke-linecap':'round','stroke-linejoin':'round',opacity:.85},g);
  const trail=el('polyline',{points:'',fill:'none',stroke:'#fff','stroke-width':2.2,'stroke-linecap':'round','stroke-linejoin':'round',opacity:.95},g);
  const mp=midPoint(leg1),lb=el('g',{transform:`translate(${mp[0]},${mp[1]-14})`},g);
  const tx=el('text',{class:'rlabel','text-anchor':'middle',fill:m.color},lb);tx.textContent=`${m.amb} → ${m.inc} · ${m.eta.toFixed(1)} min`;
  const mp2=midPoint(leg2),lb2=el('g',{transform:`translate(${mp2[0]},${mp2[1]+18})`,class:'leg2'},g);
  const t2=el('text',{class:'rlabel','text-anchor':'middle',fill:m.color,opacity:0},lb2);t2.textContent=`🏥 ${m.hosp} · +${(m.total-m.scene_time).toFixed(1)} min`;
  g.addEventListener('click',()=>setFocus(focus===i?-1:i));
  routeEls.push({g,trail,t2});
  m.alts.forEach((a,k)=>{
    const ag=el('g',{class:'altg','data-m':i},L.alt);
    el('polyline',{points:pstr(a.pts),fill:'none',stroke:'#9fb3d6','stroke-width':3.2,'stroke-dasharray':'2 8','stroke-linecap':'round','stroke-linejoin':'round',opacity:.9},ag);
    const q=midPoint(a.pts),tt=el('text',{class:'rlabel altl','text-anchor':'middle',x:q[0],y:q[1]+(k?16:-8),fill:'#b8c8e6'},ag);
    tt.textContent=`alt · +${a.extra.toFixed(1)} min`;
    el('title',{},ag).textContent=`Alternative route for ${m.amb}: ${a.names.join(' → ')} (${a.cost.toFixed(1)} min, +${a.extra.toFixed(1)} min)`;
  });
});
$('tg-alt')&&$('tg-alt').addEventListener('change',e=>{L.alt.style.display=e.target.checked?'':'none';});

/* ---- incidents ---- */
const incEls={};
D.incs.forEach(inc=>{
  const g=el('g',{class:'inc-g',transform:`translate(${inc.pos[0]-34},${inc.pos[1]-40})`},L.inc);
  el('line',{x1:0,y1:0,x2:34,y2:40,stroke:SEV[inc.sev],'stroke-width':2,'stroke-dasharray':'3 4',opacity:.8},g);
  const rp=el('circle',{r:15,fill:'none',stroke:SEV[inc.sev],'stroke-width':3,class:'ripple'},g);
  const c=el('circle',{r:15,fill:SEV[inc.sev],stroke:'#fff','stroke-width':2.2},g);
  const bang=el('text',{y:6,'text-anchor':'middle','font-size':18,'font-weight':800,fill:'#fff'},g);bang.textContent='!';
  const bw=el('g',{transform:'translate(0,-27)'},g);
  const tx=el('text',{class:'tag','text-anchor':'middle',fill:'#fff'},bw);
  tx.textContent=`${inc.id} · sev ${inc.sev} · ${inc.need}`;
  const sub=el('text',{class:'tag','text-anchor':'middle',y:36,fill:'#fecaca'},g);sub.textContent=inc.mission<0?'NO AMBULANCE':'';
  el('title',{},g).textContent=`${inc.id}: ${inc.desc}\nLocation: ${inc.loc}\nSeverity ${inc.sev}/5, needs ${inc.need}\nStatus: ${inc.status}`;
  incEls[inc.id]={g,c,rp,bang,sub,inc};
});

/* ---- ambulances ---- */
const ambEls={};
D.ambs.forEach(a=>{
  const g=el('g',{class:'amb'+(a.status==='Disabled'?' off':''),'data-id':a.id},L.amb);
  const fl=el('g',{},g);sprite(fl);
  const lb=el('g',{transform:'translate(0,34)'},g);
  const tx=el('text',{class:'tag','text-anchor':'middle',fill:a.status==='Disabled'?'#94a3b8':'#e8f1ff'},lb);tx.textContent=a.id;
  let x=null;
  if(a.status==='Disabled'){x=el('g',{transform:'translate(18,-16)'},g);el('circle',{r:9,fill:'#dc2626',stroke:'#fff','stroke-width':1.5},x);
   const xx=el('text',{y:4.5,'text-anchor':'middle','font-size':13,'font-weight':800,fill:'#fff'},x);xx.textContent='✕';}
  el('title',{},g).textContent=`${a.id} · ${a.status}\nEquipment: ${a.equip.join(', ')}\nBase: ${a.base}`+(a.status==='Disabled'?'\nOUT OF SERVICE':'');
  g.addEventListener('click',()=>{if(a.mission>=0)setFocus(focus===a.mission?-1:a.mission);});
  ambEls[a.id]={g,fl,a};
});

/* ---- motion ---- */
function pathPos(m,tt){
  const P=m.pts,T=m.times,n=P.length-1;
  if(tt<=0){return{x:P[0][0],y:P[0][1],dir:P[1][0]>=P[0][0]?1:-1,seg:0,f:0};}
  if(tt>=T[n]){return{x:P[n][0],y:P[n][1],dir:P[n][0]>=P[n-1][0]?1:-1,seg:n-1,f:1};}
  for(let i=0;i<n;i++){if(tt<T[i+1]){const f=(tt-T[i])/(T[i+1]-T[i]);
   return{x:P[i][0]+f*(P[i+1][0]-P[i][0]),y:P[i][1]+f*(P[i+1][1]-P[i][1]),dir:P[i+1][0]>=P[i][0]?1:-1,seg:i,f};}}
}
function whereIs(m,p){const c=m.names;if(p.f<.1)return 'at '+c[p.seg];if(p.f>.9)return 'at '+c[p.seg+1];return `on road ${c[p.seg]} → ${c[p.seg+1]}`;}
function phase(m,tt){if(!started&&!running)return 0;if(tt<m.scene_time)return 1;if(tt<m.total)return 2;return 3;}

function setFocus(i){focus=i;document.querySelectorAll('.altg').forEach(a=>{const on=i<0||+a.dataset.m===i;a.style.opacity=on?1:.08;a.classList.toggle('f',i>=0&&+a.dataset.m===i);});routeEls.forEach((r,k)=>{r.g.classList.toggle('dim',i>=0&&k!==i);r.t2.setAttribute('opacity',(i===k)?1:0);});
  document.querySelectorAll('.card').forEach(c=>c.classList.toggle('sel',i>=0&&+c.dataset.m===i));}

function render(){
  const anyActive=M.some(m=>{const p=phase(m,t);return p===1||p===2;});
  const allDone=M.length>0&&M.every(m=>phase(m,t)===3);
  M.forEach((m,i)=>{
    const p=phase(m,t),pos=pathPos(m,t),e=ambEls[m.amb];
    const s0=clamp(t/.8,0,1),s1=clamp((t-m.total)/.8,0,1);
    const ox=IDLE[0]*(1-s0)+(p===3?PARK[0]*s1:0),oy=IDLE[1]*(1-s0)+(p===3?PARK[1]*s1:0);
    e.g.setAttribute('transform',`translate(${pos.x+ox},${pos.y+oy})`);
    e.fl.setAttribute('transform',`scale(${pos.dir*1.12},1.12)`);
    e.g.classList.toggle('siren',p===1||p===2);
    const ic=document.querySelector('#c-'+m.amb+' svg.ic');if(ic)ic.classList.toggle('siren',p===1||p===2);
    const pts=[];for(let k=0;k<m.pts.length;k++){if(m.times[k]<=t)pts.push(m.pts[k]);}
    if(p>0)pts.push([pos.x,pos.y]);routeEls[i].trail.setAttribute('points',p>0?pstr(pts):'');
    const ie=incEls[m.inc];
    if(ie){ie.g.classList.toggle('calm',p>=2);
      ie.c.setAttribute('fill',p===3?'#22c55e':p===2?'#f59e0b':SEV[ie.inc.sev]);
      ie.bang.textContent=p===3?'✓':p===2?'🚑':'!';ie.bang.setAttribute('font-size',p===2?13:18);
      ie.sub.textContent=p===0?(m.status==='committed'?'DISPATCHED':m.amb+' ASSIGNED'):p===1?`${m.amb} EN ROUTE`:p===2?'PATIENT ABOARD':'DELIVERED';
      ie.sub.setAttribute('fill',p===3?'#86efac':p===2?'#fde68a':'#fecaca');}
    card(m,i,p,pos);
  });
  D.ambs.forEach(a=>{if(a.mission<0){const e=ambEls[a.id];e.g.setAttribute('transform',`translate(${a.pos[0]+IDLE[0]},${a.pos[1]+IDLE[1]})`);e.fl.setAttribute('transform','scale(1.12,1.12)');
    const c=document.getElementById('c-'+a.id);if(c)cardIdle(a,c);}});
  const hud=$('hud');hud.classList.toggle('active',anyActive);
  $('hud-t').textContent=!M.length?'NO DISPATCH PLAN':anyActive?'🚨 DISPATCH ACTIVE':allDone?'✔ ALL UNITS ARRIVED':started?'DISPATCH PAUSED':'STANDBY';
  $('hud-s').textContent=!M.length?'no ambulance can be assigned':`${M.filter(m=>{const q=phase(m,t);return q===1||q===2;}).length} unit(s) rolling · ${M.length} mission(s) planned`;
  $('clk').textContent='T+ '+t.toFixed(1)+' min';$('scrub').value=t;
  feed();
}
function cardIdle(a,c){const b=c.querySelector('.badge'),r=c.querySelector('.rt');
  if(a.status==='Disabled'){b.className='badge b-off';b.textContent='OUT OF SERVICE';r.textContent='Unavailable – excluded from dispatch';}
  else if(a.status==='Busy'){b.className='badge b-amber';b.textContent='BUSY';r.textContent='On another assignment';}
  else{b.className='badge b-ok';b.textContent='AVAILABLE';r.textContent='Standing by – no assignment';}}
function card(m,i,p,pos){
  const c=document.getElementById('c-'+m.amb);if(!c)return;const b=c.querySelector('.badge');
  const lo=c.querySelector('.lo'),rt=c.querySelector('.rt');
  const eta=Math.max(0,m.scene_time-t),eta2=Math.max(0,m.total-t);
  if(p===0){b.className='badge '+(m.status==='committed'?'b-red':'b-amber');b.textContent=m.status==='committed'?'DISPATCHED':'ASSIGNED';
    lo.textContent=m.names[0]+' (base)';rt.textContent=`Route ready · ${m.names.length-1} roads · ETA ${m.eta.toFixed(1)} min`;}
  else if(p===1){b.className='badge b-red flash';b.textContent='🚨 DISPATCHED';lo.textContent=whereIs(m,pos);rt.textContent=`Driving to scene · ETA ${eta.toFixed(1)} min`;}
  else if(p===2){b.className='badge b-amber';b.textContent='PATIENT ABOARD';lo.textContent=whereIs(m,pos);rt.textContent=`Transporting to ${m.hosp} · ${eta2.toFixed(1)} min left`;}
  else{b.className='badge b-ok';b.textContent='DELIVERED';lo.textContent='at '+m.hosp;rt.textContent=`Mission complete in ${m.total.toFixed(1)} min`;}
}
const events=[];M.forEach(m=>{events.push({t:0,x:`🚨 <b>${m.amb}</b> dispatched to ${m.inc} (${m.loc}, severity ${m.sev})`});
 events.push({t:m.scene_time,x:`🩺 <b>${m.amb}</b> on scene at ${m.loc} – patient loaded`});
 events.push({t:m.total,x:`🏥 <b>${m.amb}</b> delivered ${m.inc} to ${m.hosp}`});});
events.sort((a,b)=>a.t-b.t);
function feed(){const vis=(started||running)?events.filter(e=>e.t<=t+1e-9):[];if(vis.length===lastFeed)return;lastFeed=vis.length;
  $('feed').innerHTML=vis.length?vis.slice().reverse().map(e=>`<div><time>${(e.t).toFixed(1)}</time>${e.x}</div>`).join(''):
  '<div style="color:#8aa0c0">Press <b>Run dispatch</b> to start the simulation.</div>';}

/* ---- controls ---- */
function loop(ts){if(running){if(last!=null){t+=(ts-last)/1000*speed*D.horizon/16;if(t>=D.horizon){t=D.horizon;running=false;$('btn-run').textContent='↻ Replay';}}last=ts;render();}requestAnimationFrame(loop);}
$('btn-run').onclick=()=>{if(!M.length)return;
  if(!started||t>=D.horizon){t=0;lastFeed=-1;started=true;running=true;}else{running=!running;}
  last=null;$('btn-run').textContent=running?'⏸ Pause':'▶ Resume';render();};
$('btn-reset').onclick=()=>{running=false;started=false;t=0;lastFeed=-1;$('btn-run').textContent='🚨 Run dispatch';render();};
$('spd').onchange=e=>{speed=+e.target.value;};
$('scrub').max=D.horizon;$('scrub').oninput=e=>{t=+e.target.value;started=t>0;running=false;lastFeed=-1;$('btn-run').textContent=t>0?'▶ Resume':'🚨 Run dispatch';render();};
document.querySelectorAll('.card').forEach(c=>c.addEventListener('click',()=>{const i=+c.dataset.m;if(i>=0)setFocus(focus===i?-1:i);}));
window.__setTime=v=>{t=v;started=v>0;running=false;lastFeed=-1;render();};
if(D.horizon<=0){$('scrub').disabled=true;}
render();requestAnimationFrame(loop);
})();
"""


# ------------------------------------------------------------ search step-through
SEARCH_CSS = """
.sapp{height:100%;display:flex;flex-direction:column;gap:8px;padding:2px}
.panes{flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.pane{display:flex;flex-direction:column;min-height:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:8px 8px 6px}
.pane svg{flex:1;min-height:0;width:100%}.ph{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;font-size:15px}
.info{font-size:12px;height:178px;overflow-y:auto;line-height:1.5;color:#c3d0e6;padding:4px 6px;background:#0d1628;border-radius:8px;margin-top:4px}
.info b{color:#fff}.info .fr{color:#fcd34d}.info .mut{color:#8aa0c0}.info .ok{color:#86efac}.info .no{color:#94a3b8}
.info .ed{padding:1px 0 1px 8px;border-left:3px solid #334155;margin:2px 0}.info .ed.y{border-left-color:#f59e0b}
.key{display:flex;gap:6px 16px;flex-wrap:wrap;color:#b6c4dc;font-size:11.5px}.key span{display:flex;align-items:center;gap:6px}
.cur{animation:pls 1s ease-in-out infinite}
.goalline{stroke-dasharray:14 9;animation:flow 1s linear infinite}
"""

SEARCH_JS = r"""
(function(){
const D=JSON.parse(document.getElementById('data').textContent);
const NS="http://www.w3.org/2000/svg",$=id=>document.getElementById(id);
const el=(t,a,p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;};
const P=D.pos,H=new Set(D.hosp),maxK=Math.max(1,...D.algos.map(a=>a.steps.length));
let k=0,timer=null;
const pstr=p=>p.map(n=>P[n][0]+','+P[n][1]).join(' ');
const f1=v=>Number(v).toFixed(1);
const ekey=(a,b)=>[a,b].sort().join('|');
function state(al,k){
  const kk=Math.min(k,al.steps.length),closed=[],parent={};
  for(let i=0;i<kk;i++){const s=al.steps[i];closed.push(s.node);s.relaxed.forEach(r=>parent[r]=s.node);}
  const cur=kk>0?al.steps[kk-1]:null;
  const frontier=kk>0?cur.frontier:[{node:D.start,g:0,f:(al.h[D.start]||0)}];
  return{kk,closed,parent,cur,frontier,done:kk===al.steps.length};
}
/* road costs (minutes) drawn on top of the search tree; roads looked at in this step are outlined */
function weights(ov,S){
  const hl={};
  if(S.cur&&S.cur.edges)S.cur.edges.forEach(e=>hl[ekey(S.cur.node,e.to)]=e.status);
  D.roads.forEach(r=>{
    const a=P[r.a],b=P[r.b],st=hl[ekey(r.a,r.b)];
    const ring=(st==='new'||st==='better')?'#f59e0b':st?'#94a3b8':'#64748b';
    const fill=r.mult>1?(r.mult<2?'#b45309':r.mult<3.5?'#c2410c':'#b91c1c'):'#1e293b';
    const g=el('g',{transform:`translate(${(a[0]+b[0])/2},${(a[1]+b[1])/2})`},ov);
    el('rect',{x:-20,y:-11,width:40,height:22,rx:11,fill:fill,stroke:ring,'stroke-width':st?3.4:1.3},g);
    el('text',{y:4.6,'text-anchor':'middle','font-size':12,'font-weight':800,fill:'#fff'},g).textContent=f1(r.cost);
  });
}
function nodeLabel(ov,x,y,txt,col){
  const g=el('text',{x:x,y:y,'text-anchor':'middle',class:'tag',fill:col,'font-size':11.5},ov);g.textContent=txt;
}
function draw(al){
  const root=$('p-'+al.key),ov=root.querySelector('.ov'),S=state(al,k),A=al.key==='astar',hv=n=>al.h[n]||0;ov.innerHTML='';
  const route=al.route,onRoute=new Set();
  if(S.done)route.forEach(n=>onRoute.add(n));
  for(const n in S.parent){const a=P[S.parent[n]],b=P[n];
    el('line',{x1:a[0],y1:a[1],x2:b[0],y2:b[1],stroke:'#38bdf8','stroke-width':5,opacity:.75,'stroke-linecap':'round'},ov);}
  if(S.done&&route.length>1){
    el('polyline',{points:pstr(route),fill:'none',stroke:'#22c55e','stroke-width':20,opacity:.28,'stroke-linecap':'round','stroke-linejoin':'round'},ov);
    el('polyline',{points:pstr(route),fill:'none',stroke:'#4ade80','stroke-width':8,'stroke-linecap':'round','stroke-linejoin':'round'},ov);
    el('polyline',{points:pstr(route),fill:'none',stroke:'#fff','stroke-width':2.4,class:'goalline','stroke-linecap':'round','stroke-linejoin':'round'},ov);}
  weights(ov,S);
  const fset={};S.frontier.forEach(f=>fset[f.node]=f);
  Object.keys(P).forEach(n=>{
    const [x,y]=P[n],h=H.has(n),r=h?40:19,isCur=S.cur&&S.cur.node===n,ci=S.closed.indexOf(n);
    if(A&&n!==D.goal)nodeLabel(ov,x,y+(h?68:41),'h='+f1(hv(n)),'#7dd3fc');   /* straight-line estimate, fixed per node */
    if(ci>=0){
      el('circle',{cx:x,cy:y,r:r,fill:'rgba(59,130,246,.42)',stroke:onRoute.has(n)?'#4ade80':'#3b82f6','stroke-width':onRoute.has(n)?5:3.5},ov);
      const bx=x+(h?32:17),by=y-(h?32:17);el('circle',{cx:bx,cy:by,r:11,fill:'#1d4ed8',stroke:'#fff','stroke-width':1.8},ov);
      el('text',{x:bx,y:by+4,'text-anchor':'middle','font-size':12,'font-weight':800,fill:'#fff'},ov).textContent=ci+1;
      const st=al.steps[ci];
      nodeLabel(ov,x,y-(h?48:27),A?`g=${f1(st.g)}  f=${f1(st.f)}`:`g=${f1(st.g)}`,'#93c5fd');
    }
    if(fset[n]&&ci<0){
      el('circle',{cx:x,cy:y,r:r,fill:'rgba(245,158,11,.22)',stroke:'#f59e0b','stroke-width':3.5,'stroke-dasharray':'6 4'},ov);
      const f=fset[n];
      nodeLabel(ov,x,y-(h?48:27),A?`g=${f1(f.g)}  f=${f1(f.f)}`:`g=${f1(f.g)}`,'#fcd34d');}
    if(isCur&&!S.done)el('circle',{cx:x,cy:y,r:r+5,fill:'none',stroke:'#fff','stroke-width':4.5,class:'cur'},ov);
    if(n===D.start){el('circle',{cx:x-(h?32:17),cy:y-(h?32:17),r:11,fill:'#16a34a',stroke:'#fff','stroke-width':2},ov);
      el('text',{x:x-(h?32:17),y:y-(h?32:17)+4.5,'text-anchor':'middle','font-size':12,'font-weight':800,fill:'#fff'},ov).textContent='S';}
    if(n===D.goal){el('circle',{cx:x-(h?32:17),cy:y+(h?32:17),r:11,fill:'#dc2626',stroke:'#fff','stroke-width':2},ov);
      el('text',{x:x-(h?32:17),y:y+(h?32:17)+4.5,'text-anchor':'middle','font-size':12,'font-weight':800,fill:'#fff'},ov).textContent='G';}
  });
  explain(al,S);
}
/* plain-language description of the step, built only from the recorded trace */
function explain(al,S){
  const A=al.key==='astar',info=$('in-'+al.key),st=$('st-'+al.key),hv=n=>al.h[n]||0,key=A?'f':'g';
  const fl=S.frontier.slice(0,5).map(f=>A?`${f.node} <span class="fr">g ${f1(f.g)} + h ${f1(f.f-f.g)} = f ${f1(f.f)}</span>`
        :`${f.node} <span class="fr">g ${f1(f.g)}</span>`).join(' · ')||'empty';
  if(S.done){
    st.className=al.route.length?'badge b-ok':'badge b-off';st.textContent=al.route.length?'DONE':'NO ROUTE';
    info.innerHTML=al.route.length
      ?`<b class="ok">✔ Goal reached after exploring ${al.explored} nodes.</b><br>Route: <b>${al.route.join(' → ')}</b><br>`+
       `Cost: ${al.legs.map(f1).join(' + ')} = <b>${f1(al.cost)} min</b><br><span class="mut">Average run time ${al.time_ms.toFixed(4)} ms</span>`
      :`<b>No open road connects ${D.start} and ${D.goal}.</b> The search explored ${al.explored} nodes and ran out of candidates.`;
    return;}
  if(S.kk===0){st.className='badge b-off';st.textContent='READY';
    info.innerHTML=`Start: <b>${D.start}</b> is the only node waiting (g=0${A?`, h=${f1(hv(D.start))}`:''}).<br>`+
      `<span class="mut">Each step expands the waiting node with the lowest ${key}${A?' (cost so far + straight-line estimate)':' (cost so far)'}.</span>`;return;}
  st.className='badge b-amber';st.textContent='SEARCHING';
  const s=S.cur,i=S.kk-1,prev=i>0?al.steps[i-1].frontier:[{node:D.start,g:0,f:hv(D.start)}];
  const rival=prev.filter(f=>f.node!==s.node)[0];
  let t=`<b>Step ${S.kk}: expand ${s.node}</b> · g ${f1(s.g)}`+(A?` + h ${f1(s.h)} = <b>f ${f1(s.f)}</b>`:'')+'<br>';
  t+=`<span class="mut">Chosen because it has the lowest ${key} among the waiting nodes`+
     (rival?` (next best: ${rival.node} with ${key} ${f1(A?rival.f:rival.g)})`:' (it was the only one)')+'.</span><br>';
  if(s.node===D.goal)t+='<b class="ok">This is the goal, so the search stops.</b>';
  else if(!s.edges.length)t+='<span class="mut">No open road leaves this node.</span>';
  else s.edges.forEach(e=>{
    const calc=`${f1(s.g)} + ${f1(e.w)} = <b>${f1(e.new_g)}</b>`;
    let res;
    if(e.status==='new')res=`<span class="ok">✔ first path found${A?`, f = ${f1(e.new_g)} + h ${f1(e.h)} = ${f1(e.new_g+e.h)}`:''}</span>`;
    else if(e.status==='better')res=`<span class="ok">✔ cheaper than ${f1(e.old_g)}, update${A?`, f = ${f1(e.new_g+e.h)}`:''}</span>`;
    else if(e.status==='closed')res='<span class="no">✖ already explored</span>';
    else res=`<span class="no">✖ not better than ${f1(e.old_g)}, keep old</span>`;
    t+=`<div class="ed ${e.status==='new'||e.status==='better'?'y':''}">via road to <b>${e.to}</b> (${f1(e.w)} min): ${calc} ${res}</div>`;});
  t+=`<div style="margin-top:3px"><span class="mut">Waiting now (best first):</span> ${fl}</div>`;
  info.innerHTML=t;
}
function render(){D.algos.forEach(draw);$('s-scrub').value=k;$('s-step').textContent=`Step ${k} / ${maxK}`;}
function stop(){if(timer){clearInterval(timer);timer=null;}$('s-play').textContent=k>=maxK?'↻ Replay':'▶ Play search';}
function play(){if(timer){stop();return;}if(k>=maxK)k=0;$('s-play').textContent='⏸ Pause';
  timer=setInterval(()=>{if(k>=maxK){stop();return;}k++;render();if(k>=maxK)stop();},+$('s-spd').value);render();}
$('s-play').onclick=play;$('s-fwd').onclick=()=>{stop();k=Math.min(maxK,k+1);render();stop();};
$('s-back').onclick=()=>{stop();k=Math.max(0,k-1);render();stop();};$('s-reset').onclick=()=>{stop();k=0;render();stop();};
$('s-spd').onchange=()=>{if(timer){stop();play();}};
$('s-scrub').max=maxK;$('s-scrub').oninput=e=>{stop();k=+e.target.value;render();stop();};
window.__setStep=v=>{k=v;render();};
render();
})();
"""

# ------------------------------------------------------------ decision tree replay
TREE_CSS = """
html,body{overflow:auto}.tapp{padding:2px 6px 14px;display:flex;flex-direction:column;gap:10px}
.tbox{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:8px 12px}
.th2{display:flex;gap:18px;align-items:center;flex-wrap:wrap;font-size:13px;margin-bottom:2px}
.th2 b:first-child{font-size:15px}.th2 span{color:#b6c4dc}.note{color:#8aa0c0;font-size:12px;flex:1}
.th{font-size:11.5px;font-weight:600;paint-order:stroke;stroke:#111a2e;stroke-width:5px;stroke-linejoin:round}
.seq{transition:opacity .35s}.pr.flash path,.pr.flash circle{stroke:#fff}
"""

TREE_JS = r"""
(function(){
const els=[...document.querySelectorAll('.seq')],btn=document.getElementById('t-replay');
const mx=Math.max(0,...els.map(e=>+e.dataset.seq||0));let timer=null;
btn.onclick=()=>{if(timer){clearInterval(timer);timer=null;}
  els.forEach(e=>e.style.opacity=0);let s=0;btn.textContent='⏳ Searching…';
  timer=setInterval(()=>{s++;els.filter(e=>+e.dataset.seq===s).forEach(e=>{e.style.opacity=1;
    if(e.classList.contains('pr')){e.classList.add('flash');setTimeout(()=>e.classList.remove('flash'),500);}});
    if(s>=mx){clearInterval(timer);timer=null;btn.textContent='↻ Replay search order';}},320);};
})();
"""
