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
      voiceRecStart: (i)=>a.voice_record_start(i),
      voiceRecStop: (e,o,g)=>a.voice_record_stop(e,o,g),
      voiceReplay: (o)=>a.voice_replay(o),
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
const titles = { dashboard:['Dashboard','Visão geral da tua máquina de batalha.'], competitivo:['Modo Competitivo','Um clique para entrar em modo de guerra.'], ingame:['In-Game CS2 & WoW','Otimização dentro do próprio jogo, com backup.'], voz:['Estúdio de Voz','Muda a tua voz como no Voicemod.'], otimizacoes:['Otimizações Windows','Ativa cada runa de poder do sistema.'], jogos:['Meus Jogos','Lança com prioridade alta e boost.'], sistema:['Sistema','Ficha arcana da tua máquina.'] };
navBtns.forEach(b=>b.addEventListener('click',()=>go(b.dataset.page)));
function go(page){ navBtns.forEach(b=>b.classList.toggle('active',b.dataset.page===page));
  pages.forEach(p=>p.classList.toggle('active',p.id==='page-'+page));
  document.getElementById('page-title').textContent=titles[page][0];
  document.getElementById('page-desc').textContent=titles[page][1]; }
document.querySelectorAll('[data-goto]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.goto)));

function toast(msg){ const t=document.getElementById('toast'); t.textContent=msg; t.classList.add('show'); clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove('show'),3200); }
function log(msg){ const el=document.getElementById('log'); el.textContent += '\n'+msg; el.scrollTop=el.scrollHeight; }

// Sistema
async function refreshSystem(){
  if(!window.midnightAPI) return;
  toast('A consultar os espíritos do sistema…');
  const info = await window.midnightAPI.getSystemInfo();
  document.getElementById('spec-cpu').textContent = info.cpu.slice(0,60);
  document.getElementById('spec-gpu').textContent = info.gpu.slice(0,60);
  document.getElementById('spec-ram').textContent = `${info.ramFree} / ${info.ramTotal} GB livres`;
  document.getElementById('spec-disk').textContent = `${info.diskFree} GB`;
  document.getElementById('ram-pct').textContent = info.ramUsedPct+'%';
  const ring=document.getElementById('ram-ring'); const c=326; ring.style.strokeDashoffset = c-(c*info.ramUsedPct/100);
  document.getElementById('sys-os').textContent=info.os; document.getElementById('sys-cpu').textContent=info.cpu;
  document.getElementById('sys-gpu').textContent=info.gpu; document.getElementById('sys-ram').textContent=info.ramTotal+' GB';
  document.getElementById('sys-power').textContent=info.power.slice(0,120); document.getElementById('sys-host').textContent=info.hostname;
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

// Jogos (localStorage)
let games=[]; try{ games=JSON.parse(localStorage.getItem('midnight_games')||'[]'); }catch{ games=[]; }
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
function saveGames(){ localStorage.setItem('midnight_games', JSON.stringify(games)); }
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
(async ()=>{ await getBackend(); renderGames(); refreshSystem(); detectGames(); renderPros(); checkForUpdate(); initVoice(); })();
document.getElementById('status-pill').className='status-pill normal';

// ---------- ESTÚDIO DE VOZ ----------
let voiceFx='robot', voiceFxLive=true, voiceLiveOn=false, voiceRecOn=false;
function vlog(msg){ const el=document.getElementById('log-voice'); if(!el) return; el.textContent+='\n'+msg; el.scrollTop=el.scrollHeight; }
function voiceGain(){ return parseFloat(document.getElementById('voice-gain').value)||1.5; }
async function initVoice(){
  if(!window.midnightAPI || !window.midnightAPI.voiceEffects) return;
  document.getElementById('voice-gain').addEventListener('input',(e)=>{
    document.getElementById('voice-gain-val').textContent=e.target.value; });
  try{
    const fx=await window.midnightAPI.voiceEffects();
    const grid=document.getElementById('voice-grid'); grid.innerHTML='';
    fx.forEach((f,i)=>{
      const d=document.createElement('div'); d.className='pro-card'+(i===1?' selected':'');
      d.innerHTML=`<img src="${f.photo}" alt="${f.name}"><h4>${f.name}</h4><div class="emoji">${f.emoji}</div><div class="specs">${f.desc}</div><div>${f.live?'<span class="live-badge">● LIVE</span>':'<span class="rec-badge">⏺ GRAVAR</span>'}</div>`;
      d.addEventListener('click', async ()=>{
        document.querySelectorAll('#voice-grid .pro-card').forEach(c=>c.classList.remove('selected'));
        d.classList.add('selected'); voiceFx=f.id; voiceFxLive=f.live;
        document.getElementById('voice-status').textContent=`Efeito: ${f.name} — ${f.desc}`;
        if(voiceLiveOn){ await window.midnightAPI.voiceStop(); await startLive(); }
      });
      grid.appendChild(d);
    });
    voiceFx='robot';
  }catch(e){ vlog('Erro efeitos: '+e); }
  try{
    const dv=await window.midnightAPI.voiceDevices();
    if(dv.success){
      const mic=document.getElementById('voice-mic'), out=document.getElementById('voice-out');
      mic.innerHTML=''; out.innerHTML='';
      dv.inputs.forEach(d=>{ const o=document.createElement('option'); o.value=d.index; o.textContent=d.name; mic.appendChild(o); });
      dv.outputs.forEach(d=>{ const o=document.createElement('option'); o.value=d.index; o.textContent=d.name; out.appendChild(o); });
    } else vlog(dv.output);
  }catch(e){ vlog('Erro devices: '+e); }
}
async function startLive(){
  const r=await window.midnightAPI.voiceStart(voiceFx,
    parseInt(document.getElementById('voice-mic').value||'-1'),
    parseInt(document.getElementById('voice-out').value||'-1'), voiceGain());
  vlog(r.output); voiceLiveOn=r.success;
  document.getElementById('voice-status').textContent=r.success?`🔴 AO VIVO: ${voiceFx} — fala!`:'Falha: '+r.output;
  toast(r.output);
}
document.getElementById('btn-voice-live')?.addEventListener('click', async ()=>{
  if(!voiceFxLive){ toast('Este efeito é de GRAVAR — usa o botão ⏺.'); vlog('Efeito '+voiceFx+' só em modo gravar.'); return; }
  await startLive();
});
document.getElementById('btn-voice-stop')?.addEventListener('click', async ()=>{
  const r=await window.midnightAPI.voiceStop(); voiceLiveOn=false; voiceRecOn=false;
  vlog(r.output); document.getElementById('voice-status').textContent='Parado.';
});
document.getElementById('btn-voice-rec')?.addEventListener('click', async ()=>{
  if(!voiceRecOn){
    const r=await window.midnightAPI.voiceRecStart(parseInt(document.getElementById('voice-mic').value||'-1'));
    vlog(r.output);
    if(r.success){ voiceRecOn=true; document.getElementById('btn-voice-rec').textContent='⏹ Parar e transformar'; document.getElementById('voice-status').textContent='🔴 A GRAVAR… prime outra vez para transformar.'; }
    else toast(r.output);
  } else {
    document.getElementById('voice-status').textContent='A transformar…';
    const r=await window.midnightAPI.voiceRecStop(voiceFx, parseInt(document.getElementById('voice-out').value||'-1'), voiceGain());
    vlog(r.output); voiceRecOn=false;
    document.getElementById('btn-voice-rec').textContent='⏺ Gravar (segurar efeito)';
    document.getElementById('voice-status').textContent='Pronto. Toca outra vez com ↻.';
    toast(r.output);
  }
});
document.getElementById('btn-voice-replay')?.addEventListener('click', async ()=>{
  const r=await window.midnightAPI.voiceReplay(parseInt(document.getElementById('voice-out').value||'-1'));
  vlog(r.output);
});

// ---------- AUTO-UPDATE ----------
async function checkForUpdate(){
  try{
    if(!window.midnightAPI || !window.midnightAPI.checkUpdate) return;
    const r = await window.midnightAPI.checkUpdate();
    if(r && r.success && r.available){
      document.getElementById('update-banner').style.display='flex';
      document.getElementById('update-text').textContent=`Nova versão ${r.latest} disponível — atualiza sem sair da app!`;
    }
  }catch{}
}
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
    const list = await window.midnightAPI.listPros();
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
  }catch(e){ grid.innerHTML='<div class="card">Erro a carregar pros.</div>'; }
}

// ---------- IN-GAME CS2 & WOW ----------
function ilog(msg){ const el=document.getElementById('log-ingame'); if(!el) return; el.textContent += '\n'+msg; el.scrollTop=el.scrollHeight; }
async function detectGames(){
  if(!window.midnightAPI || !window.midnightAPI.detectGames) return;
  try{
    const d = await window.midnightAPI.detectGames();
    const cs = d.cs2, wow = d.wow;
    const csS = document.getElementById('cs2-status'), csP = document.getElementById('cs2-path');
    if(csS){ csS.textContent = cs.found ? '✔ CS2 detetado' : '✘ CS2 não detetado (abre no Steam uma vez)'; csS.style.color = cs.found ? '#7ef0c1' : '#ff9d9d'; }
    if(csP){ csP.textContent = cs.base || cs.cfg || ''; }
    const wowS = document.getElementById('wow-status'), wowP = document.getElementById('wow-path');
    if(wowS){ wowS.textContent = wow.found ? '✔ WoW detetado ('+(wow.flavor||'retail')+')' : (wow.base ? '⚠ WoW encontrado mas abre o jogo uma vez p/ gerar Config.wtf' : '✘ WoW não detetado'); wowS.style.color = wow.found ? '#7ef0c1' : '#ffd479'; }
    if(wowP){ wowP.textContent = wow.config || wow.base || ''; }
    ilog('Deteção: CS2 '+(cs.found?'OK':'falhou')+' | WoW '+(wow.found?'OK':'falhou'));
  }catch(e){ ilog('Erro deteção: '+e); }
}
document.getElementById('btn-detect-games')?.addEventListener('click', detectGames);
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
