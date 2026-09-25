/* ==========================================================================
   MIDNIGHT OPTIMIZER 4.0 — INTERFACE ENGINE
   SVG Icons, Ambient Particles, Accessibility, Dialog Management & HUD Effects
   ========================================================================== */

(() => {
  'use strict';

  // Biblioteca de Ícones Vetoriais SVG Ultra-Nítidos (24x24 viewBox)
  const icons = {
    dashboard: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    competitivo: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>',
    otimizacoes: '<path d="m13 2-9 12h7l-1 8 10-13h-8z"/>',
    ingame: '<path d="M12 2v4M12 18v4M2 12h4M18 12h4"/><circle cx="12" cy="12" r="7"/><path d="M9 12h6M12 9v6"/>',
    jogos: '<rect x="2" y="6" width="20" height="12" rx="4"/><path d="M6 12h4m-2-2v4m7-2h.01m3 0h.01"/>',
    servers: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15.3 15.3 0 0 1 4 9 15.3 15.3 0 0 1-4 9 15.3 15.3 0 0 1-4-9 15.3 15.3 0 0 1 4-9z"/>',
    online: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    voz: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3m-4 0h8"/>',
    sound: '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07M19.07 4.93a10 10 0 0 1 0 14.14"/>',
    sistema: '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
    bugs: '<rect x="8" y="9" width="8" height="10" rx="4"/><path d="m19 7-3 3m-8-3 3 3m-6 4h4m8 0h4m-3 4 3 3m-14-3-3 3M10 5a2 2 0 1 1 4 0"/>',
    search: '<circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="21" y2="21"/>',
    bell: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    bolt: '<path d="m13 2-9 12h7l-1 8 10-13h-8z"/>',
    eye: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    clean: '<path d="m15 3-5 9m-2-1 7 4-4 7-9-5 6-6ZM17 11h5m-3-2v4"/>',
    check: '<polyline points="20 6 9 17 4 12"/>',
    power: '<path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10"/>',
  };

  const getSvg = name => `<svg class="ui-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.otimizacoes}</svg>`;

  // Inserção automática de ícones nos elementos [data-icon]
  function applyIcons() {
    document.querySelectorAll('[data-icon]').forEach(el => {
      el.innerHTML = getSvg(el.dataset.icon);
    });
    const bigToggle = document.querySelector('.big-toggle-core');
    if (bigToggle && !bigToggle.children.length) {
      bigToggle.innerHTML = getSvg('competitivo');
    }
  }

  // Acessibilidade e navegação por teclado em diálogos/modais
  const overlays = [...document.querySelectorAll('.login-overlay, .theme-overlay, .diag-overlay, .news-overlay, .hk-capture')];
  function syncDialogs() {
    const visible = overlays.filter(o => getComputedStyle(o).display !== 'none');
    const active = visible.length > 0;
    const appEl = document.querySelector('.app');
    if (appEl) appEl.setAttribute('aria-hidden', active ? 'true' : 'false');
  }

  const dialogObserver = new MutationObserver(syncDialogs);
  overlays.forEach(overlay => dialogObserver.observe(overlay, { attributes: true, attributeFilter: ['style', 'class'] }));

  // Partículas Ambientais (Alta eficiência, pausa quando janela oculta)
  const canvas = document.getElementById('stars');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let points = [];
    let animId = null;
    let color = '168, 85, 247';

    function initPoints() {
      const w = window.innerWidth;
      const h = window.innerHeight;
      canvas.width = w;
      canvas.height = h;
      points = Array.from({ length: 45 }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.5 + 0.5,
        s: Math.random() * 0.4 + 0.1,
        a: Math.random() * Math.PI * 2
      }));
    }

    function drawAmbient() {
      if (!ctx || document.hidden || document.body.dataset.motion === 'reduced') return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const w = canvas.width;
      const h = canvas.height;

      for (let p of points) {
        p.a += 0.02;
        p.y -= p.s;
        if (p.y < 0) { p.y = h; p.x = Math.random() * w; }
        const alpha = 0.2 + Math.abs(Math.sin(p.a)) * 0.5;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${color}, ${alpha})`;
        ctx.fill();
      }
      animId = requestAnimationFrame(drawAmbient);
    }

    function syncColor() {
      const rgb = getComputedStyle(document.body).getPropertyValue('--accent-rgb').trim();
      if (rgb) color = rgb;
    }

    window.addEventListener('resize', initPoints, { passive: true });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) cancelAnimationFrame(animId);
      else drawAmbient();
    });
    document.addEventListener('midnight:theme', syncColor);

    initPoints();
    syncColor();
    drawAmbient();
  }

  // Efeito de onda de clique tátil nos botões
  document.addEventListener('click', event => {
    const button = event.target.closest('.btn');
    if (!button || button.disabled) return;
    const wave = document.createElement('span');
    const bounds = button.getBoundingClientRect();
    wave.className = 'click-wave';
    wave.style.left = (event.clientX - bounds.left) + 'px';
    wave.style.top = (event.clientY - bounds.top) + 'px';
    button.appendChild(wave);
    setTimeout(() => wave.remove(), 600);
  });

  // Alternador de redução de movimento (Acessibilidade)
  const motionBtn = document.getElementById('motion-toggle');
  if (motionBtn) {
    let reduced = localStorage.getItem('midnight-reduced-motion') === '1';
    function updateMotion() {
      document.body.dataset.motion = reduced ? 'reduced' : 'full';
      motionBtn.setAttribute('aria-pressed', String(reduced));
    }
    motionBtn.addEventListener('click', () => {
      reduced = !reduced;
      try { localStorage.setItem('midnight-reduced-motion', reduced ? '1' : '0'); } catch {}
      updateMotion();
      const toastEl = document.getElementById('toast');
      if (toastEl) {
        toastEl.textContent = reduced ? 'Efeitos visuais reduzidos.' : 'Efeitos completos ativos.';
        toastEl.classList.add('show');
        setTimeout(() => toastEl.classList.remove('show'), 2500);
      }
    });
    updateMotion();
  }

  // Título e sub-cabeçalho dinâmico na Topbar
  const pageTitles = {
    dashboard: ['CENTRO DE COMANDO', 'Dashboard Geral'],
    competitivo: ['MODO DE GUERRA', 'Modo Competitivo'],
    ingame: ['OTIMIZAÇÃO DENTRO DO JOGO', 'In-Game CS2, WoW & COD'],
    otimizacoes: ['AFINAÇÕES DO WINDOWS', 'Otimizações do Sistema'],
    servers: ['CONEXÃO RÁPIDA', 'Servidores Públicos'],
    online: ['COMUNIDADE & EQUIPA', 'Jogadores Online & Chat'],
    voz: ['TRANSFORMAÇÃO DE ÁUDIO', 'Estúdio de Voz'],
    sound: ['REPRODUTOR DE EFEITOS', 'Soundboard'],
    jogos: ['LANÇADOR COM BOOST', 'Biblioteca de Jogos'],
    sistema: ['HARDWARE & PRIVILÉGIOS', 'Ficha do Sistema'],
    bugs: ['FEEDBACK & MELHORIAS', 'Chat de Bugs']
  };

  document.addEventListener('midnight:navigate', event => {
    const page = event.detail?.page;
    if (!page) return;
    const info = pageTitles[page] || ['MIDNIGHT OPTIMIZER', page.toUpperCase()];
    const eyebrow = document.getElementById('page-eyebrow');
    const title = document.getElementById('page-title');
    if (eyebrow) eyebrow.textContent = info[0];
    if (title) title.innerHTML = `${info[1]}<span class="heading-dot">.</span>`;
  });

  // Inicialização quando DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyIcons);
  } else {
    applyIcons();
  }
})();
