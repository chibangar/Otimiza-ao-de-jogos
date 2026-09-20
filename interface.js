/* Presentation only: no OS changes or synthetic hardware measurements. */
(() => {
  'use strict';
  const paths = {
    dashboard: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    bolt: '<path d="m13 2-9 12h7l-1 8 10-13h-8z"/>',
    sliders: '<path d="M4 4v6m0 4v6M12 4v10m0 4v2M20 4v2m0 4v10M1 10h6m2 4h6m2-8h6"/>',
    gamepad: '<path d="M7 7h10c3 0 5 9 4 11s-4-1-5-3H8c-1 2-4 5-5 3S4 7 7 7Z"/><path d="M8 9v5m-2.5-2.5h5M16 10h.01M18 12h.01"/>',
    target: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 1v5m0 12v5M1 12h5m12 0h5"/>',
    mic: '<rect x="9" y="2" width="6" height="13" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-4 0h8"/>',
    wave: '<path d="M3 10v4m4-8v12m5-16v20m5-16v12m4-8v4"/>',
    globe: '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
    chat: '<path d="M21 11a9 9 0 0 1-13 8l-5 2 1-5a9 9 0 1 1 17-5Z"/><path d="M8 10h8m-8 4h5"/>',
    settings: '<path d="m9 3 1-1h4l1 3 3 1 3 1v4l-2 2v3l-2 3-3-1-2 3-3-1-1-3-3-1-1-4 2-2V7l3-2Z"/><circle cx="12" cy="12" r="3"/>',
    help: '<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 1 1 4 3c-1 .5-1 1-1 2m0 3h.01"/>',
    search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4"/>',
    sparkles: '<path d="m12 3 2.4 6.6L21 12l-6.6 2.4L12 21l-2.4-6.6L3 12l6.6-2.4ZM20 2v4m-2-2h4"/>',
    clean: '<path d="m15 3-5 9m-2-1 7 4-4 7-9-5 6-6ZM17 11h5m-3-2v4"/>',
    activity: '<path d="M2 12h5l3-8 4 16 3-8h5"/>',
  };
  const icon = name => `<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.sparkles}</svg>`;
  document.querySelectorAll('[data-icon]').forEach(el => { el.innerHTML = icon(el.dataset.icon); });
  document.querySelector('.big-toggle-core').innerHTML = icon('bolt');
  document.querySelectorAll('.nav-btn').forEach(button => {
    const label = button.querySelector('span')?.textContent || button.textContent;
    button.title = label;
    button.setAttribute('aria-label', label);
  });
  document.querySelector('.nav-btn.active')?.setAttribute('aria-current', 'page');

  // Keep keyboard focus inside visible dialogs and out of the covered app.
  const overlays = [...document.querySelectorAll('.login-overlay, .theme-overlay, .diag-overlay, .news-overlay, .hk-capture')];
  const app = document.querySelector('.app');
  let activeDialog = null;
  let previousFocus = null;
  const labels = {'login-overlay':'Entrar no Midnight', 'theme-overlay':'Escolher atmosfera', 'diag-overlay':'Diagnóstico do PC', 'news-overlay':'Novidades', 'hk-capture':'Configurar atalho'};
  overlays.forEach(overlay => {
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', labels[overlay.id]);
    overlay.tabIndex = -1;
  });
  const focusableIn = dialog => [...dialog.querySelectorAll('button, input, select, textarea, a[href], summary, [tabindex="0"]')]
    .filter(element => !element.disabled && element.getClientRects().length);
  function syncDialogs() {
    const visible = overlays.filter(overlay => getComputedStyle(overlay).display !== 'none');
    const next = visible.sort((a,b) => Number(getComputedStyle(a).zIndex) - Number(getComputedStyle(b).zIndex)).at(-1) || null;
    app.inert = Boolean(next);
    overlays.forEach(overlay => { overlay.inert = Boolean(next && overlay !== next); });
    if(next === activeDialog) return;
    if(next) {
      if(!activeDialog) previousFocus = document.activeElement;
      activeDialog = next;
      (focusableIn(next)[0] || next).focus({preventScroll: true});
    } else {
      activeDialog = null;
      if(previousFocus?.isConnected && previousFocus.getClientRects().length) previousFocus.focus({preventScroll: true});
    }
  }
  const dialogObserver = new MutationObserver(syncDialogs);
  overlays.forEach(overlay => dialogObserver.observe(overlay, {attributes: true, attributeFilter: ['style']}));
  syncDialogs();
  document.addEventListener('keydown', event => {
    if(event.key !== 'Tab' || !activeDialog) return;
    const items = focusableIn(activeDialog);
    const first = items[0], last = items.at(-1);
    if(!first) { event.preventDefault(); activeDialog.focus(); return; }
    if(event.shiftKey && (document.activeElement === first || !activeDialog.contains(document.activeElement))) {
      event.preventDefault(); last.focus();
    } else if(!event.shiftKey && (document.activeElement === last || !activeDialog.contains(document.activeElement))) {
      event.preventDefault(); first.focus();
    }
  });

  // Update section context without coupling presentation to native operations.
  const eyebrows = {
    dashboard: 'O TEU SETUP, EM SINTONIA', competitivo: 'FOCO TOTAL. CADA FRAME CONTA.',
    otimizacoes: 'MAIS CONTROLO. MAIS POTENCIAL.', jogos: 'ESCOLHE O TEU PRÓXIMO MUNDO',
    ingame: 'AFINA A TUA VANTAGEM', voz: 'A TUA CRIATIVIDADE, AO VIVO',
    sound: 'CARREGA NO PLAY', servers: 'A PRÓXIMA PARTIDA ESPERA POR TI',
    online: 'JOGAR É MELHOR EM EQUIPA', sistema: 'O MOTOR DA TUA EXPERIÊNCIA',
    bugs: 'CONSTRUÍDO COM A COMUNIDADE',
  };
  document.addEventListener('midnight:navigate', event => {
    document.getElementById('page-eyebrow').textContent = eyebrows[event.detail.page] || 'MIDNIGHT OPTIMIZER';
    const title = document.getElementById('page-title');
    const dot = document.createElement('span');
    dot.className = 'heading-dot'; dot.textContent = '.';
    title.appendChild(dot);
    title.focus({preventScroll: true});
  });
  const showConnection = () => {
    document.getElementById('connection-state').classList.add('connected');
    document.getElementById('connection-label').textContent = 'Sistema ligado';
  };
  document.addEventListener('midnight:connected', showConnection);
  if(window.midnightAPI) showConnection();

  // A persisted lightweight mode also follows the operating system preference.
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = document.getElementById('motion-toggle');
  let manualReduced = false;
  try { manualReduced = localStorage.getItem('midnight-reduced-motion') === '1'; } catch {}
  let reduced = manualReduced || media.matches;
  function syncMotion() {
    reduced = manualReduced || media.matches;
    document.body.dataset.motion = reduced ? 'reduced' : 'full';
    motionButton.setAttribute('aria-pressed', String(reduced));
    const label = reduced ? 'Ativar animações' : 'Reduzir animações';
    motionButton.title = label; motionButton.setAttribute('aria-label', label);
    scheduleAmbient();
  }
  motionButton.addEventListener('click', () => {
    if(media.matches) {
      toast('As animações estão reduzidas pela preferência de acessibilidade do sistema.');
      return;
    }
    manualReduced = !manualReduced;
    try { localStorage.setItem('midnight-reduced-motion', manualReduced ? '1' : '0'); } catch {}
    syncMotion();
    toast(reduced ? 'Efeitos reduzidos. Foco no teu jogo.' : 'Animações e efeitos ativos.');
  });
  media.addEventListener('change', syncMotion);

  // Ambient particles: 36 points, 30 fps, capped pixel ratio, no hidden-window loop.
  const canvas = document.getElementById('stars');
  const context = canvas.getContext('2d');
  const points = Array.from({length: 36}, () => ({x: Math.random(), y: Math.random(), radius: .5 + Math.random(), speed: .0003 + Math.random() * .0005}));
  let frame = 0, lastTime = 0, color = '192,247,106';
  function sizeCanvas() {
    const ratio = Math.min(devicePixelRatio || 1, 1.5);
    canvas.width = Math.round(innerWidth * ratio);
    canvas.height = Math.round(innerHeight * ratio);
    canvas.style.width = innerWidth + 'px'; canvas.style.height = innerHeight + 'px';
    context?.setTransform(ratio, 0, 0, ratio, 0, 0);
    drawAmbient(0);
  }
  function drawAmbient(delta) {
    if(!context) return;
    context.clearRect(0, 0, innerWidth, innerHeight);
    context.fillStyle = `rgba(${color},.4)`;
    for(const point of points) {
      point.y = (point.y - point.speed * delta / 40 + 1) % 1;
      context.beginPath(); context.arc(point.x * innerWidth, point.y * innerHeight, point.radius, 0, Math.PI * 2); context.fill();
    }
  }
  function animate(time) {
    if(document.hidden || reduced) { frame = 0; return; }
    if(time - lastTime >= 1000 / 30) {
      drawAmbient(Math.min(time - lastTime, 80)); lastTime = time;
    }
    frame = requestAnimationFrame(animate);
  }
  function scheduleAmbient() {
    cancelAnimationFrame(frame); frame = 0; lastTime = performance.now();
    drawAmbient(0);
    if(!document.hidden && !reduced && context) frame = requestAnimationFrame(animate);
  }
  function syncColor() {
    color = getComputedStyle(document.body).getPropertyValue('--accent-rgb').trim();
    drawAmbient(0);
  }
  window.addEventListener('resize', sizeCanvas, {passive: true});
  document.addEventListener('midnight:theme', syncColor);
  document.addEventListener('visibilitychange', () => {
    document.body.classList.toggle('app-hidden', document.hidden);
    scheduleAmbient();
  });
  sizeCanvas(); syncColor(); syncMotion();

  // Light follows the pointer only while a relevant surface is being hovered.
  let pointerFrame = 0;
  document.addEventListener('pointermove', event => {
    if(reduced || event.pointerType === 'touch') return;
    const surface = event.target.closest('.hero2, .qa');
    if(!surface) return;
    cancelAnimationFrame(pointerFrame);
    pointerFrame = requestAnimationFrame(() => {
      const bounds = surface.getBoundingClientRect();
      surface.style.setProperty('--pointer-x', `${event.clientX - bounds.left}px`);
      surface.style.setProperty('--pointer-y', `${event.clientY - bounds.top}px`);
    });
  }, {passive: true});
  document.addEventListener('click', event => {
    const button = event.target.closest('.btn');
    if(!button || reduced || button.disabled) return;
    const wave = document.createElement('span');
    const bounds = button.getBoundingClientRect();
    wave.className = 'click-wave'; wave.setAttribute('aria-hidden', 'true');
    wave.style.left = (event.detail ? event.clientX - bounds.left : bounds.width / 2) + 'px';
    wave.style.top = (event.detail ? event.clientY - bounds.top : bounds.height / 2) + 'px';
    button.appendChild(wave); wave.addEventListener('animationend', () => wave.remove(), {once: true});
    setTimeout(() => wave.remove(), 700);
  });

  document.querySelectorAll('.switch').forEach(button => {
    button.setAttribute('role', 'switch');
    button.setAttribute('aria-label', button.closest('.opt')?.querySelector('h4')?.textContent || 'Otimização');
    const sync = () => button.setAttribute('aria-checked', String(button.classList.contains('on')));
    sync(); new MutationObserver(sync).observe(button, {attributes: true, attributeFilter: ['class']});
  });

  // Keep all palettes reachable in the compact sidebar too.
  document.querySelector('.theme-switch').addEventListener('click', event => {
    const button = event.target.closest('button');
    if(button && innerWidth <= 980) document.getElementById('theme-overlay').style.display = 'flex';
  });
  document.addEventListener('keydown', event => {
    if(event.key === 'Escape') document.getElementById('theme-overlay').style.display = 'none';
  });
})();
