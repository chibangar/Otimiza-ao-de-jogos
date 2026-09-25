/**
 * PULSE GAMING OPTIMIZER — INTERACTIVE SCRIPTS
 * Efeitos Visuais, Partículas Interativas, Demonstração Web Audio e Física 3D
 */

document.addEventListener('DOMContentLoaded', () => {
  initParticleCanvas();
  initNavbarScroll();
  initTiltEffects();
  initDemoReactor();
  initSoundboardDemo();
  initThemePicker();
  initFaqAccordion();
});

/* ==========================================================================
   1. CANVAS DE PARTÍCULAS INTERATIVAS
   ========================================================================== */
function initParticleCanvas() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  const particles = [];
  const particleCount = Math.min(65, Math.floor(width / 22));
  const mouse = { x: null, y: null, radius: 140 };

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
  });

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.size = Math.random() * 2 + 1;
      this.baseX = this.x;
      this.baseY = this.y;
      this.vx = (Math.random() - 0.5) * 0.6;
      this.vy = (Math.random() - 0.5) * 0.6;
      this.color = Math.random() > 0.4 ? 'rgba(0, 240, 255, ' : 'rgba(157, 78, 221, ';
      this.alpha = Math.random() * 0.5 + 0.2;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Interação magnética com o rato
      if (mouse.x !== null && mouse.y !== null) {
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          let force = (mouse.radius - dist) / mouse.radius;
          let dirX = (dx / dist) * force * 3;
          let dirY = (dy / dist) * force * 3;
          this.x -= dirX;
          this.y -= dirY;
        }
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = this.color + this.alpha + ')';
      ctx.fill();
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);

    // Liga partículas próximas com linhas sutis
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        let dx = particles[i].x - particles[j].x;
        let dy = particles[i].y - particles[j].y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 115) {
          let opacity = (1 - dist / 115) * 0.15;
          ctx.beginPath();
          ctx.strokeStyle = `rgba(0, 240, 255, ${opacity})`;
          ctx.lineWidth = 0.8;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    particles.forEach((p) => {
      p.update();
      p.draw();
    });

    requestAnimationFrame(animate);
  }

  animate();
}

/* ==========================================================================
   2. NAVBAR SCROLL & MOBILE TOGGLE
   ========================================================================== */
function initNavbarScroll() {
  const navbar = document.getElementById('navbar');
  const toggle = document.getElementById('nav-toggle');
  const menu = document.getElementById('nav-menu');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar?.classList.add('scrolled');
    } else {
      navbar?.classList.remove('scrolled');
    }
  });

  toggle?.addEventListener('click', () => {
    menu?.classList.toggle('open');
  });

  document.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', () => {
      menu?.classList.remove('open');
    });
  });
}

/* ==========================================================================
   3. EFEITO 3D TILT NOS CARDS
   ========================================================================== */
function initTiltEffects() {
  const cards = document.querySelectorAll('[data-tilt], #mockup-tilt');

  cards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = ((y - centerY) / centerY) * -7;
      const rotateY = ((x - centerX) / centerX) * 7;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });
}

/* ==========================================================================
   4. REATOR ORBITAL INTERATIVO & SIMULAÇÃO DE BOOST
   ========================================================================== */
function initDemoReactor() {
  const reactor = document.getElementById('demo-reactor');
  const text = document.getElementById('reactor-text');
  const sub = document.getElementById('reactor-sub');
  const cpuGauge = document.getElementById('demo-gauge-cpu');
  const gpuGauge = document.getElementById('demo-gauge-gpu');
  const ramGauge = document.getElementById('demo-gauge-ram');
  const valCpu = document.getElementById('val-cpu');
  const valGpu = document.getElementById('val-gpu');
  const valRam = document.getElementById('val-ram');

  if (!reactor) return;

  let boosted = false;

  reactor.addEventListener('click', () => {
    playCyberSound('boost');
    boosted = !boosted;

    if (boosted) {
      reactor.classList.add('active');
      text.textContent = '⚡ BOOST ATIVO';
      text.style.color = '#00f0ff';
      sub.textContent = 'LATÊNCIA: 0.5ms';
      
      // Simula animação de medidores para desempenho ultra-alto
      if (cpuGauge) cpuGauge.style.strokeDashoffset = '20';
      if (gpuGauge) gpuGauge.style.strokeDashoffset = '15';
      if (ramGauge) ramGauge.style.strokeDashoffset = '40';
      if (valCpu) valCpu.textContent = '8% (Otimizado)';
      if (valGpu) valGpu.textContent = '99% (Turbo)';
      if (valRam) valRam.textContent = '1.8 GB Usado';
    } else {
      reactor.classList.remove('active');
      text.textContent = 'MODO TURBO';
      text.style.color = '#fff';
      sub.textContent = 'CLICA PARA TESTAR';

      if (cpuGauge) cpuGauge.style.strokeDashoffset = '65';
      if (gpuGauge) gpuGauge.style.strokeDashoffset = '45';
      if (ramGauge) ramGauge.style.strokeDashoffset = '95';
      if (valCpu) valCpu.textContent = '24%';
      if (valGpu) valGpu.textContent = '38%';
      if (valRam) valRam.textContent = '4.1 GB';
    }
  });
}

/* ==========================================================================
   5. SOUNDBOARD INTERATIVO COM SÍNTESE WEB AUDIO
   ========================================================================== */
function initSoundboardDemo() {
  const cards = document.querySelectorAll('.sound-card-demo');

  cards.forEach((card) => {
    card.addEventListener('click', () => {
      const type = card.dataset.sound;
      
      cards.forEach((c) => c.classList.remove('playing'));
      card.classList.add('playing');
      const status = card.querySelector('.sound-status');
      if (status) status.textContent = '🔊 A Reproduzir…';

      playCyberSound(type);

      setTimeout(() => {
        card.classList.remove('playing');
        if (status) status.textContent = '▶ Tocar Som';
      }, 1600);
    });
  });
}

// Sintetizador de Áudio nativo Web Audio API para reprodução instantânea
function playCyberSound(type) {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === 'boost') {
      // Efeito de subida laser / energia turbo
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(150, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.4);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
      osc.start(now);
      osc.stop(now + 0.5);
    } else if (type === 'kalinka') {
      // Melodia rápida folk russa / synth
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.setValueAtTime(554, now + 0.2);
      osc.frequency.setValueAtTime(659, now + 0.4);
      osc.frequency.setValueAtTime(880, now + 0.7);
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 1.2);
      osc.start(now);
      osc.stop(now + 1.2);
    } else if (type === 'mario') {
      // Salto clássico Mario 8-bit
      osc.type = 'square';
      osc.frequency.setValueAtTime(160, now);
      osc.frequency.linearRampToValueAtTime(600, now + 0.25);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.start(now);
      osc.stop(now + 0.35);
    } else if (type === 'wow') {
      // Efeito sonoro engraçado WOW
      osc.type = 'sine';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.3);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.8);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.9);
      osc.start(now);
      osc.stop(now + 0.9);
    } else if (type === 'horn') {
      // MLG Airhorn harmónico
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(466, now); // B-flat
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.7);
      osc.start(now);
      osc.stop(now + 0.7);
    }
  } catch (e) {
    console.log('Web Audio indisponível:', e);
  }
}

/* ==========================================================================
   6. PICKER DE TEMAS
   ========================================================================== */
function initThemePicker() {
  const pills = document.querySelectorAll('.theme-pill');
  const title = document.getElementById('theme-active-title');
  const card = document.getElementById('telemetry-hud-card');

  const themes = {
    midnight: { name: '☾ WoW Midnight (Roxo/Ouro)', accent: '#00f0ff', glow: 'rgba(0,240,255,0.3)' },
    blaze: { name: '◉ CS2 Blaze (Laranja/Âmbar)', accent: '#ff6600', glow: 'rgba(255,102,0,0.3)' },
    specops: { name: '★ COD SpecOps (Verde Tático)', accent: '#00f59b', glow: 'rgba(0,245,155,0.3)' },
    frost: { name: '❄ Titanium Frost (Azul Glacial)', accent: '#70d6ff', glow: 'rgba(112,214,255,0.3)' }
  };

  pills.forEach((p) => {
    p.addEventListener('click', () => {
      pills.forEach((x) => x.classList.remove('active'));
      p.classList.add('active');
      const key = p.dataset.theme;
      const t = themes[key] || themes.midnight;

      if (title) title.textContent = t.name;
      if (card) {
        card.style.borderColor = t.accent;
        card.style.boxShadow = `0 10px 40px rgba(0,0,0,0.5), 0 0 25px ${t.glow}`;
      }
    });
  });
}

/* ==========================================================================
   7. ACCORDION DE FAQ
   ========================================================================== */
function initFaqAccordion() {
  const items = document.querySelectorAll('.faq-item');

  items.forEach((item) => {
    const question = item.querySelector('.faq-question');
    question?.addEventListener('click', () => {
      const isOpen = item.classList.contains('active');
      items.forEach((i) => i.classList.remove('active'));
      if (!isOpen) {
        item.classList.add('active');
      }
    });
  });
}
