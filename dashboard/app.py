"""
PulpFiction 2.0 — Dashboard Hotel Pulp Fiction
================================================
Tema: Cisco Design System (dark enterprise)
Stack: Streamlit + Plotly + SQLite
Datos 100% sintéticos | Empresa única: Hotel Pulp Fiction SpA
"""

import sqlite3
from datetime import date
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "pulp-fiction-v2.db")

st.set_page_config(
    page_title="Hotel Pulp Fiction — Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# CISCO DESIGN TOKENS
# ──────────────────────────────────────────────
CISCO = {
    "bg":          "#0f1720",
    "surface":     "#1b2530",
    "surface2":    "#243447",
    "fg":          "#ffffff",
    "fg2":         "#e8ebf1",
    "muted":       "#9e9ea2",
    "accent":      "#049fd9",
    "accent_hover":"#0388ba",
    "border":      "#58585b",
    "border_soft": "rgba(232,235,241,0.12)",
    "success":     "#6cc04a",
    "warn":        "#ffcc00",
    "danger":      "#cf2030",
    "font":        "Inter, 'Segoe UI', Arial, sans-serif",
}

# Chart colors (Cisco-aligned)
CHART_COLORS = ["#049fd9", "#64bbe3", "#6cc04a", "#ffcc00", "#cf2030", "#ff7300", "#9e9ea2"]

# ──────────────────────────────────────────────
# CSS (Cisco dark theme)
# ──────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * {{ font-family: 'Inter', {CISCO["font"]}; }}
    .stApp, .stApp > header {{ background-color: {CISCO["bg"]} !important; }}
    .block-container {{ padding: 1rem 2.5rem !important; max-width: 1440px; }}
    
    /* Page nav */
    .page-nav {{
        display: flex; gap: 4px; margin-bottom: 20px;
        background: {CISCO["surface"]}; padding: 4px;
        border-radius: 10px; border: 1px solid {CISCO["border_soft"]};
        width: fit-content;
    }}
    .page-btn {{
        padding: 8px 20px; border-radius: 8px; cursor: pointer;
        font-size: 13px; font-weight: 500; border: none;
        background: transparent; color: {CISCO["muted"]};
        transition: all 0.15s ease;
    }}
    .page-btn:hover {{ color: {CISCO["fg2"]}; background: rgba(255,255,255,0.04); }}
    .page-btn.active {{
        background: {CISCO["accent"]}; color: #001923; font-weight: 600;
    }}

    /* KPI Card */
    .kpi-card {{
        background: {CISCO["surface"]}; border-radius: 10px;
        border: 1px solid {CISCO["border_soft"]};
        padding: 18px 20px; height: 100%;
        display: flex; flex-direction: column; justify-content: center;
    }}
    .kpi-value {{ font-size: 26px; font-weight: 700; color: {CISCO["fg"]}; line-height: 1.2; }}
    .kpi-label {{ font-size: 11px; font-weight: 600; color: {CISCO["muted"]}; text-transform: uppercase; letter-spacing: 0.6px; margin-top: 3px; }}
    .kpi-sub {{ font-size: 11px; color: {CISCO["muted"]}; margin-top: 2px; opacity: 0.7; }}

    /* Section title */
    .section-title {{
        font-size: 15px; font-weight: 600; color: {CISCO["fg2"]};
        margin: 20px 0 14px 0; padding-bottom: 8px;
        border-bottom: 1px solid {CISCO["border_soft"]};
    }}

    /* Filters bar */
    .filters-bar {{
        background: {CISCO["surface"]}; border-radius: 10px;
        padding: 12px 18px; margin-bottom: 20px;
        border: 1px solid {CISCO["border_soft"]};
        display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
    }}
    .filters-bar label {{ font-size: 11px; color: {CISCO["muted"]}; margin-right: 4px; }}

    /* DataFrame */
    .stDataFrame {{ background: transparent; }}
    .stDataFrame [data-testid="StyledDataFrame"] {{ background: {CISCO["surface"]}; border-radius: 10px; border: 1px solid {CISCO["border_soft"]}; }}

    /* Text inputs */
    .stTextInput input {{
        background: {CISCO["surface"]} !important; border: 1px solid {CISCO["border"]} !important;
        border-radius: 8px !important; color: {CISCO["fg"]} !important;
    }}

    /* Select boxes */
    .stSelectbox [data-baseweb="select"] > div {{
        background: {CISCO["surface2"]} !important; border: 1px solid {CISCO["border"]} !important;
        border-radius: 8px !important; color: {CISCO["fg"]} !important;
    }}

    /* Date inputs */
    .stDateInput input {{
        background: {CISCO["surface2"]} !important; border: 1px solid {CISCO["border"]} !important;
        border-radius: 8px !important; color: {CISCO["fg"]} !important;
    }}

    /* Slider */
    .stSlider {{ padding-top: 4px; }}
    .stSlider [data-baseweb="slider"] div {{ color: {CISCO["accent"]} !important; }}

    h1 {{ font-size: 20px; font-weight: 700; color: {CISCO["fg"]}; margin: 0 0 2px 0; }}
    .subtitle {{ font-size: 12px; color: {CISCO["muted"]}; margin: 0 0 16px 0; }}
    footer, #MainMenu, .stDeployButton {{ display: none !important; }}
    .stAlert {{ border-radius: 8px; }}
    p, li, .stMarkdown {{ color: {CISCO["fg2"]}; }}
    hr {{ border-color: {CISCO["border_soft"]} !important; margin: 4px 0 !important; }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# AUTO-GENERATE DB (fallback)
# ──────────────────────────────────────────────
if not os.path.exists(DB_PATH):
    st.error("""
    Base de datos no encontrada. 
    
    Este proyecto requiere el archivo `data/pulp-fiction-v2.db` para funcionar.
    
    Si clonaste el repositorio, asegúrate de que el archivo .db esté presente.
    En Streamlit Cloud el archivo se incluye automáticamente en el despliegue.
    """)
    st.stop()


# ──────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_boletas():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM boletas ORDER BY fecha, hora", conn)
    conn.close()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["anio_mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["hora_num"] = df["hora"].str.split(":").str[0].astype(int)
    return df


@st.cache_data(ttl=300)
def cargar_indicadores():
    conn = sqlite3.connect(DB_PATH)
    im = pd.read_sql("SELECT * FROM indicadores_mensuales ORDER BY anio, mes", conn)
    rd = pd.read_sql("SELECT * FROM resumen_diario ORDER BY fecha", conn)
    conn.close()
    im["periodo"] = im["anio"].astype(str) + "-" + im["mes"].astype(str).str.zfill(2)
    rd["fecha"] = pd.to_datetime(rd["fecha"])
    return im, rd


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def fmt(v):
    if v is None or pd.isna(v): return "$0"
    return f"${int(v):,}".replace(",", ".")

def fmtn(v):
    if v is None or pd.isna(v): return "0"
    return f"{int(v):,}".replace(",", ".")


# ──────────────────────────────────────────────
# PAGE NAVIGATION
# ──────────────────────────────────────────────
PAGES = {
    "📊 Resumen":  "resumen",
    "💰 IVA":      "iva",
    "💳 Ventas":   "ventas",
    "🏦 Pagos":    "pagos",
    "📋 Detalle":  "detalle",
}
if "page" not in st.session_state:
    st.session_state.page = "resumen"

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
col_h1, col_h2 = st.columns([1, 4])
with col_h1:
    st.markdown(f'<h1>🏨 Hotel Pulp Fiction</h1>', unsafe_allow_html=True)
with col_h2:
    st.markdown(f'<p class="subtitle">Dashboard de Ventas e IVA · RUT 12.345.678-9 · Datos 100% sintéticos</p>', unsafe_allow_html=True)

# Page nav
nav_html = '<div class="page-nav">'
for label, page_id in PAGES.items():
    cls = "page-btn active" if st.session_state.page == page_id else "page-btn"
    nav_html += f'<button class="{cls}" onclick="document.querySelector(\'#page-input\').value=\'{page_id}\'; document.querySelector(\'#page-input\').form.submit();">{label}</button>'
nav_html += '</div>'
# Hidden input trick for page switching via session_state
nav_html += f'<input type="hidden" id="page-input" value="{st.session_state.page}">'

# Use columns with buttons for page switching
cols = st.columns(len(PAGES))
for i, (label, page_id) in enumerate(PAGES.items()):
    with cols[i]:
        if st.button(label, use_container_width=True, type="secondary" if st.session_state.page != page_id else "primary"):
            st.session_state.page = page_id
            st.rerun()


# ──────────────────────────────────────────────
# FILTERS (clean bar)
# ──────────────────────────────────────────────
df_raw = cargar_boletas()
f_min, f_max = df_raw["fecha"].min().date(), df_raw["fecha"].max().date()

st.markdown('<div class="filters-bar">', unsafe_allow_html=True)
cf1, cf2, cf3, cf4, cf5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.8])
with cf1:
    fecha_desde = st.date_input("Desde", f_min, label_visibility="collapsed")
with cf2:
    fecha_hasta = st.date_input("Hasta", f_max, label_visibility="collapsed")
with cf3:
    tp_opts = ["Todos", "Credito", "Debito", "Efectivo"]
    tp_sel = st.selectbox("Tipo", tp_opts, label_visibility="collapsed")
with cf4:
    mp_opts = ["Todos"] + sorted([m for m in df_raw["medio_pago"].dropna().unique().tolist()])
    mp_sel = st.selectbox("Medio", mp_opts, label_visibility="collapsed")
with cf5:
    mn, mx = int(df_raw["total"].min()), int(df_raw["total"].max())
    monto_r = st.slider("Monto", mn, mx, (mn, mx), label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# FILTER
# ──────────────────────────────────────────────
def filtrar(df):
    m = (
        (df["fecha"].dt.date >= fecha_desde) & (df["fecha"].dt.date <= fecha_hasta)
        & (df["total"] >= monto_r[0]) & (df["total"] <= monto_r[1])
    )
    if tp_sel != "Todos": m &= df["tipo_pago"] == tp_sel
    if mp_sel != "Todos": m &= df["medio_pago"] == mp_sel
    return df[m].copy()

df = filtrar(df_raw)
if df.empty:
    st.warning("Sin datos con estos filtros.")
    st.stop()

im_df, rd_df = cargar_indicadores()

# ──────────────────────────────────────────────
# PAGE RENDERERS
# ──────────────────────────────────────────────

def kpi_card(val, label, sub=None):
    return f'<div class="kpi-card"><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div>{"<div class=kpi-sub>"+sub+"</div>" if sub else ""}</div>'

def plot_style(fig, height=340):
    fig.update_layout(
        paper_bgcolor=CISCO["surface"], plot_bgcolor=CISCO["surface"],
        font=dict(color=CISCO["fg2"], size=11, family=CISCO["font"]),
        margin=dict(l=40, r=20, t=20, b=40), height=height,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08, x=0, font=dict(size=10, color=CISCO["muted"])),
    )
    fig.update_xaxes(gridcolor=CISCO["border_soft"], tickfont=dict(size=10, color=CISCO["muted"]))
    fig.update_yaxes(gridcolor=CISCO["border_soft"], tickfont=dict(size=10, color=CISCO["muted"]),
                     title_font=dict(size=11, color=CISCO["muted"]))
    return fig


# ==================== PAGE: RESUMEN ====================
if st.session_state.page == "resumen":
    st.markdown("### 📊 Resumen Ejecutivo")

    tv = df["total"].sum(); ti = df["iva"].sum(); tb = len(df)
    tp = int(df["total"].mean()); pe = round(100*len(df[df["tipo_pago"]=="Efectivo"])/len(df),1)
    tprop = df["propina"].sum()

    c = st.columns(5)
    with c[0]: st.html(kpi_card(fmt(tv), "Ventas Totales", "Monto acumulado"))
    with c[1]: st.html(kpi_card(fmt(ti), "IVA Pagado", f"{round(100*ti/(tv-tprop),1)}% del Neto"))
    with c[2]: st.html(kpi_card(fmtn(tb), "Boletas", "Total transacciones"))
    with c[3]: st.html(kpi_card(fmt(tp), "Ticket Promedio", "Por boleta"))
    with c[4]: st.html(kpi_card(f"{pe}%", "Efectivo", f"{fmtn(len(df[df['tipo_pago']=='Efectivo']))} boletas"))

    st.markdown("---")

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown('<div class="section-title">Evolución Mensual</div>', unsafe_allow_html=True)
        dm = df.copy(); dm["p"] = dm["fecha"].dt.to_period("M").astype(str)
        ev = dm.groupby("p").agg(v=("total","sum"), i=("iva","sum"), b=("total","count")).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=ev["p"], y=ev["v"], name="Ventas", marker_color=CISCO["accent"], yaxis="y", hovertemplate="%{y:$,.0f}<extra></extra>"))
        fig.add_trace(go.Bar(x=ev["p"], y=ev["i"], name="IVA", marker_color=CISCO["danger"], yaxis="y", hovertemplate="%{y:$,.0f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=ev["p"], y=ev["b"], name="Boletas", marker_color=CISCO["warn"], yaxis="y2", line=dict(width=2), hovertemplate="%{y}<extra></extra>"))
        fig.update_layout(barmode="group", yaxis=dict(title="Monto", tickprefix="$"), yaxis2=dict(title="Boletas", overlaying="y", side="right"))
        st.plotly_chart(plot_style(fig, 380), width='stretch')

    with col_b:
        st.markdown('<div class="section-title">Composición Ventas</div>', unsafe_allow_html=True)
        nn = df["monto_neto"].sum()
        fig = go.Figure(data=[go.Pie(labels=["Neto", "IVA", "Propinas"], values=[nn, ti, tprop], hole=0.55,
            marker=dict(colors=[CISCO["accent"], CISCO["danger"], CISCO["warn"]]),
            textinfo="percent+label", textfont=dict(size=12, color=CISCO["fg"]),
            hovertemplate="%{label}: %{value:$,.0f}<extra></extra>")])
        fig.update_layout(showlegend=False, paper_bgcolor=CISCO["surface"], margin=dict(l=20,r=20,t=10,b=20), height=380)
        st.plotly_chart(fig, width='stretch')

    # Summary table
    st.markdown('<div class="section-title">Indicadores Mensuales</div>', unsafe_allow_html=True)
    imf = im_df[["periodo","total_ventas","total_iva","cantidad_boletas","ticket_promedio"]].copy()
    imf.columns = ["Período", "Ventas", "IVA", "Boletas", "Ticket Prom."]
    imf["Ventas"] = imf["Ventas"].apply(fmt)
    imf["IVA"] = imf["IVA"].apply(fmt)
    imf["Ticket Prom."] = imf["Ticket Prom."].apply(fmt)
    st.dataframe(imf, width='stretch', hide_index=True, height=280)


# ==================== PAGE: IVA ====================
elif st.session_state.page == "iva":
    st.markdown("### 💰 Análisis de IVA")

    c_iva1, c_iva2 = st.columns(2)
    with c_iva1:
        st.markdown('<div class="section-title">IVA por Mes</div>', unsafe_allow_html=True)
        dm = df.copy(); dm["p"] = dm["fecha"].dt.to_period("M").astype(str)
        im = dm.groupby("p").agg(iva=("iva","sum"), neto=("monto_neto","sum")).reset_index()
        fig = px.area(im, x="p", y="iva", labels={"p":"","iva":"IVA ($)"})
        fig.update_traces(line=dict(color=CISCO["danger"], width=2), fillcolor="rgba(207,32,48,0.10)")
        st.plotly_chart(plot_style(fig, 340), width='stretch')

    with c_iva2:
        st.markdown('<div class="section-title">% IVA vs Neto</div>', unsafe_allow_html=True)
        im["pct"] = round(100*im["iva"]/im["neto"], 2)
        fig = px.line(im, x="p", y="pct", markers=True, labels={"p":"","pct":"% IVA"})
        fig.add_hline(y=19, line_dash="dash", line_color=CISCO["danger"], annotation_text="19%", annotation_position="bottom right")
        fig.update_traces(line=dict(color=CISCO["danger"], width=2))
        st.plotly_chart(plot_style(fig, 340), width='stretch')

    st.markdown("---")
    c_iva3, c_iva4 = st.columns(2)
    with c_iva3:
        st.markdown('<div class="section-title">IVA por Medio de Pago</div>', unsafe_allow_html=True)
        im2 = df.groupby("medio_pago").agg(iva=("iva","sum")).reset_index()
        im2["medio_pago"] = im2["medio_pago"].fillna("Efectivo").str.replace(r"Débito/Crédito","").str.strip()
        im2 = im2.sort_values("iva", ascending=True)
        fig = px.bar(im2, x="iva", y="medio_pago", orientation="h", color="iva",
                     color_continuous_scale="Reds", labels={"iva":"","medio_pago":""}, height=320)
        fig.update_layout(coloraxis_showscale=False)
        fig.update_traces(hovertemplate="$%{x:,.0f}<extra></extra>")
        st.plotly_chart(plot_style(fig, 320), width='stretch')

    with c_iva4:
        st.markdown('<div class="section-title">IVA Acumulado</div>', unsafe_allow_html=True)
        dor = df.sort_values("fecha"); dor["ac"] = dor["iva"].cumsum()
        fig = px.area(dor, x="fecha", y="ac", labels={"fecha":"","ac":"IVA Acum. ($)"})
        fig.update_traces(line=dict(color=CISCO["danger"], width=2), fillcolor="rgba(207,32,48,0.08)")
        st.plotly_chart(plot_style(fig, 320), width='stretch')


# ==================== PAGE: VENTAS ====================
elif st.session_state.page == "ventas":
    st.markdown("### 💳 Análisis de Ventas")

    c_v1, c_v2 = st.columns(2)
    with c_v1:
        st.markdown('<div class="section-title">Ventas Diarias</div>', unsafe_allow_html=True)
        vd = df.groupby(df["fecha"].dt.date).agg(v=("total","sum")).reset_index()
        fig = px.bar(vd, x="fecha", y="v", labels={"fecha":"","v":"Ventas ($)"}, color_discrete_sequence=[CISCO["accent"]], height=350)
        st.plotly_chart(plot_style(fig, 350), width='stretch')

    with c_v2:
        st.markdown('<div class="section-title">Ventas Mensuales</div>', unsafe_allow_html=True)
        dm = df.copy(); dm["p"] = dm["fecha"].dt.to_period("M").astype(str)
        vm = dm.groupby("p").agg(v=("total","sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vm["p"], y=vm["v"], mode="lines+markers", fill="tozeroy",
            line=dict(color=CISCO["accent"], width=2.5), fillcolor="rgba(4,159,217,0.10)",
            hovertemplate="%{y:$,.0f}<extra></extra>"))
        st.plotly_chart(plot_style(fig, 350), width='stretch')

    st.markdown("---")
    c_v3, c_v4 = st.columns([3, 2])
    with c_v3:
        st.markdown('<div class="section-title">Actividad por Día y Hora</div>', unsafe_allow_html=True)
        de = {"Monday":"Lun","Tuesday":"Mar","Wednesday":"Mie","Thursday":"Jue","Friday":"Vie","Saturday":"Sab","Sunday":"Dom"}
        ord_d = ["Lun","Mar","Mie","Jue","Vie","Sab","Dom"]
        df["hb"] = df["hora_num"].apply(lambda h: f"{h:02d}:00")
        ht = df.groupby(["dia_semana","hb"]).size().reset_index(name="n")
        ht["dl"] = ht["dia_semana"].map(de)
        pv = ht.pivot_table(index="dl", columns="hb", values="n", aggfunc="sum", fill_value=0)
        pv = pv.reindex([d for d in ord_d if d in pv.index])
        fig = px.imshow(pv, text_auto=".0f", aspect="auto", color_continuous_scale="Blues",
                        labels={"x":"Hora","y":"Dia","color":"Bols."}, height=320)
        fig.update_layout(paper_bgcolor=CISCO["surface"], margin=dict(l=20,r=20,t=10,b=40))
        st.plotly_chart(fig, width='stretch')

    with c_v4:
        st.markdown('<div class="section-title">Ticket Promedio Diario</div>', unsafe_allow_html=True)
        td = df.groupby(df["fecha"].dt.date).agg(t=("total","mean")).reset_index()
        fig = px.line(td, x="fecha", y="t", labels={"fecha":"","t":"Ticket ($)"})
        fig.update_traces(line=dict(color=CISCO["warn"], width=2))
        st.plotly_chart(plot_style(fig, 320), width='stretch')

    st.markdown("---")
    # KPI cards for this page
    st.markdown('<div class="section-title">Resumen de Ventas</div>', unsafe_allow_html=True)
    c_v5 = st.columns(4)
    with c_v5[0]: st.html(kpi_card(fmt(df["total"].sum()), "Ventas Totales"))
    with c_v5[1]: st.html(kpi_card(fmtn(len(df)), "Total Boletas"))
    with c_v5[2]: st.html(kpi_card(fmt(int(df["total"].mean())), "Ticket Promedio"))
    with c_v5[3]: st.html(kpi_card(fmt(df["propina"].sum()), "Total Propinas"))


# ==================== PAGE: PAGOS ====================
elif st.session_state.page == "pagos":
    st.markdown("### 🏦 Medios de Pago")

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.markdown('<div class="section-title">Transacciones por Tipo</div>', unsafe_allow_html=True)
        tc = df["tipo_pago"].value_counts().reset_index()
        tc.columns = ["tipo","n"]
        fig = px.pie(tc, values="n", names="tipo", hole=0.5,
                     color_discrete_sequence=[CISCO["accent"], CISCO["warn"], CISCO["success"]], height=350)
        fig.update_traces(textinfo="percent+label", textfont=dict(size=12, color=CISCO["fg"]),
                          hovertemplate="%{label}: %{value} (%{percent})<extra></extra>")
        fig.update_layout(paper_bgcolor=CISCO["surface"], margin=dict(l=20,r=20,t=10,b=20))
        st.plotly_chart(fig, width='stretch')

    with c_p2:
        st.markdown('<div class="section-title">Monto por Tipo</div>', unsafe_allow_html=True)
        tm = df.groupby("tipo_pago").agg(m=("total","sum")).reset_index()
        fig = px.bar(tm, x="tipo_pago", y="m", color="tipo_pago",
                     color_discrete_sequence=[CISCO["accent"], CISCO["warn"], CISCO["success"]],
                     labels={"tipo_pago":"","m":"Monto ($)"}, height=350)
        fig.update_traces(hovertemplate="$%{y:,.0f}<extra></extra>")
        fig.update_layout(showlegend=False)
        st.plotly_chart(plot_style(fig, 350), width='stretch')

    st.markdown("---")
    st.markdown('<div class="section-title">Marcas de Tarjeta</div>', unsafe_allow_html=True)
    mc = df[df["marca_tarjeta"].notna()]
    if not mc.empty:
        c_p3, c_p4 = st.columns(2)
        with c_p3:
            mcnt = mc["marca_tarjeta"].value_counts().reset_index()
            mcnt.columns = ["marca","n"]
            fig = px.bar(mcnt, x="marca", y="n", color="marca", color_discrete_sequence=CHART_COLORS,
                         labels={"marca":"","n":"Boletas"}, height=340)
            fig.update_layout(showlegend=False, xaxis_tickangle=-30)
            st.plotly_chart(plot_style(fig, 340), width='stretch')
        with c_p4:
            mmo = mc.groupby("marca_tarjeta").agg(m=("total","sum")).reset_index()
            fig = px.pie(mmo, values="m", names="marca_tarjeta", hole=0.5,
                         color_discrete_sequence=CHART_COLORS, height=340)
            fig.update_traces(textinfo="percent+label", textfont=dict(size=11, color=CISCO["fg"]))
            fig.update_layout(paper_bgcolor=CISCO["surface"], margin=dict(l=20,r=20,t=10,b=20))
            st.plotly_chart(fig, width='stretch')

    st.markdown("---")
    st.markdown('<div class="section-title">Propinas por Medio</div>', unsafe_allow_html=True)
    pm = df[df["propina"]>0].groupby("tipo_pago").agg(tp=("propina","sum"),prom=("propina","mean")).reset_index()
    c_p5, c_p6 = st.columns(2)
    with c_p5:
        fig = px.bar(pm, x="tipo_pago", y="tp", color="tipo_pago",
                     color_discrete_sequence=[CISCO["accent"], CISCO["warn"], CISCO["success"]],
                     labels={"tipo_pago":"","tp":"Total Propinas ($)"}, height=300)
        fig.update_layout(showlegend=False)
        fig.update_traces(hovertemplate="$%{y:,.0f}<extra></extra>")
        st.plotly_chart(plot_style(fig, 300), width='stretch')
    with c_p6:
        fig = px.bar(pm, x="tipo_pago", y="prom", color="tipo_pago",
                     color_discrete_sequence=[CISCO["accent"], CISCO["warn"], CISCO["success"]],
                     labels={"tipo_pago":"","prom":"Propina Prom. ($)"}, height=300)
        fig.update_layout(showlegend=False)
        fig.update_traces(hovertemplate="$%{y:,.0f}<extra></extra>")
        st.plotly_chart(plot_style(fig, 300), width='stretch')


# ==================== PAGE: DETALLE ====================
elif st.session_state.page == "detalle":
    st.markdown("### 📋 Detalle de Boletas")

    cols_show = ["numero_boleta","fecha","hora","rut","empresa","total","iva","tipo_pago","marca_tarjeta","medio_pago","cuotas","estado_validacion"]
    cols_disp = [c for c in cols_show if c in df.columns]
    dt = df[cols_disp].copy()
    for c in ["total","iva"]:
        if c in dt.columns: dt[c] = dt[c].apply(fmt)
    if "fecha" in dt.columns: dt["fecha"] = dt["fecha"].dt.strftime("%Y-%m-%d")

    ren = {"numero_boleta":"N° Bol.","fecha":"Fecha","hora":"Hora","rut":"RUT","empresa":"Empresa",
           "total":"Total","iva":"IVA","tipo_pago":"Tipo","marca_tarjeta":"Marca","medio_pago":"Medio","cuotas":"Ctas.","estado_validacion":"Estado"}
    dt = dt.rename(columns=ren)

    busq = st.text_input("", placeholder="🔍 Buscar por N° boleta...", label_visibility="collapsed")
    if busq:
        dt = dt[dt["N° Bol."].str.contains(busq, case=False, na=False)]

    st.dataframe(dt, width='stretch', hide_index=True, height=500)
    st.caption(f"**{fmtn(len(dt))}** de **{fmtn(len(df))}** registros")


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.caption(f"Hotel Pulp Fiction SpA · RUT 12.345.678-9 · Datos 100% sintéticos · Diseño Cisco · {fecha_desde} — {fecha_hasta}")
