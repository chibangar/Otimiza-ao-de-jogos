/**
 * PULSE GAMING OPTIMIZER — 3D CYBERNETIC WEB ENGINE
 * Real-time WebGL 3D Quantum Core, Web Audio Synthesizer, 3D Matrix Physics & Interactive Benchmarks
 */

document.addEventListener('DOMContentLoaded', () => {
  initAudioSynthesizer();
  initThreeJsHeroCore();
  initHeroViewTabs();
  initFrametimeBenchmarkSimulator();
  initRealSoundboardPlayer();
  initSoftwareManagerShowcase();
  init3DMatrixTiltPhysics();
  initFaqAccordion();
  initNavbarScroll();
});

/* ==========================================================================
   1. SINTETIZADOR DE EFEITOS SONOROS (WEB AUDIO API)
   ========================================================================== */
let _audioCtx = null;
let _sfxEnabled = true;

function getAudioContext() {
  if (!_audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
      _audioCtx = new AudioContext();
    }
  }
  if (_audioCtx && _audioCtx.state === 'suspended') {
    _audioCtx.resume();
  }
  return _audioCtx;
}

function initAudioSynthesizer() {
  const toggleBtn = document.getElementById('btn-sfx-toggle');
  const saved = localStorage.getItem('pulse_sfx_enabled');
  if (saved !== null) {
    _sfxEnabled = saved === 'true';
  }
  updateSfxToggleBtn();

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      _sfxEnabled = !_sfxEnabled;
      localStorage.setItem('pulse_sfx_enabled', _sfxEnabled);
      updateSfxToggleBtn();
      if (_sfxEnabled) {
        playClickSound();
      }
    });
  }

  function updateSfxToggleBtn() {
    if (!toggleBtn) return;
    toggleBtn.classList.toggle('muted', !_sfxEnabled);
    const txt = toggleBtn.querySelector('.sfx-text');
    if (txt) txt.textContent = _sfxEnabled ? 'SFX ATIVO' : 'SFX MUTADO';
    const ico = toggleBtn.querySelector('.sfx-icon');
    if (ico) ico.textContent = _sfxEnabled ? '🔊' : '🔇';
  }

  // Ligar som de hover em botões e links principais
  document.querySelectorAll('button, .nav-link, .btn-hero-primary, .btn-hero-secondary, .real-sound-card, .cat-pill').forEach(el => {
    el.addEventListener('mouseenter', () => playHoverSound());
  });
}

function playHoverSound() {
  if (!_sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    const now = ctx.currentTime;
    osc.frequency.setValueAtTime(1800, now);
    osc.frequency.exponentialRampToValueAtTime(2400, now + 0.04);

    gain.gain.setValueAtTime(0.018, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.045);
  } catch {}
}

function playClickSound() {
  if (!_sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'triangle';
    const now = ctx.currentTime;
    osc.frequency.setValueAtTime(650, now);
    osc.frequency.exponentialRampToValueAtTime(180, now + 0.08);

    gain.gain.setValueAtTime(0.06, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.085);
  } catch {}
}

function playShockwaveSound() {
  if (!_sfxEnabled) return;
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;

    // Sub-bass sweep
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(160, now);
    osc.frequency.exponentialRampToValueAtTime(42, now + 0.45);

    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800, now);
    filter.frequency.exponentialRampToValueAtTime(80, now + 0.45);

    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.46);
  } catch {}
}

/* ==========================================================================
   2. THREE.JS 3D WEBGL QUANTUM CORE (HERO REAL 3D ENGINE)
   ========================================================================== */
function initThreeJsHeroCore() {
  const container = document.getElementById('webgl-container');
  const canvas = document.getElementById('webgl-hero-canvas');
  if (!container || !canvas || typeof THREE === 'undefined') return;

  const width = container.clientWidth;
  const height = container.clientHeight;

  // Cena, Câmara e Renderer
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  camera.position.set(0, 0.8, 9.2);

  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance'
  });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // Grupo Principal do Núcleo 3D
  const coreGroup = new THREE.Group();
  scene.add(coreGroup);

  // 1. Anel Exterior (Cyan Torus Wireframe & Points)
  const ring1Geom = new THREE.TorusGeometry(3.0, 0.06, 16, 90);
  const ring1Mat = new THREE.MeshStandardMaterial({
    color: 0x00f0ff,
    emissive: 0x0088aa,
    emissiveIntensity: 0.8,
    metalness: 0.9,
    roughness: 0.1,
    wireframe: true
  });
  const ring1 = new THREE.Mesh(ring1Geom, ring1Mat);
  coreGroup.add(ring1);

  // 2. Anel Médio Inclinado (Purple Torus)
  const ring2Geom = new THREE.TorusGeometry(2.3, 0.05, 16, 80);
  const ring2Mat = new THREE.MeshStandardMaterial({
    color: 0xa855f7,
    emissive: 0x6b21a8,
    emissiveIntensity: 0.8,
    metalness: 0.8,
    roughness: 0.2
  });
  const ring2 = new THREE.Mesh(ring2Geom, ring2Mat);
  ring2.rotation.x = Math.PI / 3;
  coreGroup.add(ring2);

  // 3. Anel Interior Ouro (Gold Torus)
  const ring3Geom = new THREE.TorusGeometry(1.65, 0.04, 16, 70);
  const ring3Mat = new THREE.MeshStandardMaterial({
    color: 0xffb703,
    emissive: 0xd97706,
    emissiveIntensity: 0.7,
    metalness: 0.9,
    roughness: 0.1
  });
  const ring3 = new THREE.Mesh(ring3Geom, ring3Mat);
  ring3.rotation.y = Math.PI / 4;
  coreGroup.add(ring3);

  // 4. Núcleo Cristalino Central (Icosaedro Metálico com Facetas)
  const crystalGeom = new THREE.IcosahedronGeometry(0.85, 0);
  const crystalMat = new THREE.MeshStandardMaterial({
    color: 0x00f0ff,
    emissive: 0x005577,
    metalness: 0.95,
    roughness: 0.05,
    flatShading: true
  });
  const crystal = new THREE.Mesh(crystalGeom, crystalMat);
  coreGroup.add(crystal);

  // Jaula Wireframe em volta do cristal
  const cageGeom = new THREE.IcosahedronGeometry(1.05, 1);
  const cageMat = new THREE.MeshBasicMaterial({
    color: 0x00f0ff,
    wireframe: true,
    transparent: true,
    opacity: 0.35
  });
  const cage = new THREE.Mesh(cageGeom, cageMat);
  coreGroup.add(cage);

  // 5. Enxame de Partículas Orbitais 3D
  const particleCount = 280;
  const particleGeom = new THREE.BufferGeometry();
  const particlePositions = new Float32Array(particleCount * 3);
  for (let i = 0; i < particleCount * 3; i += 3) {
    const u = Math.random();
    const v = Math.random();
    const theta = u * 2.0 * Math.PI;
    const phi = Math.acos(2.0 * v - 1.0);
    const r = Math.cbrt(Math.random()) * 2.8 + 1.2;
    particlePositions[i] = r * Math.sin(phi) * Math.cos(theta);
    particlePositions[i + 1] = r * Math.sin(phi) * Math.sin(theta);
    particlePositions[i + 2] = r * Math.cos(phi);
  }
  particleGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: 0x00f0ff,
    size: 0.07,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending
  });
  const particleSwarm = new THREE.Points(particleGeom, particleMat);
  coreGroup.add(particleSwarm);

  // 6. Grelha de Perspetiva 3D no Chão
  const gridFloor = new THREE.GridHelper(16, 24, 0x00f0ff, 0x182035);
  gridFloor.position.y = -2.8;
  scene.add(gridFloor);

  // Iluminação 3D
  const ambientLight = new THREE.AmbientLight(0x080c18, 2.0);
  scene.add(ambientLight);

  const lightCyan = new THREE.PointLight(0x00f0ff, 4.0, 20);
  lightCyan.position.set(4, 3, 5);
  scene.add(lightCyan);

  const lightPurple = new THREE.PointLight(0xa855f7, 3.5, 20);
  lightPurple.position.set(-4, -2, -4);
  scene.add(lightPurple);

  // Rastreio de Movimento do Rato com Inércia
  let targetRotX = 0;
  let targetRotY = 0;
  let isPointerOver = false;
  let overchargeSpeed = 1.0;
  let shockwaveScale = 1.0;

  container.addEventListener('mousemove', (e) => {
    const rect = container.getBoundingClientRect();
    const normX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const normY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
    targetRotY = normX * 0.9;
    targetRotX = -normY * 0.7;
    isPointerOver = true;

    // Atualiza HUD de coordenadas
    const hudCoord = document.getElementById('hud-coord-display');
    if (hudCoord) {
      hudCoord.textContent = `PITCH: ${(normY * 30).toFixed(1)}° // YAW: ${(normX * 45).toFixed(1)}°`;
    }
  });

  container.addEventListener('mouseleave', () => {
    targetRotX = 0;
    targetRotY = 0;
    isPointerOver = false;
  });

  // Clique para libertar onda de choque quântica
  container.addEventListener('click', () => {
    playShockwaveSound();
    overchargeSpeed = 3.8;
    shockwaveScale = 1.6;

    const st = document.getElementById('hud-core-status');
    if (st) {
      st.textContent = 'ESTADO: SOBRECARGA 300% ATIVA ⚡';
      st.style.color = 'var(--cyan)';
      setTimeout(() => {
        if (st) {
          st.textContent = 'ESTADO: PRONTO • CLICA PARA CARREGAR';
          st.style.color = '#fff';
        }
      }, 1600);
    }
  });

  // Redimensionamento
  window.addEventListener('resize', () => {
    const newW = container.clientWidth;
    const newH = container.clientHeight;
    camera.aspect = newW / newH;
    camera.updateProjectionMatrix();
    renderer.setSize(newW, newH);
  });

  // Loop de Animação 60FPS
  let lastTime = performance.now();
  let frames = 0;
  let fpsTimer = 0;
  const fpsDisplay = document.getElementById('hero-fps-counter');

  function renderLoop(time) {
    requestAnimationFrame(renderLoop);

    const delta = (time - lastTime) / 1000;
    lastTime = time;

    // Medição real de FPS
    frames++;
    fpsTimer += delta;
    if (fpsTimer >= 0.5) {
      const fps = Math.round(frames / fpsTimer);
      if (fpsDisplay) fpsDisplay.textContent = `${fps}.0 FPS`;
      frames = 0;
      fpsTimer = 0;
    }

    // Desaceleração suave de sobrecarga
    overchargeSpeed += (1.0 - overchargeSpeed) * 0.04;
    shockwaveScale += (1.0 - shockwaveScale) * 0.08;

    // Rotação autônoma + amortecimento do rato
    ring1.rotation.z += 0.012 * overchargeSpeed;
    ring1.rotation.x += 0.006 * overchargeSpeed;

    ring2.rotation.y += 0.016 * overchargeSpeed;
    ring2.rotation.z -= 0.008 * overchargeSpeed;

    ring3.rotation.x -= 0.02 * overchargeSpeed;
    ring3.rotation.y += 0.014 * overchargeSpeed;

    crystal.rotation.y += 0.01 * overchargeSpeed;
    crystal.rotation.x += 0.007 * overchargeSpeed;
    cage.rotation.y -= 0.008 * overchargeSpeed;

    particleSwarm.rotation.y += 0.004 * overchargeSpeed;

    // Pulsação de escala do cristal
    const pulse = Math.sin(time * 0.003) * 0.06 + 1.0;
    crystal.scale.set(pulse * shockwaveScale, pulse * shockwaveScale, pulse * shockwaveScale);

    // Interpolação suave (lerp) para a câmara / grupo seguir o cursor
    coreGroup.rotation.y += (targetRotY - coreGroup.rotation.y) * 0.05;
    coreGroup.rotation.x += (targetRotX - coreGroup.rotation.x) * 0.05;

    // Efeito de respiração suave na grelha do chão
    gridFloor.position.z = (time * 0.0006) % 1;

    renderer.render(scene, camera);
  }

  requestAnimationFrame(renderLoop);
}

/* ==========================================================================
   3. ABAS DE ALTERNÂNCIA DE VISTA NO HERO
   ========================================================================== */
function initHeroViewTabs() {
  const tabs = document.querySelectorAll('.view-tab');
  const panels = {
    '3d-core': document.getElementById('panel-3d-core'),
    'app-hud': document.getElementById('panel-app-hud'),
    'live-gauges': document.getElementById('panel-live-gauges')
  };
  const hudTitle = document.getElementById('hero-hud-title');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      playClickSound();
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const view = tab.dataset.view;
      Object.keys(panels).forEach(k => {
        if (panels[k]) panels[k].style.display = (k === view) ? 'block' : 'none';
      });

      if (hudTitle) {
        if (view === '3d-core') hudTitle.textContent = 'NÚCLEO QUÂNTICO GPU // TELEMETRIA HOLOGRÁFICA';
        else if (view === 'app-hud') hudTitle.textContent = 'INTERFACE HUD NATIVA // MODO COMPETITIVO';
        else if (view === 'live-gauges') hudTitle.textContent = 'TELEMETRIA CIRCULAR SVG EM TEMPO REAL';
      }
    });
  });

  // Interação no reator da app (Vista 2)
  const reactor = document.getElementById('demo-reactor');
  if (reactor) {
    reactor.addEventListener('click', () => {
      playShockwaveSound();
      const txt = document.getElementById('reactor-text');
      const sub = document.getElementById('reactor-sub');
      if (txt) txt.textContent = 'COMPETITIVO!';
      if (sub) sub.textContent = 'FPS MÁXIMO ATIVO';
      reactor.classList.add('active');
      setTimeout(() => {
        if (txt) txt.textContent = 'MODO TURBO';
        if (sub) sub.textContent = 'CLICA PARA ATIVAR';
        reactor.classList.remove('active');
      }, 2000);
    });
  }
}

/* ==========================================================================
   4. SIMULADOR DE BENCHMARK 3D & GRÁFICO DE FRAMETIMES
   ========================================================================== */
function initFrametimeBenchmarkSimulator() {
  const canvas = document.getElementById('frametime-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let mode = 'pulse'; // 'stock' ou 'pulse'
  let game = 'cs2';

  const gameData = {
    cs2: {
      title: 'COUNTER-STRIKE 2 — COMPETITIVO 1080P',
      desc: 'Sub-Tick Aligned • NVIDIA Reflex Boost • Latência DPC 0.05ms • Zero Stuttering',
      backdrop: 'assets/games/cs2.jpg',
      stock: { fps: '310 FPS', gain: 'Padrão Windows', lows: '145 FPS', lowGain: 'Quedas Bruscas', dpc: '0.85 ms', dpcGain: 'Input Lag Elevado', timer: '15.6 ms' },
      pulse: { fps: '385 FPS', gain: '+75 FPS (+24%)', lows: '230 FPS', lowGain: '+58% Fluidez', dpc: '0.08 ms', dpcGain: '-85% Input Lag', timer: '0.500 ms' }
    },
    cod: {
      title: 'CALL OF DUTY: WARZONE — URZIKSTAN 1440P',
      desc: 'Otimização de VRAM • Prioridade de CPU em Segundo Plano • Estabilidade DPC',
      backdrop: 'assets/games/cod.jpg',
      stock: { fps: '162 FPS', gain: 'Padrão Windows', lows: '88 FPS', lowGain: 'Micro-Stutters', dpc: '0.92 ms', dpcGain: 'Latência de Drivers', timer: '15.6 ms' },
      pulse: { fps: '215 FPS', gain: '+53 FPS (+32%)', lows: '148 FPS', lowGain: '+68% Estabilidade', dpc: '0.06 ms', dpcGain: '-90% Latência', timer: '0.500 ms' }
    },
    wow: {
      title: 'WORLD OF WARCRAFT — VALDRAKKEN / MIDNIGHT RAID',
      desc: 'Fix de Single-Core CPU • Limpeza de Cache de Partículas • Latência de Rede Otimizada',
      backdrop: 'assets/games/wow.jpg',
      stock: { fps: '85 FPS', gain: 'Padrão Windows', lows: '42 FPS', lowGain: 'Quedas em Raids', dpc: '0.78 ms', dpcGain: 'Atraso de Resposta', timer: '15.6 ms' },
      pulse: { fps: '138 FPS', gain: '+53 FPS (+62%)', lows: '98 FPS', lowGain: '+133% Fluidez', dpc: '0.05 ms', dpcGain: '-92% Latência', timer: '0.500 ms' }
    }
  };

  // Botões de modo
  const btnStock = document.getElementById('btn-mode-stock');
  const btnPulse = document.getElementById('btn-mode-pulse');

  btnStock?.addEventListener('click', () => {
    playClickSound();
    mode = 'stock';
    btnStock.classList.add('active');
    btnPulse.classList.remove('active');
    updateBenchmarkUI();
  });

  btnPulse?.addEventListener('click', () => {
    playClickSound();
    mode = 'pulse';
    btnPulse.classList.add('active');
    btnStock.classList.remove('active');
    updateBenchmarkUI();
  });

  // Abas de jogo
  document.querySelectorAll('.bench-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      playClickSound();
      document.querySelectorAll('.bench-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      game = tab.dataset.game;
      updateBenchmarkUI();
    });
  });

  function updateBenchmarkUI() {
    const data = gameData[game] || gameData.cs2;
    const cur = data[mode];

    // Atualiza backdrop
    const bd = document.getElementById('bench-backdrop');
    if (bd && data.backdrop) {
      bd.style.backgroundImage = `url('${data.backdrop}')`;
    }
    const t = document.getElementById('bench-game-title');
    if (t) t.textContent = data.title;
    const d = document.getElementById('bench-game-desc');
    if (d) d.textContent = data.desc;

    // Atualiza métricas
    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('m-fps', cur.fps);
    set('m-fps-gain', cur.gain);
    set('m-lows', cur.lows);
    set('m-lows-gain', cur.lowGain);
    set('m-dpc', cur.dpc);
    set('m-dpc-gain', cur.dpcGain);
    set('m-timer', cur.timer);

    const lbl = document.getElementById('graph-state-label');
    if (lbl) {
      if (mode === 'pulse') {
        lbl.textContent = 'ESTÁVEL // 3.2ms CONSISTENTE (ZERO STUTTER)';
        lbl.style.color = 'var(--cyan)';
      } else {
        lbl.textContent = 'INSTÁVEL // PICOS DE 38ms (STUTTER DETETADO)';
        lbl.style.color = 'var(--red)';
      }
    }
  }

  // Animação contínua da linha de frametime no Canvas
  let points = [];
  const maxPoints = 80;

  function drawFrametimes() {
    requestAnimationFrame(drawFrametimes);

    const w = (canvas.width = canvas.clientWidth);
    const h = (canvas.height = canvas.clientHeight);

    ctx.clearRect(0, 0, w, h);

    // Linhas de grelha horizontal (ms)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    [0.25, 0.5, 0.75].forEach(pct => {
      ctx.beginPath();
      ctx.moveTo(0, h * pct);
      ctx.lineTo(w, h * pct);
      ctx.stroke();
    });

    // Gera novo ponto
    let val;
    if (mode === 'pulse') {
      // Linha super suave e estável (~3.2ms)
      val = (h * 0.75) + (Math.sin(Date.now() * 0.005) * 4) + (Math.random() - 0.5) * 3;
    } else {
      // Linha errática com picos periódicos de stutter
      const isSpike = Math.random() < 0.08;
      val = isSpike ? (h * 0.2 + Math.random() * 30) : (h * 0.65 + (Math.random() - 0.5) * 25);
    }

    points.push(val);
    if (points.length > maxPoints) points.shift();

    if (points.length < 2) return;

    // Desenha gradiente de preenchimento
    ctx.beginPath();
    ctx.moveTo(0, h);
    const stepX = w / (maxPoints - 1);
    for (let i = 0; i < points.length; i++) {
      ctx.lineTo(i * stepX, points[i]);
    }
    ctx.lineTo((points.length - 1) * stepX, h);
    ctx.closePath();

    const grad = ctx.createLinearGradient(0, 0, 0, h);
    if (mode === 'pulse') {
      grad.addColorStop(0, 'rgba(0, 240, 255, 0.25)');
      grad.addColorStop(1, 'rgba(0, 240, 255, 0.0)');
    } else {
      grad.addColorStop(0, 'rgba(255, 51, 102, 0.25)');
      grad.addColorStop(1, 'rgba(255, 51, 102, 0.0)');
    }
    ctx.fillStyle = grad;
    ctx.fill();

    // Desenha linha principal
    ctx.beginPath();
    for (let i = 0; i < points.length; i++) {
      if (i === 0) ctx.moveTo(0, points[i]);
      else ctx.lineTo(i * stepX, points[i]);
    }
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = (mode === 'pulse') ? '#00f0ff' : '#ff3366';
    ctx.shadowColor = (mode === 'pulse') ? 'rgba(0, 240, 255, 0.6)' : 'rgba(255, 51, 102, 0.6)';
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  drawFrametimes();
  updateBenchmarkUI();
}

/* ==========================================================================
   5. SOUNDBOARD INTERATIVO COM ÁUDIO REAL & EQUALIZADOR
   ========================================================================== */
let _activeAudio = null;

function initRealSoundboardPlayer() {
  const cards = document.querySelectorAll('.real-sound-card');
  const stopBtn = document.getElementById('btn-sb-stop-all');

  cards.forEach(card => {
    card.addEventListener('click', () => {
      const audioSrc = card.dataset.audio;
      if (!audioSrc) return;

      playClickSound();

      // Para som anterior
      if (_activeAudio) {
        _activeAudio.pause();
        _activeAudio.currentTime = 0;
      }
      cards.forEach(c => c.classList.remove('playing'));

      const audio = new Audio(audioSrc);
      _activeAudio = audio;
      card.classList.add('playing');

      audio.play().catch(() => {
        // Fallback suave
        card.classList.remove('playing');
      });

      audio.addEventListener('ended', () => {
        card.classList.remove('playing');
        _activeAudio = null;
      });
    });
  });

  if (stopBtn) {
    stopBtn.addEventListener('click', () => {
      playClickSound();
      if (_activeAudio) {
        _activeAudio.pause();
        _activeAudio.currentTime = 0;
        _activeAudio = null;
      }
      cards.forEach(c => c.classList.remove('playing'));
    });
  }
}

/* ==========================================================================
   6. SHOWCASE DO INSTALADOR DE SOFTWARES (10 CATEGORIAS)
   ========================================================================== */
const SOFTWARE_DEMO_DATA = {
  dev: [
    { name: 'Git', winget: 'Git.Git', desc: 'Controlo de versões distribuído para desenvolvimento.', installed: true },
    { name: 'VS Code', winget: 'Microsoft.VisualStudioCode', desc: 'Editor ultra-rápido com depurador e extensões.', installed: true },
    { name: 'Python 3.12', winget: 'Python.Python.3.12', desc: 'Linguagem para scripts, automação e IA.', installed: true },
    { name: 'Notepad++', winget: 'Notepad++.Notepad++', desc: 'Editor leve com destaque de sintaxe multilíngue.', installed: false },
    { name: 'GitHub Desktop', winget: 'GitHub.GitHubDesktop', desc: 'Interface visual para gerir repositórios.', installed: false },
    { name: 'PuTTY', winget: 'PuTTY.PuTTY', desc: 'Cliente SSH e Telnet clássico para Windows.', installed: false }
  ],
  jogos: [
    { name: 'Steam', winget: 'Valve.Steam', desc: 'Plataforma líder para jogos de PC.', installed: true },
    { name: 'Battle.net', winget: 'Blizzard.BattleNet', desc: 'Launcher oficial da Blizzard Entertainment.', installed: true },
    { name: 'Epic Games', winget: 'EpicGames.EpicGamesLauncher', desc: 'Jogos gratuitos e motor Unreal Engine.', installed: false },
    { name: 'EA App', winget: 'ElectronicArts.EADesktop', desc: 'Launcher para títulos Electronic Arts.', installed: false },
    { name: 'GOG Galaxy', winget: 'GOG.Galaxy', desc: 'Jogos sem DRM com biblioteca unificada.', installed: false }
  ],
  navegadores: [
    { name: 'Brave Browser', winget: 'Brave.Brave', desc: 'Navegador com bloqueio nativo de anúncios.', installed: true },
    { name: 'Google Chrome', winget: 'Google.Chrome', desc: 'O browser mais utilizado do mundo.', installed: true },
    { name: 'Mozilla Firefox', winget: 'Mozilla.Firefox', desc: 'Rápido, privado e de código aberto.', installed: false },
    { name: 'Opera GX', winget: 'Opera.OperaGX', desc: 'Navegador desenhado especificamente para gamers.', installed: false },
    { name: 'LibreWolf', winget: 'LibreWolf.LibreWolf', desc: 'Foco estrito em privacidade e zero telemetria.', installed: false }
  ],
  imagem: [
    { name: 'OBS Studio', winget: 'OBSProject.OBSStudio', desc: 'Gravação e streaming profissional de ecrã.', installed: true },
    { name: 'Blender', winget: 'BlenderFoundation.Blender', desc: 'Criação 3D, animação e renderização.', installed: false },
    { name: 'GIMP', winget: 'GIMP.GIMP', desc: 'Editor de imagem e manipulação de fotografias.', installed: false },
    { name: 'ShareX', winget: 'ShareX.ShareX', desc: 'Captura de ecrã avançada e gravação GIF.', installed: false },
    { name: 'HandBrake', winget: 'HandBrake.HandBrake', desc: 'Conversor de vídeo aberto de alta eficiência.', installed: false }
  ],
  discos: [
    { name: 'CrystalDiskInfo', winget: 'CrystalDewWorld.CrystalDiskInfo', desc: 'Monitorização da saúde SMART de SSDs e HDDs.', installed: true },
    { name: 'Everything', winget: 'voidtools.Everything', desc: 'Pesquisa instantânea de ficheiros no Windows.', installed: false },
    { name: 'TreeSize Free', winget: 'JAMSoftware.TreeSize.Free', desc: 'Visualização da ocupação de espaço em disco.', installed: false },
    { name: 'BleachBit', winget: 'BleachBit.BleachBit', desc: 'Limpeza profunda de ficheiros temporários.', installed: false }
  ],
  docs: [
    { name: 'Adobe Acrobat', winget: 'Adobe.Acrobat.Reader.64-bit', desc: 'Visualizador padrão mundial de ficheiros PDF.', installed: true },
    { name: 'SumatraPDF', winget: 'SumatraPDF.SumatraPDF', desc: 'Leitor de PDF ultra-leve e instantâneo.', installed: false },
    { name: 'Obsidian', winget: 'Obsidian.Obsidian', desc: 'Base de conhecimento em Markdown local.', installed: false },
    { name: 'LibreOffice', winget: 'TheDocumentFoundation.LibreOffice', desc: 'Suite completa de escritório de código aberto.', installed: false }
  ],
  runtimes: [
    { name: 'Visual C++ 2015-2022', winget: 'Microsoft.VCRedist.2015+.x64', desc: 'Bibliotecas essenciais para jogos e emuladores.', installed: true },
    { name: '.NET Runtime 8', winget: 'Microsoft.DotNet.DesktopRuntime.8', desc: 'Framework de execução de apps modernas.', installed: true },
    { name: 'DirectX End-User', winget: 'Microsoft.DirectX', desc: 'Runtimes gráficos para jogos DirectX legados.', installed: true },
    { name: 'Node.js LTS', winget: 'OpenJS.NodeJS.LTS', desc: 'Ambiente de execução JavaScript no servidor.', installed: false }
  ],
  seguranca: [
    { name: 'Bitwarden', winget: 'Bitwarden.Bitwarden', desc: 'Gestor de senhas com encriptação de ponta.', installed: false },
    { name: 'KeePassXC', winget: 'KeePassXCTeam.KeePassXC', desc: 'Cofre de palavras-passe 100% offline.', installed: false },
    { name: 'Malwarebytes', winget: 'Malwarebytes.Malwarebytes', desc: 'Proteção contra ameaças digitais e trojans.', installed: false }
  ],
  compressao: [
    { name: '7-Zip', winget: '7zip.7zip', desc: 'Compactador de alta taxa de compressão 7z.', installed: true },
    { name: 'WinRAR', winget: 'RARLab.WinRAR', desc: 'Ferramenta clássica de arquivo e descompressão.', installed: false },
    { name: 'PeaZip', winget: 'GiorgioTani.PeaZip', desc: 'Gestor de ficheiros comprimidos open source.', installed: false }
  ],
  personalizacao: [
    { name: 'PowerToys', winget: 'Microsoft.PowerToys', desc: 'Utilitários oficiais da Microsoft para Windows.', installed: true },
    { name: 'EarTrumpet', winget: 'File-New-Project.EarTrumpet', desc: 'Misturador de volume por aplicação na barra.', installed: false },
    { name: 'AutoHotkey', winget: 'AutoHotkey.AutoHotkey', desc: 'Automação e teclas de atalho personalizadas.', installed: false }
  ]
};

function initSoftwareManagerShowcase() {
  const container = document.getElementById('soft-cards-container');
  const pills = document.querySelectorAll('.cat-pill');
  if (!container || !pills.length) return;

  function renderCategory(catKey) {
    const list = SOFTWARE_DEMO_DATA[catKey] || SOFTWARE_DEMO_DATA.dev;
    let html = '';

    list.forEach(item => {
      html += `
        <div class="soft-preview-item" data-name="${item.name}">
          <div class="soft-preview-check"></div>
          <div class="soft-preview-info">
            <div class="soft-preview-head">
              <span class="soft-preview-name">${item.name}</span>
              <span class="soft-preview-badge ${item.installed ? 'installed' : 'available'}">
                ${item.installed ? '● Instalado' : '○ Disponível'}
              </span>
            </div>
            <p class="soft-preview-desc">${item.desc}</p>
            <span class="soft-preview-winget">${item.winget}</span>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;

    // Toggle interativo de seleção ao clicar
    container.querySelectorAll('.soft-preview-item').forEach(card => {
      card.addEventListener('click', () => {
        playClickSound();
        card.classList.toggle('selected');
      });
    });
  }

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      playClickSound();
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      renderCategory(pill.dataset.cat);
    });
  });

  renderCategory('dev');
}

/* ==========================================================================
   7. FÍSICA DE INCLINAÇÃO 3D EM CARTÕES (MATRIX TILT)
   ========================================================================== */
function init3DMatrixTiltPhysics() {
  const tiltCards = document.querySelectorAll('[data-tilt]');

  tiltCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -7;
      const rotateY = ((x - centerX) / centerX) * 7;

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateZ(10px)`;
      card.style.setProperty('--mouse-x', `${(x / rect.width) * 100}%`);
      card.style.setProperty('--mouse-y', `${(y / rect.height) * 100}%`);
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
    });
  });
}

/* ==========================================================================
   8. FAQ ACCORDION
   ========================================================================== */
function initFaqAccordion() {
  const items = document.querySelectorAll('.faq-item');
  items.forEach(item => {
    const q = item.querySelector('.faq-question');
    if (!q) return;
    q.addEventListener('click', () => {
      playClickSound();
      const isOpen = item.classList.contains('open');
      items.forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
}

/* ==========================================================================
   9. SCROLL DA BARRA DE NAVEGAÇÃO
   ========================================================================== */
function initNavbarScroll() {
  const navbar = document.getElementById('navbar');
  const toggle = document.getElementById('nav-toggle');
  const menu = document.getElementById('nav-menu');

  window.addEventListener('scroll', () => {
    if (navbar) {
      navbar.classList.toggle('scrolled', window.scrollY > 30);
    }
  });

  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      playClickSound();
      menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
      menu.style.flexDirection = 'column';
      menu.style.position = 'absolute';
      menu.style.top = '100%';
      menu.style.left = '0';
      menu.style.right = '0';
      menu.style.background = 'rgba(4, 5, 9, 0.98)';
      menu.style.padding = '20px';
      menu.style.borderBottom = '1px solid var(--border)';
    });
  }
}
