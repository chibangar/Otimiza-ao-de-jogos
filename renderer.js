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
      powerHigh: ()=>a.power_high(),
      powerBalanced: ()=>a.power_balanced(),
      gameMode: (e)=>a.game_mode(e),
      gameBar: (d)=>a.game_bar(d),
      cleanTemp: ()=>a.clean_temp(),
      network: ()=>a.network(),
      visualEffects: (p)=>a.visual_effects(p),
      killBackground: ()=>a.kill_background(),
      gpuPriority: ()=>a.gpu_priority(),
      competitiveOn: ()=>a.competitive_on(),
      competitiveOff: ()=>a.competitive_off(),
      launchGame: (p)=>a.launch_game(p),
      pickGameFile: ()=>a.pick_game_file(),
      detectGames: ()=>a.detect_games(),
      cs2Competitive: ()=>a.cs2_competitive(),
      cs2Restore: ()=>a.cs2_restore(),
      cs2Launch: ()=>a.cs2_launch_options(),
      pickCs2Folder: ()=>a.pick_cs2_folder(),
      killCs2: ()=>a.kill_cs2(),
      wowCompetitive: ()=>a.wow_competitive(),
      wowBalanced: ()=>a.wow_balanced(),
      wowRestore: ()=>a.wow_restore(),
      listPros: ()=>a.list_pros(),
      applyPro: (id)=>a.apply_pro(id),
      checkUpdate: ()=>a.check_update(),
      startUpdate: ()=>a.start_update(),
      updateProgress: ()=>a.update_progress(),
      applyUpdate: ()=>a.apply_update_and_restart(),
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
      openReleasesPage: ()=>a.open_releases_page(),
      serversList: ()=>a.servers_list(),
      serversRefresh: ()=>a.servers_refresh(),
      serversHistory: ()=>a.servers_history(),
      serverConnect: (ip,port)=>a.server_connect(ip,port),
      oauthStatus: ()=>a.oauth_status(),
      oauthGoogle: ()=>a.oauth_google(),
      oauthDiscord: ()=>a.oauth_discord(),
      hotkeySet: (m)=>a.hotkey_set(m),
      hotkeyClear: ()=>a.hotkey_clear(),
      logError: (m)=>a.log_error(m),
    };
    return window.midnightAPI;
  }
  return null;
}
// Estrelas / void particles
const canvas = document.getElementById('stars');
const ctx = canvas.getContext('2d');
let stars = [];
function resize(){ canvas.width = innerWidth; canvas.height = innerHeight; }
addEventListener('resize', resize); resize();
for(let i=0;i<140;i++) stars.push({x:Math.random()*innerWidth,y:Math.random()*innerHeight,r:Math.random()*1.6+.3,s:Math.random()*.4+.05,tw:Math.random()*Math.PI*2});
(function anim(){ ctx.clearRect(0,0,canvas.width,canvas.height);
  for(const st of stars){ st.tw+=.02; const a=.3+Math.abs(Math.sin(st.tw))*.7;
    ctx.beginPath(); ctx.arc(st.x,st.y,st.r,0,7); ctx.fillStyle=`rgba(${150+Math.random()*20|0},${140},255,${a*.8})`; ctx.fill();
    st.y+=st.s; if(st.y>innerHeight) st.y=0; }
  requestAnimationFrame(anim); })();

// Navegação
const navBtns = document.querySelectorAll('.nav-btn');
const pages = document.querySelectorAll('.page');
const titles = { dashboard:['Dashboard','Visão geral da tua máquina de batalha.'], competitivo:['Modo Competitivo','Um clique para entrar em modo de guerra.'], ingame:['In-Game CS2 & WoW','Otimização dentro do próprio jogo, com backup.'], servers:['Servidores','Públicos PT/EU para entrar em 1 clique.'], voz:['Estúdio de Voz','Muda a tua voz como no Voicemod.'], sound:['Soundboard','Memes do myinstants com teclas de atalho.'], otimizacoes:['Otimizações Windows','Ativa cada runa de poder do sistema.'], jogos:['Meus Jogos','Lança com prioridade alta e boost.'], sistema:['Sistema','Ficha arcana da tua máquina.'] };
navBtns.forEach(b=>b.addEventListener('click',()=>go(b.dataset.page)));
function go(page){ navBtns.forEach(b=>b.classList.toggle('active',b.dataset.page===page));
  pages.forEach(p=>p.classList.toggle('active',p.id==='page-'+page));
  document.getElementById('page-title').textContent=titles[page][0];
  document.getElementById('page-desc').textContent=titles[page][1]; }
document.querySelectorAll('[data-goto]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.goto)));

function toast(msg){ const t=document.getElementById('toast'); t.textContent=msg; t.classList.add('show'); clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove('show'),3200); }
function withTimeout(p, ms, label){
  return Promise.race([p, new Promise((_,rej)=>setTimeout(()=>rej(new Error('timeout '+ms+'ms em '+label)), ms))]);
}
function log(msg){ const el=document.getElementById('log'); el.textContent += '\n'+msg; el.scrollTop=el.scrollHeight; }

// Sistema
async function refreshSystem(){
  if(!window.midnightAPI) return;
  try{
    toast('A consultar os espíritos do sistema…');
    const info = await withTimeout(window.midnightAPI.getSystemInfo(), 30000, 'getSystemInfo');
  document.getElementById('spec-cpu').textContent = info.cpu.slice(0,60);
  document.getElementById('spec-gpu').textContent = info.gpu.slice(0,60);
  document.getElementById('spec-ram').textContent = `${info.ramFree} / ${info.ramTotal} GB livres`;
  document.getElementById('spec-disk').textContent = `${info.diskFree} GB`;
  document.getElementById('ram-pct').textContent = info.ramUsedPct+'%';
  const ring=document.getElementById('ram-ring'); const c=326; ring.style.strokeDashoffset = c-(c*info.ramUsedPct/100);
  document.getElementById('sys-os').textContent=info.os; document.getElementById('sys-cpu').textContent=info.cpu;
  document.getElementById('sys-gpu').textContent=info.gpu; document.getElementById('sys-ram').textContent=info.ramTotal+' GB';
  document.getElementById('sys-power').textContent=info.power.slice(0,120); document.getElementById('sys-host').textContent=info.hostname;
  }catch(e){ try{ await window.midnightAPI.logError('refreshSystem: '+(e&&e.stack||e)); }catch{} }
}
document.getElementById('btn-refresh').addEventListener('click', refreshSystem);

// Competitivo
let competitive=false;
async function setCompetitive(on){
  const pill=document.getElementById('status-pill'), txt=document.getElementById('status-text');
  const big=document.getElementById('big-toggle'), lbl=document.getElementById('comp-state-label');
  const list=document.getElementById('comp-log');
  if(on){
    toast('⚔ A invocar o poder da Meia-Noite…'); list.innerHTML='<li>A aplicar runas…</li>';
    const r=await window.midnightAPI.competitiveOn();
    competitive=true; list.innerHTML=r.output.split('\n').map(l=>`<li>${l}</li>`).join('');
    pill.className='status-pill war'; txt.textContent='Modo Competitivo ATIVO';
    big.classList.add('active'); lbl.textContent='EM GUERRA'; lbl.style.color='#ff9d5c';
    document.getElementById('btn-hero-competitive').textContent='Desativar Modo Competitivo';
    log('⚔ COMPETITIVO ATIVO:\n'+r.output); toast('⚔ Modo Competitivo ATIVO. Boa ranked!');
  } else {
    const r=await window.midnightAPI.competitiveOff();
    competitive=false; list.innerHTML=r.output.split('\n').map(l=>`<li>${l}</li>`).join('');
    pill.className='status-pill normal'; txt.textContent='Modo Normal';
    big.classList.remove('active'); lbl.textContent='DESATIVADO'; lbl.style.color='';
    document.getElementById('btn-hero-competitive').textContent='Ativar Modo Competitivo';
    log('☾ Modo normal restaurado.'); toast('Modo normal restaurado.');
  }
}
document.getElementById('btn-comp-on').addEventListener('click',()=>setCompetitive(true));
document.getElementById('btn-comp-off').addEventListener('click',()=>setCompetitive(false));
document.getElementById('big-toggle').addEventListener('click',()=>setCompetitive(!competitive));
document.getElementById('btn-hero-competitive').addEventListener('click',()=>{ if(!competitive) go('competitivo'); setCompetitive(!competitive); });
document.getElementById('btn-quick-boost').addEventListener('click', async ()=>{
  toast('Boost rápido: temp + DNS + 2º plano…');
  await window.midnightAPI.cleanTemp(); await window.midnightAPI.killBackground();
  log('⚡ Boost rápido concluído.'); toast('⚡ Boost rápido concluído!');
});

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
    log(`${willOn?'✔':'○'} ${action}: ${r.output||'OK'}`); toast(`${willOn?'Ativado':'Desativado'}: ${action}`);
  });
});
document.querySelectorAll('[data-action="kill"]').forEach(b=>b.addEventListener('click', async ()=>{ const r=await midnightAPI.killBackground(); log('⚔ '+r.output); toast('Apps em 2º plano encerradas.'); }));
document.querySelectorAll('[data-action="temp"]').forEach(b=>b.addEventListener('click', async ()=>{ toast('A limpar…'); const r=await midnightAPI.cleanTemp(); log('🧹 '+(r.output||'Limpo')); toast('Limpeza concluída!'); }));
document.querySelectorAll('[data-action="net"]').forEach(b=>b.addEventListener('click', async ()=>{ const r=await midnightAPI.network(); log('◈ Rede:\n'+(r.output||'OK')); toast('Rede otimizada!'); }));

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
      if(cableEl) cableEl.textContent = dv.cable ? '✔ Micro virtual pronto.' : '⚠ Sem micro virtual — corre o Setup.';
      // Sem escolha guardada: usa o CABLE sozinho, como no Voicemod
      try{
        const s0=vmLoad();
        if(!s0.out){
          const c=[...out.options].find(o=>/CABLE/i.test(o.text));
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

// ---------- CONTAS ----------
let currentUser='';
function LS(k){ return 'mno_'+(currentUser||'nouser')+'_'+k; }
async function boot(){
  const step=async(n,f)=>{ try{ await f(); }catch(e){ try{ await window.midnightAPI.logError(n+': '+(e&&e.stack||e)); }catch{} } };
  try{ hkLoad(); }catch(e){}
  loadGames();
  await step('renderGames', async()=>renderGames());
  await step('refreshSystem', refreshSystem);
  await step('detectGames', detectGames);
  await step('renderPros', renderPros);
  await step('checkForUpdate', checkForUpdate);
  await step('initVoice', initVoice);
  await step('initSound', initSound);
  await step('initServers', initServers);
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
        b.innerHTML=(u&&u.avatar?`<img src="${u.avatar}" style="width:20px;height:20px;border-radius:50%;vertical-align:middle"> `:'👤 ')+name;
        b.addEventListener('click',()=>{ $('login-name').value=name; $('login-pass').focus(); });
        box.appendChild(b);
      });
    }catch{}
  }
  async function setAvatar(){
    try{
      const w=await window.midnightAPI.whoami?.();
      const img=document.getElementById('user-avatar');
      if(w && w.avatar){ img.src=w.avatar; img.style.display=''; }
      else img.style.display='none';
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
  $('btn-logout').addEventListener('click', async ()=>{
    try{ await window.midnightAPI.voiceStop(); await window.midnightAPI.monitorStop(); await window.midnightAPI.hotkeyClear(); await window.midnightAPI.accountLogout(); }catch{}
    voiceLiveOn=false; voiceMonOn=false; voiceRecOn=false; currentUser='';
    document.getElementById('vm-power')?.classList.remove('on');
    document.getElementById('vm-micbtn')?.classList.remove('on');
    $('login-name').value=''; $('login-pass').value=''; $('login-err').textContent='';
    $('login-overlay').style.display='flex';
    refreshUsers();
  });
  await refreshUsers();
  try{
    const st=await window.midnightAPI.oauthStatus();
    if(st && (st.google || st.discord)){
      $('login-social').style.display='flex';
      if(!st.google) $('btn-google').style.display='none';
      if(!st.discord) $('btn-discord').style.display='none';
    }
  }catch{}
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
      else { const c=[...sel.options].find(o=>/CABLE/i.test(o.text)); if(c) sel.value=c.value; }
      sel.addEventListener('change',()=>{ try{ localStorage.setItem(LS('sound_out'),sel.value); }catch{} });
      const sc=document.getElementById('sound-cable');
      if(sc) sc.textContent = dv.cable ? '✔ Micro virtual pronto.' : '⚠ Sem micro virtual — corre o Setup e reinicia o PC.';
    }
  }catch{}
}
document.getElementById('btn-cable-out')?.addEventListener('click', ()=>{
  const sel=document.getElementById('sound-out');
  const c=[...sel.options].find(o=>/CABLE/i.test(o.text));
  if(c){ sel.value=c.value; try{ localStorage.setItem(LS('sound_out'),c.value); }catch{} toast('✔ Sons agora saem no CABLE → CS2. No CS2 escolhe "CABLE Output" como microfone.'); }
  else toast('⚠ Sem micro virtual. Corre o Setup (instala sozinho) e reinicia o PC.');
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
    const r = await window.midnightAPI.checkUpdate();
    if(r && r.success && r.available){
      const banner=document.getElementById('update-banner');
      const wasHidden=banner.style.display==='none';
      banner.style.display='flex';
      document.getElementById('update-text').textContent=`Nova versão ${r.latest} disponível — atualiza sem sair da app!`;
      if(wasHidden) toast(`✦ Nova versão ${r.latest} disponível!`);
    }
  }catch{}
}
setInterval(()=>{ const b=document.getElementById('update-banner'); if(b && b.style.display==='none') checkForUpdate(true); }, 30*60*1000);
document.getElementById('btn-update-manual')?.addEventListener('click', async ()=>{
  toast('A abrir a página de Releases…');
  await window.midnightAPI.openReleasesPage();
});
document.getElementById('btn-update-later')?.addEventListener('click',()=>{
  document.getElementById('update-banner').style.display='none';
});
document.getElementById('btn-update-now')?.addEventListener('click', async ()=>{
  document.getElementById('btn-update-now').style.display='none';
  document.getElementById('btn-update-later').style.display='none';
  await window.midnightAPI.startUpdate();
  const fill=document.getElementById('update-fill'), txt=document.getElementById('update-text');
  const h=setInterval(async ()=>{
    const p=await window.midnightAPI.updateProgress();
    fill.style.width=(p.pct||0)+'%';
    txt.textContent=`A descarregar atualização… ${p.pct||0}%`;
    if(p.status==='ready'){ clearInterval(h); txt.textContent=`Versão ${p.version} pronta!`; document.getElementById('btn-update-restart').style.display=''; }
    if(p.status==='error'){ clearInterval(h); txt.textContent='Falha: '+p.error; }
  },500);
});
document.getElementById('btn-update-restart')?.addEventListener('click', async ()=>{
  await window.midnightAPI.applyUpdate();
});

// ---------- GALERIA PROS ----------
async function renderPros(){
  const grid = document.getElementById('pros-grid'); if(!grid) return;
  if(!window.midnightAPI || !window.midnightAPI.listPros){ grid.innerHTML='<div class="card">Backend sem pros.</div>'; return; }
  try{
    const list = await withTimeout(window.midnightAPI.listPros(), 15000, 'listPros');
    grid.innerHTML='';
    list.forEach(p=>{
      const d=document.createElement('div'); d.className='pro-card';
      d.innerHTML=`<img src="${p.photo}" alt="${p.name}" onerror="this.style.display='none'"><h4>${p.name}</h4><div class="team">${p.team} • ${p.role}</div><div class="specs">${p.dpi} DPI × ${p.sens} sens = <b>${p.edpi} eDPI</b><br>${p.res} ${p.aspect}</div><button class="btn gold small">⚔ Usar config</button>`;
      d.querySelector('button').addEventListener('click', async ()=>{
        toast(`⚔ A aplicar config de ${p.name}… (fecha o CS2 primeiro)`);
        const r = await window.midnightAPI.applyPro(p.id);
        ilog((r.success?'✔ ':'✘ ')+`[${p.name}] `+(r.output||''));
        toast(r.success ? `Config de ${p.name} aplicada!` : r.output);
      });
      grid.appendChild(d);
    });
  }catch(e){ grid.innerHTML='<div class="card">Erro a carregar pros: '+String(e&&e.message||e)+'</div>'; try{ await window.midnightAPI.logError('renderPros: '+(e&&e.stack||e)); }catch{} }
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
document.getElementById('btn-wow-apply')?.addEventListener('click', async ()=>{
  toast('⚔ A aplicar WoW Raid FPS… (fecha o jogo primeiro)');
  const r = await window.midnightAPI.wowCompetitive(); ilog((r.success?'✔ ':'✘ ')+r.output); toast(r.success?'WoW competitivo aplicado!':r.output);
});
document.getElementById('btn-wow-balanced')?.addEventListener('click', async ()=>{
  const r = await window.midnightAPI.wowBalanced(); ilog((r.success?'✔ ':'✘ ')+r.output); toast('WoW modo bonito aplicado.');
});
document.getElementById('btn-wow-restore')?.addEventListener('click', async ()=>{
  const r = await window.midnightAPI.wowRestore(); ilog(r.output); toast('Backup WoW restaurado.');
});
