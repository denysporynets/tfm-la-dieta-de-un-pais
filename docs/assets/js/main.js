/* ══════════════════════════════════════════════════════════════════
   La Dieta de un País · main.js
   - Reveal on scroll (Intersection Observer)
   - Animated counters en métricas de motores
   - Carta estelar del pipeline (Canvas)
   ══════════════════════════════════════════════════════════════════ */

// ══════════════════ REVEAL ON SCROLL ══════════════════
(() => {
  const els = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  els.forEach((el) => io.observe(el));
})();

// ══════════════════ ANIMATED COUNTERS ══════════════════
(() => {
  const metrics = document.querySelectorAll('.motor-metric');
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        const el = e.target;
        const target = parseFloat(el.dataset.target);
        if (isNaN(target)) return;
        const decimals = (el.dataset.target.split('.')[1] || '').length;
        const duration = 1400;
        const start = performance.now();
        const animate = (now) => {
          const t = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - t, 3);
          el.textContent = (target * eased).toFixed(decimals);
          if (t < 1) requestAnimationFrame(animate);
          else el.textContent = target.toFixed(decimals);
        };
        requestAnimationFrame(animate);
        io.unobserve(el);
      });
    },
    { threshold: 0.5 }
  );
  metrics.forEach((m) => io.observe(m));
})();

// ══════════════════ STELLAR CHART ══════════════════
(() => {
  const canvas = document.getElementById('stellarCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const tooltip = document.getElementById('stellarTooltip');
  const ttId = tooltip.querySelector('.tt-id');
  const ttName = tooltip.querySelector('.tt-name');
  const ttDesc = tooltip.querySelector('.tt-desc');

  let W, H, CW, CH;
  const PAD = { top: 60, right: 60, bottom: 80, left: 60 };

  // AR 0-24h = eje pipeline (X)
  // Dec ±40° = eje técnica (Y)
  function toX(ar) { return PAD.left + (ar / 24) * CW; }
  function toY(dec) { return PAD.top + CH * 0.5 - (dec / 40) * (CH * 0.5); }

  // ── NODOS ──
  const nodes = [
    { id: 'FAO-001', label: 'FAOSTAT',      ar: 1.5,  dec: -8,  r: 11, color: '#f4a261', cat: 'Origen',       desc: 'Food Balance Sheets · Emissions AFOLU · Food CPI · 2010–2022' },
    { id: 'EDA-002', label: 'EDA',          ar: 4.0,  dec: 18,  r: 7,  color: '#8fb88f', cat: 'Exploración',  desc: 'Análisis exploratorio · validación de nulos · distribuciones' },
    { id: 'FE-003',  label: 'Feature Eng.', ar: 6.5,  dec: -4,  r: 8,  color: '#8fb88f', cat: 'FE',           desc: '87 ítems FAO → 7 macrocategorías · vector %DES · golden features' },
    { id: 'KMN-004', label: 'K-Means',      ar: 9.5,  dec: 26,  r: 10, color: '#2563eb', cat: 'Motor A',      desc: 'Barrido K=3..6 · K=3 elegido · Silhouette=0.40 · 98.7% estabilidad' },
    { id: 'CL-005',  label: '3 Tipologías', ar: 11.5, dec: 30,  r: 7,  color: '#60a5fa', cat: 'Output A',     desc: 'C0 Proteica · C1 Tuberosa · C2 Cereal-Dependiente' },
    { id: 'LGB-006', label: 'LightGBM',     ar: 13.5, dec: 6,   r: 11, color: '#568259', cat: 'Motor B',      desc: '5-fold CV · R²=0.864 · MAE=0.41 t/cáp · +57 pts vs baseline' },
    { id: 'SHP-007', label: 'SHAP',         ar: 15.0, dec: 14,  r: 8,  color: '#2f4a32', cat: 'Motor B',      desc: '9 drivers · top-3 replica jerarquía IPCC Poore&Nemecek' },
    { id: 'FCT-008', label: 'Forecast',     ar: 17.5, dec: 4,   r: 10, color: '#a78bfa', cat: 'Motor C',      desc: 'LightGBM Global · R² walk-forward 0.9943 · MAE 0.0064 · IC quantile' },
    { id: 'WIF-009', label: 'What-If',      ar: 19.5, dec: -12, r: 7,  color: '#22d3ee', cat: 'Interactivo',  desc: '7 sliders → lgb_final.pkl → predicción CO₂ en tiempo real' },
    { id: 'DSH-010', label: 'Dashboard',    ar: 22.0, dec: -22, r: 13, color: '#ffd54f', cat: 'Destino',      desc: '5 vistas Streamlit · avocados.streamlit.app · QR para defensa' },
    { id: 'MEM-011', label: 'Memoria',      ar: 22.5, dec: -2,  r: 8,  color: '#e8e8e8', cat: 'Destino',      desc: 'Documentación académica v1.7 · ~85% completa · entrega 16-may' },
  ];

  // ── CONEXIONES (id_origen → id_destino) ──
  const edges = [
    ['FAO-001', 'EDA-002'],
    ['FAO-001', 'FE-003'],
    ['EDA-002', 'FE-003'],
    ['FE-003',  'KMN-004'],
    ['FE-003',  'LGB-006'],
    ['KMN-004', 'CL-005'],
    ['KMN-004', 'LGB-006'],
    ['LGB-006', 'SHP-007'],
    ['LGB-006', 'FCT-008'],
    ['LGB-006', 'WIF-009'],
    ['CL-005',  'DSH-010'],
    ['FCT-008', 'DSH-010'],
    ['WIF-009', 'DSH-010'],
    ['SHP-007', 'MEM-011'],
    ['DSH-010', 'MEM-011'],
  ];

  // ── FONDO: Estrellas de ruido ──
  let noiseStars = [];
  function generateNoiseStars() {
    noiseStars = [];
    const count = Math.floor((W * H) / 4000);
    for (let i = 0; i < count; i++) {
      noiseStars.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 1.1 + 0.2,
        a: Math.random() * 0.55 + 0.1,
        tw: Math.random() * 0.02 + 0.005,
      });
    }
  }

  // ── ESTADO DE ANIMACIÓN ──
  let edgeProgress = 0;     // 0 → 1 a medida que se dibujan las líneas
  let labelAlpha = 0;       // 0 → 1 tras dibujar líneas
  let nodeGlow = 0;         // pulso del nodo destino
  let frame = 0;
  const EDGE_DURATION = 130;  // frames
  const LABEL_DELAY = 40;
  let hoveredNode = null;

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    CW = W - PAD.left - PAD.right;
    CH = H - PAD.top - PAD.bottom;
    generateNoiseStars();
  }

  function drawBg() {
    const grad = ctx.createLinearGradient(0, 0, W, H);
    grad.addColorStop(0, '#020408');
    grad.addColorStop(0.5, '#051017');
    grad.addColorStop(1, '#020408');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Nebulosa detrás del destino (DSH-010)
    const dst = nodes.find((n) => n.id === 'DSH-010');
    const nx = toX(dst.ar), ny = toY(dst.dec);
    const neb = ctx.createRadialGradient(nx, ny, 0, nx, ny, 140);
    neb.addColorStop(0, 'rgba(255, 213, 79, 0.18)');
    neb.addColorStop(0.5, 'rgba(255, 213, 79, 0.07)');
    neb.addColorStop(1, 'rgba(255, 213, 79, 0)');
    ctx.fillStyle = neb;
    ctx.fillRect(0, 0, W, H);
  }

  function drawNoise() {
    noiseStars.forEach((s) => {
      s.a += s.tw * (Math.random() > 0.5 ? 1 : -1);
      s.a = Math.max(0.08, Math.min(0.8, s.a));
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200, 220, 220, ${s.a})`;
      ctx.fill();
    });
  }

  function drawAxes() {
    ctx.save();
    ctx.strokeStyle = 'rgba(143, 184, 143, 0.15)';
    ctx.lineWidth = 0.5;
    ctx.setLineDash([2, 6]);

    // Vertical ticks (cada 4h)
    for (let ar = 0; ar <= 24; ar += 4) {
      const x = toX(ar);
      ctx.beginPath();
      ctx.moveTo(x, PAD.top);
      ctx.lineTo(x, H - PAD.bottom);
      ctx.stroke();
    }

    // Horizontal (línea Dec=0)
    ctx.setLineDash([]);
    ctx.strokeStyle = 'rgba(143, 184, 143, 0.18)';
    const y0 = toY(0);
    ctx.beginPath();
    ctx.moveTo(PAD.left, y0);
    ctx.lineTo(W - PAD.right, y0);
    ctx.stroke();

    // Etiquetas eje X
    ctx.font = '10px "Space Mono", monospace';
    ctx.fillStyle = 'rgba(143, 184, 143, 0.55)';
    ctx.textAlign = 'center';
    const xLabels = [
      [2, 'DATOS'],
      [6, 'PREP'],
      [10, 'MOTOR A'],
      [14, 'MOTOR B'],
      [18, 'MOTOR C'],
      [22, 'ENTREGA'],
    ];
    xLabels.forEach(([ar, lbl]) => {
      ctx.fillText(lbl, toX(ar), H - PAD.bottom + 22);
      ctx.fillText(`${ar}h`, toX(ar), H - PAD.bottom + 36);
    });

    // Etiquetas eje Y
    ctx.textAlign = 'right';
    ctx.fillText('UNSUP', PAD.left - 8, toY(25) + 3);
    ctx.fillText('SUPERV', PAD.left - 8, toY(5) + 3);
    ctx.fillText('FE/DATA', PAD.left - 8, toY(-10) + 3);
    ctx.fillText('OUTPUT', PAD.left - 8, toY(-22) + 3);

    ctx.restore();
  }

  function drawEdges() {
    const totalEdges = edges.length;
    const edgesDone = Math.min(totalEdges, Math.floor(edgeProgress * totalEdges));
    const partial = edgeProgress * totalEdges - edgesDone;

    for (let i = 0; i < totalEdges; i++) {
      const [fromId, toId] = edges[i];
      const from = nodes.find((n) => n.id === fromId);
      const to = nodes.find((n) => n.id === toId);
      if (!from || !to) continue;
      const x1 = toX(from.ar), y1 = toY(from.dec);
      const x2 = toX(to.ar),   y2 = toY(to.dec);

      const prog = i < edgesDone ? 1 : (i === edgesDone ? partial : 0);
      if (prog <= 0) continue;

      const ex = x1 + (x2 - x1) * prog;
      const ey = y1 + (y2 - y1) * prog;

      const grad = ctx.createLinearGradient(x1, y1, x2, y2);
      grad.addColorStop(0, from.color + '88');
      grad.addColorStop(1, to.color + '66');

      ctx.strokeStyle = grad;
      ctx.lineWidth = 1.1;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(ex, ey);
      ctx.stroke();
    }
  }

  function drawNodes() {
    const pulse = 0.3 + 0.7 * (Math.sin(frame * 0.05) * 0.5 + 0.5);

    nodes.forEach((n) => {
      const x = toX(n.ar), y = toY(n.dec);
      const isHovered = hoveredNode === n;
      const isDest = n.cat === 'Destino';

      // Halo / glow
      const haloR = n.r * (isDest ? (3.8 + pulse * 0.8) : (isHovered ? 3.2 : 2.2));
      const halo = ctx.createRadialGradient(x, y, 0, x, y, haloR);
      halo.addColorStop(0, n.color + (isDest ? 'cc' : '66'));
      halo.addColorStop(0.5, n.color + '22');
      halo.addColorStop(1, n.color + '00');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(x, y, haloR, 0, Math.PI * 2);
      ctx.fill();

      // Núcleo
      ctx.beginPath();
      ctx.arc(x, y, n.r * (isHovered ? 1.15 : 1), 0, Math.PI * 2);
      ctx.fillStyle = n.color;
      ctx.fill();
      ctx.strokeStyle = '#ffffffdd';
      ctx.lineWidth = isHovered ? 2 : 1;
      ctx.stroke();

      // Etiqueta
      if (labelAlpha > 0.05) {
        ctx.globalAlpha = labelAlpha;
        ctx.textAlign = 'center';
        ctx.font = 'bold 11px Inter, sans-serif';
        ctx.fillStyle = '#fff';
        ctx.fillText(n.label, x, y + n.r + 18);
        ctx.font = '9px "Space Mono", monospace';
        ctx.fillStyle = 'rgba(180, 200, 180, 0.65)';
        ctx.fillText(n.id, x, y + n.r + 32);
        ctx.globalAlpha = 1;
      }
    });
  }

  function render() {
    frame++;
    drawBg();
    drawNoise();
    drawAxes();

    if (edgeProgress < 1) edgeProgress += 1 / EDGE_DURATION;
    else if (labelAlpha < 1) labelAlpha = Math.min(1, labelAlpha + 1 / LABEL_DELAY);

    drawEdges();
    drawNodes();

    requestAnimationFrame(render);
  }

  // ── HOVER INTERACTION ──
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    let found = null;
    for (const n of nodes) {
      const dx = toX(n.ar) - mx;
      const dy = toY(n.dec) - my;
      if (Math.sqrt(dx * dx + dy * dy) < n.r * 2.5) {
        found = n;
        break;
      }
    }
    hoveredNode = found;
    if (found) {
      ttId.textContent = `${found.id} · ${found.cat}`;
      ttName.textContent = found.label;
      ttDesc.textContent = found.desc;
      const ttX = Math.min(mx + 18, W - 300);
      const ttY = Math.max(my - 10, 10);
      tooltip.style.left = ttX + 'px';
      tooltip.style.top = ttY + 'px';
      tooltip.classList.add('visible');
      canvas.style.cursor = 'pointer';
    } else {
      tooltip.classList.remove('visible');
      canvas.style.cursor = 'default';
    }
  });
  canvas.addEventListener('mouseleave', () => {
    hoveredNode = null;
    tooltip.classList.remove('visible');
  });

  // ── INIT ──
  window.addEventListener('resize', () => {
    resize();
  });
  resize();
  render();
})();
