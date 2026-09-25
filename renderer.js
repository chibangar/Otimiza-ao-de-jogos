// Bridge: suporta Electron (midnightAPI) e Python pywebview (nativo Windows)
async function getBackend(){
  if (window.midnightAPI) return window.midnightAPI;
  // espera pywebview injetar
  for(let i=0;i<50;i++){
    if(window.pywebview && window.pywebview.api){ break; }
    await new Promise(r=>setTimeout(r,100));
  }
  if(window.pywebview && window.pywebview.api){
    const a = window.pywebview.api;
    window.midnightAPI = {
      getSystemInfo: ()=>a.get_system_info(),
      getPerf: ()=>a.get_perf(),
      winMin: ()=>a.window_minimize(),
      winMax: ()=>a.window_toggle_maximize(),
      winClose: ()=>a.window_close(),
      powerHigh: ()=>a.power_high(),
      powerBalanced: ()=>a.power_balanced(),
      gameMode: (e)=>a.game_mode(e),
      gameBar: (d)=>a.game_bar(d),
      cleanTemp: ()=>a.clean_temp(),
      network: ()=>a.network(),
      visualEffects: (p)=>a.visual_effects(p),
      killBackground: ()=>a.kill_background(),
      gpuPriority: ()=>a.gpu_priority(),
      privacyOn: ()=>a.privacy_on(),
      privacyOff: ()=>a.privacy_off(),
      privacyExtra: (e)=>e ? a.privacy_extra_on() : a.privacy_extra_off(),
      servicesGaming: (e)=>e ? a.services_gaming_on() : a.services_gaming_off(),
      schedTasks: (e)=>e ? a.sched_tasks_off() : a.sched_tasks_on(),
      updatesManual: (e)=>e ? a.updates_manual_on() : a.updates_manual_off(),
      soundTweaks: (e)=>e ? a.sound_tweaks_on() : a.sound_tweaks_off(),
      winNotify: (e)=>e ? a.win_notify_on() : a.win_notify_off(),
      customize: (e)=>e ? a.customize_on() : a.customize_off(),
      powerExtra: (e)=>e ? a.power_extra_on() : a.power_extra_off(),
      perfExtra: (e)=>e ? a.perf_extra_on() : a.perf_extra_off(),
      gamingExtra: (e)=>e ? a.gaming_extra_on() : a.gaming_extra_off(),
      systemExtra: (e)=>e ? a.system_extra_on() : a.system_extra_off(),
      debloat: ()=>a.debloat(),
      analyzePc: ()=>a.analyze_pc(),
      competitiveOn: ()=>a.competitive_on(),
      competitiveOff: ()=>a.competitive_off(),
      launchGame: (p)=>a.launch_game(p),
      pickGameFile: ()=>a.pick_game_file(),
      detectGames: ()=>a.detect_games(),
      cs2Competitive: ()=>a.cs2_competitive(),
      cs2Restore: ()=>a.cs2_restore(),
      cs2Launch: ()=>a.cs2_launch_options(),
      cs2HitregFix: ()=>a.cs2_hitreg_fix(),
      testOverlay: ()=>a.test_in_game_overlay(),
      pickCs2Folder: ()=>a.pick_cs2_folder(),
      killCs2: ()=>a.kill_cs2(),
      wowCompetitive: ()=>a.wow_competitive(),
      wowBalanced: ()=>a.wow_balanced(),
      wowRestore: ()=>a.wow_restore(),
      listPros: ()=>a.list_pros(),
      listCrosshairs: ()=>a.list_crosshairs(),
      listViewmodels: ()=>a.list_viewmodels(),
      applyCrosshair: (id)=>a.apply_crosshair(id),
      applyViewmodel: (id)=>a.apply_viewmodel(id),
      applyPro: (id)=>a.apply_pro(id),
      checkUpdate: ()=>a.check_update(),
      startUpdate: ()=>a.start_update(),
      updateProgress: ()=>a.update_progress(),
      applyUpdate: ()=>a.apply_update_and_restart(),
      updateLastResult: ()=>a.update_last_result(),
      voiceEffects: ()=>a.voice_effects(),
      voiceDevices: ()=>a.voice_devices(),
      voiceStart: (e,i,o,g)=>a.voice_start(e,i,o,g),
      voiceStop: ()=>a.voice_stop(),
      monitorStart: (e,i,m,g)=>a.monitor_start(e,i,m,g),
      monitorStop: ()=>a.monitor_stop(),
      voiceRecStart: (i)=>a.voice_record_start(i),
      voiceRecStop: (e,o,g)=>a.voice_record_stop(e,o,g),
      voiceReplay: (o)=>a.voice_replay(o),
      soundboardList: ()=>a.soundboard_list(),
      soundboardPlay: (id,o)=>a.soundboard_play(id,o),
      soundboardStop: ()=>a.soundboard_stop(),
      soundboardAdd: ()=>a.soundboard_add(),
      soundboardRemove: (id)=>a.soundboard_remove(id),
      usersList: ()=>a.users_list(),
      accountRegister: (u,p)=>a.account_register(u,p),
      accountLogin: (u,p)=>a.account_login(u,p),
      accountLogout: ()=>a.account_logout(),
      whoami: ()=>a.whoami(),
      sessionResume: ()=>a.session_resume(),
      sessionForget: ()=>a.session_forget(),
      openUrl: (u)=>a.open_url(u),
      openReleasesPage: ()=>a.open_releases_page(),
      isAdmin: ()=>a.is_admin(),
      restartAsAdmin: ()=>a.restart_as_admin(),
      autostartGet: ()=>a.autostart_get(),
      autostartSet: (e)=>a.autostart_set(e),
      serversList: ()=>a.servers_list(),
      serversRefresh: ()=>a.servers_refresh(),
      serversHistory: ()=>a.servers_history(),
      serverConnect: (ip,port)=>a.server_connect(ip,port),
      onlineStart: ()=>a.online_start(),
      onlineStop: ()=>a.online_stop(),
      onlineState: ()=>a.online_state(),
      lobbySend: (t)=>a.chat_lobby_send(t),
      lobbyFetch: (n)=>a.chat_lobby_fetch(n),
      dmSend: (p,t)=>a.chat_dm_send(p,t),
      dmFetch: (p,n)=>a.chat_dm_fetch(p,n),
      dmThreads: ()=>a.chat_dm_threads(),
      oauthStatus: ()=>a.oauth_status(),
      oauthGoogle: ()=>a.oauth_google(),
      oauthDiscord: ()=>a.oauth_discord(),
      oauthSaveDiscord: (id,sec)=>a.oauth_save_discord(id,sec),
      hotkeySet: (m)=>a.hotkey_set(m),
      hotkeyClear: ()=>a.hotkey_clear(),
      logError: (m)=>a.log_error(m),
      audioBrand: ()=>a.audio_brand_virtual(),
      audioRestart: ()=>a.audio_restart_service(),
      appVersion: ()=>a.app_version(),
      getNews: ()=>a.get_news(),
      bugsList: ()=>a.bugs_list(),
      bugsAdd: (t)=>a.bugs_add(t),
      bugsClear: ()=>a.bugs_clear(),
    };
    return window.midnightAPI;
  }
  return null;
}
// Navegação
const navBtns = document.querySelectorAll('.nav-btn');
const pages = document.querySelectorAll('.page');
const titles = { dashboard:['Dashboard','Visão geral da tua máquina de batalha.'], competitivo:['Modo Competitivo','Um clique para entrar em modo de guerra.'], ingame:['In-Game CS2 & WoW','Otimização dentro do próprio jogo, com backup.'], servers:['Servidores','Públicos PT/EU para entrar em 1 clique.'], online:['Online','Vê quem está na app e conversa em direto.'], voz:['Estúdio de Voz','Muda a tua voz como no Voicemod.'], sound:['Soundboard','Memes do myinstants com teclas de atalho.'], otimizacoes:['Otimizações Windows','Ativa cada runa de poder do sistema.'], jogos:['Meus Jogos','Lança com prioridade alta e boost.'], sistema:['Sistema','Ficha arcana da tua máquina.'], bugs:['Chat de Bugs','Reporta bugs e vê os já registados.'] };
navBtns.forEach(b=>b.addEventListener('click',()=>go(b.dataset.page)));
function go(page){ navBtns.forEach(b=>b.classList.toggle('active',b.dataset.page===page));
  pages.forEach(p=>p.classList.toggle('active',p.id==='page-'+page));
  try{
    const t=titles[page]||['Midnight Optimizer',''];
    document.title=t[0]+' — Midnight Optimizer';
    const h=document.getElementById('page-title'), d=document.getElementById('page-desc');
    if(h) h.textContent=t[0];
    if(d) d.textContent=t[1];
    document.dispatchEvent(new CustomEvent('midnight:navigate', { detail: { page } }));
  }catch{}
}
document.querySelectorAll('[data-goto]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.goto)));

function toast(msg){
  const t = document.getElementById('toast');
  if(!t) return;
  t.textContent = msg;
  t.classList.remove('hide');
  t.classList.add('show');
  clearTimeout(t._h);
  t._h = setTimeout(()=>{
    t.classList.remove('show');
    t.classList.add('hide');
    setTimeout(()=>t.classList.remove('hide'), 220);
  }, 3400);
}
function withTimeout(p, ms, label){
  return Promise.race([p, new Promise((_,rej)=>setTimeout(()=>rej(new Error('timeout '+ms+'ms em '+label)), ms))]);
}
function log(msg){ const el=document.getElementById('log'); el.textContent += '\n'+msg; el.scrollTop=el.scrollHeight; }

// Versão da app (sidebar + página Sistema)
async function refreshVersion(){
  try{
    if(!window.midnightAPI || !window.midnightAPI.appVersion) return;
    const r=await withTimeout(window.midnightAPI.appVersion(), 10000, 'appVersion');
    const v=(r && r.version) || '?';
    const sb=document.getElementById('app-version');
    if(sb) sb.textContent=`Midnight Optimizer • v${v}`;
    const sv=document.getElementById('sys-version');
    if(sv) sv.textContent='v'+v;
  }catch{}
}

// Sistema + gauges do dashboard (dados 100% reais)
function shortGpu(name){
  const m=(name||'').match(/RTX\s*\d+|GTX\s*\d+|RX\s*[\w ]+|Radeon[^\|]*/i);
  return (m?m[0]:name||'GPU').trim().slice(0,22);
}
function setGauge(id, pct){
  const el=document.getElementById(id); if(!el) return;
  const c=326.7, p=Math.max(0,Math.min(100,pct||0));
  el.style.strokeDashoffset=(c-(c*p/100)).toFixed(1);
}
let _sysCache=null;
async function refreshSystem(){
  if(!window.midnightAPI) return;
  try{
    const info = await withTimeout(window.midnightAPI.getSystemInfo(), 30000, 'getSystemInfo');
    _sysCache=info;
    const set=(id,v)=>{ const e=document.getElementById(id); if(e) e.textContent=v; };
    set('sys2-cpu', (info.cpu||'CPU').slice(0,48));
    set('sys2-gpu', (info.gpu||'GPU').split('|').map(s=>s.trim()).filter(Boolean).slice(-1)[0]?.slice(0,48) || 'GPU');
    set('sys2-ram', `${info.ramTotal} GB`);
    set('sys2-os', `${info.os} ${info.hostname?'• '+info.hostname:''}`.slice(0,64));
    set('sys2-board', (info.motherboard||'—').slice(0,48));
    set('sys-os',info.os); set('sys-cpu',info.cpu);
    set('sys-gpu',info.gpu); set('sys-ram',info.ramTotal+' GB');
    set('sys-power',(info.power||'').slice(0,120)); set('sys-host',info.hostname);
    set('sys-board',info.motherboard||'—');
    await refreshPerf();
  }catch(e){ try{ await window.midnightAPI.logError('refreshSystem: '+(e&&e.stack||e)); }catch{} }
  try{
    const adm=await window.midnightAPI.isAdmin();
    const el=document.getElementById('sys-admin');
    if(el){ el.textContent=adm.admin?'Sim ✔':'Não — prime o botão para poder total'; el.style.color=adm.admin?'#34c98e':'#e5a83c'; }
    const hint=document.getElementById('admin-hint');
    if(hint) hint.innerHTML=adm.admin?'A correr como <b>Administrador</b> ✔':'Executa como <b>Administrador</b> para poder total.';
  }catch{}
}
async function refreshPerf(){
  if(!window.midnightAPI || !window.midnightAPI.getPerf) return;
  try{
    const p=await withTimeout(window.midnightAPI.getPerf(), 15000, 'getPerf');
    const set=(id,v)=>{ const e=document.getElementById(id); if(e) e.textContent=v; };
    if(p.cpuPct!==null && p.cpuPct!==undefined){ set('g-cpu-pct',p.cpuPct+'%'); setGauge('g-cpu-ring',p.cpuPct); }
    else { set('g-cpu-pct','–'); }
    set('g-cpu-sub', p.cpuGHz? p.cpuGHz.toFixed(1)+' GHz' : ((_sysCache&&_sysCache.cpu)||'CPU').split('@')[0].slice(0,26));
    const gpuName=_sysCache? shortGpu((_sysCache.gpu||'').split('|').map(s=>s.trim()).filter(Boolean).slice(-1)[0]||'GPU') : 'GPU';
    if(p.gpuPct!==null && p.gpuPct!==undefined){ set('g-gpu-pct',p.gpuPct+'%'); setGauge('g-gpu-ring',p.gpuPct); }
    else { set('g-gpu-pct','–'); setGauge('g-gpu-ring',0); }
    set('g-gpu-sub', gpuName);
    if(p.ramPct!==null && p.ramPct!==undefined){ set('g-ram-pct',p.ramPct+'%'); setGauge('g-ram-ring',p.ramPct); }
    if(p.ramUsed!==null && p.ramUsed!==undefined) set('g-ram-sub',`${p.ramUsed} / ${p.ramTotal} GB`);
    if(p.diskPct!==null && p.diskPct!==undefined){ set('g-disk-pct',p.diskPct+'%'); setGauge('g-disk-ring',p.diskPct); }
    if(p.diskUsed!==null && p.diskUsed!==undefined) set('g-disk-sub',`${p.diskUsed} / ${p.diskTotal} GB`);
  }catch(e){ /* mantém últimos valores */ }
}

// Competitivo
let competitive=false;
async function setCompetitive(on){
  const pill=document.getElementById('status-pill'), txt=document.getElementById('status-text');
  const big=document.getElementById('big-toggle'), lbl=document.getElementById('comp-state-label');
  const list=document.getElementById('comp-log');
  if(on){
    toast('A ativar Modo Competitivo…'); if(list) list.innerHTML='<li>A aplicar…</li>';
    const r=await window.midnightAPI.competitiveOn();
    competitive=true; if(list) list.innerHTML=r.output.split('\n').map(l=>`<li>${l}</li>`).join('');
    if(pill) pill.className='status-pill war'; if(txt) txt.textContent='Modo Competitivo ATIVO';
    if(big) big.classList.add('active'); if(lbl){ lbl.textContent='EM GUERRA'; lbl.style.color='#ff9d5c'; }
    setCompetitiveUI(true); histAdd('✓','Perfil Competitivo ativado');
    log('COMPETITIVO ATIVO:\n'+r.output); toast('Modo Competitivo ATIVO. Boa ranked!');
  } else {
    const r=await window.midnightAPI.competitiveOff();
    competitive=false; if(list) list.innerHTML=r.output.split('\n').map(l=>`<li>${l}</li>`).join('');
    if(pill) pill.className='status-pill normal'; if(txt) txt.textContent='Modo Normal';
    if(big) big.classList.remove('active'); if(lbl){ lbl.textContent='DESATIVADO'; lbl.style.color=''; }
    setCompetitiveUI(false); histAdd('○','Perfil Normal restaurado');
    log('Modo normal restaurado.'); toast('Modo normal restaurado.');
  }
}
document.getElementById('btn-comp-on').addEventListener('click',()=>setCompetitive(true));
document.getElementById('btn-comp-off').addEventListener('click',()=>setCompetitive(false));
document.getElementById('big-toggle').addEventListener('click',()=>setCompetitive(!competitive));
document.getElementById('btn-qa-perfil')?.addEventListener('click',()=>setCompetitive(!competitive));
document.getElementById('btn-profile-change')?.addEventListener('click',()=>setCompetitive(!competitive));
document.getElementById('pm-toggle')?.addEventListener('click',()=>{ document.getElementById('profile-menu').style.display='none'; setCompetitive(!competitive); });
document.getElementById('pm-goto')?.addEventListener('click',()=>{ document.getElementById('profile-menu').style.display='none'; go('competitivo'); });
document.getElementById('btn-profile-menu')?.addEventListener('click',(e)=>{ e.stopPropagation(); const m=document.getElementById('profile-menu'); m.style.display=m.style.display==='none'?'':'none'; });
document.addEventListener('click',()=>{ const m=document.getElementById('profile-menu'); if(m) m.style.display='none'; });
document.getElementById('btn-hist-toggle')?.addEventListener('click',()=>{ toast(histLoad().length+' ações no histórico desta conta.'); });

// ---------- DIAGNÓSTICO: melhor otimização para ESTE pc (popout animado) ----------
const DIAG_ACTIONS={
  power:{run:()=>midnightAPI.powerHigh(),sw:'power',msg:'Energia máxima ativada! ⚡'},
  gamemode:{run:()=>midnightAPI.gameMode(true),sw:'gamemode',msg:'Modo Jogo ligado! 🎮'},
  gamebar:{run:()=>midnightAPI.gameBar(true),sw:'gamebar',msg:'DVR desligado, FPS livre! 📼'},
  visual:{run:()=>midnightAPI.visualEffects(true),sw:'visual',msg:'Efeitos em desempenho! ✨'},
  gpu:{run:()=>midnightAPI.gpuPriority(),sw:'gpu',msg:'GPU priorizada! 🖥️'},
  kill:{run:()=>midnightAPI.killBackground(),msg:'Background limpo! 🧹'},
  temp:{run:()=>midnightAPI.cleanTemp(),msg:'Disco limpo! 🧺'},
  net:{run:()=>midnightAPI.network(),msg:'Rede otimizada! 🌐'},
};
async function runDiagAction(action){
  const d=DIAG_ACTIONS[action];
  if(!d) return {success:false};
  const r=await d.run();
  if(r && r.success!==false){
    if(d.sw) document.querySelector(`.switch[data-action="${d.sw}"]`)?.classList.add('on');
    histAdd('✓',d.msg);
    log('🔍 '+(r.output||d.msg));
  }
  return r||{success:true};
}
function renderDiag(data){
  const ov=document.getElementById('diag-overlay'), list=document.getElementById('diag-list');
  document.getElementById('diag-score').textContent=(data.score??'–');
  document.getElementById('diag-verdict').textContent=data.verdict||'';
  document.getElementById('diag-specs').textContent=data.specs||'';
  list.innerHTML='';
  const recs=data.recs||[];
  if(!recs.length){
    list.innerHTML='<div class="diag-item" style="animation-delay:.1s"><span class="diag-ico">🏆</span><div class="diag-info"><b>Nada a fazer!</b><p>O teu PC já está no ponto. Boa ranked! ⚔</p></div></div>';
  }
  recs.forEach((rc,i)=>{
    const el=document.createElement('div');
    el.className='diag-item'; el.style.animationDelay=(0.08+i*0.12)+'s';
    el.innerHTML=`<span class="diag-ico">${rc.icon||'🔧'}</span>
      <div class="diag-info"><b>${rc.title} <span class="diag-badge ${rc.impact==='ALTO'?'alto':'medio'}">${rc.impact}</span></b><p>${rc.reason}</p></div>
      <button class="btn gold small diag-apply">Aplicar</button>`;
    el.querySelector('.diag-apply').addEventListener('click',async(ev)=>{
      const btn=ev.target; btn.disabled=true; btn.textContent='A aplicar…';
      const r=await runDiagAction(rc.action);
      if(r.success!==false){ el.classList.add('done'); btn.textContent='✔'; toast(DIAG_ACTIONS[rc.action]?.msg||'Aplicado!'); }
      else { btn.disabled=false; btn.textContent='Aplicar'; toast('Falha: '+(r.output||'tenta como Administrador')); }
    });
    list.appendChild(el);
  });
  document.getElementById('btn-diag-all').style.display=recs.length?'':'none';
  ov.style.display='flex';
}
async function openDiag(){
  const ov=document.getElementById('diag-overlay'), list=document.getElementById('diag-list');
  ov.style.display='flex';
  document.getElementById('diag-score').textContent='…';
  document.getElementById('diag-verdict').textContent='A ler o teu PC (energia, registo, RAM, disco)…';
  document.getElementById('diag-specs').textContent='';
  list.innerHTML='<div class="diag-item" style="animation-delay:.05s"><span class="diag-ico">⏳</span><div class="diag-info"><b>A analisar…</b><p>Isto demora uns segundos.</p></div></div>';
  try{
    const data=await withTimeout(window.midnightAPI.analyzePc(),120000,'analyzePc');
    if(data && data.success) renderDiag(data);
    else { document.getElementById('diag-verdict').textContent='Falha: '+((data&&data.output)||'tenta outra vez'); list.innerHTML=''; }
  }catch(e){ document.getElementById('diag-verdict').textContent='Falha: '+e.message; list.innerHTML=''; }
}
document.getElementById('btn-diag')?.addEventListener('click',openDiag);
document.getElementById('btn-diag-close')?.addEventListener('click',()=>{ document.getElementById('diag-overlay').style.display='none'; });
document.getElementById('btn-diag-later')?.addEventListener('click',()=>{ document.getElementById('diag-overlay').style.display='none'; });
document.getElementById('diag-overlay')?.addEventListener('click',(e)=>{ if(e.target.id==='diag-overlay') e.target.style.display='none'; });
document.getElementById('btn-diag-all')?.addEventListener('click',async()=>{
  const btn=document.getElementById('btn-diag-all'); btn.disabled=true; btn.textContent='A aplicar…';
  const items=[...document.querySelectorAll('#diag-list .diag-item:not(.done)')];
  for(const el of items){
    const b=el.querySelector('.diag-apply');
    if(b) b.click();
    await new Promise(r=>setTimeout(r,900));
  }
  btn.disabled=false; btn.textContent='⚔ Aplicar tudo';
  toast('Tudo aplicado! Volta a analisar para confirmar. 🎯');
});

// ---------- DASHBOARD: perfil, histórico, pesquisa, janelas ----------
function setCompetitiveUI(on){
  const pn=document.getElementById('profile-name'), pd=document.getElementById('profile-desc');
  if(pn) pn.textContent = on ? 'Modo Competitivo' : 'Modo Normal';
  if(pd) pd.textContent = on ? 'Desempenho máximo para jogos competitivos.' : 'Equilíbrio entre desempenho e conforto.';
  const bq=document.getElementById('btn-qa-perfil');
  if(bq) bq.textContent = on ? 'Desativar' : 'Otimizar Agora';
  const bh=document.getElementById('btn-profile-change');
  if(bh) bh.textContent = on ? 'Desativar Perfil' : 'Alterar Perfil';
}
// Histórico real de ações (persistente, por conta)
function histLoad(){ try{ return JSON.parse(localStorage.getItem(LS('history'))||'[]'); }catch{ return []; } }
function histSave(h){ try{ localStorage.setItem(LS('history'), JSON.stringify(h.slice(-30))); }catch{} }
function histAdd(icon, text){
  const h=histLoad();
  const now=new Date();
  const hh=String(now.getHours()).padStart(2,'0'), mm=String(now.getMinutes()).padStart(2,'0');
  h.push({t:`${hh}:${mm}`, icon, text});
  histSave(h); renderHistory();
}
function renderHistory(){
  const box=document.getElementById('opt-history'); if(!box) return;
  const h=histLoad().slice(-8).reverse();
  if(!h.length){ box.innerHTML='<p class="muted small">Ainda sem ações registadas.</p>'; return; }
  box.innerHTML='';
  h.forEach(e=>{
    const d=document.createElement('div'); d.className='hist-item';
    const t=document.createElement('span'); t.className='hist-time'; t.textContent=e.t;
    const i=document.createElement('span'); i.className='hist-ico'; i.textContent=e.icon;
    const p=document.createElement('span'); p.textContent=e.text;
    d.appendChild(t); d.appendChild(i); d.appendChild(p);
    box.appendChild(d);
  });
  const nl=document.getElementById('notif-list');
  if(nl){ nl.innerHTML=''; h.slice(0,5).forEach(e=>{
    const d=document.createElement('div'); d.className='hist-item';
    d.innerHTML=''; const t=document.createElement('span'); t.className='hist-time'; t.textContent=e.t;
    const p=document.createElement('span'); p.textContent=e.icon+' '+e.text;
    d.appendChild(t); d.appendChild(p); nl.appendChild(d); }); }
}

// Switches individuais
document.querySelectorAll('.switch').forEach(sw=>{
  sw.addEventListener('click', async ()=>{
    const action=sw.dataset.action; const willOn=!sw.classList.contains('on');
    sw.classList.toggle('on', willOn);
    let r={output:'OK'};
    if(action==='power') r = willOn ? await midnightAPI.powerHigh() : await midnightAPI.powerBalanced();
    if(action==='gamemode') r = await midnightAPI.gameMode(willOn);
    if(action==='gamebar') r = await midnightAPI.gameBar(willOn); // on = desativado
    if(action==='visual') r = await midnightAPI.visualEffects(willOn);
    if(action==='gpu') r = await midnightAPI.gpuPriority();
    if(action==='privacy') r = willOn ? await midnightAPI.privacyOn() : await midnightAPI.privacyOff();
    if(action==='privacyx') r = willOn ? await midnightAPI.privacyExtra(true) : await midnightAPI.privacyExtra(false);
    if(action==='services') r = willOn ? await midnightAPI.servicesGaming(true) : await midnightAPI.servicesGaming(false);
    if(action==='schedtasks') r = willOn ? await midnightAPI.schedTasks(true) : await midnightAPI.schedTasks(false);
    if(action==='updates') r = willOn ? await midnightAPI.updatesManual(true) : await midnightAPI.updatesManual(false);
    if(action==='soundx') r = willOn ? await midnightAPI.soundTweaks(true) : await midnightAPI.soundTweaks(false);
    if(action==='winnotify') r = willOn ? await midnightAPI.winNotify(false) : await midnightAPI.winNotify(true);
    if(action==='customize') r = willOn ? await midnightAPI.customize(true) : await midnightAPI.customize(false);
    if(action==='powerx') r = willOn ? await midnightAPI.powerExtra(true) : await midnightAPI.powerExtra(false);
    if(action==='perfx') r = willOn ? await midnightAPI.perfExtra(true) : await midnightAPI.perfExtra(false);
    if(action==='gamingx') r = willOn ? await midnightAPI.gamingExtra(true) : await midnightAPI.gamingExtra(false);
    if(action==='systemx') r = willOn ? await midnightAPI.systemExtra(true) : await midnightAPI.systemExtra(false);
    log(`${willOn?'✔':'○'} ${action}: ${r.output||'OK'}`); toast(`${willOn?'Ativado':'Desativado'}: ${action}`);
  });
});
document.querySelectorAll('[data-action="kill"]').forEach(b=>b.addEventListener('click', async ()=>{ const r=await midnightAPI.killBackground(); log('⚔ '+r.output); toast('Apps em 2º plano encerradas.'); histAdd('✓','Apps em 2º plano encerradas'); }));
document.querySelectorAll('[data-action="temp"]').forEach(b=>b.addEventListener('click', async ()=>{ toast('A limpar…'); const r=await midnightAPI.cleanTemp(); log('🧹 '+(r.output||'Limpo')); toast('Limpeza concluída!'); histAdd('✓','Limpeza de sistema concluída'); }));
document.querySelectorAll('[data-action="net"]').forEach(b=>b.addEventListener('click', async ()=>{ const r=await midnightAPI.network(); log('◈ Rede:\n'+(r.output||'OK')); toast('Rede otimizada!'); histAdd('✓','DNS otimizado'); }));
document.querySelectorAll('[data-action="debloat"]').forEach(b=>b.addEventListener('click', async ()=>{ toast('A remover bloatware…'); const r=await midnightAPI.debloat(); log('🧹 '+(r.output||'OK')); toast(r.output||'Debloat concluído!'); histAdd('✓','Bloatware removido'); }));

// Jogos (por conta)
let games=[];
function loadGames(){ try{ games=JSON.parse(localStorage.getItem(LS('midnight_games'))||'[]'); }catch{ games=[]; } }
function renderGames(){
  const g=document.getElementById('games-grid');
  if(!games.length){ g.innerHTML='<div class="card">Nenhum jogo ainda. Clica em <b>＋ Adicionar jogo</b> e escolhe o .exe (ex: Valorant, CS2, LoL, Fortnite).</div>'; return; }
  g.innerHTML='';
  games.forEach((gm,i)=>{
    const d=document.createElement('div'); d.className='game-card';
    d.innerHTML=`<div class="g-icon">♞</div><h4>${gm.name}</h4><p>${gm.path}</p><div class="g-btns"><button class="btn gold">▶ Boost & Jogar</button><button class="btn ghost">✕</button></div>`;
    d.querySelector('.btn.gold').addEventListener('click', async ()=>{ toast('⚔ Boost + a lançar '+gm.name+'…'); const r=await midnightAPI.launchGame(gm.path); toast(r.output); });
    d.querySelector('.btn.ghost').addEventListener('click', ()=>{ games.splice(i,1); saveGames(); renderGames(); });
    g.appendChild(d);
  });
}
function saveGames(){ localStorage.setItem(LS('midnight_games'), JSON.stringify(games)); }
document.getElementById('btn-add-game').addEventListener('click', async ()=>{
  // Se for app Python nativa, usa diálogo real do Windows
  if(window.pywebview && window.pywebview.api && window.pywebview.api.pick_game_file){
    const r = await window.pywebview.api.pick_game_file();
    if(r && r.success){ games.push({name:r.name, path:r.path}); saveGames(); renderGames(); toast('Jogo adicionado!'); }
    return;
  }
  document.getElementById('file-game').click();
});
document.getElementById('file-game').addEventListener('change',(e)=>{
  const f=e.target.files[0]; if(!f) return;
  // No Electron, path real vem de file.path
  const p=f.path || f.name;
  games.push({name:p.split(/[\\/]/).pop().replace('.exe','').replace('.lnk',''), path:p});
  saveGames(); renderGames(); toast('Jogo adicionado!');
});
(async ()=>{
  const step=async(n,f)=>{ try{ await f(); }catch(e){ try{ await window.midnightAPI.logError(n+': '+(e&&e.stack||e)); }catch{} } };
  await step('getBackend', getBackend);
  await step('initLogin', initLogin);
  await step('sessionResume', async ()=>{
    try{
      const r=await window.midnightAPI.sessionResume();
      if(r && r.success && r.user){
        currentUser=r.user;
        document.getElementById('user-name').textContent=r.user;
        document.getElementById('login-overlay').style.display='none';
        try{ await window._setAvatar(); }catch{}
        await boot();
      }
    }catch{}
  });
})();
window.addEventListener('error',(ev)=>{
  try{ const m='JSERR '+(ev.message||'')+' @'+(ev.lineno||''); if(window.midnightAPI&&window.midnightAPI.logError) window.midnightAPI.logError(m); }catch{}
});
document.getElementById('status-pill').className='status-pill normal';

// ---------- ESTÚDIO DE VOZ (estilo Voicemod) ----------
let voiceFx='radio', voiceFxLive=true, voiceLiveOn=false, voiceRecOn=false, voiceMonOn=false;
let voiceAll=[], voiceCat='Todos';
const VOICE_CATS=["Todos","Memes","Agudo","Humano","Dispositivos","Profundo","Terror","FPS","Musical","Ficcao","Robotico","Interpretacao"];
const VOICE_CAT_PT={"Todos":"Todos","Memes":"Memes","Agudo":"Agudo","Humano":"Humano","Dispositivos":"Dispositivos","Profundo":"Profundo","Terror":"Terror","FPS":"FPS","Musical":"Musical","Ficcao":"Ficção científica","Robotico":"Robótico","Interpretacao":"Interpretação de papéis"};
function vlog(msg){ const el=document.getElementById('log-voice'); if(!el) return; el.textContent+='\n'+msg; el.scrollTop=el.scrollHeight; }
function voiceGain(){ return parseFloat(document.getElementById('voice-gain').value)||1.5; }
function vmSave(){ try{ localStorage.setItem(LS('vm_voice'), JSON.stringify({fx:voiceFx, mic:document.getElementById('voice-mic').value, out:document.getElementById('voice-out').value, mon:document.getElementById('voice-mon').value, gain:document.getElementById('voice-gain').value})); }catch{} }
function vmLoad(){ try{ return JSON.parse(localStorage.getItem(LS('vm_voice'))||'{}'); }catch{ return {}; } }
async function initVoice(){
  if(!window.midnightAPI || !window.midnightAPI.voiceEffects) return;
  if(!window._vmwired){
    window._vmwired=true;
    document.getElementById('voice-gain').addEventListener('input',(e)=>{
      document.getElementById('voice-gain-val').textContent=e.target.value; vmSave(); });
    document.getElementById('voice-mic').addEventListener('change', async ()=>{ vmSave(); if(voiceLiveOn){ await window.midnightAPI.voiceStop(); await startLive(); } });
    document.getElementById('voice-out').addEventListener('change', async ()=>{ vmSave(); if(voiceLiveOn){ await window.midnightAPI.voiceStop(); await startLive(); } });
    document.getElementById('voice-mon').addEventListener('change', async ()=>{ vmSave(); if(voiceMonOn){ await window.midnightAPI.monitorStop(); await startMonitor(); } });
  }
  try{
    voiceAll=await withTimeout(window.midnightAPI.voiceEffects(), 15000, 'voiceEffects');
    const tabs=document.getElementById('vm-tabs'); tabs.innerHTML='';
    VOICE_CATS.forEach(c=>{
      const b=document.createElement('button'); b.className='vm-tab'+(c==='Todos'?' active':''); b.textContent=VOICE_CAT_PT[c]||c;
      b.addEventListener('click',()=>{ voiceCat=c; tabs.querySelectorAll('.vm-tab').forEach(t=>t.classList.remove('active')); b.classList.add('active'); renderVoiceGrid(); });
      tabs.appendChild(b);
    });
    renderVoiceGrid();
    const _sel=voiceAll.find(f=>f.id==='radio'); if(_sel && !vmLoad().fx){ voiceFx=_sel.id; voiceFxLive=_sel.live; }
  }catch(e){ vlog('Erro efeitos: '+e); const _g=document.getElementById('voice-grid'); if(_g) _g.innerHTML='<div class="card">Erro a carregar efeitos: '+String(e&&e.message||e)+'</div>'; try{ await window.midnightAPI.logError('initVoice: '+(e&&e.stack||e)); }catch{} }
  try{
    const dv=await withTimeout(window.midnightAPI.voiceDevices(), 20000, 'voiceDevices');
    if(dv.success){
      const mic=document.getElementById('voice-mic'), out=document.getElementById('voice-out'), mon=document.getElementById('voice-mon');
      mic.innerHTML=''; out.innerHTML=''; mon.innerHTML='';
      dv.inputs.forEach(d=>{ const o=document.createElement('option'); o.value=d.index; o.textContent=d.name; mic.appendChild(o); });
      dv.outputs.forEach(d=>{ const o=document.createElement('option'); o.value=d.index; o.textContent=d.name; out.appendChild(o); const m=document.createElement('option'); m.value=d.index; m.textContent=d.name; mon.appendChild(m); });
      const cableEl=document.getElementById('voice-cable');
      const virtOk = (dv.virtual !== undefined) ? dv.virtual : dv.cable;
      if(cableEl) cableEl.textContent = virtOk ? '✔ Micro virtual Midnight pronto.' : '⚠ Sem micro virtual — corre o Setup.';
      // Sem escolha guardada: usa o Midnight sozinho, como no Voicemod
      try{
        const s0=vmLoad();
        if(!s0.out){
          const c=[...out.options].find(o=>/midnight|cable/i.test(o.text));
          if(c){ out.value=c.value; vmSave(); }
        }
      }catch{}
    } else vlog(dv.output);
  }catch(e){ vlog('Erro devices: '+e); }
  // Privacidade: NUNCA liga o micro sozinho. Restaura tudo, mas o ⏻ começa desligado.
  try{
    const s=vmLoad();
    if(s.gain){ document.getElementById('voice-gain').value=s.gain; document.getElementById('voice-gain-val').textContent=s.gain; }
    const mic=document.getElementById('voice-mic'), out=document.getElementById('voice-out'), mon=document.getElementById('voice-mon');
    if(s.mic && [...mic.options].some(o=>o.value==s.mic)) mic.value=s.mic;
    if(s.out && [...out.options].some(o=>o.value==s.out)) out.value=s.out;
    if(s.mon && [...mon.options].some(o=>o.value==s.mon)) mon.value=s.mon;
    if(s.fx && voiceAll.some(f=>f.id===s.fx)){ const f=voiceAll.find(x=>x.id===s.fx); voiceFx=f.id; voiceFxLive=f.live; renderVoiceGrid(); }
    document.getElementById('voice-status').textContent='Micro desligado. Prime ⏻ para ativar a voz.';
    vlog('🔇 Arranque silencioso: micro desligado por privacidade.');
  }catch(e){ vlog('Restore: '+e); }
}
function renderVoiceGrid(){
  const grid=document.getElementById('voice-grid'); if(!grid) return; grid.innerHTML='';
  voiceAll.filter(f=>voiceCat==='Todos'||(f.cats||[]).includes(voiceCat)).forEach(f=>{
    const hk=hkFind('voice',f.id);
    const b=document.createElement('div'); b.className='vm-item'+(f.id===voiceFx?' selected':'');
    b.innerHTML=`<span class="vm-avatar"><button class="vm-key${hk?' bound':''}" title="Tecla de atalho">⌨</button><img src="${f.photo}" alt="${f.name}" onerror="this.style.display='none'">${f.badge?`<span class="vm-badge ${f.badge}">${f.badge}</span>`:''}<span class="${f.live?'vm-live':'vm-rec'}">${f.live?'LIVE':'⏺'}</span></span><span class="vm-name">${f.name}</span><span class="vm-hk">${hk||''}</span>`;
    b.querySelector('img').addEventListener('click', ()=>selectVoice(f.id));
    b.querySelector('.vm-key').addEventListener('click',(ev)=>{ ev.stopPropagation(); hkToggle('voice',f.id,f.name); });
    grid.appendChild(b);
  });
}
async function selectVoice(id){
  const f=voiceAll.find(x=>x.id===id); if(!f) return;
  const wasOn=voiceLiveOn;
  voiceFx=f.id; voiceFxLive=f.live; renderVoiceGrid(); vmSave();
  document.getElementById('voice-status').textContent=`${f.emoji} ${f.name} — ${f.desc||''}`;
  if(wasOn){ await window.midnightAPI.voiceStop(); await startLive(); }
  if(voiceMonOn){ await window.midnightAPI.monitorStop(); await startMonitor(); }
}
function vmSelectFromHotkey(id){ selectVoice(id); }

// ---------- TEMAS ----------
function applyTheme(t){
  if (!['cs2', 'cod', 'frost', 'wow'].includes(t)) t = 'wow';
  document.body.dataset.theme = t;
  try{ localStorage.setItem(LS('theme'), t); }catch{}
  document.querySelectorAll('.theme-switch button').forEach(b=>b.classList.toggle('sel', b.dataset.theme===t));
  document.querySelectorAll('.theme-opt').forEach(b=>b.classList.toggle('sel', b.dataset.theme===t));
  document.dispatchEvent(new CustomEvent('midnight:theme', { detail: { theme: t } }));
}
function themeSaved(){ try{ return localStorage.getItem(LS('theme'))||''; }catch{ return ''; } }
document.querySelectorAll('.theme-switch button').forEach(b=>b.addEventListener('click',()=>{
  applyTheme(b.dataset.theme);
  const labels = { cs2: 'Atmosfera CS2 Blaze ativa.', cod: 'Atmosfera COD SpecOps ativa.', frost: 'Atmosfera Titanium Frost ativa.', wow: 'Atmosfera WoW Midnight ativa.' };
  toast(labels[b.dataset.theme] || 'Tema atualizado.');
}));
document.querySelectorAll('.theme-opt').forEach(b=>b.addEventListener('click',()=>{
  applyTheme(b.dataset.theme);
  document.getElementById('theme-overlay').style.display='none';
}));
document.getElementById('reactor-trigger')?.addEventListener('click', () => {
  if (typeof setCompetitive === 'function') setCompetitive(!competitive);
});

// ---------- NOVIDADES DA APP (popup ao iniciar) ----------
const NEWS_FALLBACK = [
  '★ Novo tema Call of Duty — verde militar + ouro, com imagens do jogo',
  '📰 Este popup de novidades — vês sempre o que mudou ao ligar a app',
  '🎮 Tile Call of Duty no Dashboard + dicas de performance no In-Game',
  '🛠️ Correções e melhorias de estabilidade',
];
function newsSeenKey(v){ return 'mno_news_seen_' + (v || 'x'); }
async function fetchNews(){
  try{
    if(window.midnightAPI && window.midnightAPI.getNews){
      const r = await withTimeout(window.midnightAPI.getNews(), 10000, 'getNews');
      if(r && r.version) return r;
    }
  }catch{}
  try{
    const r = await window.midnightAPI.appVersion();
    return {version: (r && r.version) || '2.3.0', news: NEWS_FALLBACK};
  }catch{}
  return {version: '2.3.0', news: NEWS_FALLBACK};
}
async function showNewsIfNeeded(){
  const ov = document.getElementById('news-overlay');
  if(!ov) return;
  if(!window._newsWired){
    window._newsWired = true;
    document.getElementById('btn-news-ok')?.addEventListener('click', ()=>{ ov.style.display='none'; });
    document.getElementById('btn-news-later')?.addEventListener('click', ()=>{ ov.style.display='none'; });
    ov.addEventListener('click', (e)=>{ if(e.target === ov) ov.style.display='none'; });
  }
  try{
    const n = await fetchNews();
    const ver = n.version || '?';
    let seen = '';
    try{ seen = localStorage.getItem(newsSeenKey(ver)) || ''; }catch{}
    if(seen) return; // esta versão já foi vista
    const list = document.getElementById('news-list');
    if(list){
      list.innerHTML = '';
      (n.news || NEWS_FALLBACK).forEach(t=>{
        const li = document.createElement('li'); li.textContent = t; list.appendChild(li);
      });
    }
    const vv = document.getElementById('news-ver');
    if(vv) vv.textContent = 'NOVIDADES • v' + ver;
    try{ localStorage.setItem(newsSeenKey(ver), '1'); }catch{}
    ov.style.display = 'flex';
  }catch{}
}

// ---------- CONTAS ----------
let currentUser='';
function LS(k){ return 'mno_'+(currentUser||'nouser')+'_'+k; }
async function boot(){
  const step=async(n,f)=>{ try{ await f(); }catch(e){ try{ await window.midnightAPI.logError(n+': '+(e&&e.stack||e)); }catch{} } };
  try{ hkLoad(); }catch(e){}
  loadGames();
  if(!themeSaved()) document.getElementById('theme-overlay').style.display='flex';
  else applyTheme(themeSaved());
  await step('renderGames', async()=>renderGames());
  await step('refreshVersion', refreshVersion);
  await step('refreshSystem', refreshSystem);
  await step('initDashboard', initDashboard);
  await step('detectGames', detectGames);
  await step('renderPros', renderPros);
  await step('checkForUpdate', checkForUpdate);
  await step('showNews', showNewsIfNeeded);
  await step('initVoice', initVoice);
  await step('initSound', initSound);
  await step('initServers', initServers);
  await step('initOnline', initOnline);
  await step('initBugs', initBugs);
  await step('initAutostart', initAutostart);
  await step('hkRegister', hkRegister);
}
async function initLogin(){
  const $=id=>document.getElementById(id);
  async function refreshUsers(){
    try{
      const r=await window.midnightAPI.usersList();
      const box=$('login-users'); box.innerHTML='';
      (r.users||[]).forEach(u=>{
        const name=(u&&u.name)||u;
        const b=document.createElement('button');
        b.innerHTML=(u&&u.avatar?`<img src="${u.avatar}" onerror="this.style.display='none'" style="width:20px;height:20px;border-radius:50%;vertical-align:middle"> `:'👤 ')+name;
        b.addEventListener('click',()=>{ $('login-name').value=name; $('login-pass').focus(); });
        box.appendChild(b);
      });
    }catch{}
  }
  async function setAvatar(){
    try{
      const w=await window.midnightAPI.whoami?.();
      const img=document.getElementById('user-avatar');
      img.onerror=()=>{ img.removeAttribute('src'); img.style.display='none'; };
      if(w && w.avatar){ img.src=w.avatar; img.style.display=''; }
      else { img.removeAttribute('src'); img.style.display='none'; }
    }catch{}
  }
  window._setAvatar=setAvatar;
  async function enter(name){
    currentUser=name; $('user-name').textContent=name;
    $('login-overlay').style.display='none';
    voiceLiveOn=false; voiceMonOn=false; voiceRecOn=false;
    await setAvatar();
    await boot();
  }
  async function doLogin(){
    const u=$('login-name').value.trim(), p=$('login-pass').value;
    const r=await window.midnightAPI.accountLogin(u,p);
    if(r.success){
      if(!$('login-keep').checked){ try{ await window.midnightAPI.sessionForget(); }catch{} }
      enter(u||'convidado');
    }
    else { const e=$('login-err'); e.textContent=r.output; e.style.color=''; }
  }
  $('btn-login').addEventListener('click', doLogin);
  $('login-pass').addEventListener('keydown',(e)=>{ if(e.key==='Enter') doLogin(); });
  $('btn-register').addEventListener('click', async ()=>{
    const u=$('login-name').value.trim(), p=$('login-pass').value;
    const r=await window.midnightAPI.accountRegister(u,p);
    if(r.success){
      $('login-pass').value='';
      const e=$('login-err'); e.textContent=`Conta "${u}" criada! Agora prime Entrar.`; e.style.color='#7ef0c1';
      refreshUsers();
    }
    else { const e=$('login-err'); e.textContent=r.output; e.style.color=''; }
  });
  $('btn-guest').addEventListener('click', async ()=>{
    await window.midnightAPI.accountLogin('convidado',''); enter('convidado');
  });
  async function doOauth(kind){
    const e=$('login-err'); e.style.color=''; e.textContent='A abrir o browser… confirma lá e volta aqui.';
    const r = kind==='google' ? await window.midnightAPI.oauthGoogle() : await window.midnightAPI.oauthDiscord();
    if(r.success){ e.textContent=''; enter(r.user); refreshUsers(); }
    else e.textContent=r.output;
  }
  $('btn-google').addEventListener('click', ()=>doOauth('google'));
  $('btn-discord').addEventListener('click', ()=>doOauth('discord'));
  $('link-discord-portal')?.addEventListener('click', async (e)=>{
    e.preventDefault();
    try{ await window.midnightAPI.openUrl('https://discord.com/developers/applications'); }
    catch{ toast('Abre discord.com/developers/applications no browser.'); }
  });
  $('btn-discord-save')?.addEventListener('click', async ()=>{
    const st=$('cfg-discord-status'); st.style.color=''; st.textContent='A guardar…';
    try{
      const r=await window.midnightAPI.oauthSaveDiscord($('cfg-discord-id').value, $('cfg-discord-secret').value);
      st.textContent=r.output; st.style.color=r.success?'#7ef0c1':'';
      if(r.success){
        $('cfg-discord-id').value=''; $('cfg-discord-secret').value='';
        toast('Discord ativo!');
        await refreshOAuth();
      }
    }catch(e){ st.textContent='Falha: '+e; }
  });
  $('btn-logout').addEventListener('click', async ()=>{
    try{ await window.midnightAPI.voiceStop(); await window.midnightAPI.monitorStop(); await window.midnightAPI.hotkeyClear(); await window.midnightAPI.accountLogout(); }catch{}
    voiceLiveOn=false; voiceMonOn=false; voiceRecOn=false; currentUser='';
    try{ stopWatch(); }catch{}
    document.getElementById('vm-power')?.classList.remove('on');
    document.getElementById('vm-micbtn')?.classList.remove('on');
    $('login-name').value=''; $('login-pass').value=''; $('login-err').textContent='';
    $('login-overlay').style.display='flex';
    refreshUsers();
  });
  function paintOAuth(st){
    st = st || {};
    if(st.google || st.discord){
      $('login-social').style.display='flex';
      if(!st.google) $('btn-google').style.display='none'; else $('btn-google').style.display='';
      if(!st.discord) $('btn-discord').style.display='none'; else $('btn-discord').style.display='';
    }
    // Se o Discord já está configurado, esconde o formulário de chaves.
    // (Os campos aparecem sempre vazios por segurança — vazio NÃO é erro.)
    const dc=$('discord-cfg');
    let note=document.getElementById('discord-active-note');
    if(st.discord && dc){
      dc.style.display='none'; dc.open=false;
      if(!note){
        note=document.createElement('p');
        note.id='discord-active-note';
        note.className='muted small';
        note.innerHTML='℈ Login com Discord ativo ✔ (<a href="#" id="link-discord-reconfig">mudar chaves</a>)';
        const a=note.querySelector('#link-discord-reconfig');
        a.style.color='var(--accent)';
        a.addEventListener('click',(ev)=>{ ev.preventDefault(); dc.style.display=''; dc.open=true; note.style.display='none'; });
        dc.parentNode.insertBefore(note, dc.nextSibling);
      }
      note.style.display='';
    } else if(note) note.style.display='none';
  }
  async function refreshOAuth(){
    try{
      if(!window.midnightAPI || !window.midnightAPI.oauthStatus){
        const s=$('cfg-discord-status');
        if(s) s.textContent='Login social só funciona na app nativa (.exe). Aqui no Electron está desligado.';
        return;
      }
      paintOAuth(await window.midnightAPI.oauthStatus());
    }catch{}
  }
  await refreshUsers();
  await refreshOAuth();
}

// ---------- SERVIDORES ----------
let srvAll=[], srvModes=["Todos"], srvCat="Todos";
async function initServers(){
  if(!window.midnightAPI || !window.midnightAPI.serversList) return;
  try{
    const r=await window.midnightAPI.serversList();
    srvAll=r.servers||[];
    srvModes=r.modes||["Todos"];
    const tabs=document.getElementById('srv-tabs'); tabs.innerHTML='';
    srvModes.forEach(m=>{
      const b=document.createElement('button'); b.className='vm-tab'+(m==='Todos'?' active':''); b.textContent=m;
      b.addEventListener('click',()=>{ srvCat=m; tabs.querySelectorAll('.vm-tab').forEach(t=>t.classList.remove('active')); b.classList.add('active'); renderServers(); });
      tabs.appendChild(b);
    });
    renderServers();
    renderSrvHistory();
    serversRefreshNow(true);
  }catch(e){ document.getElementById('servers-grid').innerHTML='<div class="card">Erro: '+e+'</div>'; }
}
async function serversRefreshNow(auto){
  if(!auto) toast('A sondar servidores…');
  try{
    const r=await window.midnightAPI.serversRefresh();
    if(r.success){ srvAll=r.servers; renderServers(); if(!auto) toast('Estado atualizado!'); }
    else if(!auto) toast(r.output);
  }catch(e){ if(!auto) toast('Falha: '+e); }
}
function renderServers(){
  const grid=document.getElementById('servers-grid'); if(!grid) return; grid.innerHTML='';
  const list=srvAll.filter(s=>srvCat==='Todos'||s.mode===srvCat);
  if(!list.length){ grid.innerHTML='<div class="card">Nada aqui. Tenta outra categoria.</div>'; return; }
  list.forEach(s=>{
    const pct=s.max?Math.min(100,Math.round(s.players/s.max*100)):0;
    const d=document.createElement('div'); d.className='card srv-card';
    d.innerHTML=`<span class="srv-mode">${s.mode||''}</span><h4>${s.online===false?'🔴':'🟢'} ${s.name||s.sample_name||s.ip}</h4>
      <div class="srv-meta">${s.ip}:${s.port} • mapa <b>${s.map||s.sample_map||'?'}</b></div>
      <div class="srv-players"><div style="width:${pct}%"></div></div>
      <div class="srv-meta">${s.players??'?'}/${s.max??'?'} jogadores</div>
      <p class="srv-desc">${s.desc||''}</p>
      <div class="srv-actions"><button class="btn gold small">▶ Ligar</button><button class="btn ghost small">📋 IP</button></div>`;
    d.querySelector('.btn.gold').addEventListener('click', async ()=>{
      toast(`A ligar a ${s.ip}… (abre o CS2 se preciso)`);
      const r=await window.midnightAPI.serverConnect(s.ip,s.port);
      toast(r.output); renderSrvHistory();
    });
    d.querySelector('.btn.ghost').addEventListener('click', async ()=>{
      try{ await navigator.clipboard.writeText(`connect ${s.ip}:${s.port}`); toast('IP copiado! Cola na consola do CS2.'); }
      catch{ toast(`${s.ip}:${s.port}`); }
    });
    grid.appendChild(d);
  });
}
async function renderSrvHistory(){
  const box=document.getElementById('servers-history'); if(!box) return;
  try{
    const r=await window.midnightAPI.serversHistory();
    const h=r.history||[];
    if(!h.length){ box.innerHTML='<p class="muted">Ainda não entraste em nenhum.</p>'; return; }
    box.innerHTML='';
    h.forEach(e=>{
      const d=document.createElement('div');
      d.innerHTML=`<label>${e.when||''} • ${e.mode||''}</label><p>${e.name||e.ip}:${e.port} <button class="btn small gold" style="margin-left:8px">▶</button></p>`;
      d.querySelector('button').addEventListener('click', async ()=>{
        const rr=await window.midnightAPI.serverConnect(e.ip,e.port); toast(rr.output);
      });
      box.appendChild(d);
    });
  }catch{}
}
document.getElementById('btn-servers-refresh')?.addEventListener('click', ()=>serversRefreshNow(false));

// ---------- ONLINE (pessoas + chat) ----------
let chatTab = 'lobby'; // 'lobby' ou 'dm:<cid>'
let chatCursor = 0;
let chatThreads = [];
let _onlineWired = false;
let _onlineTimer = null;
// ---------- Notificações de mensagens (vigia corre em qualquer página) ----------
let _watchTimer = null, _watchInit = false;
let _seenLobby = 0, _seenDM = {};
let _unread = { lobby: 0, dms: {} };
function chatPeer(){ return chatTab.startsWith('dm:') ? chatTab.slice(3) : ''; }
function chatAppend(box, m){
  const d = document.createElement('div');
  d.className = 'chat-msg' + (m.mine ? ' mine' : '');
  const h = document.createElement('div'); h.className = 'chat-head';
  const b = document.createElement('b'); b.textContent = m.mine ? 'Tu' : (m.from || m.from_name || '?');
  const s = document.createElement('span'); s.textContent = m.ts || '';
  h.appendChild(b); h.appendChild(s);
  const p = document.createElement('p'); p.textContent = m.text || '';
  d.appendChild(h); d.appendChild(p);
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
}
function renderChatTabs(){
  const tabs = document.getElementById('chat-tabs'); if(!tabs) return;
  tabs.innerHTML = '';
  const mk = (key, label)=>{
    const b = document.createElement('button');
    b.className = 'vm-tab' + (chatTab === key ? ' active' : '');
    b.textContent = label;
    b.addEventListener('click', ()=>{ chatTab = key; chatCursor = 0; clearUnread(key); renderChatTabs(); pollChat(true); });
    tabs.appendChild(b);
  };
  mk('lobby', '🌍 Geral');
  chatThreads.forEach(t=>mk('dm:' + t.id, '💬 ' + (t.name || '?') + (t.online ? '' : ' (off)')));
}
async function pollOnline(){
  if(!window.midnightAPI || !window.midnightAPI.onlineState) return;
  try{
    const r = await window.midnightAPI.onlineState();
    const st = document.getElementById('online-status');
    const list = document.getElementById('online-list');
    const cnt = document.getElementById('online-count');
    if(!(r && r.success)){
      if(st) st.textContent = '⚠ ' + ((r && r.output) || 'Offline');
      return;
    }
    if(!r.connected){
      if(st) st.textContent = '🟡 A ligar ao broker… ' + (r.error || '');
    } else {
      const n = (r.users || []).length;
      if(st) st.textContent = `✔ Ligado como ${r.me.user} — ${n} pessoa(s) online.`;
      if(cnt) cnt.textContent = n;
    }
    if(list){
      const users = r.users || [];
      list.innerHTML = '';
      if(!users.length){
        list.innerHTML = '<p class="muted small">Só tu por aqui. Partilha a app com os amigos!</p>';
      }
      users.forEach(u=>{
        const d = document.createElement('div'); d.className = 'online-user';
        const dot = document.createElement('span'); dot.className = 'online-dot';
        const b = document.createElement('b'); b.textContent = u.name;
        const btn = document.createElement('button'); btn.className = 'btn small gold'; btn.textContent = '💬';
        btn.title = 'Conversar com ' + u.name;
        btn.addEventListener('click', ()=>{ chatTab = 'dm:' + u.id; chatCursor = 0; clearUnread('dm:' + u.id); renderChatTabs(); pollChat(true); });
        d.appendChild(dot); d.appendChild(b); d.appendChild(btn);
        list.appendChild(d);
      });
    }
  }catch{}
}
async function pollChat(reset){
  const box = document.getElementById('chat-box'); if(!box) return;
  if(!window.midnightAPI) return;
  try{
    if(reset){ box.innerHTML = ''; chatCursor = 0; }
    const peer = chatPeer();
    let msgs = [];
    if(!peer && window.midnightAPI.lobbyFetch){
      const r = await window.midnightAPI.lobbyFetch(chatCursor);
      msgs = (r && r.msgs) || [];
    } else if(peer && window.midnightAPI.dmFetch){
      const r = await window.midnightAPI.dmFetch(peer, chatCursor);
      msgs = (r && r.msgs) || [];
    }
    msgs.forEach(m=>{ chatAppend(box, m); if(m.id > chatCursor) chatCursor = m.id; });
    // estás a ver esta aba -> marca como lida (sincroniza o vigia, limpa badge)
    if(!peer){ _seenLobby = Math.max(_seenLobby, chatCursor); _unread.lobby = 0; }
    else { _seenDM[peer] = Math.max(_seenDM[peer] || 0, chatCursor); _unread.dms[peer] = 0; }
    paintUnread();
    if(window.midnightAPI.dmThreads){
      const t = await window.midnightAPI.dmThreads();
      const ids = JSON.stringify(((t && t.threads) || []).map(x=>x.id));
      if(ids !== JSON.stringify(chatThreads.map(x=>x.id))){ chatThreads = (t && t.threads) || []; renderChatTabs(); }
      else chatThreads = (t && t.threads) || [];
    }
  }catch{}
}
async function sendChat(){
  const inp = document.getElementById('chat-input'); if(!inp) return;
  const text = (inp.value || '').trim();
  if(!text) return;
  const peer = chatPeer();
  try{
    const r = peer ? await window.midnightAPI.dmSend(peer, text)
                   : await window.midnightAPI.lobbySend(text);
    if(r && r.success){ inp.value = ''; await pollChat(false); }
    else toast((r && r.output) || 'Falha a enviar.');
  }catch(e){ toast('Falha a enviar: ' + e); }
}
// ---------- NOTIFICAÇÕES de mensagens novas (vigia em 2º plano) ----------
function unreadTotal(){
  return (_unread.lobby || 0) + Object.values(_unread.dms || {}).reduce((a, b)=>a + b, 0);
}
function paintUnread(){
  const n = unreadTotal();
  const b = document.getElementById('online-badge');
  if(b){ b.textContent = n > 99 ? '99+' : n; b.style.display = n ? '' : 'none'; }
  const d = document.getElementById('notif-dot');
  if(d) d.style.display = n ? '' : 'none';
}
function clearUnread(key){
  if(key === 'lobby') _unread.lobby = 0;
  else if(key.startsWith('dm:')) _unread.dms[key.slice(3)] = 0;
  paintUnread();
}
function viewingTab(key){
  return document.getElementById('page-online')?.classList.contains('active') && chatTab === key;
}
function notifyBeep(){
  try{
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if(!Ctx) return;
    const ctx = notifyBeep._c || (notifyBeep._c = new Ctx());
    if(ctx.state === 'suspended') ctx.resume();
    const t = ctx.currentTime;
    [660, 880].forEach((f, i)=>{
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine'; o.frequency.value = f;
      g.gain.setValueAtTime(0.0001, t + i * 0.12);
      g.gain.exponentialRampToValueAtTime(0.25, t + i * 0.12 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + i * 0.12 + 0.11);
      o.connect(g); g.connect(ctx.destination);
      o.start(t + i * 0.12); o.stop(t + i * 0.12 + 0.13);
    });
  }catch{}
}
function notifyMessage(who, text){
  toast(`${who}: ${(text || '').slice(0, 90)}`);
  notifyBeep();
  paintUnread();
}
async function watchMessages(){
  // Corre em QUALQUER página. Na 1ª volta só marca a posição (sem barulho pelo histórico).
  try{
    if(!currentUser || !window.midnightAPI || !window.midnightAPI.lobbyFetch) return;
    try{
      const r = await window.midnightAPI.lobbyFetch(_seenLobby);
      const msgs = (r && r.msgs) || [];
      msgs.forEach(m=>{ if(m.id > _seenLobby) _seenLobby = m.id; });
      if(_watchInit) msgs.filter(m=>!m.mine).forEach(m=>{
        if(viewingTab('lobby')) return;
        _unread.lobby = (_unread.lobby || 0) + 1;
        notifyMessage('🌍 ' + (m.from || '?'), m.text);
      });
    }catch{}
    try{
      const t = await window.midnightAPI.dmThreads();
      for(const th of ((t && t.threads) || [])){
        let msgs = [];
        try{
          const r = await window.midnightAPI.dmFetch(th.id, _seenDM[th.id] || 0);
          msgs = (r && r.msgs) || [];
        }catch{ continue; }
        msgs.forEach(m=>{ if(m.id > (_seenDM[th.id] || 0)) _seenDM[th.id] = m.id; });
        if(!_watchInit) continue;
        const key = 'dm:' + th.id;
        msgs.filter(m=>!m.mine).forEach(m=>{
          if(viewingTab(key)) return;
          _unread.dms[th.id] = (_unread.dms[th.id] || 0) + 1;
          notifyMessage('💬 ' + (th.name || m.from || m.from_name || '?'), m.text);
        });
      }
    }catch{}
    _watchInit = true;
    paintUnread();
  }catch{}
}
function stopWatch(){
  try{ if(_watchTimer) clearInterval(_watchTimer); }catch{}
  _watchTimer = null; _watchInit = false;
  _seenLobby = 0; _seenDM = {}; _unread = { lobby: 0, dms: {} };
  paintUnread();
}
async function initOnline(){
  if(!window.midnightAPI) return;
  if(!_onlineWired){
    _onlineWired = true;
    document.getElementById('btn-chat-send')?.addEventListener('click', sendChat);
    document.getElementById('chat-input')?.addEventListener('keydown', (e)=>{
      if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); sendChat(); }
    });
    document.getElementById('btn-online-refresh')?.addEventListener('click', async ()=>{
      await pollOnline(); await pollChat(false);
    });
    _onlineTimer = setInterval(()=>{
      if(document.getElementById('page-online')?.classList.contains('active')){
        pollOnline(); pollChat(false);
      }
    }, 3000);
    // Vigia de mensagens novas: corre em qualquer página, de 5 em 5s.
    if(_watchTimer) clearInterval(_watchTimer);
    _watchTimer = setInterval(watchMessages, 5000);
    // Abrir a página Online limpa as não-lidas da aba que estás a ver.
    document.querySelector('.nav-btn[data-page="online"]')?.addEventListener('click', ()=>{
      setTimeout(()=>clearUnread(chatTab), 400);
    });
  }
  try{
    if(window.midnightAPI.onlineStart) await window.midnightAPI.onlineStart();
  }catch{}
  await pollOnline();
  renderChatTabs();
  await pollChat(true);
}

// ---------- HOTKEYS ----------
let hkMap={}, hkOn=true;
function hkLoad(){ try{ hkMap=JSON.parse(localStorage.getItem(LS('vm_hotkeys'))||'{}'); hkOn=localStorage.getItem(LS('vm_hkon'))!=='0'; }catch{ hkMap={}; } }
function hkSave(){ try{ localStorage.setItem(LS('vm_hotkeys'),JSON.stringify(hkMap)); localStorage.setItem(LS('vm_hkon'),hkOn?'1':'0'); }catch{} }
function hkFind(kind,id){ for(const [c,b] of Object.entries(hkMap)) if(b.kind===kind&&b.id===id) return c; return ''; }
async function hkRegister(){
  if(!window.midnightAPI || !window.midnightAPI.hotkeySet) return;
  try{
    const r = (hkOn && Object.keys(hkMap).length)
      ? await window.midnightAPI.hotkeySet(hkMap)
      : await window.midnightAPI.hotkeyClear();
    if(r && r.output && /falha/i.test(r.output)) toast(r.output);
  }catch(e){ toast('Atalhos falharam: '+e); }
  const t=document.getElementById('btn-hk-toggle'); if(t) t.textContent=`⌨ Atalhos: ${hkOn?'ON':'OFF'}`;
}
let hkCapturing=null;
function hkBuildCombo(e){
  const mods=[]; if(e.ctrlKey)mods.push('ctrl'); if(e.altKey)mods.push('alt'); if(e.shiftKey)mods.push('shift');
  const k=e.key||'', loc=e.location||0, lower=k.toLowerCase();
  if(loc===3 && /^[0-9]$/.test(k)) return [...mods,'num '+k].join('+');
  if(/^f([1-9]|1[0-2])$/i.test(k)) return [...mods,lower].join('+');
  const special={insert:'insert',delete:'delete',home:'home',end:'end',pageup:'page up',pagedown:'page down',pause:'pause',scrolllock:'scroll lock',printscreen:'print screen'};
  if(special[lower]) return [...mods,special[lower]].join('+');
  if(k===' ') return mods.length? [...mods,'space'].join('+') : '';
  if(/^[a-z0-9]$/i.test(k)) return (mods.includes('ctrl')||mods.includes('alt')) ? [...mods,lower].join('+') : '';
  return '';
}
function hkToggle(kind,id,label){
  const cur=hkFind(kind,id);
  if(cur){ delete hkMap[cur]; hkSave(); hkRegister(); renderVoiceGrid(); renderSoundGrid(); toast(`Atalho ${cur} removido.`); return; }
  hkCapturing={kind,id,label};
  document.getElementById('hk-cap-title').textContent=`Tecla para "${label}"`;
  document.getElementById('hk-capture').style.display='flex';
}
window.addEventListener('keydown',(e)=>{
  if(!hkCapturing) return;
  e.preventDefault(); e.stopPropagation();
  if(e.key==='Escape'){ hkCapturing=null; document.getElementById('hk-capture').style.display='none'; return; }
  if(['Control','Alt','Shift','Meta'].includes(e.key)) return;
  const combo=hkBuildCombo(e);
  if(!combo){ toast('Tecla inválida — usa F1-F12, Insert, Numpad ou letra com Ctrl/Alt.'); return; }
  hkMap[combo]={kind:hkCapturing.kind,id:hkCapturing.id};
  const label=hkCapturing.label;
  hkCapturing=null; document.getElementById('hk-capture').style.display='none';
  hkSave(); hkRegister(); renderVoiceGrid(); renderSoundGrid();
  toast(`⌨ ${combo} → ${label}`);
}, true);
document.getElementById('btn-hk-toggle')?.addEventListener('click', async ()=>{
  hkOn=!hkOn; hkSave(); hkRegister(); toast(`Atalhos ${hkOn?'ligados':'desligados'}.`);
});

// ---------- SOUNDBOARD ----------
let soundAll=[];
function slog(m){ const el=document.getElementById('log-sound'); if(!el)return; el.textContent+='\n'+m; el.scrollTop=el.scrollHeight; }
function soundOut(){ const o=document.getElementById('sound-out'); if(o && o.value!==undefined && o.value!=='') return parseInt(o.value); const v=document.getElementById('voice-out'); return parseInt((v&&v.value)||'-1'); }
async function initSound(){
  if(!window.midnightAPI || !window.midnightAPI.soundboardList) return;
  try{ soundAll=await window.midnightAPI.soundboardList(); }catch{ soundAll=[]; }
  renderSoundGrid();
  try{
    const dv=await window.midnightAPI.voiceDevices();
    const sel=document.getElementById('sound-out');
    if(dv.success && sel){
      const saved=localStorage.getItem(LS('sound_out'))||'';
      sel.innerHTML='';
      dv.outputs.forEach(d=>{ const o=document.createElement('option'); o.value=d.index; o.textContent=d.name; sel.appendChild(o); });
      if(saved && [...sel.options].some(o=>o.value==saved)) sel.value=saved;
      else { const c=[...sel.options].find(o=>/midnight|cable/i.test(o.text)); if(c) sel.value=c.value; }
      sel.addEventListener('change',()=>{ try{ localStorage.setItem(LS('sound_out'),sel.value); }catch{} });
      const sc=document.getElementById('sound-cable');
      const virtOk2 = (dv.virtual !== undefined) ? dv.virtual : dv.cable;
      if(sc) sc.textContent = virtOk2 ? '✔ Micro virtual Midnight pronto.' : '⚠ Sem micro virtual — corre o Setup e reinicia o PC.';
    }
  }catch{}
}
document.getElementById('btn-cable-out')?.addEventListener('click', ()=>{
  const sel=document.getElementById('sound-out');
  const c=[...sel.options].find(o=>/midnight|cable/i.test(o.text));
  if(c){ sel.value=c.value; try{ localStorage.setItem(LS('sound_out'),c.value); }catch{} toast('✔ Sons agora saem no Midnight → CS2/Discord. No jogo escolhe "Midnight Mic" como microfone.'); }
  else toast('⚠ Sem micro virtual. Corre o Setup (instala sozinho) e reinicia o PC.');
});
document.getElementById('btn-brand-audio')?.addEventListener('click', async ()=>{
  toast('A rebatizar micro virtual para Midnight…');
  try{
    const r=await window.midnightAPI.audioBrand();
    toast(r.output);
    try{ await initSound(); await initVoice(); }catch{}
  }catch(e){ toast('Falha: '+e); }
});
document.getElementById('btn-audio-restart')?.addEventListener('click', async ()=>{
  toast('A reiniciar áudio do Windows (o som corta uns segundos)…');
  try{
    const r=await window.midnightAPI.audioRestart();
    toast(r.output);
    try{ await initSound(); await initVoice(); }catch{}
  }catch(e){ toast('Falha: '+e); }
});
function renderSoundGrid(){
  const grid=document.getElementById('sound-grid'); if(!grid) return; grid.innerHTML='';
  if(!soundAll.length){ grid.innerHTML='<div class="card">Sem sons.</div>'; return; }
  soundAll.forEach(s=>{
    const hk=hkFind('sound',s.id);
    const b=document.createElement('div'); b.className='vm-item';
    b.innerHTML=`<span class="vm-avatar"><button class="vm-key${hk?' bound':''}" title="Tecla de atalho">⌨</button>${s.custom?'<button class="vm-del" title="Remover meu som">✕</button>':''}<img src="${s.photo||''}" alt="" onerror="this.style.display='none'"></span><span class="vm-name">${s.title}</span><span class="vm-hk">${hk||''}</span>`;
    b.querySelector('img').addEventListener('click', async ()=>{
      const r=await window.midnightAPI.soundboardPlay(s.id,soundOut()); slog(r.output);
    });
    b.querySelector('.vm-key').addEventListener('click',(ev)=>{ ev.stopPropagation(); hkToggle('sound',s.id,s.title); });
    const del=b.querySelector('.vm-del');
    if(del) del.addEventListener('click', async (ev)=>{
      ev.stopPropagation();
      const r=await window.midnightAPI.soundboardRemove(s.id);
      slog(r.output); toast(r.output);
      try{ soundAll=await window.midnightAPI.soundboardList(); }catch{ }
      renderSoundGrid();
    });
    grid.appendChild(b);
  });
}
document.getElementById('btn-add-sound')?.addEventListener('click', async ()=>{
  toast('Escolhe um mp3/wav/ogg…');
  const r=await window.midnightAPI.soundboardAdd();
  slog(r.output); toast(r.output);
  if(r.success){ try{ soundAll=await window.midnightAPI.soundboardList(); }catch{} renderSoundGrid(); }
});
document.getElementById('btn-sound-stop')?.addEventListener('click', async ()=>{
  const r=await window.midnightAPI.soundboardStop(); slog(r.output);
});
async function startLive(){
  const r=await window.midnightAPI.voiceStart(voiceFx,
    parseInt(document.getElementById('voice-mic').value||'-1'),
    parseInt(document.getElementById('voice-out').value||'-1'), voiceGain());
  vlog(r.output); voiceLiveOn=r.success;
  document.getElementById('vm-power').classList.toggle('on', r.success);
  document.getElementById('voice-status').textContent=r.success?`🔴 AO VIVO: ${voiceFx} — fala!`:'Falha: '+r.output;
  if(!r.success) toast(r.output);
}
document.getElementById('vm-power')?.addEventListener('click', async ()=>{
  if(voiceLiveOn){ await window.midnightAPI.voiceStop(); voiceLiveOn=false; document.getElementById('vm-power').classList.remove('on'); document.getElementById('voice-status').textContent='Desligado.'; }
  else {
    if(!voiceFxLive){ toast('Este efeito é de GRAVAR — usa o microfone grande.'); return; }
    await startLive();
  }
});
async function startMonitor(){
  const r=await window.midnightAPI.monitorStart(voiceFx,
    parseInt(document.getElementById('voice-mic').value||'-1'),
    parseInt(document.getElementById('voice-mon').value||'-1'), voiceGain());
  vlog(r.output); voiceMonOn=r.success;
  document.getElementById('vm-micbtn').classList.toggle('on', r.success);
  if(!r.success) toast(r.output);
}
document.getElementById('vm-micbtn')?.addEventListener('click', async ()=>{
  const btn=document.getElementById('vm-micbtn');
  if(voiceMonOn){ await window.midnightAPI.monitorStop(); voiceMonOn=false; btn.classList.remove('on'); document.getElementById('voice-status').textContent='Monitor desligado.'; }
  else { await startMonitor(); if(voiceMonOn) document.getElementById('voice-status').textContent=`🎙️ A ouvires-te com ${voiceFx}.`; }
});
document.getElementById('btn-voice-rec')?.addEventListener('click', async ()=>{
  const btn=document.getElementById('btn-voice-rec');
  if(!voiceRecOn){
    const r=await window.midnightAPI.voiceRecStart(parseInt(document.getElementById('voice-mic').value||'-1'));
    vlog(r.output);
    if(r.success){ voiceRecOn=true; btn.textContent='⏹ Parar e transformar'; document.getElementById('voice-status').textContent='🔴 A GRAVAR… prime outra vez para transformar.'; }
    else toast(r.output);
  } else {
    document.getElementById('voice-status').textContent='A transformar…';
    const r=await window.midnightAPI.voiceRecStop(voiceFx, parseInt(document.getElementById('voice-out').value||'-1'), voiceGain());
    vlog(r.output); voiceRecOn=false; btn.textContent='⏺ Gravar e transformar';
    document.getElementById('voice-status').textContent='Pronto. Ouve com 👂.';
    toast(r.output);
  }
});
document.getElementById('vm-ear')?.addEventListener('click', async ()=>{
  const r=await window.midnightAPI.voiceReplay(parseInt(document.getElementById('voice-out').value||'-1'));
  vlog(r.output);
});

// ---------- AUTO-UPDATE ----------
async function checkForUpdate(silent){
  try{
    if(!window.midnightAPI || !window.midnightAPI.checkUpdate) return;
    const banner = document.getElementById('update-banner');
    if(!banner) return;

    try{
      const last = await window.midnightAPI.updateLastResult();
      if(last && last.success === false && !silent){
        toast('⚠ ' + last.output);
      }
    }catch{}

    const r = await window.midnightAPI.checkUpdate();
    if(r && r.success && r.available){
      const wasHidden = banner.style.display === 'none';
      banner.style.display = 'flex';
      document.getElementById('update-text').textContent = `Nova versão ${r.latest} disponível — atualiza com 1 clique!`;
      document.getElementById('btn-update-now').style.display = '';
      document.getElementById('btn-update-later').style.display = '';
      document.getElementById('btn-update-restart').style.display = 'none';
      document.getElementById('update-fill').style.width = '0%';
      if(wasHidden || !silent) toast(`✦ Nova versão ${r.latest} disponível!`);
    } else {
      banner.style.display = 'none';
      if(!silent && r && r.success){
        toast(`✔ Tens a versão mais recente instalada (${r.current || 'v3.2.4'})!`);
      }
    }
  }catch(e){
    try{ await window.midnightAPI.logError('checkForUpdate: '+(e&&e.stack||e)); }catch{}
    if(!silent) toast('⚠ Falha ao verificar atualizações: ' + e);
  }
}

setInterval(()=>{
  checkForUpdate(true);
}, 10*60*1000);

document.getElementById('btn-check-update')?.addEventListener('click', async ()=>{
  toast('🔍 A verificar atualizações no GitHub…');
  await checkForUpdate(false);
});

document.getElementById('btn-check-update-sys')?.addEventListener('click', async ()=>{
  toast('🔍 A verificar atualizações no GitHub…');
  await checkForUpdate(false);
});

document.getElementById('btn-update-manual')?.addEventListener('click', async ()=>{
  toast('A abrir a página de Releases…');
  await window.midnightAPI.openReleasesPage();
});

document.getElementById('btn-update-later')?.addEventListener('click',()=>{
  document.getElementById('update-banner').style.display = 'none';
});

document.getElementById('btn-update-now')?.addEventListener('click', async ()=>{
  const btnNow = document.getElementById('btn-update-now');
  const btnLater = document.getElementById('btn-update-later');
  if(btnNow) btnNow.style.display = 'none';
  if(btnLater) btnLater.style.display = 'none';

  toast('⬇ A descarregar atualização oficial do GitHub…');
  await window.midnightAPI.startUpdate();

  const fill = document.getElementById('update-fill');
  const txt = document.getElementById('update-text');

  const h = setInterval(async ()=>{
    const p = await window.midnightAPI.updateProgress();
    const pct = p.pct || 0;
    if(fill) fill.style.width = pct + '%';
    if(txt) txt.textContent = `A descarregar atualização… ${pct}%`;

    if(p.status === 'ready'){
      clearInterval(h);
      if(fill) fill.style.width = '100%';
      if(txt) txt.textContent = `Versão ${p.version} pronta! A reiniciar…`;
      toast(`✔ Versão ${p.version} pronta! A reiniciar a app…`);
      const rBtn = document.getElementById('btn-update-restart');
      if(rBtn) rBtn.style.display = '';

      // Reinicia automaticamente após 1.5 segundos
      setTimeout(async ()=>{
        try {
          await window.midnightAPI.applyUpdate();
        } catch(e) {
          toast('Falha ao reiniciar: ' + e);
        }
      }, 1500);
    }
    if(p.status === 'error'){
      clearInterval(h);
      if(txt) txt.textContent = 'Falha no download: ' + (p.error || 'Erro');
      toast('Falha no download: ' + p.error);
      if(btnNow) btnNow.style.display = '';
    }
  }, 500);
});

document.getElementById('btn-update-restart')?.addEventListener('click', async ()=>{
  const btn = document.getElementById('btn-update-restart');
  btn.disabled = true;
  btn.textContent = 'A reiniciar…';
  toast('A aplicar atualização e a reiniciar…');
  try{
    const r = await window.midnightAPI.applyUpdate();
    btn.disabled = false;
    btn.textContent = 'Reiniciar agora';
    const msg = (r && r.output) || 'Falha no restart.';
    toast('⚠ ' + msg);
  }catch(e){
    btn.disabled = false;
    btn.textContent = 'Reiniciar agora';
    toast('⚠ Falha no restart: ' + e);
  }
});

// ---------- CS2: MIRAS & VIEWMODELS ----------
function buildCrosshairSvg(c) {
  const col = c.color_hex || '#00ff91';
  const p = c.params || { size: 1.5, thick: 1, gap: -4, dot: 0 };
  const center = 14;
  const gap = Math.max(2, 4 + (p.gap !== undefined ? p.gap : -4));
  const len = Math.max(3, (p.size !== undefined ? p.size : 1) * 3.5);
  const thick = Math.max(1, p.thick !== undefined ? p.thick : 1);
  const dot = p.dot ? `<circle cx="${center}" cy="${center}" r="1.5" fill="${col}"/>` : '';
  return `
    <svg viewBox="0 0 28 28" width="28" height="28" style="overflow:visible">
      <line x1="${center}" y1="${center - gap - len}" x2="${center}" y2="${center - gap}" stroke="${col}" stroke-width="${thick}" stroke-linecap="square"/>
      <line x1="${center}" y1="${center + gap}" x2="${center}" y2="${center + gap + len}" stroke="${col}" stroke-width="${thick}" stroke-linecap="square"/>
      <line x1="${center - gap - len}" y1="${center}" x2="${center - gap}" y2="${center}" stroke="${col}" stroke-width="${thick}" stroke-linecap="square"/>
      <line x1="${center + gap}" y1="${center}" x2="${center + gap + len}" y2="${center}" stroke="${col}" stroke-width="${thick}" stroke-linecap="square"/>
      ${dot}
    </svg>
  `;
}

async function renderPros() {
  const cGrid = document.getElementById('crosshairs-grid');
  const vGrid = document.getElementById('viewmodels-grid');
  const tabCross = document.getElementById('tab-btn-crosshairs');
  const tabVm = document.getElementById('tab-btn-viewmodels');
  const contCross = document.getElementById('tab-content-crosshairs');
  const contVm = document.getElementById('tab-content-viewmodels');

  // Subtabs alternância
  if (tabCross && tabVm && contCross && contVm) {
    tabCross.onclick = () => {
      tabCross.classList.add('active');
      tabVm.classList.remove('active');
      contCross.style.display = 'block';
      contVm.style.display = 'none';
    };
    tabVm.onclick = () => {
      tabVm.classList.add('active');
      tabCross.classList.remove('active');
      contVm.style.display = 'block';
      contCross.style.display = 'none';
    };
  }

  // 1. Renderizar Miras (Crosshairs)
  if (cGrid && window.midnightAPI && window.midnightAPI.listCrosshairs) {
    try {
      const list = await withTimeout(window.midnightAPI.listCrosshairs(), 12000, 'listCrosshairs');
      cGrid.innerHTML = '';
      (list || []).forEach(c => {
        const d = document.createElement('div');
        d.className = 'crosshair-card';
        d.innerHTML = `
          <div class="crosshair-header">
            <img src="${c.photo}" alt="${c.name}" onerror="this.src='assets/games/cs2.jpg'">
            <div class="crosshair-player-info">
              <h4>${c.name}</h4>
              <div class="team">${c.team} • ${c.role}</div>
            </div>
          </div>
          <div class="crosshair-preview-box" title="${c.desc}">
            <div class="crosshair-reticle">
              ${buildCrosshairSvg(c)}
            </div>
          </div>
          <p class="muted small" style="margin:0;font-size:10.5px;line-height:1.3">${c.desc}</p>
          <input type="text" class="crosshair-code-input" readonly value="${c.share_code}">
          <div class="crosshair-actions">
            <button class="btn gold small btn-copy-code" title="Copiar código para colar nas definições do CS2">📋 Código</button>
            <button class="btn ghost small btn-copy-cmd" title="Copiar comandos para a consola (~) da Valve">⌨ Consola</button>
          </div>
          <button class="btn ghost small btn-apply-cross" style="margin-top:2px;width:100%">⚡ Aplicar ao CS2 (Seguro)</button>
        `;

        d.querySelector('.btn-copy-code').onclick = async () => {
          try {
            await navigator.clipboard.writeText(c.share_code);
            toast(`Código de mira de ${c.name} copiado! Cola no CS2 (Definições > Mira > Partilhar/Importar).`);
          } catch {
            prompt('Copia o código da mira:', c.share_code);
          }
        };

        d.querySelector('.btn-copy-cmd').onclick = async () => {
          try {
            await navigator.clipboard.writeText(c.console_cmd);
            toast(`Comandos da mira de ${c.name} copiados! Cola na consola do CS2 (~).`);
          } catch {
            prompt('Copia os comandos da consola:', c.console_cmd);
          }
        };

        d.querySelector('.btn-apply-cross').onclick = async () => {
          toast(`⚡ A aplicar mira de ${c.name} de forma segura…`);
          const r = await window.midnightAPI.applyCrosshair(c.id);
          ilog((r.success ? '✔ ' : '✘ ') + (r.output || ''));
          toast(r.success ? `Mira de ${c.name} aplicada sem alterar binds!` : r.output);
        };

        cGrid.appendChild(d);
      });
    } catch (e) {
      cGrid.innerHTML = `<div class="card">Falha ao carregar miras: ${e}</div>`;
    }
  }

  // 2. Renderizar Viewmodels (Posicionamento da Arma)
  if (vGrid && window.midnightAPI && window.midnightAPI.listViewmodels) {
    try {
      const list = await withTimeout(window.midnightAPI.listViewmodels(), 12000, 'listViewmodels');
      vGrid.innerHTML = '';
      (list || []).forEach(v => {
        const d = document.createElement('div');
        d.className = 'viewmodel-card';
        d.innerHTML = `
          <div class="viewmodel-img-wrap">
            <img src="${v.image}" alt="${v.name}" loading="lazy">
          </div>
          <div>
            <span class="viewmodel-badge">${v.tag}</span>
            <h4 class="viewmodel-title">${v.name}</h4>
          </div>
          <p class="viewmodel-desc">${v.desc}</p>
          <div class="muted small" style="font-family:var(--font-mono);font-size:10px;background:var(--bg-inset);padding:4px 6px;border-radius:var(--r-xs);border:1px solid var(--border)">
            FOV ${v.fov} • x:${v.x} y:${v.y} z:${v.z}
          </div>
          <div class="viewmodel-actions">
            <button class="btn gold small btn-copy-vm" style="flex:1">📋 Copiar Consola (~)</button>
            <button class="btn ghost small btn-apply-vm" style="flex:1">⚡ Aplicar CS2</button>
          </div>
        `;

        d.querySelector('.btn-copy-vm').onclick = async () => {
          try {
            await navigator.clipboard.writeText(v.console_cmd);
            toast(`Comandos de viewmodel copiados! Cola na consola do CS2 (~).`);
          } catch {
            prompt('Copia os comandos do viewmodel:', v.console_cmd);
          }
        };

        d.querySelector('.btn-apply-vm').onclick = async () => {
          toast(`⚡ A aplicar viewmodel '${v.name}'…`);
          const r = await window.midnightAPI.applyViewmodel(v.id);
          ilog((r.success ? '✔ ' : '✘ ') + (r.output || ''));
          toast(r.success ? `Viewmodel '${v.name}' configurado com sucesso!` : r.output);
        };

        vGrid.appendChild(d);
      });
    } catch (e) {
      vGrid.innerHTML = `<div class="card">Falha ao carregar viewmodels: ${e}</div>`;
    }
  }
}

// ---------- IN-GAME CS2 & WOW ----------
function ilog(msg){ const el=document.getElementById('log-ingame'); if(!el) return; el.textContent += '\n'+msg; el.scrollTop=el.scrollHeight; }
async function detectGames(){
  if(!window.midnightAPI || !window.midnightAPI.detectGames) return;
  try{
    const d = await withTimeout(window.midnightAPI.detectGames(), 30000, 'detectGames');
    const cs = d.cs2, wow = d.wow;
    const csS = document.getElementById('cs2-status'), csP = document.getElementById('cs2-path');
    const csR = document.getElementById('cs2-run');
    if(csS){ csS.textContent = cs.found ? `✔ CS2 detetado (via ${cs.source||'steam'})` : '✘ CS2 não detetado — prime "📁 Escolher pasta do CS2"'; csS.style.color = cs.found ? '#7ef0c1' : '#ff9d9d'; }
    if(csP){ csP.textContent = cs.base || cs.cfg || ''; }
    if(csR){
      const killBtn=document.getElementById('btn-cs2-kill');
      if(cs.running){
        csR.textContent='🟢 CS2 A CORRER — fecha o jogo para aplicar. Se já fechaste, o processo ficou preso: prime "🔪 Fechar CS2 à força".';
        csR.style.color='#ffd479';
        if(killBtn) killBtn.style.display='';
      }
      else if(cs.found){ csR.textContent='⚪ CS2 fechado — pronto para aplicar.'; csR.style.color='#9a94b8'; if(killBtn) killBtn.style.display='none'; }
      else { csR.textContent=''; if(killBtn) killBtn.style.display='none'; }
    }
    const wowS = document.getElementById('wow-status'), wowP = document.getElementById('wow-path');
    if(wowS){ wowS.textContent = wow.found ? '✔ WoW detetado ('+(wow.flavor||'retail')+')' : (wow.base ? '⚠ WoW encontrado mas abre o jogo uma vez p/ gerar Config.wtf' : '✘ WoW não detetado'); wowS.style.color = wow.found ? '#7ef0c1' : '#ffd479'; }
    if(wowP){ wowP.textContent = wow.config || wow.base || ''; }
    ilog('Deteção: CS2 '+(cs.found?'OK':'falhou')+' | WoW '+(wow.found?'OK':'falhou'));
    window._detectedCs2=!!cs.found; window._detectedWow=!!wow.found;
    try{ renderSupportedGames(); window._fpsRefill&&window._fpsRefill(); }catch{}
  }catch(e){ ilog('Erro deteção: '+e); }
}
document.getElementById('btn-detect-games')?.addEventListener('click', detectGames);
document.getElementById('btn-cs2-folder')?.addEventListener('click', async ()=>{
  toast('Escolhe a pasta do CS2…');
  const r = await window.midnightAPI.pickCs2Folder();
  ilog((r.success?'✔ ':'✘ ')+r.output); toast(r.output);
  if(r.success) detectGames();
});
document.getElementById('btn-cs2-kill')?.addEventListener('click', async ()=>{
  toast('A fechar CS2 à força…');
  const r = await window.midnightAPI.killCs2();
  ilog((r.success?'✔ ':'✘ ')+r.output); toast(r.output);
  detectGames();
});
document.getElementById('btn-cs2-apply')?.addEventListener('click', async ()=>{
  toast('⚔ A aplicar CS2 competitivo…'); const r = await window.midnightAPI.cs2Competitive();
  if(r.success) histAdd('✓','Otimização CS2 aplicada');
  ilog((r.success?'✔ ':'✘ ')+(r.output||'')); if(r.launch){ document.getElementById('cs2-launch-preview').textContent = 'Launch Options:\n'+r.launch; }
  toast(r.success ? 'CS2 competitivo aplicado!' : 'CS2: '+r.output);
});
document.getElementById('btn-cs2-launch')?.addEventListener('click', async ()=>{
  const r = await window.midnightAPI.cs2Launch();
  try{ await navigator.clipboard.writeText(r.output); toast('Launch options copiadas! Cola no Steam.'); }
  catch{ document.getElementById('cs2-launch-preview').textContent = r.output; toast('Copia manual: vê a pré-visualização.'); }
  ilog('Launch Options: '+r.output);
});
document.getElementById('btn-cs2-restore')?.addEventListener('click', async ()=>{
  const r = await window.midnightAPI.cs2Restore(); ilog(r.output); toast('Backup CS2 restaurado.');
});
document.getElementById('btn-cs2-hitreg')?.addEventListener('click', async ()=>{
  toast('🎯 A corrigir registo de tiros e desfasamento sub-tick…');
  const r = await window.midnightAPI.cs2HitregFix();
  ilog((r.success?'✔ ':'✘ ')+(r.output||''));
  if(r.clean_count !== undefined){
    ilog(`Limpeza de Shaders: ${r.clean_count} ficheiros removidos.`);
  }
  toast(r.success ? '✔ Registo de tiros do CS2 corrigido! Buffer em 0 ticks e shaders limpos.' : 'Hitreg: '+(r.output||''));
  if(r.success) histAdd('✓','CS2 Hitreg & Sub-Tick Otimizado');
});
document.getElementById('btn-cs2-overlay-test')?.addEventListener('click', async ()=>{
  toast('🔔 A disparar overlay in-game…');
  await window.midnightAPI.testOverlay();
  toast('Notificação overlay in-game disparada no ecrã com popout!');
});
document.getElementById('btn-wow-apply')?.addEventListener('click', async ()=>{
  toast('⚔ A aplicar WoW Raid FPS… (fecha o jogo primeiro)');
  const r = await window.midnightAPI.wowCompetitive(); ilog((r.success?'✔ ':'✘ ')+r.output); toast(r.success?'WoW competitivo aplicado!':r.output);
  if(r.success) histAdd('✓','Otimização WoW aplicada');
});
document.getElementById('btn-wow-balanced')?.addEventListener('click', async ()=>{
  const r = await window.midnightAPI.wowBalanced(); ilog((r.success?'✔ ':'✘ ')+r.output); toast('WoW modo bonito aplicado.');
});
document.getElementById('btn-wow-restore')?.addEventListener('click', async ()=>{
  const r = await window.midnightAPI.wowRestore(); ilog(r.output); toast('Backup WoW restaurado.');
});

// ---------- DASHBOARD NOVO ----------
function initDashboard(){
  setCompetitiveUI(competitive);
  renderHistory();
  initSearch(); initTopbar(); initFpsCard(); renderSupportedGames();
  try{
    if(window._perfTimer) clearInterval(window._perfTimer);
    window._perfTimer=setInterval(()=>{ if(document.getElementById('page-dashboard')?.classList.contains('active')) refreshPerf(); }, 5000);
  }catch{}
}
// Pesquisa global (Ctrl+K)
const SEARCH_INDEX=[
  {label:'Dashboard', run:()=>go('dashboard')},
  {label:'Modo Competitivo — ativar', run:()=>setCompetitive(true)},
  {label:'In-Game CS2 & WoW', run:()=>go('ingame')},
  {label:'Servidores', run:()=>go('servers')},
  {label:'Pessoas online', run:()=>go('online')},
  {label:'Chat', run:()=>go('online')},
  {label:'Estúdio de Voz', run:()=>go('voz')},
  {label:'Soundboard', run:()=>go('sound')},
  {label:'Otimizações Windows', run:()=>go('otimizacoes')},
  {label:'Meus Jogos', run:()=>go('jogos')},
  {label:'Sistema', run:()=>go('sistema')},
  {label:'Chat de Bugs', run:()=>go('bugs')},
  {label:'Limpeza do sistema', run:()=>go('otimizacoes')},
  {label:'Otimizar rede / ping', run:()=>go('otimizacoes')},
];
function initSearch(){
  const inp=document.getElementById('tb-search'), box=document.getElementById('search-results');
  if(!inp||!box) return;
  document.addEventListener('keydown',(e)=>{
    if((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==='k'){ e.preventDefault(); go('dashboard'); inp.focus(); }
  });
  inp.addEventListener('input',()=>{
    const q=inp.value.trim().toLowerCase();
    if(!q){ box.style.display='none'; return; }
    const hits=SEARCH_INDEX.filter(s=>s.label.toLowerCase().includes(q)).slice(0,7);
    box.innerHTML='';
    if(!hits.length){ box.innerHTML='<div class="search-hit muted">Sem resultados.</div>'; }
    hits.forEach(h=>{
      const d=document.createElement('div'); d.className='search-hit'; d.textContent=h.label;
      d.addEventListener('click',()=>{ box.style.display='none'; inp.value=''; h.run(); });
      box.appendChild(d);
    });
    box.style.display='';
  });
  inp.addEventListener('keydown',(e)=>{
    if(e.key==='Enter'){ const f=box.querySelector('.search-hit'); if(f) f.click(); }
    if(e.key==='Escape'){ box.style.display='none'; inp.blur(); }
  });
  document.addEventListener('click',(e)=>{ if(!e.target.closest('.search-wrap')) box.style.display='none'; });
}
// Topbar: notificações, definições, controlos de janela
function initTopbar(){
  document.getElementById('settings-btn')?.addEventListener('click',()=>go('sistema'));
  const panel=document.getElementById('notif-panel');
  document.getElementById('notif-btn')?.addEventListener('click',(e)=>{
    e.stopPropagation(); renderHistory();
    panel.style.display=panel.style.display==='none'?'':'none';
    const dot=document.getElementById('notif-dot'); if(dot) dot.style.display='none';
  });
  document.addEventListener('click',(e)=>{ if(panel && !e.target.closest('#notif-panel') && !e.target.closest('#notif-btn')) panel.style.display='none'; });
  document.getElementById('win-min')?.addEventListener('click', async ()=>{ try{ await window.midnightAPI.winMin(); }catch(e){ toast('Falha: '+e); } });
  document.getElementById('win-max')?.addEventListener('click', async ()=>{ try{ await window.midnightAPI.winMax(); }catch(e){ toast('Falha: '+e); } });
  document.getElementById('win-close')?.addEventListener('click', async ()=>{ try{ await window.midnightAPI.winClose(); }catch(e){ toast('Falha: '+e); } });
}
// FPS: sem telemetria real -> "Sem dados" (nunca inventar números)
function initFpsCard(){
  const sel=document.getElementById('fps-game'); if(!sel) return;
  const draw=()=>{
    const cv=document.getElementById('fps-canvas'); if(!cv) return;
    const ctx=cv.getContext('2d'); const W=cv.width, H=cv.height;
    ctx.clearRect(0,0,W,H);
    ctx.strokeStyle='rgba(255,255,255,.08)'; ctx.fillStyle='rgba(255,255,255,.35)'; ctx.font='10px Inter,sans-serif';
    [400,300,200,100,0].forEach(v=>{ const y=H-8-(v/400)*(H-16); ctx.beginPath(); ctx.moveTo(28,y); ctx.lineTo(W,y); ctx.stroke(); ctx.fillText(v,4,y+3); });
  };
  const refill=()=>{
    sel.innerHTML='';
    const names=[...(games||[]).map(g=>g.name)];
    try{ if(window._detectedCs2) names.unshift('Counter-Strike 2'); }catch{}
    try{ if(window._detectedWow) names.unshift('World of Warcraft'); }catch{}
    [...new Set(names)].slice(0,12).forEach(n=>{ const o=document.createElement('option'); o.textContent=n; sel.appendChild(o); });
    if(!sel.options.length){ const o=document.createElement('option'); o.textContent='Sem jogos'; sel.appendChild(o); }
  };
  refill(); draw();
  window._fpsRefill=refill;
}
// Jogos suportados: CS2/WoW com deteção real; restantes são atalhos
function renderSupportedGames(){
  const box=document.getElementById('supported-games'); if(!box) return;
  box.innerHTML='';
  const tiles=[
    {name:'Counter-Strike 2', short:'CS2', cls:'cs2', page:'ingame', live:window._detectedCs2, img:'assets/games/cs2.jpg'},
    {name:'World of Warcraft', short:'WoW', cls:'wow', page:'ingame', live:window._detectedWow, img:'assets/games/wow.jpg'},
    {name:'Call of Duty', short:'COD', cls:'cod', page:'ingame', img:'assets/games/cod.jpg'},
    {name:'Valorant', short:'VAL', cls:'val', page:'jogos'},
    {name:'Fortnite', short:'FORT', cls:'fort', page:'jogos'},
    {name:'GTA V', short:'V', cls:'gta', page:'jogos'},
  ];
  tiles.forEach(t=>{
    const d=document.createElement('div'); d.className='sup-game '+t.cls+(t.img?' has-img':''); d.title=t.name;
    d.innerHTML=t.img
      ? `<img src="${t.img}" alt="${t.name}" loading="lazy"><small>${t.name}</small>${t.live?'<span class="sup-live"></span>':''}`
      : `<b>${t.short}</b><small>${t.name}</small>${t.live?'<span class="sup-live"></span>':''}`;
    d.addEventListener('click',()=>go(t.page));
    box.appendChild(d);
  });
  const add=document.createElement('div'); add.className='sup-game add'; add.title='Adicionar jogo';
  add.innerHTML='<b>+</b><small>Adicionar Jogo</small>';
  add.addEventListener('click',()=>document.getElementById('btn-add-game')?.click());
  box.appendChild(add);
}
function bugsLocalLoad(){ try{ return JSON.parse(localStorage.getItem(LS('bugs'))||'[]'); }catch{ return []; } }
function bugsLocalSave(l){ try{ localStorage.setItem(LS('bugs'), JSON.stringify(l.slice(-500))); }catch{} }
function renderBugsList(list){
  const box=document.getElementById('bugs-list'); if(!box) return;
  if(!list.length){ box.innerHTML='<p class="muted">Sem bugs registados. Sê o primeiro a reportar!</p>'; return; }
  box.innerHTML='';
  list.forEach(b=>{
    const d=document.createElement('div'); d.className='bug-item';
    const user=document.createElement('b'); user.textContent='🐞 '+(b.user||'anónimo');
    const when=document.createElement('span'); when.className='bug-when'; when.textContent=b.when||'';
    const p=document.createElement('p'); p.textContent=b.text||'';
    d.appendChild(user); d.appendChild(when); d.appendChild(p);
    box.appendChild(d);
  });
  box.scrollTop=box.scrollHeight;
}
async function initBugs(){
  await refreshBugs();
  document.getElementById('btn-bugs-refresh')?.addEventListener('click', refreshBugs);
  document.getElementById('btn-bugs-send')?.addEventListener('click', sendBug);
  document.getElementById('bugs-input')?.addEventListener('keydown',(e)=>{
    if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); sendBug(); }
  });
}
async function refreshBugs(){
  const box=document.getElementById('bugs-list'); if(!box) return;
  try{
    if(window.midnightAPI && window.midnightAPI.bugsList){
      const r=await window.midnightAPI.bugsList();
      if(r && r.success){ renderBugsList(r.bugs||[]); return; }
    }
    renderBugsList(bugsLocalLoad());
  }catch{ renderBugsList(bugsLocalLoad()); }
}
async function sendBug(){
  const inp=document.getElementById('bugs-input'); if(!inp) return;
  const text=(inp.value||'').trim();
  if(!text){ toast('Escreve o bug primeiro.'); return; }
  try{
    if(window.midnightAPI && window.midnightAPI.bugsAdd){
      const r=await window.midnightAPI.bugsAdd(text);
      toast(r.output||'Enviado!');
      if(!r.success) return;
    } else {
      const l=bugsLocalLoad();
      l.push({user:currentUser||'eu', text, when:new Date().toLocaleString('pt-PT')});
      bugsLocalSave(l);
      toast('Bug registado!');
    }
    inp.value='';
    await refreshBugs();
  }catch(e){ toast('Falha a enviar: '+e); }
}

// ---------- ARRANQUE COM O WINDOWS + ADMIN ----------
let _autostartOn = false;
function paintAutostart(){
  const btn = document.getElementById('btn-autostart');
  const st = document.getElementById('autostart-status');
  if (btn) btn.textContent = _autostartOn ? 'Desativar arranque automático' : 'Ativar arranque automático';
  if (st) st.textContent = _autostartOn ? '✔ A app abre sozinha quando ligas o PC.' : '○ A app NÃO arranca com o Windows.';
}
async function initAutostart(){
  // Botão admin (estava sem listener): reinicia como administrador.
  document.getElementById('btn-admin')?.addEventListener('click', async ()=>{
    try{
      toast('A reiniciar como administrador…');
      const r = await window.midnightAPI.restartAsAdmin();
      toast(r.output || 'OK');
    }catch(e){ toast('Falha: ' + e); }
  });
  const btn = document.getElementById('btn-autostart');
  if (btn && !btn._wired){
    btn._wired = true;
    btn.addEventListener('click', async ()=>{
      try{
        btn.disabled = true;
        toast(_autostartOn ? 'A desativar arranque…' : 'A ativar arranque…');
        const r = await window.midnightAPI.autostartSet(!_autostartOn);
        if (r && r.success) _autostartOn = !!r.enabled;
        else if (r && r.output) toast(r.output);
        paintAutostart();
        toast((r && r.output) || 'OK');
      }catch(e){ toast('Falha: ' + e); }
      finally { btn.disabled = false; }
    });
  }
  try{
    if (window.midnightAPI && window.midnightAPI.autostartGet){
      const r = await withTimeout(window.midnightAPI.autostartGet(), 10000, 'autostartGet');
      if (r && r.success) _autostartOn = !!r.enabled;
    }
  }catch{}
  paintAutostart();
}
