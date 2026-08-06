/* ══════════════════════════════════════════════════════════════════════════
   La Dieta de un País · main.js
   - mando día/noche (clave compartida con todo el portfolio)
   - fondo: el campo sembrado (estático + parallax por transform)
   - reveal al hacer scroll · contadores de las cifras de motor
   - SIMULADOR: el Motor B real, 500 árboles, corriendo aquí
   - constelación del pipeline
   ══════════════════════════════════════════════════════════════════════════ */

const MENOS_MOVIMIENTO = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ─── MANDO DÍA/NOCHE ───────────────────────────────────────────────────── */
(() => {
  const btn = document.getElementById("btnTema");
  if (!btn) return;

  const aplicar = (t) => {
    if (t === "dark") document.documentElement.setAttribute("data-theme", "dark");
    else document.documentElement.removeAttribute("data-theme");
    document.dispatchEvent(new CustomEvent("tema-cambiado"));
  };

  btn.addEventListener("click", () => {
    const oscuro = document.documentElement.getAttribute("data-theme") === "dark";
    const nuevo = oscuro ? "light" : "dark";
    try { localStorage.setItem("portfolio-tema", nuevo); } catch (e) {}
    aplicar(nuevo);
  });

  // Seguir al sistema mientras el visitante no haya elegido nada.
  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  const alCambiarSistema = (e) => {
    let guardado = null;
    try { guardado = localStorage.getItem("portfolio-tema"); } catch (err) {}
    if (guardado !== "light" && guardado !== "dark") aplicar(e.matches ? "dark" : "light");
  };
  if (mq.addEventListener) mq.addEventListener("change", alCambiarSistema);
  else if (mq.addListener) mq.addListener(alCambiarSistema);  // Safari < 14
})();

/* ─── UTILIDAD: leer un token del tema ──────────────────────────────────── */
function token(nombre) {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
}

/* ─── FONDO: EL CAMPO SEMBRADO ─────────────────────────────────────────────
   Surcos en fuga y siembra en malla con desviación. Se dibuja UNA vez (y al
   cambiar tamaño o tema); el parallax mueve el canvas por transform, sin
   redibujar. Sin bucle de animación: nada que cancelar, nada que se triplique
   con la pestaña oculta.
   ───────────────────────────────────────────────────────────────────────── */
(() => {
  const lienzo = document.getElementById("bgCampo");
  if (!lienzo) return;
  const ctx = lienzo.getContext("2d");
  let W = 0, H = 0;

  function dibujar() {
    const dpr = window.devicePixelRatio || 1;
    W = window.innerWidth;
    H = window.innerHeight * 1.35;          // margen para el parallax
    lienzo.width = W * dpr;
    lienzo.height = H * dpr;
    lienzo.style.width = W + "px";
    lienzo.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    const linea = token("--line-2") || "rgba(30,58,52,0.09)";
    const semilla = token("--sage") || "#6E7A6F";

    // surcos: convergen hacia un punto de fuga alto y fuera del encuadre
    const fugaX = W * 0.5, fugaY = -H * 0.75;
    ctx.strokeStyle = linea;
    ctx.lineWidth = 1;
    const nSurcos = Math.max(9, Math.round(W / 110));
    for (let i = 0; i <= nSurcos; i++) {
      const x = (i / nSurcos) * W * 2 - W * 0.5;
      ctx.beginPath();
      ctx.moveTo(x, H);
      ctx.lineTo(fugaX + (x - fugaX) * 0.18, fugaY + (H - fugaY) * 0.18);
      ctx.stroke();
    }

    // siembra: malla con desviación, más densa y opaca cerca del suelo
    const paso = 46;
    ctx.fillStyle = semilla;
    for (let fila = 0; fila * paso < H; fila++) {
      const y = fila * paso;
      const prof = y / H;                    // 0 arriba (lejos) → 1 abajo (cerca)
      for (let col = 0; col * paso < W; col++) {
        const x = col * paso + (fila % 2 ? paso / 2 : 0);
        // desviación determinista: la misma siembra en cada pintado
        const dx = (Math.sin(fila * 12.9898 + col * 78.233) * 43758.5453 % 1) * paso * 0.34;
        const dy = (Math.sin(col * 39.3468 + fila * 11.135) * 24634.6345 % 1) * paso * 0.34;
        ctx.globalAlpha = 0.05 + prof * 0.14;
        ctx.beginPath();
        ctx.arc(x + dx, y + dy, 0.7 + prof * 1.1, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
  }

  // parallax acotado: sin tope, el canvas se sale del buffer en scroll largo
  let pendiente = false;
  function alScroll() {
    if (pendiente || MENOS_MOVIMIENTO) return;
    pendiente = true;
    requestAnimationFrame(() => {
      const y = Math.min(window.scrollY * 0.07, window.innerHeight * 0.25);
      lienzo.style.transform = "translateY(" + -y + "px)";
      pendiente = false;
    });
  }

  let temporizador;
  window.addEventListener("resize", () => {
    clearTimeout(temporizador);
    temporizador = setTimeout(dibujar, 160);
  });
  window.addEventListener("scroll", alScroll, { passive: true });
  document.addEventListener("tema-cambiado", dibujar);
  dibujar();
})();

/* ─── REVEAL ────────────────────────────────────────────────────────────── */
(() => {
  const els = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    els.forEach((el) => el.classList.add("visible"));
    return;
  }
  const io = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("visible"); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  els.forEach((el) => io.observe(el));
})();

/* ─── CONTADORES DE LAS CIFRAS DE MOTOR ─────────────────────────────────── */
(() => {
  const cifras = document.querySelectorAll(".motor-cifra");
  if (!cifras.length || !("IntersectionObserver" in window)) return;

  const escribir = (el, v, dec) => { el.textContent = v.toFixed(dec).replace(".", ","); };

  const io = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const objetivo = parseFloat(el.dataset.objetivo);
      io.unobserve(el);
      if (isNaN(objetivo)) return;
      const dec = (el.dataset.objetivo.split(".")[1] || "").length;
      if (MENOS_MOVIMIENTO) { escribir(el, objetivo, dec); return; }

      const duracion = 1300;
      const inicio = performance.now();
      const paso = (ahora) => {
        const t = Math.min((ahora - inicio) / duracion, 1);
        escribir(el, objetivo * (1 - Math.pow(1 - t, 3)), dec);
        if (t < 1) requestAnimationFrame(paso);
        else escribir(el, objetivo, dec);   // el valor exacto, siempre, al cerrar
      };
      requestAnimationFrame(paso);
    });
  }, { threshold: 0.5 });
  cifras.forEach((c) => io.observe(c));
})();

/* ══════════════════════════════════════════════════════════════════════════
   SIMULADOR · el Motor B real
   ══════════════════════════════════════════════════════════════════════════ */
(() => {
  const raiz = document.getElementById("sim");
  if (!raiz) return;

  const MODELO = window.__DIETA_MODELO__;
  const PAISES = window.__DIETA_PAISES__;
  if (!MODELO || !PAISES) {
    raiz.innerHTML = '<p class="sim-aviso">No se ha podido cargar el modelo. El dashboard enlazado arriba hace lo mismo en el servidor.</p>';
    return;
  }

  const MACROS = ["Cereales", "Tubérculos", "Azúcares", "Aceites y grasas",
                  "Carnes", "Lácteos y huevos", "Frutas y verduras"];
  const TIPOS = ["Proteica Diversificada", "Tuberosa Subsahariana", "Cereal-Dependiente"];
  const MAX_ESCALA = 12;   // toneladas, igual que el gauge del dashboard

  /* — el evaluador: recorre los 500 árboles y suma sus hojas —
     Verificado contra booster_.predict() en 430 muestras: coincidencia exacta. */
  function predecir(x) {
    const arboles = MODELO.trees;
    let suma = 0;
    for (let k = 0; k < arboles.length; k++) {
      const a = arboles[k], f = a[0], t = a[1], l = a[2], r = a[3], v = a[4];
      if (f.length === 0) { suma += v[0]; continue; }
      let i = 0;
      for (;;) {
        const siguiente = x[f[i]] <= t[i] ? l[i] : r[i];
        if (siguiente < 0) { suma += v[-siguiente - 1]; break; }
        i = siguiente;
      }
    }
    return suma;
  }

  /* Vector de entrada: 7 proporciones normalizadas + log(CPI) + tipología.
     La normalización por la suma bruta es la misma que hace el dashboard. */
  function vector(brutos, cpi, tipo) {
    const total = brutos.reduce((a, b) => a + b, 0) || 1;
    const x = brutos.map((v) => v / total);
    x.push(Math.log(cpi));
    x.push(tipo);
    return x;
  }

  const estado = { brutos: MACROS.map(() => 14), cpi: 110, tipo: 0, pais: null };

  /* — construir los mandos — */
  const contenedor = document.getElementById("simControles");
  const mandos = MACROS.map((nombre, i) => {
    const bloque = document.createElement("div");
    bloque.className = "mando";
    bloque.innerHTML =
      '<div class="mando-fila"><label class="mando-nombre" for="m' + i + '">' + nombre + '</label>' +
      '<span class="mando-valor" id="v' + i + '">14 %</span></div>' +
      '<input type="range" id="m' + i + '" min="0" max="100" step="1" value="14" ' +
      'aria-label="' + nombre + ', porcentaje calórico">';
    contenedor.appendChild(bloque);
    return { rango: bloque.querySelector("input"), valor: bloque.querySelector(".mando-valor") };
  });

  const secundarios = document.createElement("div");
  secundarios.className = "sim-secundarios";
  secundarios.innerHTML =
    '<div class="mando"><div class="mando-fila">' +
    '<label class="mando-nombre" for="mCpi">Índice de precios de alimentos</label>' +
    '<span class="mando-valor" id="vCpi">110</span></div>' +
    '<input type="range" id="mCpi" min="50" max="500" step="5" value="110" ' +
    'aria-label="Índice de precios de alimentos, base 2015 igual a 100"></div>' +
    '<div class="mando-nombre" style="margin-top:6px">Tipología dietaria del escenario</div>' +
    '<div class="sim-tipologia" id="simTipos"></div>' +
    '<div class="sim-suma" id="simSuma"></div>';
  contenedor.appendChild(secundarios);

  const mandoCpi = secundarios.querySelector("#mCpi");
  const valorCpi = secundarios.querySelector("#vCpi");
  const cajaTipos = secundarios.querySelector("#simTipos");
  const suma = secundarios.querySelector("#simSuma");

  TIPOS.forEach((nombre, i) => {
    const etiqueta = document.createElement("label");
    etiqueta.className = "t" + i;
    etiqueta.innerHTML = '<input type="radio" name="simTipo" value="' + i + '"' +
      (i === 0 ? " checked" : "") + '><span>C' + i + ' · ' + nombre + "</span>";
    cajaTipos.appendChild(etiqueta);
  });

  /* — selector de país — */
  const selector = document.getElementById("simPais");
  PAISES.forEach((p, i) => {
    const op = document.createElement("option");
    op.value = String(i);
    op.textContent = p.n;
    selector.appendChild(op);
  });

  /* — salida — */
  const elCifra = document.getElementById("simCifra");
  const elZona = document.getElementById("simZona");
  const elDelta = document.getElementById("simDelta");
  const elIndice = document.getElementById("escalaIndice");
  const elMarcaPais = document.getElementById("marcaPais");
  const elPalancas = document.getElementById("simPalancas");
  document.getElementById("marcaIpcc").style.left = (2 / MAX_ESCALA * 100) + "%";

  function zonaDe(v) {
    if (v < 2) return ["Sostenible", "var(--co2-bajo)"];
    if (v < 4) return ["Moderado", "var(--co2-medio)"];
    if (v < 8) return ["Elevado", "var(--co2-alto)"];
    return ["Crítico", "var(--co2-alto)"];
  }

  const num = (v, d) => v.toFixed(d).replace(".", ",");

  function actualizar() {
    const co2 = predecir(vector(estado.brutos, estado.cpi, estado.tipo));
    const [nombreZona, color] = zonaDe(co2);

    elCifra.textContent = num(co2, 2);
    raiz.style.setProperty("--co2", color);
    elZona.textContent = nombreZona;
    elIndice.style.left = Math.max(0, Math.min(100, co2 / MAX_ESCALA * 100)) + "%";

    const total = estado.brutos.reduce((a, b) => a + b, 0);
    suma.textContent = total === 0
      ? "Sube alguna macrocategoría: la dieta no puede ser cero."
      : "Suma bruta " + total + " % → normalizada a 100 % antes de entrar al modelo.";

    // referencia contra el país de partida
    const p = estado.pais;
    if (p) {
      const d = co2 - p.co2;
      elDelta.textContent = (d >= 0 ? "+" : "−") + num(Math.abs(d), 2) +
        " t frente a " + p.n + " (" + num(p.co2, 2) + " t observadas en 2022)";
      elMarcaPais.hidden = false;
      elMarcaPais.style.left = Math.max(0, Math.min(100, p.co2 / MAX_ESCALA * 100)) + "%";
      elMarcaPais.setAttribute("data-nota", p.n);
    } else {
      elDelta.textContent = "Elige un país arriba para comparar con su dieta real.";
      elMarcaPais.hidden = true;
    }

    palancas(co2);
  }

  /* Sensibilidad local: mueve cada macro ±2 puntos y vuelve a preguntar al
     modelo. Es medición en vivo, no el ranking SHAP global del informe.

     Un modelo de árboles no responde con una curva suave, sino con escalones:
     al cruzar el umbral de una rama la predicción salta de golpe. Recorremos
     el tramo en cuartos para detectarlo — si un solo cuarto concentra casi
     todo el cambio, el número no es una pendiente, es un acantilado, y se
     marca como tal en vez de presentarlo como si fuera gradual. */
  function tramo(i, delta) {
    const pasos = [];
    for (let k = 1; k <= 4; k++) {
      const b = estado.brutos.slice();
      b[i] = Math.max(0, Math.min(100, b[i] + delta * k / 4));
      pasos.push(predecir(vector(b, estado.cpi, estado.tipo)));
    }
    return pasos;
  }

  function palancas(base) {
    const efectos = MACROS.map((nombre, i) => {
      const subida = tramo(i, 2), bajada = tramo(i, -2);
      const dArriba = subida[3] - base, dAbajo = bajada[3] - base;
      const usaSubida = Math.abs(dArriba) >= Math.abs(dAbajo);
      const efecto = usaSubida ? dArriba : dAbajo;
      const pasos = [base].concat(usaSubida ? subida : bajada);

      // ¿un solo cuarto se lleva más del 70 % del recorrido?
      let mayorSalto = 0;
      for (let k = 1; k < pasos.length; k++) mayorSalto = Math.max(mayorSalto, Math.abs(pasos[k] - pasos[k - 1]));
      const escalon = Math.abs(efecto) > 0.2 && mayorSalto > Math.abs(efecto) * 0.7;

      return { nombre, efecto, escalon, signo: usaSubida ? "+2" : "−2" };
    }).sort((a, b) => Math.abs(b.efecto) - Math.abs(a.efecto)).slice(0, 5);

    const mayor = Math.abs(efectos[0].efecto) || 1;
    elPalancas.innerHTML = efectos.map((e) => {
      const pct = Math.abs(e.efecto) / mayor * 100;
      const clase = e.efecto >= 0 ? "palanca-sube" : "palanca-baja";
      const texto = (e.efecto >= 0 ? "+" : "−") + num(Math.abs(e.efecto), 3) + " t";
      const aviso = e.escalon
        ? ' <abbr class="escalon" title="No es una pendiente: el modelo cruza aquí el umbral de una rama y la predicción salta de golpe.">escalón</abbr>'
        : "";
      return '<li class="' + clase + '"><span>' + e.nombre + ' <small>' + e.signo +
        " pts</small>" + aviso + '</span><span class="palanca-cifra">' + texto + "</span>" +
        '<span class="palanca-barra"><i style="width:' + pct.toFixed(1) + '%"></i></span></li>';
    }).join("");
  }

  /* — sincronizar controles con el estado — */
  function pintarControles() {
    mandos.forEach((m, i) => {
      m.rango.value = String(estado.brutos[i]);
      m.valor.textContent = estado.brutos[i] + " %";
    });
    mandoCpi.value = String(estado.cpi);
    valorCpi.textContent = String(estado.cpi);
    const radio = cajaTipos.querySelector('input[value="' + estado.tipo + '"]');
    if (radio) radio.checked = true;
  }

  function cargarPais(indice) {
    if (indice === "") {
      estado.pais = null;
      estado.brutos = MACROS.map(() => 14);
      estado.cpi = 110;
      estado.tipo = 0;
    } else {
      const p = PAISES[Number(indice)];
      estado.pais = p;
      // el dashboard redondea a entero el porcentaje de cada macro
      estado.brutos = p.p.map((v) => Math.max(1, Math.round(v * 100)));
      estado.cpi = Math.max(50, Math.min(500, Math.round(p.cpi / 5) * 5));
      estado.tipo = p.c;
    }
    pintarControles();
    actualizar();
  }

  mandos.forEach((m, i) => {
    m.rango.addEventListener("input", () => {
      estado.brutos[i] = Number(m.rango.value);
      m.valor.textContent = estado.brutos[i] + " %";
      actualizar();
    });
  });
  mandoCpi.addEventListener("input", () => {
    estado.cpi = Number(mandoCpi.value);
    valorCpi.textContent = String(estado.cpi);
    actualizar();
  });
  cajaTipos.addEventListener("change", (e) => {
    if (e.target.name !== "simTipo") return;
    estado.tipo = Number(e.target.value);
    actualizar();
  });
  selector.addEventListener("change", () => cargarPais(selector.value));
  document.getElementById("simReiniciar").addEventListener("click", () => cargarPais(selector.value));

  // arranca en España si está, que es el mismo arranque que el dashboard
  const espana = PAISES.findIndex((p) => p.n === "España");
  selector.value = espana >= 0 ? String(espana) : "";
  cargarPais(selector.value);
})();

/* ══════════════════════════════════════════════════════════════════════════
   CONSTELACIÓN DEL PIPELINE
   ══════════════════════════════════════════════════════════════════════════ */
(() => {
  const lienzo = document.getElementById("stellarCanvas");
  if (!lienzo) return;
  const ctx = lienzo.getContext("2d");
  const pista = document.getElementById("stellarTooltip");
  const pId = pista.querySelector(".pista-id");
  const pNombre = pista.querySelector(".pista-nombre");
  const pDesc = pista.querySelector(".pista-desc");

  let W = 0, H = 0, CW = 0, CH = 0, estrecho = false;
  /* El margen izquierdo lo dicta el texto más largo del eje Y: con 62 px,
     "NO SUPERV." a 10 px mono se salía del lienzo por la izquierda. En
     pantallas estrechas no se regatea espacio, se quitan las etiquetas. */
  const MARGEN = { arriba: 46, derecha: 54, abajo: 66, izquierda: 88 };

  const NODOS = [
    { id: "FAO-001", etiqueta: "FAOSTAT",      x: 1.5,  y: -8,  r: 11, tono: "brass",  cat: "Origen",      desc: "Food Balance Sheets · Emissions AFOLU · Food CPI · 2010–2022" },
    { id: "EDA-002", etiqueta: "EDA",          x: 4.0,  y: 18,  r: 7,  tono: "sage",   cat: "Exploración", desc: "Análisis exploratorio · validación de nulos · distribuciones" },
    { id: "FE-003",  etiqueta: "Features",     x: 6.5,  y: -4,  r: 8,  tono: "sage",   cat: "FE",          desc: "87 ítems FAO → 7 macrocategorías · vector %DES" },
    { id: "KMN-004", etiqueta: "K-Means",      x: 9.5,  y: 26,  r: 10, tono: "t0",     cat: "Motor A",     desc: "Barrido K=3..6 · K=3 elegido · Silhouette 0,40 · 98,7 % de estabilidad" },
    { id: "CL-005",  etiqueta: "3 tipologías", x: 11.5, y: 30,  r: 7,  tono: "t0",     cat: "Salida A",    desc: "C0 Proteica · C1 Tuberosa · C2 Cereal-Dependiente" },
    { id: "LGB-006", etiqueta: "LightGBM",     x: 13.5, y: 6,   r: 11, tono: "t1",     cat: "Motor B",     desc: "5-fold CV · R² 0,864 · MAE 0,41 t/cáp · +57 puntos sobre el baseline" },
    { id: "SHP-007", etiqueta: "SHAP",         x: 15.0, y: 14,  r: 8,  tono: "t1",     cat: "Motor B",     desc: "9 drivers · el top-3 replica la jerarquía de Poore & Nemecek" },
    { id: "FCT-008", etiqueta: "Forecast",     x: 17.5, y: 4,   r: 10, tono: "t2",     cat: "Motor C",     desc: "LightGBM Global · R² walk-forward 0,9943 · MAE 0,0064 · IC por quantile" },
    { id: "WIF-009", etiqueta: "What-If",      x: 19.5, y: -12, r: 7,  tono: "t2",     cat: "Interactivo", desc: "7 controles → lgb_final.pkl → predicción de CO₂ al vuelo. Es el de esta página." },
    { id: "DSH-010", etiqueta: "Dashboard",    x: 22.0, y: -22, r: 13, tono: "signal", cat: "Destino",     desc: "5 vistas Streamlit · avocados.streamlit.app" },
    { id: "MEM-011", etiqueta: "Memoria",      x: 22.5, y: -2,  r: 8,  tono: "pine",   cat: "Destino",     desc: "Documentación académica del TFM · defendida en 2026" },
  ];

  const ARISTAS = [
    ["FAO-001", "EDA-002"], ["FAO-001", "FE-003"], ["EDA-002", "FE-003"],
    ["FE-003", "KMN-004"], ["FE-003", "LGB-006"], ["KMN-004", "CL-005"],
    ["KMN-004", "LGB-006"], ["LGB-006", "SHP-007"], ["LGB-006", "FCT-008"],
    ["LGB-006", "WIF-009"], ["CL-005", "DSH-010"], ["FCT-008", "DSH-010"],
    ["WIF-009", "DSH-010"], ["SHP-007", "MEM-011"], ["DSH-010", "MEM-011"],
  ];

  const porId = new Map(NODOS.map((n) => [n.id, n]));   // una vez, no por fotograma
  let colores = {};
  function leerColores() {
    colores = {
      brass: token("--brass"), sage: token("--sage"), pine: token("--pine"),
      signal: token("--signal"), t0: token("--t0"), t1: token("--t1"), t2: token("--t2"),
      linea: token("--line"), tinta: token("--ink"), papel: token("--paper-2"),
      // el texto del diagrama usa la tinta legible, no el gris decorativo
      sageTinta: token("--sage-tinta"),
    };
  }
  const colorDe = (n) => colores[n.tono] || colores.pine;

  const aX = (v) => MARGEN.izquierda + (v / 24) * CW;
  const aY = (v) => MARGEN.arriba + CH * 0.5 - (v / 40) * (CH * 0.5);

  let progresoAristas = 0, alfaEtiquetas = 0, fotograma = 0, sobreNodo = null;
  const DURACION = 110, RETARDO = 34;

  function medir() {
    const dpr = window.devicePixelRatio || 1;
    const caja = lienzo.getBoundingClientRect();
    W = caja.width; H = caja.height;
    if (!W || !H) return;
    lienzo.width = W * dpr; lienzo.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    estrecho = W < 620;
    MARGEN.izquierda = estrecho ? 24 : 88;
    MARGEN.derecha = estrecho ? 24 : 54;
    MARGEN.abajo = estrecho ? 48 : 66;
    CW = W - MARGEN.izquierda - MARGEN.derecha;
    CH = H - MARGEN.arriba - MARGEN.abajo;
  }

  function ejes() {
    ctx.save();
    ctx.strokeStyle = colores.linea;
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 6]);
    for (let v = 0; v <= 24; v += 4) {
      ctx.beginPath();
      ctx.moveTo(aX(v), MARGEN.arriba);
      ctx.lineTo(aX(v), H - MARGEN.abajo);
      ctx.stroke();
    }
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(MARGEN.izquierda, aY(0));
    ctx.lineTo(W - MARGEN.derecha, aY(0));
    ctx.stroke();

    ctx.font = '10px "IBM Plex Mono", monospace';
    ctx.fillStyle = colores.sageTinta;
    ctx.textAlign = "center";
    // en estrecho solo los tres hitos: seis etiquetas se solapan
    (estrecho
      ? [[2, "DATOS"], [13, "MOTORES"], [22, "ENTREGA"]]
      : [[2, "DATOS"], [6, "PREPARACIÓN"], [10, "MOTOR A"], [14, "MOTOR B"], [18, "MOTOR C"], [22, "ENTREGA"]]
    ).forEach(([v, txt]) => ctx.fillText(txt, aX(v), H - MARGEN.abajo + 22));

    if (!estrecho) {
      ctx.textAlign = "right";
      [[25, "NO SUPERV."], [5, "SUPERVISADO"], [-10, "DATOS/FE"], [-22, "SALIDA"]]
        .forEach(([v, txt]) => ctx.fillText(txt, MARGEN.izquierda - 10, aY(v) + 3));
    }
    ctx.restore();
  }

  function aristas() {
    const hechas = Math.min(ARISTAS.length, Math.floor(progresoAristas * ARISTAS.length));
    const parcial = progresoAristas * ARISTAS.length - hechas;
    ctx.lineWidth = 1.1;
    for (let i = 0; i < ARISTAS.length; i++) {
      const desde = porId.get(ARISTAS[i][0]), hasta = porId.get(ARISTAS[i][1]);
      if (!desde || !hasta) continue;
      const avance = i < hechas ? 1 : (i === hechas ? parcial : 0);
      if (avance <= 0) continue;
      const x1 = aX(desde.x), y1 = aY(desde.y);
      const x2 = aX(hasta.x), y2 = aY(hasta.y);
      const grad = ctx.createLinearGradient(x1, y1, x2, y2);
      grad.addColorStop(0, colorDe(desde));
      grad.addColorStop(1, colorDe(hasta));
      ctx.strokeStyle = grad;
      ctx.globalAlpha = 0.5;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x1 + (x2 - x1) * avance, y1 + (y2 - y1) * avance);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  function nodos() {
    const pulso = 0.35 + 0.65 * (Math.sin(fotograma * 0.045) * 0.5 + 0.5);
    NODOS.forEach((n) => {
      const x = aX(n.x), y = aY(n.y);
      const encima = sobreNodo === n;
      const destino = n.cat === "Destino";
      const color = colorDe(n);

      ctx.globalAlpha = destino ? 0.10 + pulso * 0.10 : (encima ? 0.20 : 0.10);
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, n.r * (encima ? 3.0 : 2.3), 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;

      ctx.beginPath();
      ctx.arc(x, y, n.r * (encima ? 1.12 : 1), 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = colores.papel;
      ctx.lineWidth = encima ? 2.4 : 1.4;
      ctx.stroke();

      if (alfaEtiquetas > 0.05) {
        ctx.globalAlpha = alfaEtiquetas;
        ctx.textAlign = "center";
        ctx.font = '500 11px "IBM Plex Sans", sans-serif';
        ctx.fillStyle = colores.tinta;
        ctx.fillText(n.etiqueta, x, y + n.r + 17);
        ctx.font = '9px "IBM Plex Mono", monospace';
        ctx.fillStyle = colores.sageTinta;
        ctx.fillText(n.id, x, y + n.r + 30);
        ctx.globalAlpha = 1;
      }
    });
  }

  function pintar() {
    ctx.clearRect(0, 0, W, H);
    ejes();
    aristas();
    nodos();
  }

  /* El bucle solo corre cuando hace falta: si la pestaña se oculta o el
     diagrama sale de pantalla, se cancela. Sin esto, cada vuelta a la pestaña
     suma un rAF y los redibujados se multiplican. */
  let animando = false, id = 0, visible = false;

  function vuelta() {
    fotograma++;
    if (progresoAristas < 1) progresoAristas += 1 / DURACION;
    else if (alfaEtiquetas < 1) alfaEtiquetas = Math.min(1, alfaEtiquetas + 1 / RETARDO);
    pintar();
    // el pulso del destino no para nunca; el resto sí converge
    id = requestAnimationFrame(vuelta);
  }

  function arrancar() {
    if (animando || !visible || document.hidden) return;
    if (MENOS_MOVIMIENTO) { progresoAristas = 1; alfaEtiquetas = 1; pintar(); return; }
    animando = true;
    id = requestAnimationFrame(vuelta);
  }
  function parar() {
    if (!animando) return;
    cancelAnimationFrame(id);
    animando = false;
  }

  if ("IntersectionObserver" in window) {
    new IntersectionObserver((entradas) => {
      visible = entradas[0].isIntersecting;
      if (visible) arrancar(); else parar();
    }, { threshold: 0.05 }).observe(lienzo);
  } else {
    visible = true;
  }
  document.addEventListener("visibilitychange", () => { if (document.hidden) parar(); else arrancar(); });
  document.addEventListener("tema-cambiado", () => { leerColores(); pintar(); });

  /* — señalar un nodo: ratón y táctil — */
  function señalar(clienteX, clienteY) {
    const caja = lienzo.getBoundingClientRect();
    const mx = clienteX - caja.left, my = clienteY - caja.top;
    let hallado = null;
    for (const n of NODOS) {
      const dx = aX(n.x) - mx, dy = aY(n.y) - my;
      if (Math.sqrt(dx * dx + dy * dy) < Math.max(n.r * 2.5, 22)) { hallado = n; break; }
    }
    sobreNodo = hallado;
    if (hallado) {
      pId.textContent = hallado.id + " · " + hallado.cat;
      pNombre.textContent = hallado.etiqueta;
      pDesc.textContent = hallado.desc;
      pista.style.left = Math.min(mx + 16, Math.max(0, W - 292)) + "px";
      pista.style.top = Math.max(my - 8, 8) + "px";
      pista.classList.add("visible");
      lienzo.style.cursor = "pointer";
    } else {
      pista.classList.remove("visible");
      lienzo.style.cursor = "default";
    }
    if (MENOS_MOVIMIENTO) pintar();
  }

  lienzo.addEventListener("pointermove", (e) => señalar(e.clientX, e.clientY));
  lienzo.addEventListener("pointerdown", (e) => señalar(e.clientX, e.clientY));
  lienzo.addEventListener("pointerleave", () => {
    sobreNodo = null;
    pista.classList.remove("visible");
    if (MENOS_MOVIMIENTO) pintar();
  });

  let temporizador;
  window.addEventListener("resize", () => {
    clearTimeout(temporizador);
    temporizador = setTimeout(() => { medir(); pintar(); }, 160);
  });

  leerColores();
  medir();
  pintar();
  arrancar();
})();
