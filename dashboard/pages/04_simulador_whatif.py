"""
04_simulador_whatif.py — Simulador What-If: ajusta la dieta → predicción CO₂ en tiempo real
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path
import streamlit.components.v1 as components


# ── CUSTOM CO₂ GAUGE ─────────────────────────────────────────────
_GAUGE_TMPL = r"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;overflow:hidden;font-family:'Inter',-apple-system,sans-serif}
#wrap{background:linear-gradient(140deg,#1a2638 0%,#0d1520 100%);border-radius:14px;
  padding:10px 14px 6px;box-shadow:0 0 40px __GLOW__}
#top{text-align:center;font-size:9px;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;color:rgba(255,255,255,.28);margin-bottom:2px}
#bot{display:flex;justify-content:center;align-items:center;gap:10px;margin-top:4px}
.zone-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;
  border-radius:20px;font-size:11px;font-weight:700;letter-spacing:.05em;
  background:__ZONE_BG__;color:__ZONE_COL__}
.ref-info{font-size:10px;color:rgba(255,255,255,.4);font-weight:400}
</style></head>
<body><div id="wrap">
  <div id="top">CO₂eq per cápita · proyección Motor B</div>
  <canvas id="g" style="display:block;margin:0 auto"></canvas>
  <div id="bot">
    <span class="zone-badge">__ZONE_ICO__ __ZONE_LBL__</span>
    <span class="ref-info">__REF_LBL__</span>
  </div>
</div>
<script>
const CO2=__CO2__;
const REF=__REF__;
const PAIS='__PAIS__';
const ZONE_COL='__ZONE_COL__';
const wrap=document.getElementById('wrap');
const c=document.getElementById('g');
const ctx=c.getContext('2d');
const W=Math.min((wrap.clientWidth||400)-28,460);
const H=Math.round(W*.56);
c.width=W;c.height=H;
const cx=W/2,cy=Math.round(H*.82);
const R1=Math.min(Math.round(W*.415),Math.round(cy*.84));
const R2=Math.round(R1*.67);
const Rn=Math.round(R1*.83);
const SA=Math.PI*.75,SW=Math.PI*1.5,MAX=12;

function va(v){return SA+Math.max(0,Math.min(MAX,v))/MAX*SW}

function lc(a,b,t){
  const p=s=>[parseInt(s.slice(1,3),16),parseInt(s.slice(3,5),16),parseInt(s.slice(5,7),16)];
  const ca=p(a),cb=p(b);
  return'rgb('+[0,1,2].map(i=>Math.round(ca[i]+(cb[i]-ca[i])*t)).join(',')+')'
}
function ac(t){
  if(t<.167)return'#0d9488';
  if(t<.333)return lc('#0d9488','#eab308',(t-.167)/.166);
  if(t<.583)return lc('#eab308','#f97316',(t-.333)/.25);
  return lc('#f97316','#ef4444',(t-.583)/.417)
}

function draw(na){
  ctx.clearRect(0,0,W,H);
  const N=280,ft=Math.max(0,(na-SA)/SW),Nf=Math.round(ft*N);

  // Outer glow ring
  const grd=ctx.createRadialGradient(cx,cy,R1*.9,cx,cy,R1*1.18);
  grd.addColorStop(0,'rgba(0,0,0,0)');
  grd.addColorStop(1,ZONE_COL.replace(')',',0.06)').replace('rgb','rgba'));
  ctx.beginPath();ctx.arc(cx,cy,R1*1.18,SA,SA+SW);
  ctx.arc(cx,cy,R1*.9,SA+SW,SA,true);ctx.closePath();
  ctx.fillStyle=grd;ctx.fill();

  // Track (dim)
  for(let i=0;i<N;i++){
    const t1=i/N,t2=(i+1)/N,a1=SA+t1*SW,a2=SA+t2*SW;
    ctx.beginPath();ctx.arc(cx,cy,R1,a1,a2);ctx.arc(cx,cy,R2,a2,a1,true);
    ctx.closePath();ctx.fillStyle=ac((t1+t2)/2);ctx.globalAlpha=.14;ctx.fill();
  }
  // Filled arc
  for(let i=0;i<Nf;i++){
    const t1=i/N,t2=(i+1)/N,a1=SA+t1*SW,a2=SA+t2*SW;
    ctx.beginPath();ctx.arc(cx,cy,R1,a1,a2);ctx.arc(cx,cy,R2,a2,a1,true);
    ctx.closePath();ctx.fillStyle=ac((t1+t2)/2);ctx.globalAlpha=.92;ctx.fill();
  }
  ctx.globalAlpha=1;

  // Tick marks
  [0,2,4,6,8,10,12].forEach(v=>{
    const a=va(v),co=Math.cos(a),si=Math.sin(a);
    const isMajor=v%4===0;
    ctx.beginPath();
    ctx.moveTo(cx+(R1+(isMajor?8:5))*co,cy+(R1+(isMajor?8:5))*si);
    ctx.lineTo(cx+(R2-(isMajor?4:2))*co,cy+(R2-(isMajor?4:2))*si);
    ctx.strokeStyle=isMajor?'rgba(255,255,255,.55)':'rgba(255,255,255,.3)';
    ctx.lineWidth=isMajor?2:1.2;ctx.stroke();
    if(isMajor||v===2||v===12){
      const fs=Math.max(9,Math.round(W*.024));
      ctx.font='500 '+fs+'px Inter,sans-serif';
      ctx.fillStyle='rgba(255,255,255,.38)';
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(v+'t',cx+(R1+21)*co,cy+(R1+21)*si);
    }
  });

  // IPCC 2t target line
  const ia=va(2),ico=Math.cos(ia),isi=Math.sin(ia);
  ctx.beginPath();
  ctx.moveTo(cx+(R1+4)*ico,cy+(R1+4)*isi);
  ctx.lineTo(cx+(R2-4)*ico,cy+(R2-4)*isi);
  ctx.strokeStyle='#4ade80';ctx.lineWidth=2.5;ctx.stroke();
  const fsi=Math.max(7,Math.round(W*.019));
  ctx.font='600 '+fsi+'px Inter,sans-serif';
  ctx.fillStyle='#4ade80';ctx.textAlign='center';ctx.textBaseline='middle';
  ctx.fillText('IPCC 2t',cx+(R1+30)*ico,cy+(R1+30)*isi);

  // Reference country marker
  if(REF!==null){
    const ra=va(REF),rco=Math.cos(ra),rsi=Math.sin(ra);
    ctx.beginPath();
    ctx.moveTo(cx+(R1+3)*rco,cy+(R1+3)*rsi);
    ctx.lineTo(cx+(R2-3)*rco,cy+(R2-3)*rsi);
    ctx.strokeStyle='rgba(255,255,255,.75)';ctx.lineWidth=2.2;
    ctx.setLineDash([3,2]);ctx.stroke();ctx.setLineDash([]);
  }

  // Needle shadow
  const nco=Math.cos(na),nsi=Math.sin(na);
  const pco=-nsi,psi=nco,bw=R1*.04,bd=R2*.14;
  ctx.beginPath();
  ctx.moveTo(cx+Rn*nco,cy+Rn*nsi);
  ctx.lineTo(cx-bd*nco+bw*pco,cy-bd*nsi+bw*psi);
  ctx.lineTo(cx-bd*nco-bw*pco,cy-bd*nsi-bw*psi);
  ctx.closePath();
  ctx.shadowColor='rgba(0,0,0,.5)';ctx.shadowBlur=10;ctx.shadowOffsetX=2;ctx.shadowOffsetY=2;
  ctx.fillStyle='rgba(255,255,255,.08)';ctx.fill();ctx.shadowBlur=0;ctx.shadowOffsetX=0;ctx.shadowOffsetY=0;

  // Needle
  ctx.beginPath();
  ctx.moveTo(cx+Rn*nco,cy+Rn*nsi);
  ctx.lineTo(cx-bd*nco+bw*pco,cy-bd*nsi+bw*psi);
  ctx.lineTo(cx-bd*nco-bw*pco,cy-bd*nsi-bw*psi);
  ctx.closePath();
  ctx.shadowColor='rgba(255,255,255,.35)';ctx.shadowBlur=6;
  ctx.fillStyle='#ffffff';ctx.fill();ctx.shadowBlur=0;

  // Cap
  ctx.beginPath();ctx.arc(cx,cy,R1*.07,0,Math.PI*2);
  ctx.fillStyle='#e2e8f0';ctx.fill();
  ctx.beginPath();ctx.arc(cx,cy,R1*.042,0,Math.PI*2);
  ctx.fillStyle='#0d1520';ctx.fill();

  // Animated value
  const disp=Math.max(0,(na-SA)/SW*MAX);
  const fs2=Math.max(20,Math.round(W*.076));
  ctx.font='700 '+fs2+'px Inter,sans-serif';
  ctx.fillStyle='#ffffff';ctx.textAlign='center';ctx.textBaseline='bottom';
  ctx.fillText(disp.toFixed(2)+' t',cx,cy-R2*.28);
  ctx.font='400 '+Math.max(9,Math.round(W*.024))+'px Inter,sans-serif';
  ctx.fillStyle='rgba(255,255,255,.38)';ctx.textBaseline='top';
  ctx.fillText('CO₂eq / cápita',cx,cy-R2*.28+2);
}

let cur=SA;
const tgt=va(CO2);
function anim(){
  cur+=(tgt-cur)*.07;
  draw(cur);
  if(Math.abs(cur-tgt)>.0015)requestAnimationFrame(anim);
  else draw(tgt);
}
anim();
</script></body></html>"""


def _make_co2_gauge(co2_pred: float, co2_ref=None, pais_ref: str = "") -> str:
    v = float(co2_pred)
    if v < 2:
        zone_ico, zone_lbl = "🌿", "SOSTENIBLE"
        zone_col, zone_bg = "rgb(52,211,153)", "rgba(13,148,136,.18)"
        glow = "rgba(13,148,136,.22)"
    elif v < 4:
        zone_ico, zone_lbl = "⚡", "MODERADO"
        zone_col, zone_bg = "rgb(250,204,21)", "rgba(234,179,8,.18)"
        glow = "rgba(234,179,8,.20)"
    elif v < 8:
        zone_ico, zone_lbl = "⚠️", "ELEVADO"
        zone_col, zone_bg = "rgb(251,146,60)", "rgba(249,115,22,.18)"
        glow = "rgba(249,115,22,.22)"
    else:
        zone_ico, zone_lbl = "🔥", "CRÍTICO"
        zone_col, zone_bg = "rgb(248,113,113)", "rgba(239,68,68,.18)"
        glow = "rgba(239,68,68,.25)"

    ref_js  = "null" if co2_ref is None else str(round(float(co2_ref), 3))
    ref_lbl = f"{pais_ref}: {co2_ref:.2f} t" if co2_ref is not None and pais_ref else ""

    return (
        _GAUGE_TMPL
        .replace("__CO2__",      str(round(v, 3)))
        .replace("__REF__",      ref_js)
        .replace("__PAIS__",     pais_ref or "")
        .replace("__GLOW__",     glow)
        .replace("__ZONE_COL__", zone_col)
        .replace("__ZONE_BG__",  zone_bg)
        .replace("__ZONE_ICO__", zone_ico)
        .replace("__ZONE_LBL__", zone_lbl)
        .replace("__REF_LBL__",  ref_lbl)
    )

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    load_clusters, load_css, render_nav,
    load_lgb_model,
    MACROS, MACRO_LABELS, MACRO_COLORS,
    CLUSTER_NAMES, CLUSTER_COLORS,
    predict_co2,
)

st.set_page_config(
    page_title="Simulador What-If · La Dieta de un País",
    page_icon="🎛️",
    layout="wide",
)
load_css()
render_nav("simulador", hide_sidebar=True)

st.title("🎛️ Simulador What-If")
st.caption(
    "Ajusta la composición dietaria con los sliders y obtén la predicción de CO₂ en tiempo real. "
    "Modelo: LightGBM (R²=0.864 · 5-fold CV)"
)

df = load_clusters()
paises = sorted(df["Area"].unique())

# ── SHAP narrativo (top-5 drivers, texto fijo basado en ranking global) ──
SHAP_NARRATIVA = [
    ("Cereales", "Principal discriminador entre tipologías. Alto % de cereales → alta varianza CO₂."),
    ("Azúcares", "Señal de dieta procesada/transición nutricional. A mayor % azúcares, mayor CO₂ asociado."),
    ("Carnes", "Coherente con IPCC: ganadería intensiva = alta huella. Efecto amplificado en C0."),
    ("Tubérculos", "Marcador clave de la tipología C1 (Nigeria). Tubérculos → baja huella por kcal."),
    ("Aceites y Grasas", "Señal de dietas de renta media-alta. Moderado impacto en CO₂."),
]

# ── LAYOUT ───────────────────────────────────────────────────────

# País selector (compacto, fila única)
col_pais, _ = st.columns([1, 2])
with col_pais:
    pais_ref = st.selectbox(
        "🌍 País de referencia (2022)",
        ["— personalizado —"] + paises,
        index=paises.index("Spain") + 1 if "Spain" in paises else 1,
        key="pais_sel",
    )

# Valores iniciales según país
if pais_ref != "— personalizado —":
    fila_ref = df[(df["Area"] == pais_ref) & (df["Year"] == 2022)]
    if fila_ref.empty:
        fila_ref = df[df["Area"] == pais_ref].sort_values("Year").iloc[[-1]]
    vals_init    = {m: float(fila_ref[m].values[0]) * 100 for m in MACROS}
    cpi_init     = float(fila_ref["Food_CPI"].values[0])
    cluster_init = int(fila_ref["cluster_id"].values[0])
    co2_ref_val  = float(fila_ref["CO2eq_t_per_capita"].values[0])
else:
    vals_init    = {m: 100 / 7 for m in MACROS}
    cpi_init     = 110.0
    cluster_init = 0
    co2_ref_val  = None

# Resetear session state cuando cambia el país
if st.session_state.get("_last_pais") != pais_ref:
    for m in MACROS:
        st.session_state[f"sl_{m}"] = max(1, int(round(vals_init[m])))
    st.session_state["sl_cpi"]     = max(50, min(500, int(round(cpi_init))))
    st.session_state["sl_cluster"] = cluster_init
    st.session_state["_last_pais"] = pais_ref

# Leer valores actuales de sliders ANTES de renderizarlos (para gauge arriba)
sliders_cur  = {m: st.session_state.get(f"sl_{m}", max(1, int(round(vals_init[m])))) for m in MACROS}
cpi_cur      = st.session_state.get("sl_cpi", max(50, min(500, int(round(cpi_init)))))
cluster_cur  = st.session_state.get("sl_cluster", cluster_init)
total_cur    = sum(sliders_cur.values()) or 1
pct_norm_cur = {m: sliders_cur[m] / total_cur for m in MACROS}
co2_pred     = predict_co2([pct_norm_cur[m] for m in MACROS], cpi_cur, cluster_cur)

# ── SECCIÓN 1: KPIs + GAUGE (ancho completo) ─────────────────────
st.markdown("---")
k1, k2, k3 = st.columns(3)
k1.metric(
    "CO₂ predicho",
    f"{co2_pred:.2f} t/cáp",
    delta=f"{co2_pred - co2_ref_val:+.2f} t vs {pais_ref}" if co2_ref_val else None,
    delta_color="inverse",
)
k2.metric("Tipología", f"C{cluster_cur} — {CLUSTER_NAMES[cluster_cur]}")
k3.metric("Referencia", f"{pais_ref}: {co2_ref_val:.2f} t" if co2_ref_val else "—")

components.html(
    _make_co2_gauge(co2_pred, co2_ref_val, pais_ref if pais_ref != "— personalizado —" else None),
    height=340,
    scrolling=False,
)

# ── SECCIÓN 2: SLIDERS 4+3 ────────────────────────────────────────
st.markdown("---")
st.markdown("**⚙️ Ajusta la composición dietaria (%)**")

row1_cols = st.columns(4)
row2_cols = st.columns(4)

sliders = {}
for i, macro in enumerate(MACROS):
    col = row1_cols[i] if i < 4 else row2_cols[i - 4]
    with col:
        sliders[macro] = st.slider(
            MACRO_LABELS[macro],
            min_value=0, max_value=100,
            value=max(1, int(round(vals_init[macro]))),
            step=1, key=f"sl_{macro}",
        )

total_raw = sum(sliders.values())
if total_raw == 0:
    st.error("Al menos una macrocategoría debe ser > 0.")
    st.stop()

pct_norm = {m: sliders[m] / total_raw for m in MACROS}

# CPI + Tipología en fila compacta
cpi_col, _, cluster_col = st.columns([1, 0.08, 2])
with cpi_col:
    cpi_slider = st.slider(
        "Food CPI (2015 = 100)", min_value=50, max_value=500,
        value=max(50, min(500, int(round(cpi_init)))), step=5, key="sl_cpi",
        help="Índice de precios de alimentos (base 2015=100). Rango real: ~45–1076.",
    )
with cluster_col:
    cluster_radio = st.radio(
        "Tipología dietaria",
        options=list(CLUSTER_NAMES.keys()),
        format_func=lambda c: f"C{c} — {CLUSTER_NAMES[c]}",
        index=cluster_init, horizontal=True, key="sl_cluster",
    )

st.info(f"Suma bruta: **{total_raw}** → normalizado automáticamente a 100 %")

# ── SECCIÓN 3: BARRAS COMPARATIVAS ───────────────────────────────
st.markdown("---")
st.markdown("**Composición dietaria del escenario**")
labels_bar = [MACRO_LABELS[m] for m in MACROS]
vals_esc   = [pct_norm[m] * 100 for m in MACROS]
colors_esc = [MACRO_COLORS[m] for m in MACROS]
x_max      = 80

fig_bars = go.Figure()
if co2_ref_val is not None:
    vals_ref = [
        float(df[(df["Area"] == pais_ref) & (df["Year"] == 2022)][m].values[0]) * 100
        for m in MACROS
    ]
    x_max = max(x_max, max(vals_ref) * 1.25, max(vals_esc) * 1.25)
    fig_bars.add_trace(go.Bar(
        x=vals_ref, y=labels_bar, orientation="h", name=f"{pais_ref} 2022",
        marker=dict(color=colors_esc, opacity=0.30, line=dict(color=colors_esc, width=1.5)),
        text=[f"{v:.1f}%" for v in vals_ref], textposition="outside",
        textfont=dict(size=11, color="#555"),
    ))
else:
    x_max = max(x_max, max(vals_esc) * 1.25)

fig_bars.add_trace(go.Bar(
    x=vals_esc, y=labels_bar, orientation="h", name="Escenario simulado",
    marker=dict(color=colors_esc, opacity=0.90),
    text=[f"{v:.1f}%" for v in vals_esc], textposition="outside",
    textfont=dict(size=11, color="#1a1a2e"),
))
fig_bars.update_layout(
    barmode="group", height=340,
    xaxis=dict(title="% calórico", range=[0, x_max], ticksuffix="%", gridcolor="#ececec"),
    yaxis=dict(title="", autorange="reversed"),
    plot_bgcolor="#ffffff",
    legend=dict(orientation="h", yanchor="bottom", y=-0.22, x=0),
    margin=dict(t=10, b=70, l=10, r=90),
)
st.plotly_chart(fig_bars, use_container_width=True)

# ── DRIVERS SHAP ──────────────────────────────────────────────────
st.markdown("---")
st.subheader("📌 Top-5 drivers de CO₂ (SHAP global)")
cols_shap = st.columns(5)
for i, (macro_name, narrativa) in enumerate(SHAP_NARRATIVA):
    with cols_shap[i]:
        st.markdown(
            f"<div style='background:#f8f9fa; border-radius:8px; padding:10px; height:100%;'>"
            f"<strong style='font-size:0.85rem;'>#{i+1} {macro_name}</strong><br>"
            f"<span style='font-size:0.78rem; color:#555;'>{narrativa}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.caption(
    "Ranking basado en |SHAP| medio global del Motor B (LightGBM, 5-fold CV, 390 obs). "
    "Los signos SHAP se interpretan con el beeswarm — en datos composicionales (suma=1.0) "
    "el SHAP medio con signo ≈ 0 es comportamiento esperado."
)

# ── SECCIÓN LITERATURA Y VISIÓN DE NEGOCIO ───────────────────────
st.markdown("---")
components.html(
    """
    <div style="background:#f5f5f7; border-radius:12px; padding:28px 32px; margin-top:8px; font-family:Inter,-apple-system,sans-serif;">

      <h3 style="color:#1a1a2e; font-size:1.15rem; font-weight:700; margin-bottom:18px;">
        📖 Acerca del Global Dietary Simulator
      </h3>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">

        <div>
          <h4 style="color:#1a1a2e; font-size:0.9rem; font-weight:700; margin-bottom:8px;">
            ¿Cómo se usa?
          </h4>
          <ol style="color:#444; font-size:0.83rem; line-height:1.75; padding-left:18px; margin:0;">
            <li><strong>Selecciona un país</strong> como punto de partida — los sliders se cargan con su dieta real de 2022.</li>
            <li><strong>Ajusta los sliders</strong> de cada macrocategoría calórica. La suma se normaliza automáticamente a 100 %.</li>
            <li><strong>Elige la tipología</strong> dietaria del escenario (C0 Proteica · C1 Tuberosa · C2 Cereal-Dependiente).</li>
            <li><strong>Lee el resultado</strong>: el gauge muestra la huella de CO₂eq predicha; las barras comparan tu escenario con el país de referencia.</li>
          </ol>
        </div>

        <div>
          <h4 style="color:#1a1a2e; font-size:0.9rem; font-weight:700; margin-bottom:8px;">
            ¿Para qué sirve?
          </h4>
          <ul style="color:#444; font-size:0.83rem; line-height:1.75; padding-left:18px; margin:0;">
            <li><strong>Políticas públicas:</strong> cuantifica el impacto de cambios dietarios antes de legislar incentivos o subsidios alimentarios.</li>
            <li><strong>Industria agroalimentaria:</strong> evalúa la huella de reformulaciones de producto o cambios en la cesta de compra.</li>
            <li><strong>Investigación nutricional:</strong> contrasta hipótesis dietarias con un modelo entrenado en datos reales FAOSTAT (2010–2022).</li>
            <li><strong>Educación:</strong> ilustra en tiempo real la relación entre patrón alimentario y emisiones de CO₂eq.</li>
          </ul>
        </div>

      </div>

      <div style="margin-top:22px; padding-top:18px; border-top:1px solid #ddd;">
        <h4 style="color:#1a1a2e; font-size:0.9rem; font-weight:700; margin-bottom:10px;">
          Base científica
        </h4>
        <p style="color:#444; font-size:0.83rem; line-height:1.7; margin:0;">
          El modelo predictivo reproduce la jerarquía de emisiones documentada por
          <strong>Poore &amp; Nemecek (2018, <em>Science</em>)</strong> — sin haber sido entrenado con esa información —,
          lo que valida su coherencia con el consenso IPCC sobre impacto agroalimentario.
          Los datos de composición dietaria provienen de las <strong>Food Balance Sheets de FAOSTAT</strong>
          (30 países · 2010–2022), y el índice de precios alimentarios de la
          <strong>FAO Food Price Index</strong> (base 2015 = 100).
          La huella de carbono objetivo integra emisiones de producción, procesado y distribución
          expresadas en <strong>CO₂ equivalente per cápita</strong> (t CO₂eq/año).
        </p>
        <p style="color:#777; font-size:0.78rem; margin-top:10px; margin-bottom:0;">
          Poore, J. &amp; Nemecek, T. (2018). Reducing food's environmental impacts through producers and consumers.
          <em>Science</em>, 360(6392), 987–992. · FAO (2024). FAOSTAT Food Balance Sheets. · IPCC (2022). AR6 WGIII Ch.12.
        </p>
      </div>

    </div>
    """,
    height=380,
    scrolling=False,
)
