import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO
import datetime
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EQUITY PULSE · Market Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;700;800&display=swap');

  :root {
    --bg:       #070b12;
    --surface:  #0e1420;
    --border:   #1c2a3a;
    --accent1:  #00f5c4;
    --accent2:  #ff4d6d;
    --accent3:  #f5a623;
    --accent4:  #4da6ff;
    --text:     #c8d8e8;
    --muted:    #7a9ab0;
  }

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stApp"],
  [data-testid="stHeader"],
  header[data-testid="stHeader"],
  .stApp, .stAppHeader,
  section[data-testid="stSidebarUserContent"],
  div[data-testid="stToolbar"],
  div[data-testid="stDecoration"],
  div[data-testid="stStatusWidget"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
  }

  [data-testid="stDecoration"]  { display: none !important; }
  [data-testid="stToolbar"]     { background: var(--bg) !important; }
  header[data-testid="stHeader"] {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
  }

  [data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
  }

  .block-container { padding-top: 4.5rem; padding-bottom: 2rem; }
  h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

  .main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--accent1);
    letter-spacing: -1px;
    line-height: 1;
    text-transform: uppercase;
  }
  .sub-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 2px;
  }

  .section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 4px;
    margin-bottom: 12px;
    margin-top: 28px;
  }

  .metric-tile {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
  }
  .metric-tile::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent1);
  }
  .metric-tile.red::before   { background: var(--accent2); }
  .metric-tile.amber::before { background: var(--accent3); }
  .metric-tile.blue::before  { background: var(--accent4); }

  .metric-label {
    font-size: 0.6rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
  }
  .metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
    color: #eaf3ff;
  }
  .metric-delta { font-size: 0.72rem; margin-top: 2px; }
  .up   { color: var(--accent1); }
  .down { color: var(--accent2); }
  .flat { color: var(--muted);   }

  .pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 2px;
    font-size: 0.6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
  }
  .pill-bull { background: rgba(0,245,196,0.12);  color: var(--accent1); border: 1px solid var(--accent1); }
  .pill-bear { background: rgba(255,77,109,0.12); color: var(--accent2); border: 1px solid var(--accent2); }
  .pill-neut { background: rgba(245,166,35,0.12); color: var(--accent3); border: 1px solid var(--accent3); }

  /* ── Sidebar labels ── */
  .sidebar-section {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent3);
    margin-top: 22px;
    margin-bottom: 4px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 4px;
  }
  /* Input labels dentro la sidebar: più grandi e leggibili */
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stFileUploader label {
    font-size: 0.72rem !important;
    color: #c8d8e8 !important;
    letter-spacing: 0.5px !important;
    font-family: 'Space Mono', monospace !important;
  }
  /* Link sidebar in cyan brillante */
  [data-testid="stSidebar"] a {
    color: #00f5c4 !important;
    text-decoration: none !important;
    font-weight: 700;
  }
  [data-testid="stSidebar"] a:hover { text-decoration: underline !important; }

  div[data-testid="stMetric"] { display: none; }

  .ts-bar {
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 2px;
    text-align: right;
    margin-bottom: 16px;
  }

  [data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
  }

  .js-plotly-plot { border: 1px solid var(--border) !important; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
PLOT_BG  = "#070b12"
PAPER_BG = "#0e1420"
GRID_COL = "#1c2a3a"
CYAN     = "#00f5c4"
RED      = "#ff4d6d"
AMBER    = "#f5a623"
BLUE     = "#4da6ff"
TEXT_COL = "#c8d8e8"

def base_layout(title="", height=320):
    return dict(
        height=height,
        title=dict(text=title, font=dict(family="Syne", size=13, color=TEXT_COL), x=0.01),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family="Space Mono", color=TEXT_COL, size=10),
        xaxis=dict(gridcolor=GRID_COL, showgrid=True, zeroline=False, tickfont=dict(size=9)),
        yaxis=dict(gridcolor=GRID_COL, showgrid=True, zeroline=False, tickfont=dict(size=9)),
        margin=dict(l=48, r=16, t=40, b=36),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        hovermode="x unified",
    )

def gauge(value, title, min_val=0, max_val=100, thresholds=None, unit="", fmt=".1f", invert=False):
    """
    invert=True  → alto = rosso (danger), basso = verde — per VIX, PCR
    invert=False → alto = verde (good),  basso = rosso  — per breadth, HYG/LQD
    """
    if thresholds is None:
        thresholds = [33, 66]
    pct = (value - min_val) / (max_val - min_val) * 100 if (max_val - min_val) else 50

    if invert:
        color = RED if pct > thresholds[1] else (AMBER if pct > thresholds[0] else CYAN)
        step_colors = ["#0a1a14", "#1a150a", "#1a0a0a"]
    else:
        color = CYAN if pct > thresholds[1] else (AMBER if pct > thresholds[0] else RED)
        step_colors = ["#1a0a0a", "#1a150a", "#0a1a14"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix=unit, valueformat=fmt, font=dict(family="Syne", size=28, color=color)),
        title=dict(text=title, font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        gauge=dict(
            axis=dict(range=[min_val, max_val], tickfont=dict(size=8, color="#7a9ab0"),
                      tickcolor="#1c2a3a", tickwidth=1),
            bar=dict(color=color, thickness=0.55),
            bgcolor=PLOT_BG,
            borderwidth=0,
            steps=[
                dict(range=[min_val, min_val + (max_val-min_val)*thresholds[0]/100], color=step_colors[0]),
                dict(range=[min_val + (max_val-min_val)*thresholds[0]/100,
                            min_val + (max_val-min_val)*thresholds[1]/100], color=step_colors[1]),
                dict(range=[min_val + (max_val-min_val)*thresholds[1]/100, max_val], color=step_colors[2]),
            ],
            threshold=dict(line=dict(color="#2a3a4a", width=2), thickness=0.75, value=value),
        )
    ))
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        height=220, margin=dict(l=20, r=20, t=40, b=10),
        font=dict(family="Space Mono", color=TEXT_COL),
    )
    return fig

def signal_pill(label):
    cls = {"BULL": "pill-bull", "BEAR": "pill-bear", "NEUTRAL": "pill-neut"}.get(label, "pill-neut")
    return f'<span class="pill {cls}">{label}</span>'

def tile(label, value, delta=None, color_class="", unit="", pill_label=None):
    delta_html = ""
    if delta is not None:
        cls  = "up" if delta >= 0 else "down"
        sign = "▲"  if delta >= 0 else "▼"
        delta_html = f'<div class="metric-delta {cls}">{sign} {abs(delta):.2f}{unit}</div>'
    pill_html = f'<div style="margin-top:6px">{signal_pill(pill_label)}</div>' if pill_label else ""
    return f"""
    <div class="metric-tile {color_class}">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {delta_html}
      {pill_html}
    </div>"""

# ─────────────────────────────────────────────
#  DATA FETCHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=14400, show_spinner=False)
def fetch_price_data(period="1y"):
    tickers = ["SPY", "QQQ", "^VIX", "^VIX3M", "^CPC", "HYG", "LQD"]
    data = {}
    for t in tickers:
        try:
            df = yf.download(t, period=period, progress=False, auto_adjust=True, timeout=15)
            if not df.empty:
                data[t] = df
        except Exception:
            pass
    return data

def get_close(data, ticker):
    df = data.get(ticker)
    if df is None or df.empty:
        return None
    close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.squeeze().dropna()

def compute_skew_vix(data):
    vix   = get_close(data, "^VIX")
    vix3m = get_close(data, "^VIX3M")
    if vix is None or vix3m is None:
        return None, None, None
    vix3m_a, vix_a = vix3m.align(vix, join="inner")
    if hasattr(vix3m_a, "squeeze"): vix3m_a = vix3m_a.squeeze()
    if hasattr(vix_a,   "squeeze"): vix_a   = vix_a.squeeze()
    if not isinstance(vix3m_a, pd.Series) or not isinstance(vix_a, pd.Series):
        return None, None, None
    vix3m_a = pd.Series(vix3m_a.values, index=vix3m_a.index)
    vix_a   = pd.Series(vix_a.values,   index=vix_a.index)
    return vix3m_a / vix_a, vix3m_a, vix_a

def compute_pcr(data):
    return get_close(data, "^CPC")

@st.cache_data(ttl=14400, show_spinner=False)
def fetch_hyg_lqd_long():
    """Fetch HYG e LQD su 5 anni per storico grafico completo."""
    result = {}
    for t in ["HYG", "LQD"]:
        try:
            df = yf.download(t, period="5y", progress=False, auto_adjust=True, timeout=15)
            if not df.empty:
                result[t] = df
        except Exception:
            pass
    return result

def compute_hyg_lqd(data):
    hyg = get_close(data, "HYG")
    lqd = get_close(data, "LQD")
    if hyg is None or lqd is None:
        return None
    h, l = hyg.align(lqd, join="inner")
    h = pd.Series(h.values, index=h.index)
    l = pd.Series(l.values, index=l.index)
    return (h / l).dropna()

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
_ss_defaults = {
    "s5th": 55, "s5fi": 48, "ndth": 52, "ndfi": 44,
    "sp_oi": 1_932_596, "sp_oi_prev": 1_918_311,
    "margin_debt": 1_279_042, "margin_debt_prev": 1_225_597,  # FINRA Jan-26 / Dec-25
    "period": "1y",
}
for _k, _v in _ss_defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-family:Syne;font-size:1.2rem;font-weight:800;'
        'color:#00f5c4;letter-spacing:-0.5px;">⚡ EQUITY PULSE</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.6rem;letter-spacing:3px;color:#4a6070;'
        'text-transform:uppercase;margin-bottom:16px;">Manual Data Input</div>',
        unsafe_allow_html=True)

    # ── Breadth S&P ──────────────────────────
    st.markdown('<div class="sidebar-section">📊 Breadth — S&P 500</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:2.1;margin-bottom:6px;">'
        '<a href="https://www.barchart.com/stocks/quotes/$S5TH/overview" target="_blank" style="color:#00f5c4;font-weight:700;">→ $S5TH</a>'
        ' · % S&amp;P500 sopra 200MA<br>'
        '<a href="https://www.barchart.com/stocks/quotes/$S5FI/overview" target="_blank" style="color:#00f5c4;font-weight:700;">→ $S5FI</a>'
        ' · % S&amp;P500 sopra 50MA</div>',
        unsafe_allow_html=True)
    s5th = st.number_input("S5TH · % S&P500 sopra 200MA", 0, 100,
        value=st.session_state["s5th"], key="s5th")
    s5fi = st.number_input("S5FI · % S&P500 sopra 50MA", 0, 100,
        value=st.session_state["s5fi"], key="s5fi")

    # ── Breadth Nasdaq ────────────────────────
    st.markdown('<div class="sidebar-section">📊 Breadth — Nasdaq</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:2.1;margin-bottom:6px;">'
        '<a href="https://www.barchart.com/stocks/quotes/$NDTH/overview" target="_blank" style="color:#00f5c4;font-weight:700;">→ $NDTH</a>'
        ' · % Nasdaq sopra 200MA<br>'
        '<a href="https://www.barchart.com/stocks/quotes/$NDFI/overview" target="_blank" style="color:#00f5c4;font-weight:700;">→ $NDFI</a>'
        ' · % Nasdaq sopra 50MA</div>',
        unsafe_allow_html=True)
    ndth = st.number_input("NDTH · % Nasdaq sopra 200MA", 0, 100,
        value=st.session_state["ndth"], key="ndth")
    ndfi = st.number_input("NDFI · % Nasdaq sopra 50MA", 0, 100,
        value=st.session_state["ndfi"], key="ndfi")

    # ── Futures OI ───────────────────────────
    st.markdown('<div class="sidebar-section">📈 Futures Open Interest</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:1.7;margin-bottom:6px;">'
        'Fonte: <a href="https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.volume.html"'
        ' target="_blank">CMEGroup.com</a>'
        ' → E-mini S&P500 → Volume &amp; OI → <b>MAR26 AT CLOSE</b></div>',
        unsafe_allow_html=True)
    sp_oi = st.number_input("S&P500 Futures OI (contratti)", min_value=0,
        value=st.session_state["sp_oi"], step=10_000, key="sp_oi")
    sp_oi_prev = st.number_input("OI settimana precedente", min_value=0,
        value=st.session_state["sp_oi_prev"], step=10_000, key="sp_oi_prev")

    # ── Margin Debt ───────────────────────────
    st.markdown('<div class="sidebar-section">💳 Margin Debt (FINRA)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:1.7;margin-bottom:6px;">'
        'Fonte: <a href="https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics"'
        ' target="_blank">FINRA.org</a>'
        ' → Margin Statistics → aggiorna <b>mensilmente</b></div>',
        unsafe_allow_html=True)
    margin_debt = st.number_input("Margin Debt corrente ($M)", min_value=0,
        value=st.session_state["margin_debt"], step=1_000, key="margin_debt")
    margin_debt_prev = st.number_input("Margin Debt mese precedente ($M)", min_value=0,
        value=st.session_state["margin_debt_prev"], step=1_000, key="margin_debt_prev")

    # ── Put/Call CSV ──────────────────────────
    st.markdown('<div class="sidebar-section">📂 Put/Call CSV (Barchart)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:1.7;margin-bottom:6px;">'
        'Fonte: <a href="https://www.barchart.com/options/put-call-ratios/spx" target="_blank">'
        'Barchart.com</a>'
        ' → SPX Options → Put/Call Ratios → <b>Download CSV</b></div>',
        unsafe_allow_html=True)
    _uploaded = st.file_uploader("SPX P/C CSV", type="csv", label_visibility="collapsed")
    if _uploaded is not None:
        _bytes = _uploaded.getvalue()
        if _bytes and len(_bytes) > 10:
            st.session_state["pcr_csv_bytes"] = _bytes
            st.session_state["pcr_csv_name"]  = _uploaded.name
    if "pcr_csv_bytes" in st.session_state:
        _fname = st.session_state.get("pcr_csv_name", "file.csv")
        st.markdown(
            f'<div style="font-size:0.65rem;color:#00f5c4;margin-top:4px;">✅ {_fname}</div>',
            unsafe_allow_html=True)
        if st.button("🗑 Rimuovi CSV", use_container_width=True):
            del st.session_state["pcr_csv_bytes"]
            del st.session_state["pcr_csv_name"]
            st.rerun()

    # ── Settings ─────────────────────────────
    st.markdown('<div class="sidebar-section">⚙️ Impostazioni</div>', unsafe_allow_html=True)
    period_opts = ["6mo", "1y", "2y", "5y"]
    period = st.selectbox("Finestra storica", period_opts,
        index=period_opts.index(st.session_state["period"]), key="period")

    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.58rem;color:#4a6070;line-height:1.8;">'
        'Automatico: SPY, QQQ, VIX, VIX3M, HYG, LQD<br>'
        'Manuale: Breadth (settimanale), OI, Margin Debt<br>'
        'P/C Ratio: CSV Barchart (giornaliero)'
        '</div>',
        unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Equity Pulse</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multi-Indicator Market Timing · S&P 500 &amp; Nasdaq</div>',
            unsafe_allow_html=True)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(
    f'<div class="ts-bar">Last fetch: {now} &nbsp;|&nbsp; Breadth/OI/Margin: manuale</div>',
    unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FETCH & COMPUTE
# ─────────────────────────────────────────────
data          = fetch_price_data(period)
hyg_lqd       = compute_hyg_lqd(data)
data_hyg_long = fetch_hyg_lqd_long()
hyg_lqd_long  = compute_hyg_lqd(data_hyg_long)  # 5y per grafico

# ── PCR da CSV Barchart ──
pcr_barchart_val  = None
pcr_barchart_puts = None
pcr_barchart_call = None
if "pcr_csv_bytes" in st.session_state:
    try:
        import io as _io
        _raw   = st.session_state["pcr_csv_bytes"].decode("utf-8")
        _lines = [l for l in _raw.splitlines() if not l.startswith('"Downloaded')]
        _clean = "\n".join(_lines).replace("Put/Call\tVol", "PC_Vol_Ratio")
        _df    = pd.read_csv(_io.StringIO(_clean))
        _df["DTE"]      = pd.to_numeric(_df["DTE"],      errors="coerce")
        _df["Put Vol"]  = pd.to_numeric(_df["Put Vol"],  errors="coerce")
        _df["Call Vol"] = pd.to_numeric(_df["Call Vol"], errors="coerce")
        _df_near = _df[_df["DTE"] <= 60].dropna(subset=["Put Vol", "Call Vol"])
        if not _df_near.empty:
            pcr_barchart_puts = int(_df_near["Put Vol"].sum())
            pcr_barchart_call = int(_df_near["Call Vol"].sum())
            if pcr_barchart_call > 0:
                pcr_barchart_val = round(pcr_barchart_puts / pcr_barchart_call, 4)
    except Exception as _e:
        st.session_state["pcr_parse_error"] = str(_e)

spy_s  = get_close(data, "SPY")
qqq_s  = get_close(data, "QQQ")
vix_s  = get_close(data, "^VIX")
skew_ratio, vix3m_s, vix_s2 = compute_skew_vix(data)
pcr_s  = compute_pcr(data)

def last(series):
    if series is None or len(series) == 0: return None
    try:
        val = series.iloc[-1]
        if isinstance(val, pd.Series): val = val.iloc[0]
        return float(val)
    except Exception: return None

def prev(series, n=1):
    if series is None or len(series) <= n: return None
    try:
        val = series.iloc[-(n+1)]
        if isinstance(val, pd.Series): val = val.iloc[0]
        return float(val)
    except Exception: return None

spy_last      = last(spy_s)
qqq_last      = last(qqq_s)
vix_last      = last(vix_s)
skew_last     = last(skew_ratio)
pcr_last      = last(pcr_s)
hyg_lqd_last  = last(hyg_lqd)

# PCR attivo: CSV ha priorità su yfinance
active_pcr = pcr_barchart_val if pcr_barchart_val else (pcr_last if pcr_last else None)

spy_delta = (spy_last - prev(spy_s)) if spy_s is not None and len(spy_s) > 1 else None
qqq_delta = (qqq_last - prev(qqq_s)) if qqq_s is not None and len(qqq_s) > 1 else None
vix_delta = (vix_last - prev(vix_s)) if vix_s is not None and len(vix_s) > 1 else None

# ─────────────────────────────────────────────
#  COMPOSITE SIGNAL
# ─────────────────────────────────────────────
max_score = 8

def score_breadth(s5, nd, s5f, ndf):
    pts = 0
    if s5  > 60: pts += 1
    if nd  > 60: pts += 1
    if s5f > 55: pts += 0.5
    if ndf > 55: pts += 0.5
    return pts  # max 3

def score_vix(v):
    if v is None: return 0
    if v < 15: return 1
    if v < 25: return 0.5
    return 0

def score_pcr(p):
    if p is None: return 0
    if p < 0.7:  return 0
    if p < 1.0:  return 1
    return 0.5

def score_skew(r):
    if r is None: return 0
    return 1 if r < 1.05 else 0

def score_oi(oi, prev_oi):
    return 1 if oi > prev_oi else 0

def score_margin(m, mp):
    return 1 if m > mp else 0

def score_hyg_lqd(ratio):
    """HYG/LQD price ratio — range storico 0.60-1.02.
    > 0.80 = risk-on (spread compressi)
    0.70-0.80 = neutrale (zona normale attuale)
    < 0.70 = stress / risk-off (area COVID-like)"""
    if ratio is None: return 0
    if ratio > 0.80: return 1
    if ratio > 0.70: return 0.5
    return 0

total = (score_breadth(s5th, ndth, s5fi, ndfi) +
         score_vix(vix_last) +
         score_pcr(active_pcr) +
         score_skew(skew_last) +
         score_oi(sp_oi, sp_oi_prev) +
         score_margin(margin_debt, margin_debt_prev) +
         score_hyg_lqd(hyg_lqd_last))

composite_pct   = (total / max_score) * 100
composite_label = "BULL" if composite_pct > 60 else ("BEAR" if composite_pct < 38 else "NEUTRAL")

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📡 Overview", "📊 Breadth", "😰 Sentiment", "🏗️ Structure"])

# ══════════════════════════════════════════════
#  TAB 1 · OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    col_g, col_m = st.columns([1, 2])

    with col_g:
        st.markdown('<div class="section-label">Composite Signal</div>', unsafe_allow_html=True)
        fig_comp = gauge(composite_pct, "MARKET PULSE", 0, 100, [33, 66], "%", ".0f")
        st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div style="text-align:center;margin-top:-10px">{signal_pill(composite_label)}</div>',
            unsafe_allow_html=True)

    with col_m:
        st.markdown('<div class="section-label">Price &amp; Volatility</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            v  = f"${spy_last:.2f}" if spy_last else "N/A"
            cc = "" if (spy_delta is None or spy_delta >= 0) else "red"
            st.markdown(tile("SPY · S&P 500 ETF", v, spy_delta, cc, "$"), unsafe_allow_html=True)
        with c2:
            v  = f"${qqq_last:.2f}" if qqq_last else "N/A"
            cc = "" if (qqq_delta is None or qqq_delta >= 0) else "red"
            st.markdown(tile("QQQ · Nasdaq ETF", v, qqq_delta, cc, "$"), unsafe_allow_html=True)
        with c3:
            v        = f"{vix_last:.2f}" if vix_last else "N/A"
            vix_pill = "BULL" if vix_last and vix_last < 15 else ("BEAR" if vix_last and vix_last > 25 else "NEUTRAL")
            cc       = "red" if vix_last and vix_last > 25 else ("" if vix_last and vix_last < 15 else "amber")
            st.markdown(tile("VIX · Fear Index", v, vix_delta, cc, "", vix_pill), unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px">Quick Indicators</div>',
                    unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4:
            skew_v = f"{skew_last:.3f}" if skew_last else "N/A"
            sp_s   = "BULL" if (skew_last and skew_last < 1.05) else "NEUTRAL"
            st.markdown(tile("VIX3M/VIX Ratio", skew_v, None, "blue", "", sp_s), unsafe_allow_html=True)
        with c5:
            pcr_v  = f"{active_pcr:.2f}" if active_pcr else "N/A"
            pp     = "BULL" if (active_pcr and 0.7 < active_pcr < 1.0) else ("BEAR" if (active_pcr and active_pcr > 1.1) else "NEUTRAL")
            pcr_cc = "red" if (active_pcr and active_pcr > 1.1) else ("amber" if active_pcr else "amber")
            st.markdown(tile("Put/Call Ratio", pcr_v, None, pcr_cc, "", pp), unsafe_allow_html=True)
        with c6:
            oi_delta = sp_oi - sp_oi_prev
            oi_v     = f"{sp_oi/1e6:.2f}M"
            op       = "BULL" if oi_delta > 0 else "BEAR"
            st.markdown(tile("S&P Futures OI", oi_v, oi_delta/1e3,
                             "blue" if oi_delta > 0 else "red", "K", op), unsafe_allow_html=True)
        with c7:
            if hyg_lqd_last:
                hl_v = f"{hyg_lqd_last:.4f}"
                hl_p = "BULL" if hyg_lqd_last > 0.80 else ("BEAR" if hyg_lqd_last < 0.70 else "NEUTRAL")
                hl_c = "blue" if hyg_lqd_last > 0.80 else ("red" if hyg_lqd_last < 0.70 else "amber")
            else:
                hl_v, hl_p, hl_c = "N/A", "NEUTRAL", "amber"
            st.markdown(tile("HYG/LQD · Credit", hl_v, None, hl_c, "", hl_p), unsafe_allow_html=True)

    st.markdown('<div class="section-label">Price History</div>', unsafe_allow_html=True)
    if spy_s is not None and qqq_s is not None:
        fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   vertical_spacing=0.03, subplot_titles=("SPY", "QQQ"))
        fig_price.add_trace(go.Scatter(x=spy_s.index, y=spy_s.values, name="SPY",
                                        line=dict(color=CYAN, width=1.5)), row=1, col=1)
        fig_price.add_trace(go.Scatter(x=qqq_s.index, y=qqq_s.values, name="QQQ",
                                        line=dict(color=BLUE, width=1.5)), row=2, col=1)
        fig_price.update_layout(**base_layout("", 380))
        fig_price.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                                  xaxis2=dict(gridcolor=GRID_COL), yaxis2=dict(gridcolor=GRID_COL))
        st.plotly_chart(fig_price, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
#  TAB 2 · BREADTH
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Breadth Gauges — % Stocks Above Moving Averages</div>',
                unsafe_allow_html=True)
    st.info("⌨️  Aggiorna settimanalmente i valori nella sidebar → StockCharts: $S5TH, $S5FI, $NDTH, $NDFI",
            icon="ℹ️")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.plotly_chart(gauge(s5th, "S5TH · S&P >200MA", 0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.plotly_chart(gauge(s5fi, "S5FI · S&P >50MA",  0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})
    with c3:
        st.plotly_chart(gauge(ndth, "NDTH · NDX >200MA", 0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})
    with c4:
        st.plotly_chart(gauge(ndfi, "NDFI · NDX >50MA",  0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})

    # ── Signal Interpretation Table (dark HTML) ──
    st.markdown('<div class="section-label">Signal Interpretation</div>', unsafe_allow_html=True)

    def _interp_row(name, val, bull_thresh, bear_thresh, bull_txt, bear_txt, neutral_txt):
        is_bull  = val > bull_thresh
        is_bear  = val < bear_thresh
        zone_col = "#00f5c4" if is_bull else ("#ff4d6d" if is_bear else "#f5a623")
        zone_ico = "▲ BULL"  if is_bull else ("▼ BEAR"  if is_bear else "◆ NEUTRAL")
        txt      = bull_txt   if is_bull else (bear_txt  if is_bear else neutral_txt)
        return (
            f'<tr>'
            f'<td style="padding:8px 12px;font-family:Space Mono;font-size:0.7rem;color:#c8d8e8;border-bottom:1px solid #1c2a3a">{name}</td>'
            f'<td style="padding:8px 12px;font-family:Syne;font-size:0.85rem;font-weight:700;color:{zone_col};border-bottom:1px solid #1c2a3a">{val}%</td>'
            f'<td style="padding:8px 12px;font-size:0.65rem;color:{zone_col};border-bottom:1px solid #1c2a3a;letter-spacing:1px">{zone_ico}</td>'
            f'<td style="padding:8px 12px;font-size:0.65rem;color:#8ab0c8;border-bottom:1px solid #1c2a3a">{txt}</td>'
            f'</tr>'
        )

    rows = (
        _interp_row("S5TH · S&P >200MA", s5th, 70, 30,
            "Ampia partecipazione — trend solido",
            "Breadth debole — mercato fragile",
            "Partecipazione mista — attendere conferma") +
        _interp_row("S5FI · S&P >50MA",  s5fi, 60, 30,
            "Momentum breve termine positivo",
            "Pressione di vendita ST diffusa",
            "Deterioramento in corso — cautela") +
        _interp_row("NDTH · NDX >200MA", ndth, 70, 30,
            "Nasdaq in salute — tech leader",
            "Nasdaq debole — tech in crisi",
            "Tech misto — divergenza possibile") +
        _interp_row("NDFI · NDX >50MA",  ndfi, 60, 30,
            "Trend breve NDX confermato",
            "NDX sotto pressione ST",
            "NDX border — monitorare")
    )

    breadth_score = sum([s5th > 60, s5fi > 55, ndth > 60, ndfi > 55])
    b_color = "#00f5c4" if breadth_score >= 3 else ("#ff4d6d" if breadth_score <= 1 else "#f5a623")
    b_label = "BULL"   if breadth_score >= 3 else ("BEAR"   if breadth_score <= 1 else "NEUTRAL")
    b_bg    = "#0a1a14" if b_label == "BULL" else ("#1a0a0a" if b_label == "BEAR" else "#1a150a")

    st.markdown(f"""
    <div style="border:1px solid #1c2a3a;border-radius:4px;overflow:hidden">
      <table style="width:100%;border-collapse:collapse;background:#080e14">
        <thead>
          <tr style="background:#0e1420">
            <th style="padding:8px 12px;text-align:left;font-size:0.58rem;letter-spacing:2px;color:#4a6070">INDICATORE</th>
            <th style="padding:8px 12px;text-align:left;font-size:0.58rem;letter-spacing:2px;color:#4a6070">VALORE</th>
            <th style="padding:8px 12px;text-align:left;font-size:0.58rem;letter-spacing:2px;color:#4a6070">ZONA</th>
            <th style="padding:8px 12px;text-align:left;font-size:0.58rem;letter-spacing:2px;color:#4a6070">INTERPRETAZIONE</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
        <tfoot>
          <tr style="background:#0e1420">
            <td colspan="3" style="padding:8px 12px;font-size:0.62rem;color:#7a9ab0;font-family:Space Mono">BREADTH COMPOSITE</td>
            <td style="padding:8px 12px">
              <span style="background:{b_bg};color:{b_color};border:1px solid {b_color};
                           padding:2px 10px;border-radius:2px;font-size:0.6rem;
                           letter-spacing:2px;font-family:Space Mono">{b_label} ({breadth_score}/4)</span>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
    """, unsafe_allow_html=True)

    # ── A/D Line screenshot ──
    st.markdown(
        '<div class="section-label">NYSE Advance/Decline Line — Screenshot Settimanale</div>',
        unsafe_allow_html=True)

    _ad_img = st.file_uploader(
        "Carica screenshot A/D Line (PNG/JPG)",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
        key="ad_screenshot")

    if _ad_img is not None:
        st.session_state["ad_img_bytes"] = _ad_img.getvalue()
        st.session_state["ad_img_name"]  = _ad_img.name
        st.session_state["ad_img_date"]  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if "ad_img_bytes" in st.session_state:
        _upload_date = st.session_state.get("ad_img_date", "")
        _upload_name = st.session_state.get("ad_img_name", "")
        st.markdown(f"""
        <div style="border:1px solid #1c2a3a;border-radius:4px;overflow:hidden;margin-bottom:8px">
          <div style="background:#0e1420;padding:6px 12px;font-size:0.58rem;
                      color:#7a9ab0;letter-spacing:2px;display:flex;justify-content:space-between">
            <span>📊 NYSE A/D LINE</span>
            <span>Caricato: {_upload_date} · {_upload_name}</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.image(st.session_state["ad_img_bytes"], use_container_width=True)
        c_rem, c_src = st.columns([1, 3])
        with c_rem:
            if st.button("🗑 Rimuovi", use_container_width=True, key="rm_ad_img"):
                del st.session_state["ad_img_bytes"]
                del st.session_state["ad_img_name"]
                del st.session_state["ad_img_date"]
                st.rerun()
        with c_src:
            st.markdown(
                '<div style="font-size:0.6rem;color:#4a6070;padding-top:8px">'
                'Fonte: marketinout.com → Advance/Decline Line &nbsp;|&nbsp; stockcharts.com → $NYAD'
                '</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#0e1420;border:1px solid #1c2a3a;border-radius:4px;
                    padding:32px;text-align:center">
          <div style="font-size:2rem;margin-bottom:8px">📸</div>
          <div style="font-family:Syne;font-size:0.9rem;color:#c8d8e8;margin-bottom:8px">
            Carica lo screenshot A/D Line
          </div>
          <div style="font-size:0.62rem;color:#7a9ab0;line-height:1.9">
            Trascina qui un'immagine oppure usa il pulsante sopra<br>
            <b style="color:#8ab0c8">Fonti:</b>
            marketinout.com → Advance/Decline Line &nbsp;|&nbsp;
            stockcharts.com → $NYAD &nbsp;|&nbsp;
            barchart.com → NYSE Breadth
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  TAB 3 · SENTIMENT
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Volatility &amp; Options Sentiment</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # ── VIX gauge + history ──
    with c1:
        vix_val = vix_last if vix_last else 20
        # Range VIX 10-50: soglie 15 e 25 in %
        # (15-10)/(50-10)*100 = 12.5 → threshold[0]=12
        # (25-10)/(50-10)*100 = 37.5 → threshold[1]=38
        fig_vix = gauge(vix_val, "VIX · CBOE Volatility Index", 10, 50,
                         thresholds=[12, 38], unit="", fmt=".1f", invert=True)
        st.plotly_chart(fig_vix, use_container_width=True, config={"displayModeBar": False})

        if vix_s is not None:
            fig_vh = go.Figure()
            fig_vh.add_trace(go.Scatter(x=vix_s.index, y=vix_s.values, name="VIX",
                                         line=dict(color=RED, width=1.3)))
            fig_vh.add_hline(y=25, line_dash="dot", line_color=RED,  line_width=1,
                              annotation_text="25 Paura",  annotation_position="right",
                              annotation_font=dict(color=RED, size=8))
            fig_vh.add_hline(y=20, line_dash="dot", line_color=AMBER, line_width=1,
                              annotation_text="20 Attenzione", annotation_position="right",
                              annotation_font=dict(color=AMBER, size=8))
            fig_vh.add_hline(y=15, line_dash="dot", line_color=CYAN, line_width=1,
                              annotation_text="15 Calma", annotation_position="right",
                              annotation_font=dict(color=CYAN, size=8))
            fig_vh.update_layout(**base_layout("VIX History", 260))
            st.plotly_chart(fig_vh, use_container_width=True, config={"displayModeBar": False})

    # ── VIX3M/VIX gauge + history ──
    with c2:
        skew_val = skew_last if skew_last else 1.0
        fig_sk = gauge(skew_val, "VIX3M/VIX · Term Structure Ratio", 0.8, 1.4,
                        thresholds=[15, 55], unit="x", fmt=".3f", invert=False)
        st.plotly_chart(fig_sk, use_container_width=True, config={"displayModeBar": False})

        if skew_ratio is not None:
            fig_skh = go.Figure()
            fig_skh.add_trace(go.Scatter(x=skew_ratio.index, y=skew_ratio.values,
                                          name="VIX3M/VIX",
                                          line=dict(color=AMBER, width=1.3)))
            fig_skh.add_hline(y=1.0, line_dash="dot", line_color=TEXT_COL, line_width=1,
                               annotation_text="1.0", annotation_position="right",
                               annotation_font=dict(color=TEXT_COL, size=8))
            fig_skh.update_layout(**base_layout("VIX3M/VIX Ratio History", 260))
            st.plotly_chart(fig_skh, use_container_width=True, config={"displayModeBar": False})

    # ── Put/Call Ratio ──
    st.markdown('<div class="section-label">Put/Call Ratio SPX — Near-Term Options</div>',
                unsafe_allow_html=True)

    _csv_loaded = "pcr_csv_bytes" in st.session_state
    _parse_err  = st.session_state.get("pcr_parse_error", None)
    if not _csv_loaded:
        st.info("📂 Carica il CSV Barchart nella sidebar per il P/C Ratio SPX.", icon="📂")
    elif _parse_err:
        st.error(f"⚠️ Errore parsing CSV: {_parse_err}")
    elif pcr_barchart_val:
        st.success(f"✅ CSV caricato · PCR SPX = **{pcr_barchart_val:.4f}** "
                   f"({st.session_state.get('pcr_csv_name','')})")

    pcr_source = "Barchart CSV" if pcr_barchart_val else ("yfinance ^CPC" if pcr_last else "N/A")
    pcr_series = pcr_s

    c3, c4 = st.columns([1, 3])
    with c3:
        # PCR gauge: range 0.4-1.8, invert=True (alto=rosso)
        # Soglie P/C: 0.4→1.8 span=1.4
        # 1.0 = (1.0-0.4)/1.4*100 = 42.9% → threshold[0]=35 (zona verde sotto 0.8)
        # 1.1 = (1.1-0.4)/1.4*100 = 50%   → threshold[1]=50 (rosso sopra 1.1)
        # Ricalibrato: threshold[0]=21 = 0.7, threshold[1]=50 = 1.1
        # A 1.29: pct=(1.29-0.4)/1.4*100=63.6% > 50 → RED ✓
        fig_pcr_g = gauge(
            active_pcr if active_pcr else 0.85,
            f"Put/Call · {pcr_source}",
            0.4, 1.8,
            thresholds=[21, 50],
            unit="x", fmt=".2f", invert=True)
        st.plotly_chart(fig_pcr_g, use_container_width=True, config={"displayModeBar": False})

        if pcr_barchart_val and pcr_barchart_puts and pcr_barchart_call:
            pct_put = pcr_barchart_puts / (pcr_barchart_puts + pcr_barchart_call) * 100
            st.markdown(f"""
            <div style="font-size:0.62rem;color:#8ab0c8;border:1px solid #1c2a3a;
                        padding:8px;border-radius:4px;margin-top:8px;line-height:1.9">
              <b style="color:#c8d8e8">SPX Near-Term (&lt;60 DTE)</b><br>
              Put Vol: <b style="color:{RED}">{pcr_barchart_puts:,}</b><br>
              Call Vol: <b style="color:{CYAN}">{pcr_barchart_call:,}</b><br>
              % Put: <b>{pct_put:.1f}%</b>
            </div>""", unsafe_allow_html=True)

    with c4:
        if pcr_series is not None:
            pcr_ma = pcr_series.rolling(10).mean()
            fig_pcr = go.Figure()
            fig_pcr.add_trace(go.Bar(x=pcr_series.index, y=pcr_series.values,
                                      name="Daily P/C", marker_color="rgba(77,166,255,0.25)"))
            fig_pcr.add_trace(go.Scatter(x=pcr_ma.index, y=pcr_ma.values, name="10d SMA",
                                          line=dict(color=BLUE, width=1.8)))
            if pcr_barchart_val:
                fig_pcr.add_hline(y=pcr_barchart_val, line_dash="solid",
                                   line_color=AMBER, line_width=1.5,
                                   annotation_text=f"Oggi CSV: {pcr_barchart_val:.2f}",
                                   annotation_position="top right",
                                   annotation_font=dict(color=AMBER, size=9))
            fig_pcr.add_hline(y=1.1, line_dash="dot", line_color=RED,  line_width=1,
                               annotation_text="1.1 Bear", annotation_position="right",
                               annotation_font=dict(color=RED, size=8))
            fig_pcr.add_hline(y=0.7, line_dash="dot", line_color=CYAN, line_width=1,
                               annotation_text="0.7 Bull", annotation_position="right",
                               annotation_font=dict(color=CYAN, size=8))
            fig_pcr.update_layout(**base_layout("Storico P/C (^CPC yfinance) + oggi CSV", 280))
            st.plotly_chart(fig_pcr, use_container_width=True, config={"displayModeBar": False})
        elif pcr_barchart_val:
            color_pcr = "#ff4d6d" if pcr_barchart_val > 1.1 else ("#f5a623" if pcr_barchart_val > 0.7 else "#00f5c4")
            st.markdown(f"""
            <div style="background:#0e1420;border:1px solid #1c2a3a;padding:20px;
                        border-radius:4px;text-align:center;margin-top:20px">
              <div style="font-size:0.6rem;letter-spacing:3px;color:#7a9ab0">P/C RATIO OGGI (CSV)</div>
              <div style="font-family:Syne;font-size:3rem;font-weight:700;color:{color_pcr}">
                {pcr_barchart_val:.3f}
              </div>
              <div style="font-size:0.65rem;color:#7a9ab0">Carica il CSV ogni giorno per aggiornare</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("📂 Carica il CSV Barchart nella sidebar per il P/C Ratio SPX.")

    st.markdown("""
    <div style="font-size:0.65rem;color:#8ab0c8;border:1px solid #1c2a3a;
                padding:10px;border-radius:4px;line-height:1.8;margin-top:12px">
      <b style="color:#c8d8e8">P/C Ratio Guide:</b>&nbsp;
      P/C &lt; 0.7 → Complacency / Risk &nbsp;|&nbsp;
      0.7–1.0 → Healthy Fear / Opportunity &nbsp;|&nbsp;
      P/C &gt; 1.1 → Capitulation / Bear signal &nbsp;|&nbsp;
      <b>VIX3M/VIX &lt; 1</b> = inverted term structure → stress
    </div>
    """, unsafe_allow_html=True)

    # ── HYG/LQD Credit Spread ──
    st.markdown(
        '<div class="section-label" style="margin-top:28px">HYG / LQD · Credit Spread Proxy</div>',
        unsafe_allow_html=True)

    c_hyg1, c_hyg2 = st.columns([1, 2])
    with c_hyg1:
        hl_val = hyg_lqd_last if hyg_lqd_last else 0.86
        # Range 0.80-0.94, invert=False (alto=verde=risk-on)
        # 0.88 = (0.88-0.80)/(0.94-0.80)*100 = 57% → threshold[1]=57
        # 0.84 = (0.84-0.80)/(0.94-0.80)*100 = 29% → threshold[0]=29
        fig_hl_g = gauge(hl_val, "HYG/LQD · Credit Ratio", 0.60, 1.02,
                          thresholds=[24, 48], unit="x", fmt=".4f", invert=False)
        st.plotly_chart(fig_hl_g, use_container_width=True, config={"displayModeBar": False})

        if hyg_lqd_last:
            if hyg_lqd_last > 0.80:
                hl_label, hl_msg, hl_col = "🟢 RISK-ON",  "Spread compressi · HY reggono · no stress sistemico", CYAN
            elif hyg_lqd_last > 0.70:
                hl_label, hl_msg, hl_col = "🟡 NEUTRALE", "Zona normale · HY stabile · monitorare trend", AMBER
            else:
                hl_label, hl_msg, hl_col = "🔴 RISK-OFF", "Spread ampi · stress HY in corso · possibile recessione pricing", RED
            st.markdown(f"""
            <div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;
                        border-radius:4px;font-size:0.63rem;line-height:1.9">
              <b style="color:{hl_col}">{hl_label}</b><br>
              <span style="color:#8ab0c8">{hl_msg}</span><br><br>
              <span style="color:#4a6070">Range storico: ~0.60 crisi → ~1.02 picco (attuale ~0.73 = neutrale)<br>
              HYG = iShares HY Corp · LQD = iShares IG Corp<br>
              Ratio ↓ = spread si allarga = risk-off</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("HYG/LQD: dati non disponibili.")

    with c_hyg2:
        _hl_data = hyg_lqd_long if (hyg_lqd_long is not None and len(hyg_lqd_long) > 5) else hyg_lqd
        if _hl_data is not None and len(_hl_data) > 5:
            hl_ma20 = _hl_data.rolling(20).mean()
            fig_hl  = go.Figure()
            fig_hl.add_trace(go.Scatter(
                x=_hl_data.index, y=_hl_data.values, name="HYG/LQD",
                line=dict(color=CYAN, width=1.5),
                fill="tozeroy", fillcolor="rgba(0,245,196,0.05)"))
            fig_hl.add_trace(go.Scatter(
                x=hl_ma20.index, y=hl_ma20.values, name="MA20",
                line=dict(color=AMBER, width=1.2, dash="dot")))
            fig_hl.add_hline(y=0.80, line_dash="dot", line_color=CYAN, line_width=1,
                annotation_text="0.80 Risk-On", annotation_position="right",
                annotation_font=dict(color=CYAN, size=8))
            fig_hl.add_hline(y=0.70, line_dash="dot", line_color=RED, line_width=1,
                annotation_text="0.70 Stress", annotation_position="right",
                annotation_font=dict(color=RED, size=8))
            fig_hl.update_layout(**base_layout("HYG/LQD Ratio History", 300))
            fig_hl.update_yaxes(range=[0.55, 1.05])
            st.plotly_chart(fig_hl, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("HYG/LQD: dati non disponibili — verifica connessione.")

# ══════════════════════════════════════════════
#  TAB 4 · STRUCTURE
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-label">Market Structure Indicators</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # ── Futures OI ──
    with c1:
        st.markdown('<div class="section-label">S&amp;P 500 Futures Open Interest</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;color:#8ab0c8;margin-bottom:10px;line-height:1.8">'
            '📌 Fonte: <a href="https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.volume.html"'
            ' target="_blank" style="color:#00f5c4;font-weight:700;text-decoration:none;">'
            'CMEGroup.com → E-mini S&P500 → Volume &amp; OI</a>'
            ' → seleziona <b>MAR26 AT CLOSE</b>'
            '</div>',
            unsafe_allow_html=True)

        oi_chg     = sp_oi - sp_oi_prev
        oi_chg_pct = (oi_chg / sp_oi_prev * 100) if sp_oi_prev else 0

        fig_oi = go.Figure(go.Indicator(
            mode="number+delta",
            value=sp_oi,
            delta=dict(reference=sp_oi_prev, valueformat=",", suffix=" contracts",
                       increasing=dict(color=CYAN), decreasing=dict(color=RED)),
            number=dict(valueformat=",",
                        font=dict(family="Syne", size=32, color=CYAN if oi_chg > 0 else RED)),
            title=dict(text="E-mini S&P 500 OI (input manuale)",
                       font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        ))
        fig_oi.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                               height=180, margin=dict(l=20, r=20, t=40, b=10),
                               font=dict(family="Space Mono", color=TEXT_COL))
        st.plotly_chart(fig_oi, use_container_width=True, config={"displayModeBar": False})

        oi_pill = "BULL" if oi_chg > 0 else "BEAR"
        st.markdown(f"""
        <div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;
                    border-radius:4px;font-size:0.7rem;line-height:2">
          WoW Change: <b style="color:{'#00f5c4' if oi_chg>0 else '#ff4d6d'}">{oi_chg:+,} contracts ({oi_chg_pct:+.1f}%)</b><br>
          Signal: {signal_pill(oi_pill)}<br>
          <span style="color:#8ab0c8">Rising OI + rising price = strong trend<br>
          Rising OI + falling price = distribution</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px">COT Data Source</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.62rem;color:#8ab0c8;line-height:1.9">
          → CFTC pubblica COT ogni venerdì ~15:30 ET<br>
          → URL: cftc.gov → Market Reports → Commitments of Traders<br>
          → Filtra: "E-Mini S&P 500 Stock Index" (codice 13874A)<br>
          → Net Non-Commercial = posizionamento grandi speculatori
        </div>
        """, unsafe_allow_html=True)

    # ── Margin Debt ──
    with c2:
        st.markdown('<div class="section-label">Margin Debt (FINRA Mensile)</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;color:#8ab0c8;margin-bottom:10px;line-height:1.8">'
            '📌 Fonte: <a href="https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics"'
            ' target="_blank" style="color:#00f5c4;font-weight:700;text-decoration:none;">'
            'FINRA.org → Margin Statistics</a>'
            ' → aggiorna mensilmente (lag ~3-4 settimane)'
            '</div>',
            unsafe_allow_html=True)

        md_chg     = margin_debt - margin_debt_prev
        md_chg_pct = (md_chg / margin_debt_prev * 100) if margin_debt_prev else 0

        fig_md = go.Figure(go.Indicator(
            mode="number+delta",
            value=margin_debt,
            delta=dict(reference=margin_debt_prev, valueformat=",.0f", suffix="M",
                       increasing=dict(color=CYAN), decreasing=dict(color=RED)),
            number=dict(valueformat=",.0f", suffix="M",
                        font=dict(family="Syne", size=32,
                                  color=CYAN if md_chg > 0 else RED)),
            title=dict(text="FINRA Margin Debt — USD ($M)",
                       font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        ))
        fig_md.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                               height=180, margin=dict(l=20, r=20, t=40, b=10),
                               font=dict(family="Space Mono", color=TEXT_COL))
        st.plotly_chart(fig_md, use_container_width=True, config={"displayModeBar": False})

        md_pill = "BULL" if md_chg > 0 else "NEUTRAL"
        st.markdown(f"""
        <div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;
                    border-radius:4px;font-size:0.7rem;line-height:2">
          MoM Change: <b style="color:{'#00f5c4' if md_chg>0 else '#ff4d6d'}">${md_chg:+,}M ({md_chg_pct:+.1f}%)</b><br>
          Signal: {signal_pill(md_pill)}<br>
          <span style="color:#8ab0c8">Rising margin → leveraged risk-on<br>
          Rapid margin collapse → forced selling risk</span>
        </div>
        """, unsafe_allow_html=True)

    # ── SPY vs VIX overlay ──
    st.markdown('<div class="section-label">SPY vs VIX Overlay</div>', unsafe_allow_html=True)
    if spy_s is not None and vix_s is not None:
        fig_ov = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.04,
                                subplot_titles=("SPY Price", "VIX"),
                                row_heights=[0.65, 0.35])
        fig_ov.add_trace(go.Scatter(x=spy_s.index, y=spy_s.values, name="SPY",
                                     line=dict(color=CYAN, width=1.5)), row=1, col=1)
        if len(spy_s) >= 200:
            ma200 = spy_s.rolling(200).mean()
            fig_ov.add_trace(go.Scatter(x=ma200.index, y=ma200.values, name="200d MA",
                                         line=dict(color=AMBER, width=1, dash="dot")), row=1, col=1)
        fig_ov.add_trace(go.Scatter(x=vix_s.index, y=vix_s.values, name="VIX",
                                     fill="tozeroy", fillcolor="rgba(255,77,109,0.08)",
                                     line=dict(color=RED, width=1.2)), row=2, col=1)
        fig_ov.update_layout(**base_layout("", 360))
        fig_ov.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                               xaxis2=dict(gridcolor=GRID_COL),
                               yaxis2=dict(gridcolor=GRID_COL))
        st.plotly_chart(fig_ov, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#4a6a80;text-align:center;line-height:2">
  EQUITY PULSE · For informational purposes only · Not financial advice<br>
  Automatico: SPY, QQQ, VIX, VIX3M, HYG, LQD (yfinance) · Manuale: Breadth, OI, Margin Debt, P/C CSV<br>
  Deploy: Streamlit Cloud · Source: GitHub
</div>
""", unsafe_allow_html=True)
