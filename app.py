import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import warnings
import re

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
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stFileUploader label {
    font-size: 0.72rem !important;
    color: #c8d8e8 !important;
    letter-spacing: 0.5px !important;
    font-family: 'Space Mono', monospace !important;
  }
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

  .regime-panel {
    background: #080e14;
    border: 1px solid #1c2a3a;
    border-radius: 4px;
    padding: 14px 18px;
    margin-bottom: 12px;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
PLOT_BG  = "#070b12"
PAPER_BG = "#0e1420"
GRID_COL = "#1c2a3a"
CYAN     = "#00f5c4"
RED      = "#ff4d6d"
AMBER    = "#f5a623"
BLUE     = "#4da6ff"
TEXT_COL = "#c8d8e8"

# ─────────────────────────────────────────────
#  HELPERS — LAYOUT
# ─────────────────────────────────────────────
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

def tile(label, value, delta, color_key, unit, pill_label, pct=None, pct_invert=False):
    c = {"cyan": CYAN, "red": RED, "amber": AMBER, "blue": BLUE}.get(color_key, CYAN)
    cls = "metric-tile " + color_key
    delta_html = f'<div class="metric-delta {"up" if "▲" in str(delta) or "+" in str(delta) else "down"}">{delta}</div>' if delta else ""
    pct_html = ""
    if pct is not None:
        p_col = CYAN if (pct > 75 if not pct_invert else pct < 25) else (RED if (pct < 25 if not pct_invert else pct > 75) else AMBER)
        pct_html = f'<div class="pct-badge"><div class="pct-bar-wrap"><div class="pct-bar-fill" style="width:{pct}%; background:{p_col}"></div></div> {pct}%</div>'
    pill_html = f'<div style="margin-top:8px">{signal_pill(pill_label)}</div>' if pill_label else ""
    return f"""
    <div class="{cls}">
      <div class="metric-label">{label}</div>
      <div class="metric-value" style="color:{c}">{value}<span style="font-size:0.8rem;margin-left:2px;color:var(--muted)">{unit}</span></div>
      {delta_html}
      {pct_html}
      {pill_html}
    </div>"""

# ─────────────────────────────────────────────
#  PERCENTILE HELPERS
# ─────────────────────────────────────────────
def percentile_of(series, value):
    if series is None or len(series) < 10 or value is None:
        return None
    clean = series.dropna()
    return round(float((clean < value).sum() / len(clean) * 100), 1)

def percentile_badge_html(pct, invert=False):
    if pct is None: return ""
    p_col = CYAN if (pct > 75 if not invert else pct < 25) else (RED if (pct < 25 if not invert else pct > 75) else AMBER)
    return f'<div class="pct-badge"><div class="pct-bar-wrap"><div class="pct-bar-fill" style="width:{pct}%; background:{p_col}"></div></div> {pct}% 2Y PCT</div>'

# ─────────────────────────────────────────────
#  CFTC PARSER LOGIC
# ─────────────────────────────────────────────
def parse_cftc_report(text):
    """
    Parses the CFTC report text specifically for E-MINI S&P 500.
    """
    try:
        # Trova la sezione E-MINI S&P 500
        section_pattern = r"E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE.*?Positions\n(.*?)\n(.*?)\n"
        match = re.search(section_pattern, text, re.DOTALL | re.IGNORECASE)
        if not match:
            return None, "Sezione 'E-MINI S&P 500' non trovata nel testo."
        
        # Estrai le righe dei dati (Positions e Changes)
        data_lines = text.split("E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE")[1].split("--------------------------------------------------------------------------------")[1]
        lines = [l.strip() for l in data_lines.split("\n") if l.strip()]
        
        # Riga 1: Positions (Dealer, Asset Manager, Leveraged Funds, Other)
        # Formato tipico: Long Short Spreading | Long Short Spreading | Long Short Spreading
        pos_values = re.findall(r"[\d,]+", lines[0])
        
        if len(pos_values) < 9:
            return None, "Formato dati non riconosciuto (troppi pochi valori)."

        # Mapping valori (basato su struttura standard Traders in Financial Futures)
        # Asset Manager: pos_values[3], pos_values[4]
        # Leveraged Funds: pos_values[6], pos_values[7]
        
        results = {
            "asset_long": int(pos_values[3].replace(",", "")),
            "asset_short": int(pos_values[4].replace(",", "")),
            "leveraged_long": int(pos_values[6].replace(",", "")),
            "leveraged_short": int(pos_values[7].replace(",", "")),
            "date": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        return results, None
    except Exception as e:
        return None, f"Errore durante il parsing: {str(e)}"

# ─────────────────────────────────────────────
#  DATA FETCHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=14400, show_spinner=False)
def fetch_price_data(period="1y"):
    tickers = ["SPY", "QQQ", "^VIX", "^VIX3M", "^CPC", "HYG", "LQD", "^TNX", "^IRX"]
    data_display = {}
    data_2y      = {}
    for t in tickers:
        try:
            df_disp = yf.download(t, period=period, progress=False, auto_adjust=True, timeout=15)
            if not df_disp.empty:
                data_display[t] = df_disp
            df_2y = yf.download(t, period="2y", progress=False, auto_adjust=True, timeout=15)
            if not df_2y.empty:
                data_2y[t] = df_2y
        except Exception:
            pass
    return data_display, data_2y

@st.cache_data(ttl=14400, show_spinner=False)
def fetch_hyg_lqd_long():
    result = {}
    for t in ["HYG", "LQD"]:
        try:
            df = yf.download(t, period="5y", progress=False, auto_adjust=True, timeout=15)
            if not df.empty:
                result[t] = df
        except Exception:
            pass
    return result

def get_close(data, ticker):
    df = data.get(ticker)
    if df is None or df.empty:
        return None
    close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.squeeze().dropna()

def compute_hyg_lqd(data):
    hyg = get_close(data, "HYG")
    lqd = get_close(data, "LQD")
    if hyg is None or lqd is None:
        return None
    h, l = hyg.align(lqd, join="inner")
    h = pd.Series(h.values, index=h.index)
    l = pd.Series(l.values, index=l.index)
    return (h / l).dropna()

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

def compute_spy_vix_regime(spy_series, vix_series, window=63):
    if spy_series is None or vix_series is None:
        return None, None, None
    spy_a, vix_a = spy_series.align(vix_series, join="inner")
    spy_a = pd.Series(spy_a.values, index=spy_a.index)
    vix_a = pd.Series(vix_a.values, index=vix_a.index)
    if len(spy_a) < window + 5:
        return None, None, None
    raw   = spy_a / vix_a
    rmean = raw.rolling(window).mean()
    rstd  = raw.rolling(window).std()
    z     = ((raw - rmean) / rstd).dropna()
    z_clipped = z.clip(-3, 3)
    z_norm    = (z_clipped + 3) / 6 * 100
    return z_norm, z, raw

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
_ss_defaults = {
    "s5th": 55, "s5fi": 48, "ndth": 52, "ndfi": 44,
    "sp_oi": 1_932_596, "sp_oi_prev": 1_918_311,
    "margin_debt": 1_279_042, "margin_debt_prev": 1_225_597,
    "period": "1y",
    "cftc_data": None,
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

    st.markdown('<div class="sidebar-section">📊 Breadth — S&P 500</div>', unsafe_allow_html=True)
    s5th = st.number_input("S5TH · % S&P500 sopra 200MA", 0, 100, value=st.session_state["s5th"], key="s5th")
    s5fi = st.number_input("S5FI · % S&P500 sopra 50MA",  0, 100, value=st.session_state["s5fi"], key="s5fi")

    st.markdown('<div class="sidebar-section">📊 Breadth — Nasdaq</div>', unsafe_allow_html=True)
    ndth = st.number_input("NDTH · % Nasdaq sopra 200MA", 0, 100, value=st.session_state["ndth"], key="ndth")
    ndfi = st.number_input("NDFI · % Nasdaq sopra 50MA",  0, 100, value=st.session_state["ndfi"], key="ndfi")

    st.markdown('<div class="sidebar-section">📈 Futures Open Interest</div>', unsafe_allow_html=True)
    sp_oi      = st.number_input("S&P500 Futures OI (contratti)", min_value=0, value=st.session_state["sp_oi"],      step=10_000, key="sp_oi")
    sp_oi_prev = st.number_input("OI settimana precedente",        min_value=0, value=st.session_state["sp_oi_prev"], step=10_000, key="sp_oi_prev")

    st.markdown('<div class="sidebar-section">🏛️ Report CFTC COT</div>', unsafe_allow_html=True)
    cftc_text = st.text_area("Incolla Report CFTC (E-mini S&P)", height=100, placeholder="Copia e incolla il testo dal sito CFTC...")
    if st.button("Parsa dati CFTC incollati", use_container_width=True):
        if cftc_text:
            parsed, err = parse_cftc_report(cftc_text)
            if parsed:
                st.session_state["cftc_data"] = parsed
                st.success("✅ Dati CFTC elaborati con successo!")
            else:
                st.error(f"❌ {err}")
        else:
            st.warning("Incolla il testo prima di parsare.")

    st.markdown('<div class="sidebar-section">💳 Margin Debt (FINRA)</div>', unsafe_allow_html=True)
    margin_debt      = st.number_input("Margin Debt corrente ($M)",        min_value=0, value=st.session_state["margin_debt"],      step=1_000, key="margin_debt")
    margin_debt_prev = st.number_input("Margin Debt mese precedente ($M)", min_value=0, value=st.session_state["margin_debt_prev"], step=1_000, key="margin_debt_prev")

    st.markdown('<div class="sidebar-section">📂 Put/Call CSV (Barchart)</div>', unsafe_allow_html=True)
    _uploaded = st.file_uploader("SPX P/C CSV", type="csv", label_visibility="collapsed")
    if _uploaded is not None:
        _bytes = _uploaded.getvalue()
        if _bytes and len(_bytes) > 10:
            st.session_state["pcr_csv_bytes"] = _bytes
            st.session_state["pcr_csv_name"]  = _uploaded.name
    if "pcr_csv_bytes" in st.session_state:
        _fname = st.session_state.get("pcr_csv_name", "file.csv")
        st.markdown(f'<div style="font-size:0.65rem;color:#00f5c4;margin-top:4px;">✅ {_fname}</div>', unsafe_allow_html=True)
        if st.button("🗑 Rimuovi CSV", use_container_width=True):
            del st.session_state["pcr_csv_bytes"]
            del st.session_state["pcr_csv_name"]
            st.rerun()

    st.markdown('<div class="sidebar-section">⚙️ Impostazioni</div>', unsafe_allow_html=True)
    period_opts = ["6mo", "1y", "2y", "5y"]
    period = st.selectbox("Finestra storica grafici", period_opts,
        index=period_opts.index(st.session_state["period"]), key="period")

    if st.button("🔄 Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Equity Pulse</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multi-Indicator Market Timing · S&P 500 &amp; Nasdaq</div>', unsafe_allow_html=True)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(
    f'<div class="ts-bar">Last fetch: {now} &nbsp;|&nbsp; Breadth/OI/Margin/COT: manuale &nbsp;|&nbsp; Percentili: 2Y rolling</div>',
    unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FETCH & COMPUTE
# ─────────────────────────────────────────────
with st.spinner("Caricamento dati mercato..."):
    data_display, data_2y = fetch_price_data(period)
    data_hyg_long         = fetch_hyg_lqd_long()

spy_s        = get_close(data_display, "SPY")
qqq_s        = get_close(data_display, "QQQ")
vix_s        = get_close(data_display, "^VIX")
tnx_s        = get_close(data_display, "^TNX")
irx_s        = get_close(data_display, "^IRX")
hyg_lqd      = compute_hyg_lqd(data_display)
hyg_lqd_long = compute_hyg_lqd(data_hyg_long)
skew_ratio, vix3m_s, vix_s2 = compute_skew_vix(data_display)
pcr_s        = compute_pcr(data_display)

spy_2y        = get_close(data_2y, "SPY")
vix_2y        = get_close(data_2y, "^VIX")
tnx_2y        = get_close(data_2y, "^TNX")
pcr_2y        = get_close(data_2y, "^CPC")

vix_last      = vix_s.iloc[-1] if vix_s is not None else None
skew_last     = skew_ratio.iloc[-1] if skew_ratio is not None else None
tnx_last      = tnx_s.iloc[-1] if tnx_s is not None else None
spread_2y10y  = (tnx_s.iloc[-1] - irx_s.iloc[-1]) if tnx_s is not None and irx_s is not None else None

pct_vix = percentile_of(vix_2y, vix_last)
pct_tnx = percentile_of(tnx_2y, tnx_last)

# PCR Logic
pcr_last = pcr_s.iloc[-1] if pcr_s is not None else None
pcr_barchart_val, pcr_barchart_puts, pcr_barchart_call = None, None, None
if "pcr_csv_bytes" in st.session_state:
    try:
        import io
        df_pcr = pd.read_csv(io.BytesIO(st.session_state["pcr_csv_bytes"]))
        if "Symbol" in df_pcr.columns:
            spx_row = df_pcr[df_pcr["Symbol"] == "$SPX"].iloc[0]
            pcr_barchart_val  = float(spx_row["Put/Call Ratio"])
            pcr_barchart_puts = int(spx_row["Put Volume"])
            pcr_barchart_call = int(spx_row["Call Volume"])
    except: pass

active_pcr = pcr_barchart_val if pcr_barchart_val else pcr_last
pct_pcr    = percentile_of(pcr_2y, active_pcr)

# ─────────────────────────────────────────────
#  COMPOSITE SCORE & REGIME (WEIGHTED)
# ─────────────────────────────────────────────
# Weights: 
# Breadth: 30%, VIX: 20%, PCR: 15%, HYG/LQD: 15%, OI: 10%, COT: 10%

# Breadth Score (30%)
b_vals = [s5th if s5th is not None else 50, s5fi if s5fi is not None else 50, 
          ndth if ndth is not None else 50, ndfi if ndfi is not None else 50]
breadth_score = sum([b_vals[0] > 60, b_vals[1] > 55, b_vals[2] > 60, b_vals[3] > 55]) / 4 * 100

# VIX Score (20%)
vix_score = 50
if vix_last is not None:
    vix_score = 100 if vix_last < 15 else (0 if vix_last > 25 else 50)

# PCR Score (15%)
pcr_score = 50
if active_pcr is not None:
    pcr_score = 100 if active_pcr < 0.8 else (0 if active_pcr > 1.2 else 50)

# HYG/LQD Score (15%)
hyg_score = 50
if hyg_lqd is not None and not hyg_lqd.empty:
    hyg_score = 100 if hyg_lqd.iloc[-1] > hyg_lqd.mean() else 0

# OI Score (10%)
oi_score = 50
if sp_oi is not None and sp_oi_prev is not None:
    oi_score = 100 if sp_oi > sp_oi_prev else 0

# COT Score (10%)
cot_score = 50
if st.session_state.get("cftc_data") is not None:
    cftc = st.session_state["cftc_data"]
    net_lev = cftc["leveraged_long"] - cftc["leveraged_short"]
    # Bullish if Leveraged Funds are less short than usual or net positive
    cot_score = 100 if net_lev > -300_000 else (0 if net_lev < -600_000 else 50)

total_score = (breadth_score * 0.30) + (vix_score * 0.20) + (pcr_score * 0.15) + (hyg_score * 0.15) + (oi_score * 0.10) + (cot_score * 0.10)
regime_label = "BULL" if total_score > 60 else ("BEAR" if total_score < 40 else "NEUTRAL")
regime_color = CYAN if regime_label == "BULL" else (RED if regime_label == "BEAR" else AMBER)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📡 Overview", "📊 Breadth", "😰 Sentiment", "🏗️ Structure", "📐 Regime"])

# TAB 1 - OVERVIEW (Simplified for brevity, similar to original)
with tab1:
    st.markdown(f'<div class="section-label">Market Pulse Summary · Score: {total_score:.0f}/100</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(tile("Breadth Score", f"{breadth_score:.0f}", None, "cyan", "%", "BULL" if breadth_score > 60 else "NEUTRAL"), unsafe_allow_html=True)
    with c2: st.markdown(tile("VIX Regime", f"{vix_last:.1f}" if vix_last else "N/A", None, "blue", "", "BULL" if vix_last < 18 else "BEAR"), unsafe_allow_html=True)
    with c3: st.markdown(tile("COT Sentiment", "BULL" if cot_score > 60 else ("BEAR" if cot_score < 40 else "NEUTRAL"), None, "amber", "", ""), unsafe_allow_html=True)
    with c4: st.markdown(tile("Global Regime", regime_label, f"{total_score:.0f}%", "cyan" if regime_label=="BULL" else "red", "", regime_label), unsafe_allow_html=True)

# TAB 4 - STRUCTURE (The updated section)
with tab4:
    st.markdown('<div class="section-label">Market Structure Indicators</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">S&amp;P 500 Futures Open Interest</div>', unsafe_allow_html=True)
        oi_chg = sp_oi - sp_oi_prev
        fig_oi = go.Figure(go.Indicator(
            mode="number+delta",
            value=sp_oi,
            delta=dict(reference=sp_oi_prev, valueformat=",", suffix=" contracts", increasing=dict(color=CYAN), decreasing=dict(color=RED)),
            number=dict(valueformat=",", font=dict(family="Syne", size=32, color=CYAN if oi_chg > 0 else RED)),
            title=dict(text="E-mini S&P 500 OI (Manuale)", font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        ))
        fig_oi.update_layout(**base_layout("", 180))
        st.plotly_chart(fig_oi, use_container_width=True, config={"displayModeBar": False})
        
        st.markdown(f"""
        <div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;font-size:0.7rem;line-height:2">
          WoW Change: <b style="color:{'#00f5c4' if oi_chg>0 else '#ff4d6d'}">{oi_chg:+,} contracts</b><br>
          Signal: {signal_pill("BULL" if oi_chg > 0 else "BEAR")}<br>
          <span style="color:#8ab0c8">L'aumento dell'OI conferma il trend in corso.</span>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-label">CFTC Commitments of Traders (COT)</div>', unsafe_allow_html=True)
        if st.session_state["cftc_data"]:
            d = st.session_state["cftc_data"]
            net_asset = d["asset_long"] - d["asset_short"]
            net_lev   = d["leveraged_long"] - d["leveraged_short"]
            
            # Gauge per Leveraged Funds (Speculators)
            fig_cot = go.Figure()
            fig_cot.add_trace(go.Bar(
                x=["Asset Managers", "Leveraged Funds"],
                y=[net_asset, net_lev],
                marker_color=[CYAN, RED if net_lev < 0 else CYAN],
                text=[f"{net_asset:+,}", f"{net_lev:+,}"],
                textposition='auto',
            ))
            fig_cot.update_layout(**base_layout("Net Positioning (Contracts)", 220))
            st.plotly_chart(fig_cot, use_container_width=True, config={"displayModeBar": False})
            
            st.markdown(f"""
            <div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;font-size:0.65rem;line-height:1.6">
              <b style="color:#f5a623">Legenda Operatori:</b><br>
              🏛️ <b>Asset Manager/Institutional:</b> "Long Only" strutturali (Fondi pensione, Assicurazioni). Solitamente net-long.<br>
              ⚡ <b>Leveraged Funds:</b> Hedge Funds e speculatori. Il loro posizionamento netto guida spesso i reversal di mercato.<br>
              🔄 <b>Spreading:</b> Posizioni compensate (long e short simultanei) per strategie relative value.
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Incolla il report CFTC nella sidebar per visualizzare l'analisi del posizionamento.")

    st.markdown('<div class="section-label">Margin Debt & Macro Context</div>', unsafe_allow_html=True)
    # ... Rest of Tab 4 (Margin Debt, Treasury) remains same as original ...
    c3, c4 = st.columns(2)
    with c3:
        md_chg = margin_debt - margin_debt_prev
        st.plotly_chart(gauge(margin_debt, "FINRA Margin Debt ($M)", 500_000, 1_500_000, unit="M"), use_container_width=True)
    with c4:
        st.plotly_chart(gauge(tnx_last if tnx_last else 4.0, "10Y Treasury Yield", 1, 6, unit="%", invert=True), use_container_width=True)

# Note: Other tabs (tab2, tab3, tab5) should be kept from original file to ensure full functionality.
