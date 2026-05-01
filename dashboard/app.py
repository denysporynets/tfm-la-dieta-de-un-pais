"""
app.py — Home page del dashboard
La Dieta de un País · Aguacate Team · Nuclio DS&AI 2026
"""

import json
import numpy as np


class _NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        return super().default(obj)
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from utils import (
    load_clusters,
    load_css,
    render_nav,
    CLUSTER_NAMES,
    CLUSTER_COLORS,
    MACROS,
    MACRO_LABELS,
    COUNTRY_ISO3,
    dominant_macro,
)

# ── GALAXY HTML TEMPLATE ──────────────────────────────────────────
_GALAXY_TMPL = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;overflow:hidden;font-family:'Inter',-apple-system,sans-serif}
#wrap{position:relative;width:100%;height:600px;border-radius:16px;overflow:hidden;
  background:linear-gradient(135deg,#0a1628 0%,#0f2448 40%,#162e5c 70%,#0a1628 100%)}
#bg,#main{position:absolute;top:0;left:0;width:100%;height:100%}
#tip{position:absolute;display:none;background:rgba(5,14,26,.95);border:1px solid rgba(255,255,255,.12);
  border-radius:12px;padding:12px 16px;color:#fff;font-size:12px;pointer-events:none;
  backdrop-filter:blur(12px);z-index:20;min-width:190px;box-shadow:0 8px 32px rgba(0,0,0,.45)}
#hdr{position:absolute;top:16px;left:20px;color:rgba(255,255,255,.35);font-size:9px;
  font-weight:600;letter-spacing:.12em;text-transform:uppercase}
#legend{position:absolute;bottom:16px;left:20px;display:flex;gap:16px;align-items:center}
.li{display:flex;align-items:center;gap:6px;color:rgba(255,255,255,.5);font-size:10px;font-weight:500}
.ld{width:8px;height:8px;border-radius:50%}
#axx{position:absolute;bottom:16px;right:18px;color:rgba(255,255,255,.2);font-size:8px;
  letter-spacing:.06em;font-family:'JetBrains Mono',monospace}
#axy{position:absolute;top:50%;left:5px;transform:translateY(-50%) rotate(-90deg);
  transform-origin:center center;color:rgba(255,255,255,.2);font-size:8px;
  letter-spacing:.06em;font-family:'JetBrains Mono',monospace;white-space:nowrap}
</style></head>
<body><div id="wrap">
  <canvas id="bg"></canvas>
  <canvas id="main"></canvas>
  <div id="hdr">🌌 Galaxia Dietaria &nbsp;·&nbsp; Espacio PCA &nbsp;·&nbsp; 30 países · 2022</div>
  <div id="tip"></div>
  <div id="axy">PC2 ↕</div>
  <div id="axx">PC1 ↔</div>
  <div id="legend">
    <div class="li"><div class="ld" style="background:#26d9c7"></div>C0 Proteica (17)</div>
    <div class="li"><div class="ld" style="background:#ffd54f"></div>C1 Tuberosa (1)</div>
    <div class="li"><div class="ld" style="background:#ff8a65"></div>C2 Cereal-Dep. (11)</div>
    <div class="li"><div style="width:22px;height:1.5px;background:rgba(255,255,255,.28);border-radius:1px"></div>CO₂ = tamaño ★</div>
  </div>
</div>
<script>
const STARS=__STARS__;
const EDGES=__EDGES__;

window.addEventListener('load',()=>{
  const wrap=document.getElementById('wrap');
  const bgC=document.getElementById('bg');
  const mainC=document.getElementById('main');
  const tip=document.getElementById('tip');
  const W=wrap.clientWidth||900, H=600;
  bgC.width=mainC.width=W; bgC.height=mainC.height=H;
  const bgX=bgC.getContext('2d'), ctx=mainC.getContext('2d');

  const PAD={t:52,b:60,l:46,r:30};
  const CW=W-PAD.l-PAD.r, CH=H-PAD.t-PAD.b;
  const toX=x=>PAD.l+(x+1)/2*CW;
  const toY=y=>PAD.t+(1-(y+1)/2)*CH;
  const hex=(h)=>[parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)];

  // Background noise stars
  const bgS=Array.from({length:280},()=>({
    x:Math.random()*W, y:Math.random()*H,
    r:.25+Math.random()*.95,
    a:.08+Math.random()*.55,
    da:(Math.random()-.5)*.007
  }));
  function animBg(){
    bgX.clearRect(0,0,W,H);
    bgS.forEach(s=>{
      s.a+=s.da; if(s.a<.05||s.a>.8)s.da*=-1;
      bgX.beginPath(); bgX.arc(s.x,s.y,s.r,0,Math.PI*2);
      bgX.fillStyle=`rgba(255,255,255,${s.a})`; bgX.fill();
    });
  }
  setInterval(animBg,50);

  function drawAxes(){
    const cx=toX(0), cy=toY(0);
    ctx.save(); ctx.strokeStyle='rgba(255,255,255,.055)';
    ctx.setLineDash([3,9]); ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(PAD.l,cy); ctx.lineTo(W-PAD.r,cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx,PAD.t); ctx.lineTo(cx,H-PAD.b); ctx.stroke();
    ctx.setLineDash([]); ctx.restore();
  }

  let lineP=0, starA=0, labA=0, phase=0;

  function frame(){
    ctx.clearRect(0,0,W,H);
    drawAxes();
    if(phase===0){lineP=Math.min(1,lineP+.009); if(lineP>=1)phase=1;}
    if(phase===1){starA=Math.min(1,starA+.032);  if(starA>=1)phase=2;}
    if(phase===2){labA =Math.min(1,labA +.022);  if(labA >=1)phase=3;}

    // Constellation lines
    const vis=Math.round(lineP*EDGES.length);
    for(let i=0;i<vis;i++){
      const [ai,bi]=EDGES[i];
      const sa=STARS[ai],sb=STARS[bi];
      const [r,g,b]=hex(sa.color);
      ctx.beginPath(); ctx.moveTo(toX(sa.x),toY(sa.y)); ctx.lineTo(toX(sb.x),toY(sb.y));
      ctx.strokeStyle=`rgba(${r},${g},${b},.18)`; ctx.lineWidth=.85; ctx.stroke();
    }

    // Stars
    if(starA>0){
      STARS.forEach(s=>{
        const sx=toX(s.x),sy=toY(s.y);
        const [r,g,b]=hex(s.color);
        // Glow
        const grd=ctx.createRadialGradient(sx,sy,0,sx,sy,s.r*4.5);
        grd.addColorStop(0,`rgba(${r},${g},${b},${.38*starA})`);
        grd.addColorStop(1,`rgba(${r},${g},${b},0)`);
        ctx.beginPath(); ctx.arc(sx,sy,s.r*4.5,0,Math.PI*2);
        ctx.fillStyle=grd; ctx.fill();
        // Core
        ctx.beginPath(); ctx.arc(sx,sy,s.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(${r},${g},${b},${starA})`; ctx.fill();
        // Specular
        ctx.beginPath(); ctx.arc(sx-s.r*.28,sy-s.r*.28,s.r*.32,0,Math.PI*2);
        ctx.fillStyle=`rgba(255,255,255,${.55*starA})`; ctx.fill();
      });
    }

    // Labels
    if(labA>0){
      ctx.font='500 8px "JetBrains Mono",monospace';
      ctx.textBaseline='middle';
      STARS.forEach(s=>{
        const [r,g,b]=hex(s.color);
        ctx.fillStyle=`rgba(${r},${g},${b},${labA*.88})`;
        ctx.fillText(s.iso,toX(s.x)+s.r+4,toY(s.y)+1);
      });
    }

    requestAnimationFrame(frame);
  }
  frame();

  // Hover
  mainC.addEventListener('mousemove',e=>{
    const rect=mainC.getBoundingClientRect();
    const scX=W/rect.width, scY=H/rect.height;
    const mx=(e.clientX-rect.left)*scX, my=(e.clientY-rect.top)*scY;
    let hit=null;
    STARS.forEach(s=>{ if(Math.hypot(mx-toX(s.x),my-toY(s.y))<s.r+14)hit=s; });
    if(hit){
      const [r,g,b]=hex(hit.color);
      tip.style.display='block';
      tip.style.left=Math.min(e.offsetX+18,wrap.clientWidth-210)+'px';
      tip.style.top=Math.max(e.offsetY-75,8)+'px';
      tip.innerHTML=`
        <div style="font-size:13px;font-weight:700;color:${hit.color};margin-bottom:4px">${hit.id}</div>
        <div style="font-size:9px;color:rgba(255,255,255,.4);letter-spacing:.05em;margin-bottom:10px">${hit.cluster_name.toUpperCase()}</div>
        <div style="display:flex;gap:18px">
          <div>
            <div style="font-size:8px;color:rgba(255,255,255,.35);letter-spacing:.05em;margin-bottom:3px">CO₂EQ</div>
            <div style="font-size:17px;font-weight:700;color:rgba(${r},${g},${b},1);line-height:1">${hit.co2}</div>
            <div style="font-size:9px;color:rgba(255,255,255,.4);margin-top:1px">t / cápita</div>
          </div>
          <div>
            <div style="font-size:8px;color:rgba(255,255,255,.35);letter-spacing:.05em;margin-bottom:3px">MACRO PRINCIPAL</div>
            <div style="font-size:11px;font-weight:600;color:rgba(255,255,255,.85);margin-top:4px">${hit.dominant}</div>
          </div>
        </div>`;
    } else {
      tip.style.display='none';
    }
  });
  mainC.addEventListener('mouseleave',()=>tip.style.display='none');
});
</script></body></html>"""


def make_galaxy_html(df: pd.DataFrame) -> str:
    # Filter to 2022; fall back to last available year per country
    df22 = df[df["Year"] == 2022].copy()
    missing = set(df["Area"].unique()) - set(df22["Area"].unique())
    if missing:
        fills = (
            df[df["Area"].isin(missing)]
            .sort_values("Year")
            .groupby("Area")
            .last()
            .reset_index()
        )
        df22 = pd.concat([df22, fills], ignore_index=True)
    df22 = df22.dropna(subset=MACROS + ["CO2eq_t_per_capita", "cluster_id"])

    # PCA via numpy SVD (no sklearn dependency)
    X = df22[MACROS].values.astype(float)
    X_c = X - X.mean(axis=0)
    _, _, Vt = np.linalg.svd(X_c, full_matrices=False)
    coords = X_c @ Vt[:2].T  # (n, 2)
    for i in range(2):
        m = np.abs(coords[:, i]).max()
        if m > 0:
            normed = coords[:, i] / m  # [-1, 1]
            coords[:, i] = np.sign(normed) * np.abs(normed) ** 0.5 * 0.92

    _colors = {0: "#26d9c7", 1: "#ffd54f", 2: "#ff8a65"}
    co2_vals = df22["CO2eq_t_per_capita"].values
    co2_min, co2_max = co2_vals.min(), co2_vals.max()

    stars = []
    for i, (_, row) in enumerate(df22.iterrows()):
        co2 = float(row["CO2eq_t_per_capita"])
        r_norm = (co2 - co2_min) / max(co2_max - co2_min, 1e-9)
        cid = int(row["cluster_id"])
        dom = max(MACROS, key=lambda m: float(row[m]))
        stars.append({
            "id":           row["Area"],
            "iso":          COUNTRY_ISO3.get(row["Area"], row["Area"][:3].upper()),
            "x":            round(float(coords[i, 0]), 4),
            "y":            round(float(coords[i, 1]), 4),
            "r":            round(7.0 + r_norm * 11.0, 1),
            "color":        _colors[cid],
            "cluster":      cid,
            "cluster_name": CLUSTER_NAMES[cid],
            "co2":          round(co2, 2),
            "dominant":     MACRO_LABELS.get(dom, dom),
        })

    # Edges: k=3 nearest neighbours within same cluster
    edges, seen = [], set()
    for ai, a in enumerate(stars):
        mates = sorted(
            [(bi, b) for bi, b in enumerate(stars) if b["cluster"] == a["cluster"] and bi != ai],
            key=lambda t: (t[1]["x"] - a["x"]) ** 2 + (t[1]["y"] - a["y"]) ** 2,
        )
        for bi, _ in mates[:3]:
            key = (min(ai, bi), max(ai, bi))
            if key not in seen:
                seen.add(key)
                edges.append([ai, bi])

    return (
        _GALAXY_TMPL
        .replace("__STARS__", json.dumps(stars, cls=_NpEncoder, ensure_ascii=False))
        .replace("__EDGES__", json.dumps(edges, cls=_NpEncoder))
    )

st.set_page_config(
    page_title="La Dieta de un País",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_css()
render_nav("home", hide_sidebar=True)

# ── HEADER ───────────────────────────────────────────────────────
st.markdown(
    """
    <div style="border-bottom: 3px solid #1a1a2e; padding-bottom: 16px; margin-bottom: 24px;">
      <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.12em; color:#888;">
        Nuclio Digital School · Máster en Data Science &amp; AI · Madrid 2026
      </span>
      <h1 style="font-size:2.2rem; font-weight:800; color:#1a1a2e; margin:4px 0;">
        🥑 La Dieta de un País
      </h1>
      <p style="color:#555; font-size:0.95rem; margin:0;">
        Tipologías dietarias globales, huella de carbono y simulación de escenarios · 30 países · 2010–2030
      </p>
      <p style="color:#888; font-size:0.8rem; margin-top:6px;">
        Rafael Montero · Marina Aguinacio · Ignacio Garrido · Denys Porynets · Tutor: Pedro Costa del Amo
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPIs ─────────────────────────────────────────────────────────
df = load_clusters()
co2_medio = df[df["Year"] == 2022]["CO2eq_t_per_capita"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🌍 Países", "30", help="30 países seleccionados por máxima varianza geográfica, PIB y climática")
k2.metric("🍽️ Tipologías", "3", help="K-Means K=3 · Silhouette=0.40 · Estabilidad temporal 98.7%")
k3.metric("🤖 R² Motor B", "0.864", help="LightGBM CO₂ predictor · 5-fold CV · vs baseline LinReg 0.29")
k4.metric("📅 Serie temporal", "13 años", help="FAOSTAT Food Balance Sheets 2010–2022")
k5.metric("🌡️ CO₂ medio 2022", f"{co2_medio:.2f} t/cáp", help="CO₂eq t/cápita media de los 30 países en 2022")

st.markdown("---")

# ── GALAXIA DIETARIA ─────────────────────────────────────────────
st.markdown(
    "<p style='font-size:.78rem;color:#a8a29e;font-weight:600;letter-spacing:.08em;"
    "text-transform:uppercase;margin-bottom:8px'>"
    "🌌 Espacio dietario PCA — cada estrella es un país, tamaño = CO₂eq, color = tipología"
    "</p>",
    unsafe_allow_html=True,
)
components.html(make_galaxy_html(df), height=620, scrolling=False)

st.markdown("---")

# ── DESCRIPCIÓN DEL PROYECTO ─────────────────────────────────────
col_desc, col_motores = st.columns([1.4, 1])

with col_desc:
    st.subheader("¿Qué es este proyecto?")
    st.markdown(
        """
        Triangulamos **nutrición**, **coste** y **clima** para descubrir las tipologías dietarias
        no evidentes de 30 países y cuantificar su impacto en CO₂.

        Los datos provienen de FAOSTAT (Food Balance Sheets, Emisiones AFOLU, Food CPI)
        y cubren el período 2010–2022. Las 87 categorías de alimentos se comprimieron en
        **7 Macro-Categorías** para el análisis.

        **Hallazgo clave:** el modelo reproduce la jerarquía de impacto de Poore & Nemecek (2018)
        sin ningún conocimiento previo — el top-3 SHAP coincide con el top-3 IPCC.
        """
    )

with col_motores:
    st.subheader("Los 3 motores analíticos")
    st.markdown(
        """
        | Motor | Técnica | Output |
        |---|---|---|
        | **A — Clustering** | K-Means K=3 | 3 tipologías dietarias |
        | **B — LightGBM+SHAP** | Gradient Boosting | R²=0.864 · 9 drivers CO₂ |
        | **C — Forecast** | LightGBM Global | Proyección 2023–2030 |
        """
    )

st.markdown("---")

# ── TABLA DE CLÚSTERES ───────────────────────────────────────────
st.subheader("Las 3 tipologías dietarias descubiertas")

for cid, cname in CLUSTER_NAMES.items():
    color = CLUSTER_COLORS[cid]
    sub = df[(df["cluster_id"] == cid) & (df["Year"] == 2022)]
    paises = sorted(sub["Area"].unique())
    co2_c  = sub["CO2eq_t_per_capita"].mean()
    n_paises = len(paises)

    # macrocategoría dominante del centroide
    centroide = df[df["cluster_id"] == cid][MACROS].mean()
    top3 = centroide.nlargest(3)
    top3_str = " · ".join(f"{MACRO_LABELS[m]} {v*100:.0f}%" for m, v in top3.items())

    with st.container():
        st.markdown(
            f"""
            <div style="border-left: 5px solid {color}; padding: 12px 16px; margin-bottom: 12px;
                        background:#fafafa; border-radius: 0 8px 8px 0;">
              <strong style="color:{color}; font-size:1rem;">C{cid} — {cname}</strong>
              &nbsp;&nbsp;
              <span style="font-size:0.8rem; color:#555;">
                {n_paises} {'país' if n_paises == 1 else 'países'} · CO₂ medio {co2_c:.2f} t/cáp
              </span>
              <br/>
              <span style="font-size:0.82rem; color:#333;">
                <strong>Centroide top-3:</strong> {top3_str}
              </span>
              <br/>
              <span style="font-size:0.78rem; color:#666;">
                {' · '.join(paises)}
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── NAVEGACIÓN ───────────────────────────────────────────────────
st.subheader("Módulos del dashboard")
st.markdown(
    """
    Usa el menú lateral para navegar entre las 5 vistas:

    | Módulo | Descripción |
    |---|---|
    | **01 · Vista País** | Series temporales de composición dietaria y CO₂ por país (2010–2022) |
    | **02 · Comparador** | Radar chart comparativo entre 2–4 países |
    | **03 · Mapa Clústeres** | Mapa mundial coroplético coloreado por tipología dietaria |
    | **04 · Simulador What-If** | Ajusta la dieta con sliders → predicción CO₂ en tiempo real |
    | **05 · Motor C Forecast** | Proyección dietaria 2023–2030 con LightGBM Global |
    """
)

# ── FOOTER ───────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; font-size:0.75rem; color:#aaa; margin-top:40px;
                padding-top:16px; border-top:1px solid #eee;">
      Aguacate Team · TFM "La Dieta de un País" · Nuclio Digital School · Madrid 2026<br>
      Datos: FAOSTAT (FAO, 2023) · Modelo: LightGBM (Ke et al., 2017) · SHAP (Lundberg & Lee, 2017)
    </div>
    """,
    unsafe_allow_html=True,
)
