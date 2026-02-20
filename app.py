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
#  GLOBAL CSS  (dark terminal-finance aesthetic)
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;700;800&display=swap');

  :root {
    --bg:       #070b12;
    --surface:  #0e1420;
    --border:   #1c2a3a;
    --accent1:  #00f5c4;   /* cyan-green  */
    --accent2:  #ff4d6d;   /* red         */
    --accent3:  #f5a623;   /* amber       */
    --accent4:  #4da6ff;   /* blue        */
    --text:     #c8d8e8;
    --muted:    #7a9ab0;
  }

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stApp"],
  [data-testid="stHeader"],
  header[data-testid="stHeader"],
  .stApp,
  .stAppHeader,
  section[data-testid="stSidebarUserContent"],
  div[data-testid="stToolbar"],
  div[data-testid="stDecoration"],
  div[data-testid="stStatusWidget"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
  }

  /* Hide Streamlit top decoration bar and toolbar completely */
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

  /* Section headers */
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

  /* Metric tiles */
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
  .metric-delta {
    font-size: 0.72rem;
    margin-top: 2px;
  }
  .up   { color: var(--accent1); }
  .down { color: var(--accent2); }
  .flat { color: var(--muted);   }

  /* Signal pill */
  .pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 2px;
    font-size: 0.6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
  }
  .pill-bull  { background: rgba(0,245,196,0.12); color: var(--accent1); border: 1px solid var(--accent1); }
  .pill-bear  { background: rgba(255,77,109,0.12); color: var(--accent2); border: 1px solid var(--accent2); }
  .pill-neut  { background: rgba(245,166,35,0.12); color: var(--accent3); border: 1px solid var(--accent3); }

  /* Sidebar labels */
  .sidebar-section {
    font-size: 0.6rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent3);
    margin-top: 20px;
    margin-bottom: 6px;
  }

  div[data-testid="stMetric"] { display: none; }  /* hide default metrics */

  /* Timestamp bar */
  .ts-bar {
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 2px;
    text-align: right;
    margin-bottom: 16px;
  }

  /* Tab styling */
  [data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
  }

  /* Plotly background match */
  .js-plotly-plot { border: 1px solid var(--border) !important; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
PLOT_BG   = "#070b12"
PAPER_BG  = "#0e1420"
GRID_COL  = "#1c2a3a"
CYAN      = "#00f5c4"
RED       = "#ff4d6d"
AMBER     = "#f5a623"
BLUE      = "#4da6ff"
TEXT_COL  = "#c8d8e8"

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
    """Plotly gauge with dark theme.
    invert=True  → alto = rosso (danger), basso = verde (safe) — per VIX, PCR
    invert=False → alto = verde (good),  basso = rosso (bad)  — per breadth, A/D
    """
    if thresholds is None:
        thresholds = [33, 66]
    pct = (value - min_val) / (max_val - min_val) * 100 if (max_val - min_val) else 50

    if invert:
        # Valore alto = pericolo (rosso), valore basso = calma (verde)
        color = RED if pct > 66 else (AMBER if pct > 33 else CYAN)
        step_colors = ["#0a1a14", "#1a150a", "#1a0a0a"]  # green zone → amber → red
    else:
        # Valore alto = buono (verde), valore basso = pericolo (rosso)
        color = CYAN if pct > 60 else (AMBER if pct > 33 else RED)
        step_colors = ["#1a0a0a", "#1a150a", "#0a1a14"]  # red zone → amber → green

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
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        height=220,
        margin=dict(l=20, r=20, t=40, b=10),
        font=dict(family="Space Mono", color=TEXT_COL),
    )
    return fig

def signal_pill(label):
    cls = {"BULL": "pill-bull", "BEAR": "pill-bear", "NEUTRAL": "pill-neut"}.get(label, "pill-neut")
    return f'<span class="pill {cls}">{label}</span>'

def tile(label, value, delta=None, color_class="", unit="", pill_label=None):
    delta_html = ""
    if delta is not None:
        cls = "up" if delta >= 0 else "down"
        sign = "▲" if delta >= 0 else "▼"
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
    """Fetch all market data. Cached 4h to avoid re-fetch on sidebar interactions."""
    tickers = ["SPY", "QQQ", "^VIX", "^VIX3M", "^NYADV", "^NYDEC", "^CPC"]
    data = {}
    for t in tickers:
        try:
            df = yf.download(t, period=period, progress=False, auto_adjust=True,
                             timeout=15)
            if not df.empty:
                data[t] = df
        except Exception:
            pass
    return data

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_cot_data():
    """Fetch CFTC COT report for E-mini S&P 500 (code 13874A)."""
    try:
        url = "https://www.cftc.gov/files/dea/history/fut_fin_xls_2024.zip"
        # Fallback: use cached placeholder if network fails
        return None
    except Exception:
        return None

def get_close(data, ticker):
    df = data.get(ticker)
    if df is None or df.empty:
        return None
    close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
    # yfinance can return a DataFrame with multi-level columns → squeeze to Series
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.squeeze().dropna()

def compute_ad_line(data):
    """
    Costruisce A/D Line cumulativa NYSE.
    Ritorna tuple (ad_line, adv_series, dec_series) oppure (None,None,None).
    """
    adv = get_close(data, "^NYADV")
    dec = get_close(data, "^NYDEC")
    if adv is None or dec is None:
        return None, None, None
    adv_a, dec_a = adv.align(dec, join="inner")
    adv_a = pd.Series(adv_a.values, index=adv_a.index)
    dec_a = pd.Series(dec_a.values, index=dec_a.index)
    diff  = adv_a - dec_a
    ad_cum = diff.cumsum()
    return ad_cum, adv_a, dec_a

def compute_skew_vix(data):
    vix   = get_close(data, "^VIX")
    vix3m = get_close(data, "^VIX3M")
    if vix is None or vix3m is None:
        return None, None, None
    vix3m_aligned, vix_aligned = vix3m.align(vix, join="inner")
    # Ensure both are 1-D Series (yfinance sometimes returns DataFrame)
    if hasattr(vix3m_aligned, "squeeze"):
        vix3m_aligned = vix3m_aligned.squeeze()
    if hasattr(vix_aligned, "squeeze"):
        vix_aligned = vix_aligned.squeeze()
    # Final guard: if still not a plain Series, bail out
    if not isinstance(vix3m_aligned, pd.Series) or not isinstance(vix_aligned, pd.Series):
        return None, None, None
    # Drop any remaining multi-index columns
    vix3m_aligned = pd.Series(vix3m_aligned.values, index=vix3m_aligned.index)
    vix_aligned   = pd.Series(vix_aligned.values,   index=vix_aligned.index)
    ratio = vix3m_aligned / vix_aligned
    return ratio, vix3m_aligned, vix_aligned

def compute_pcr(data):
    """Try yfinance first, fallback returns None (handled by CSV upload)."""
    cpc = get_close(data, "^CPC")
    return cpc

def parse_barchart_pcr(uploaded_file):
    """
    Parsa CSV Barchart SPX Put/Call ratios.
    Aggrega per data: somma Put Vol e Call Vol di tutte le scadenze → PCR giornaliero totale.
    """
    try:
        import io
        raw = uploaded_file.read().decode("utf-8")
        # Rimuovi ultima riga (footer Barchart "Downloaded from...")
        lines = [l for l in raw.splitlines() if not l.startswith('"Downloaded')]
        clean = "\n".join(lines)
        # Tab in header → sostituisci
        clean = clean.replace("Put/Call\tVol", "PC_Vol_Ratio")
        df = pd.read_csv(io.StringIO(clean))
        df.columns = df.columns.str.strip().str.replace('"','')
        # Aggrega per data: weighted PCR = sum(PutVol) / sum(CallVol)
        df["Expiration Date"] = pd.to_datetime(df["Expiration Date"])
        # Filtra solo scadenze entro 60 giorni (near-term, più rilevanti per sentiment)
        df_near = df[df["DTE"] <= 60].copy()
        if df_near.empty:
            df_near = df.copy()
        total_put  = df_near["Put Vol"].sum()
        total_call = df_near["Call Vol"].sum()
        pcr_today  = total_put / total_call if total_call > 0 else None
        # Per grafico storico: restituiamo il PCR aggregato as-of today
        # (il CSV è snapshot giornaliero → un solo punto per upload)
        return pcr_today, total_put, total_call
    except Exception as e:
        return None, None, None


# ─────────────────────────────────────────────
#  SESSION STATE — valori sidebar persistenti
#  Evita re-run completo ad ogni modifica input
# ─────────────────────────────────────────────
_ss_defaults = {
    "s5th": 55, "s5fi": 48, "ndth": 52, "ndfi": 44,
    "sp_oi": 1_932_596, "sp_oi_prev": 1_918_311,  # CME MAR26 19-Feb-2026
    "margin_debt": 798_000, "margin_debt_prev": 782_000,
    "period": "1y",
}
for _k, _v in _ss_defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────
#  SIDEBAR  (manual inputs)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Syne;font-size:1.2rem;font-weight:800;color:#00f5c4;letter-spacing:-0.5px;">⚡ EQUITY PULSE</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.55rem;letter-spacing:3px;color:#4a6070;text-transform:uppercase;margin-bottom:20px;">Manual Data Input</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">📊 Breadth — S&P 500</div>', unsafe_allow_html=True)
    s5th = st.number_input("S5TH · Stocks > 200MA (%)", 0, 100,
        value=st.session_state["s5th"], key="s5th",
        help="% S&P500 above 200d MA — StockCharts: $S5TH")
    s5fi = st.number_input("S5FI · Stocks > 50MA (%)", 0, 100,
        value=st.session_state["s5fi"], key="s5fi",
        help="% S&P500 above 50d MA — StockCharts: $S5FI")

    st.markdown('<div class="sidebar-section">📊 Breadth — Nasdaq</div>', unsafe_allow_html=True)
    ndth = st.number_input("NDTH · Stocks > 200MA (%)", 0, 100,
        value=st.session_state["ndth"], key="ndth",
        help="% Nasdaq above 200d MA — StockCharts: $NDTH")
    ndfi = st.number_input("NDFI · Stocks > 50MA (%)", 0, 100,
        value=st.session_state["ndfi"], key="ndfi",
        help="% Nasdaq above 50d MA — StockCharts: $NDFI")

    st.markdown('<div class="sidebar-section">📈 Futures OI</div>', unsafe_allow_html=True)
    sp_oi = st.number_input("S&P500 Futures OI (contracts)", min_value=0,
        value=st.session_state["sp_oi"], step=10_000, key="sp_oi",
        help="CME: cmegroup.com → E-mini S&P500 → Volume & OI → MAR26 AT CLOSE")
    sp_oi_prev = st.number_input("OI prev. week", min_value=0,
        value=st.session_state["sp_oi_prev"], step=10_000, key="sp_oi_prev")

    st.markdown('<div class="sidebar-section">💳 Margin Debt (FINRA)</div>', unsafe_allow_html=True)
    margin_debt = st.number_input("Margin Debt current ($M)", min_value=0,
        value=st.session_state["margin_debt"], step=1_000, key="margin_debt")
    margin_debt_prev = st.number_input("Margin Debt prev. month ($M)", min_value=0,
        value=st.session_state["margin_debt_prev"], step=1_000, key="margin_debt_prev")

    st.markdown('<div class="sidebar-section">📂 Put/Call CSV (Barchart)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.58rem;color:#7a9ab0;line-height:1.6;margin-bottom:4px;">Upload daily CSV da barchart.com<br>→ SPX Options → Put/Call Ratios → Download</div>', unsafe_allow_html=True)
    _uploaded = st.file_uploader("SPX P/C CSV", type="csv", label_visibility="collapsed")
    if _uploaded is not None:
        _bytes = _uploaded.getvalue()   # getvalue() è più sicuro di read() su Streamlit
        if _bytes and len(_bytes) > 10:
            st.session_state["pcr_csv_bytes"] = _bytes
            st.session_state["pcr_csv_name"]  = _uploaded.name
    if "pcr_csv_bytes" in st.session_state:
        _fname = st.session_state.get("pcr_csv_name", "file.csv")
        st.markdown(f'<div style="font-size:0.58rem;color:#00f5c4;margin-top:4px;">✅ {_fname}</div>', unsafe_allow_html=True)
        if st.button("🗑 Rimuovi CSV", use_container_width=True):
            del st.session_state["pcr_csv_bytes"]
            del st.session_state["pcr_csv_name"]
            st.rerun()

    st.markdown('<div class="sidebar-section">⚙️ Settings</div>', unsafe_allow_html=True)
    period_opts = ["6mo", "1y", "2y", "5y"]
    period = st.selectbox("History window", period_opts,
        index=period_opts.index(st.session_state["period"]), key="period")

    refresh = st.button("🔄 Refresh Data", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown('<div style="font-size:0.55rem;color:#4a6070;line-height:1.6;">Data: yfinance, CBOE<br>Breadth/OI/Margin: manual<br>Update breadth weekly via StockCharts</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">Equity Pulse</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multi-Indicator Market Timing · S&P 500 & Nasdaq</div>', unsafe_allow_html=True)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f'<div class="ts-bar">Last fetch: {now} &nbsp;|&nbsp; Breadth/OI/Margin: manual</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FETCH
# ─────────────────────────────────────────────
# Dati fetchati con cache 4h — non si ricaricano ad ogni interazione sidebar
data = fetch_price_data(period)

# ── PCR da CSV Barchart — legge da session_state (bytes persistenti) ──
pcr_barchart_val  = None
pcr_barchart_puts = None
pcr_barchart_call = None
if "pcr_csv_bytes" in st.session_state:
    try:
        import io as _io
        _raw = st.session_state["pcr_csv_bytes"].decode("utf-8")
        _lines = [l for l in _raw.splitlines() if not l.startswith('"Downloaded')]
        _clean = "\n".join(_lines).replace("Put/Call\tVol", "PC_Vol_Ratio")
        _df = pd.read_csv(_io.StringIO(_clean))
        _df["DTE"]      = pd.to_numeric(_df["DTE"], errors="coerce")
        _df["Put Vol"]  = pd.to_numeric(_df["Put Vol"], errors="coerce")
        _df["Call Vol"] = pd.to_numeric(_df["Call Vol"], errors="coerce")
        _df_near = _df[_df["DTE"] <= 60].dropna(subset=["Put Vol","Call Vol"])
        if not _df_near.empty:
            pcr_barchart_puts = int(_df_near["Put Vol"].sum())
            pcr_barchart_call = int(_df_near["Call Vol"].sum())
            if pcr_barchart_call > 0:
                pcr_barchart_val = round(pcr_barchart_puts / pcr_barchart_call, 4)
    except Exception as _e:
        st.session_state["pcr_parse_error"] = str(_e)

if "pcr_parse_error" in st.session_state:
    # verrà mostrato nel tab Sentiment, non qui
    pass

spy_s  = get_close(data, "SPY")
qqq_s  = get_close(data, "QQQ")
vix_s  = get_close(data, "^VIX")
skew_ratio, vix3m_s, vix_s2 = compute_skew_vix(data)
ad_line, adv_series, dec_series = compute_ad_line(data)
pcr_s   = compute_pcr(data)

def last(series):
    if series is None or len(series) == 0:
        return None
    try:
        val = series.iloc[-1]
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        return float(val)
    except Exception:
        return None

def prev(series, n=1):
    if series is None or len(series) <= n:
        return None
    try:
        val = series.iloc[-(n+1)]
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        return float(val)
    except Exception:
        return None

spy_last  = last(spy_s)
qqq_last  = last(qqq_s)
vix_last  = last(vix_s)
skew_last = last(skew_ratio)
pcr_last  = last(pcr_s)
ad_last   = last(ad_line)

spy_delta  = (spy_last  - prev(spy_s))  if spy_s  is not None and len(spy_s)  > 1 else None
qqq_delta  = (qqq_last  - prev(qqq_s))  if qqq_s  is not None and len(qqq_s)  > 1 else None
vix_delta  = (vix_last  - prev(vix_s))  if vix_s  is not None and len(vix_s)  > 1 else None

# ─────────────────────────────────────────────
#  COMPOSITE SIGNAL (simple scoring)
# ─────────────────────────────────────────────
score = 0
max_score = 7

def score_breadth(s5th, ndth, s5fi, ndfi):
    pts = 0
    if s5th > 60: pts += 1
    if ndth > 60: pts += 1
    if s5fi > 55: pts += 0.5
    if ndfi > 55: pts += 0.5
    return pts   # max 3

def score_vix(v):
    if v is None: return 0
    if v < 15: return 1
    if v < 20: return 0.5
    return 0

def score_pcr(p):
    if p is None: return 0
    if p < 0.7: return 0    # too complacent
    if p < 1.0: return 1    # healthy fear
    return 0.5

def score_skew(r):
    if r is None: return 0
    if r < 1.05: return 1   # flat term structure → calm
    return 0

def score_oi(oi, prev_oi):
    if oi > prev_oi: return 1  # rising OI → conviction
    return 0

def score_margin(m, mp):
    if m > mp: return 1  # rising margin → risk-on
    return 0

total = (score_breadth(s5th, ndth, s5fi, ndfi) +
         score_vix(vix_last) +
         score_pcr(pcr_last) +
         score_skew(skew_last) +
         score_oi(sp_oi, sp_oi_prev) +
         score_margin(margin_debt, margin_debt_prev))

composite_pct = (total / max_score) * 100
composite_label = "BULL" if composite_pct > 60 else ("BEAR" if composite_pct < 38 else "NEUTRAL")

# ─────────────────────────────────────────────
#  LAYOUT — TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📡 Overview", "📊 Breadth", "😰 Sentiment", "🏗️ Structure"])

# ══════════════════════════════════════════════
#  TAB 1 · OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    # Composite gauge + price tiles
    col_g, col_m = st.columns([1, 2])

    with col_g:
        st.markdown('<div class="section-label">Composite Signal</div>', unsafe_allow_html=True)
        fig_comp = gauge(composite_pct, "MARKET PULSE", 0, 100, [33, 66], "%", ".0f")
        st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div style="text-align:center;margin-top:-10px">{signal_pill(composite_label)}</div>', unsafe_allow_html=True)

    with col_m:
        st.markdown('<div class="section-label">Price & Volatility</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            v = f"${spy_last:.2f}" if spy_last else "N/A"
            d = spy_delta
            cc = "" if (d is None or d >= 0) else "red"
            st.markdown(tile("SPY · S&P 500 ETF", v, d, cc, "$"), unsafe_allow_html=True)
        with c2:
            v = f"${qqq_last:.2f}" if qqq_last else "N/A"
            d = qqq_delta
            cc = "" if (d is None or d >= 0) else "red"
            st.markdown(tile("QQQ · Nasdaq ETF", v, d, cc, "$"), unsafe_allow_html=True)
        with c3:
            v = f"{vix_last:.2f}" if vix_last else "N/A"
            d = vix_delta
            vix_pill = "BULL" if vix_last and vix_last < 15 else ("BEAR" if vix_last and vix_last > 25 else "NEUTRAL")
            cc = "red" if vix_last and vix_last > 25 else ("" if vix_last and vix_last < 15 else "amber")
            st.markdown(tile("VIX · Fear Index", v, d, cc, "", vix_pill), unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px">Quick Indicators</div>', unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4:
            skew_v = f"{skew_last:.3f}" if skew_last else "N/A"
            sp = "BULL" if (skew_last and skew_last < 1.05) else "NEUTRAL"
            st.markdown(tile("VIX3M/VIX Ratio", skew_v, None, "blue", "", sp), unsafe_allow_html=True)
        with c5:
            pcr_v = f"{pcr_last:.2f}" if pcr_last else "N/A"
            pp = "BULL" if (pcr_last and 0.7 < pcr_last < 1.0) else ("BEAR" if (pcr_last and pcr_last > 1.1) else "NEUTRAL")
            st.markdown(tile("Put/Call Ratio", pcr_v, None, "amber", "", pp), unsafe_allow_html=True)
        with c6:
            oi_delta = sp_oi - sp_oi_prev
            oi_v = f"{sp_oi/1e6:.2f}M"
            op = "BULL" if oi_delta > 0 else "BEAR"
            st.markdown(tile("S&P Futures OI", oi_v, oi_delta/1e3, "blue" if oi_delta>0 else "red", "K", op), unsafe_allow_html=True)

    # SPY + QQQ time series
    st.markdown('<div class="section-label">Price History</div>', unsafe_allow_html=True)
    if spy_s is not None and qqq_s is not None:
        fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                                   subplot_titles=("SPY", "QQQ"))
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
    st.markdown('<div class="section-label">Breadth Gauges — % Stocks Above Moving Averages</div>', unsafe_allow_html=True)
    st.info("⌨️  Aggiorna settimanalmente i valori nella sidebar → StockCharts: $S5TH, $S5FI, $NDTH, $NDFI", icon="ℹ️")

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

    # Interpretation matrix
    st.markdown('<div class="section-label">Signal Interpretation</div>', unsafe_allow_html=True)
    interp_data = {
        "Indicator": ["S5TH", "S5FI", "NDTH", "NDFI"],
        "Value": [f"{s5th}%", f"{s5fi}%", f"{ndth}%", f"{ndfi}%"],
        "Zone": [
            "🟢 Bull" if v > 70 else ("🔴 Bear" if v < 30 else "🟡 Neutral")
            for v in [s5th, s5fi, ndth, ndfi]
        ],
        "Interpretation": [
            "Strong participation" if s5th > 70 else ("Weak breadth" if s5th < 30 else "Mixed breadth"),
            "Short-term momentum OK" if s5fi > 60 else ("ST selling pressure" if s5fi < 30 else "Deteriorating"),
            "Nasdaq healthy" if ndth > 70 else ("Nasdaq weak" if ndth < 30 else "Tech mixed"),
            "NDX near-term trend OK" if ndfi > 60 else ("NDX caution" if ndfi < 30 else "Watch closely"),
        ],
    }
    df_interp = pd.DataFrame(interp_data)
    st.dataframe(df_interp, hide_index=True, use_container_width=True)

    # Advance/Decline
    st.markdown('<div class="section-label">NYSE Advance/Decline Line (cumulative)</div>', unsafe_allow_html=True)
    if ad_line is not None and spy_s is not None:
        # Grafico stile marketinout: indice sopra, A/D line sotto
        fig_ad = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            subplot_titles=("SPY Price", "NYSE Advance / Decline Line (cumulative)"),
            row_heights=[0.45, 0.55],
        )
        # Panel 1: SPY price
        fig_ad.add_trace(go.Scatter(
            x=spy_s.index, y=spy_s.values, name="SPY",
            line=dict(color=CYAN, width=1.5)), row=1, col=1)

        # Panel 2: A/D line con area
        fig_ad.add_trace(go.Scatter(
            x=ad_line.index, y=ad_line.values, name="A/D Line",
            fill="tozeroy",
            fillcolor="rgba(77,166,255,0.10)",
            line=dict(color=BLUE, width=1.8)), row=2, col=1)

        # A/D smoothed MA 20
        ad_ma = ad_line.rolling(20).mean()
        fig_ad.add_trace(go.Scatter(
            x=ad_ma.index, y=ad_ma.values, name="MA20",
            line=dict(color=AMBER, width=1.2, dash="dot")), row=2, col=1)

        fig_ad.add_hline(y=0, line_dash="dot", line_color="#4a6070", line_width=1, row=2, col=1)

        fig_ad.update_layout(**base_layout("", 420))
        fig_ad.update_layout(
            paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            xaxis2=dict(gridcolor=GRID_COL),
            yaxis2=dict(gridcolor=GRID_COL,
                        title=dict(text="A/D cumul.", font=dict(size=9, color=TEXT_COL))),
        )
        st.plotly_chart(fig_ad, use_container_width=True, config={"displayModeBar": False})

        # Riga metrica A/D
        ad_today = float(ad_line.iloc[-1])
        adv_today = int(adv_series.iloc[-1]) if adv_series is not None else 0
        dec_today = int(dec_series.iloc[-1]) if dec_series is not None else 0
        ad_trend = "🟢 Bullish" if ad_line.iloc[-1] > ad_line.iloc[-5] else "🔴 Bearish"
        st.markdown(f"""
        <div style="display:flex;gap:12px;margin-top:8px">
          <div class="metric-tile blue" style="flex:1">
            <div class="metric-label">A/D Cumulativo</div>
            <div class="metric-value" style="font-size:1.4rem">{ad_today:,.0f}</div>
          </div>
          <div class="metric-tile" style="flex:1">
            <div class="metric-label">Advancing oggi</div>
            <div class="metric-value up" style="font-size:1.4rem">{adv_today:,}</div>
          </div>
          <div class="metric-tile red" style="flex:1">
            <div class="metric-label">Declining oggi</div>
            <div class="metric-value down" style="font-size:1.4rem">{dec_today:,}</div>
          </div>
          <div class="metric-tile amber" style="flex:1">
            <div class="metric-label">Trend A/D (5d)</div>
            <div class="metric-value" style="font-size:1.1rem">{ad_trend}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("A/D Line: ^NYADV / ^NYDEC non disponibili via yfinance in questo momento.")

# ══════════════════════════════════════════════
#  TAB 3 · SENTIMENT
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Volatility & Options Sentiment</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # VIX gauge
    with c1:
        vix_val = vix_last if vix_last else 20
        fig_vix = gauge(vix_val, "VIX · CBOE Volatility Index", 10, 50,
                         thresholds=[25, 60], unit="", fmt=".1f", invert=True)
        st.plotly_chart(fig_vix, use_container_width=True, config={"displayModeBar": False})

        # VIX history
        if vix_s is not None:
            fig_vh = go.Figure()
            fig_vh.add_trace(go.Scatter(x=vix_s.index, y=vix_s.values, name="VIX",
                                         line=dict(color=RED, width=1.3)))
            fig_vh.add_hline(y=20, line_dash="dot", line_color=AMBER, line_width=1,
                              annotation_text="20", annotation_position="right")
            fig_vh.add_hline(y=15, line_dash="dot", line_color=CYAN, line_width=1,
                              annotation_text="15", annotation_position="right")
            fig_vh.update_layout(**base_layout("VIX History", 260))
            st.plotly_chart(fig_vh, use_container_width=True, config={"displayModeBar": False})

    # SKEW proxy + PCR
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
            fig_skh.add_hline(y=1.0, line_dash="dot", line_color=TEXT_COL, line_width=1)
            fig_skh.update_layout(**base_layout("VIX3M/VIX Ratio History", 260))
            st.plotly_chart(fig_skh, use_container_width=True, config={"displayModeBar": False})

    # Put/Call Ratio — CSV Barchart ha priorità, poi yfinance
    st.markdown('<div class="section-label">Put/Call Ratio SPX — Near-Term Options</div>', unsafe_allow_html=True)

    # Debug stato CSV
    _csv_loaded = "pcr_csv_bytes" in st.session_state
    _parse_err  = st.session_state.get("pcr_parse_error", None)
    if not _csv_loaded:
        st.info("📂 Carica il CSV Barchart nella sidebar (Browse files) per il P/C Ratio SPX in tempo reale.", icon="📂")
    elif _parse_err:
        st.error(f"⚠️ Errore parsing CSV: {_parse_err}")
    elif pcr_barchart_val:
        st.success(f"✅ CSV caricato · PCR SPX = **{pcr_barchart_val:.4f}** ({st.session_state.get('pcr_csv_name','')})")

    # Determina valore PCR attivo
    active_pcr   = pcr_barchart_val if pcr_barchart_val else (pcr_last if pcr_last else None)
    pcr_source   = "Barchart CSV" if pcr_barchart_val else ("yfinance ^CPC" if pcr_last else "N/A")
    pcr_series   = pcr_s  # storico yfinance se disponibile

    c3, c4 = st.columns([1, 3])
    with c3:
        pcr_display = active_pcr if active_pcr else 0.85
        fig_pcr_g = gauge(pcr_display, f"Put/Call · {pcr_source}", 0.4, 1.8,
                           thresholds=[35, 65], unit="x", fmt=".2f", invert=True)
        st.plotly_chart(fig_pcr_g, use_container_width=True, config={"displayModeBar": False})

        # Se CSV: mostra breakdown Put/Call volumi
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
            fig_pcr.add_trace(go.Bar(x=pcr_series.index, y=pcr_series.values, name="Daily P/C",
                                      marker_color="rgba(77,166,255,0.25)"))
            fig_pcr.add_trace(go.Scatter(x=pcr_ma.index, y=pcr_ma.values, name="10d SMA",
                                          line=dict(color=BLUE, width=1.8)))
            # Marca valore oggi da CSV se disponibile
            if pcr_barchart_val:
                fig_pcr.add_hline(y=pcr_barchart_val, line_dash="solid",
                                   line_color=AMBER, line_width=1.5,
                                   annotation_text=f"Today CSV: {pcr_barchart_val:.2f}",
                                   annotation_position="top right",
                                   annotation_font=dict(color=AMBER, size=9))
            fig_pcr.add_hline(y=1.0, line_dash="dot", line_color=RED, line_width=1)
            fig_pcr.add_hline(y=0.7, line_dash="dot", line_color=CYAN, line_width=1,
                               annotation_text="0.70", annotation_position="right",
                               annotation_font=dict(color=CYAN, size=8))
            fig_pcr.update_layout(**base_layout("Storico P/C (^CPC yfinance) + oggi CSV", 280))
            st.plotly_chart(fig_pcr, use_container_width=True, config={"displayModeBar": False})
        elif pcr_barchart_val:
            # Solo dato oggi, nessuno storico
            st.markdown(f"""
            <div style="background:#0e1420;border:1px solid #1c2a3a;padding:20px;
                        border-radius:4px;text-align:center;margin-top:20px">
              <div style="font-size:0.6rem;letter-spacing:3px;color:#7a9ab0">P/C RATIO OGGI (CSV)</div>
              <div style="font-family:Syne;font-size:3rem;font-weight:700;
                          color:{'#ff4d6d' if pcr_barchart_val > 1.0 else '#00f5c4'}">{pcr_barchart_val:.3f}</div>
              <div style="font-size:0.65rem;color:#7a9ab0">Carica il CSV ogni giorno per aggiornare</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("📂 Carica il CSV Barchart nella sidebar per visualizzare il P/C Ratio SPX.")

    # PCR interpretation note
    st.markdown("""
    <div style="font-size:0.65rem;color:#8ab0c8;border:1px solid #1c2a3a;padding:10px;border-radius:4px;line-height:1.8">
      <b style="color:#c8d8e8">P/C Ratio Guide:</b>&nbsp;
      P/C &lt; 0.7 → Complacency / Risk &nbsp;|&nbsp;
      0.7–1.0 → Healthy Fear / Opportunity &nbsp;|&nbsp;
      P/C &gt; 1.1 → Capitulation Signal &nbsp;|&nbsp;
      <b>VIX3M/VIX &lt; 1</b> = inverted term structure → stress
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  TAB 4 · STRUCTURE
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-label">Market Structure Indicators</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # --- Futures OI
    with c1:
        st.markdown('<div class="section-label">S&P 500 Futures Open Interest</div>', unsafe_allow_html=True)
        oi_chg = sp_oi - sp_oi_prev
        oi_chg_pct = (oi_chg / sp_oi_prev * 100) if sp_oi_prev else 0

        fig_oi = go.Figure(go.Indicator(
            mode="number+delta",
            value=sp_oi,
            delta=dict(reference=sp_oi_prev, valueformat=",", suffix=" contracts",
                       increasing=dict(color=CYAN), decreasing=dict(color=RED)),
            number=dict(valueformat=",", font=dict(family="Syne", size=32, color=CYAN
                                                    if oi_chg > 0 else RED)),
            title=dict(text="E-mini S&P 500 OI (manual input)", font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        ))
        fig_oi.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                               height=180, margin=dict(l=20, r=20, t=40, b=10),
                               font=dict(family="Space Mono", color=TEXT_COL))
        st.plotly_chart(fig_oi, use_container_width=True, config={"displayModeBar": False})

        oi_pill = "BULL" if oi_chg > 0 else "BEAR"
        st.markdown(f"""
        <div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;font-size:0.7rem;line-height:2">
          WoW Change: <b style="color:{'#00f5c4' if oi_chg>0 else '#ff4d6d'}">{oi_chg:+,} contracts ({oi_chg_pct:+.1f}%)</b><br>
          Signal: {signal_pill(oi_pill)}<br>
          <span style="color:#8ab0c8">Rising OI + rising price = strong trend<br>
          Rising OI + falling price = distribution</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px">COT Data Source</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.62rem;color:#8ab0c8;line-height:1.9">
          → CFTC publishes COT every Friday ~15:30 ET<br>
          → URL: cftc.gov → Market Reports → Commitments of Traders<br>
          → Filter: "E-Mini S&P 500 Stock Index" (code 13874A)<br>
          → Net Non-Commercial = large speculator positioning
        </div>
        """, unsafe_allow_html=True)

    # --- Margin Debt
    with c2:
        st.markdown('<div class="section-label">Margin Debt (FINRA Monthly)</div>', unsafe_allow_html=True)
        md_chg = margin_debt - margin_debt_prev
        md_chg_pct = (md_chg / margin_debt_prev * 100) if margin_debt_prev else 0

        fig_md = go.Figure(go.Indicator(
            mode="number+delta",
            value=margin_debt,
            delta=dict(reference=margin_debt_prev, valueformat=",.0f", suffix="M",
                       increasing=dict(color=CYAN), decreasing=dict(color=RED)),
            number=dict(valueformat=",.0f", suffix="M",
                        font=dict(family="Syne", size=32,
                                  color=CYAN if md_chg > 0 else RED)),
            title=dict(text="FINRA Margin Debt — USD ($M)", font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        ))
        fig_md.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                               height=180, margin=dict(l=20, r=20, t=40, b=10),
                               font=dict(family="Space Mono", color=TEXT_COL))
        st.plotly_chart(fig_md, use_container_width=True, config={"displayModeBar": False})

        md_pill = "BULL" if md_chg > 0 else "NEUTRAL"
        st.markdown(f"""
        <div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;font-size:0.7rem;line-height:2">
          MoM Change: <b style="color:{'#00f5c4' if md_chg>0 else '#ff4d6d'}">${md_chg:+,}M ({md_chg_pct:+.1f}%)</b><br>
          Signal: {signal_pill(md_pill)}<br>
          <span style="color:#8ab0c8">Rising margin → leveraged risk-on<br>
          Rapid margin collapse → forced selling risk</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px">Data Source</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.62rem;color:#8ab0c8;line-height:1.9">
          → finra.org → Investors → Margin Statistics<br>
          → Published monthly, ~3-4 week lag<br>
          → Historical CSV available for download<br>
          → Update sidebar values monthly
        </div>
        """, unsafe_allow_html=True)

    # SPY + VIX overlay
    st.markdown('<div class="section-label">SPY vs VIX Overlay</div>', unsafe_allow_html=True)
    if spy_s is not None and vix_s is not None:
        fig_ov = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.04,
                                subplot_titles=("SPY Price", "VIX"),
                                row_heights=[0.65, 0.35])
        fig_ov.add_trace(go.Scatter(x=spy_s.index, y=spy_s.values, name="SPY",
                                     line=dict(color=CYAN, width=1.5)), row=1, col=1)

        # 200-day MA overlay
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
  Automated: SPY, QQQ, VIX, VIX3M, Put/Call (yfinance/CBOE) · Manual: Breadth, OI, Margin Debt<br>
  Deploy: Streamlit Cloud · Source: GitHub
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#4a6a80;text-align:center;line-height:2">
  EQUITY PULSE · For informational purposes only · Not financial advice<br>
  Automated: SPY, QQQ, VIX, VIX3M, Put/Call (yfinance/CBOE) · Manual: Breadth, OI, Margin Debt<br>
  Deploy: Streamlit Cloud · Source: GitHub
</div>
""", unsafe_allow_html=True)
