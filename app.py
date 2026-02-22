import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import warnings
warnings.filterwarnings("ignore")

# PAGE CONFIG
st.set_page_config(
    page_title="EQUITY PULSE - Market Dashboard",
    page_icon="EP",
    layout="wide",
    initial_sidebar_state="expanded",
)

# GLOBAL CSS
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
  .pct-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    margin-top: 5px;
    font-size: 0.58rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--muted);
  }
  .pct-bar-wrap {
    display: inline-block;
    width: 48px;
    height: 3px;
    background: #1c2a3a;
    border-radius: 2px;
    vertical-align: middle;
    position: relative;
    overflow: hidden;
  }
  .pct-bar-fill {
    position: absolute;
    top: 0; left: 0;
    height: 100%;
    border-radius: 2px;
  }
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

# CONSTANTS
PLOT_BG  = "#070b12"
PAPER_BG = "#0e1420"
GRID_COL = "#1c2a3a"
CYAN     = "#00f5c4"
RED      = "#ff4d6d"
AMBER    = "#f5a623"
BLUE     = "#4da6ff"
TEXT_COL = "#c8d8e8"

# HELPERS
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

def percentile_of(series, value):
    if series is None or len(series) < 10 or value is None:
        return None
    clean = series.dropna()
    return round(float((clean < value).sum() / len(clean) * 100), 1)

def pct_color(pct, invert=False):
    if pct is None:
        return AMBER
    if invert:
        return RED if pct > 75 else (AMBER if pct > 40 else CYAN)
    else:
        return CYAN if pct > 75 else (AMBER if pct > 40 else RED)

def percentile_badge_html(pct, invert=False):
    if pct is None:
        return ""
    col = pct_color(pct, invert)
    width = int(pct)
    return (
        f'<div class="pct-badge">'
        f'<span class="pct-bar-wrap">'
        f'<span class="pct-bar-fill" style="width:{width}%;background:{col}"></span>'
        f'</span>'
        f'<span style="color:{col};font-weight:700">{pct:.0f} pct 2Y</span>'
        f'</div>'
    )

def tile(label, value, delta=None, color_class="", unit="", pill_label=None, pct=None, pct_invert=False):
    delta_html = ""
    if delta is not None:
        cls  = "up" if delta >= 0 else "down"
        sign = "+" if delta >= 0 else "-"
        delta_html = f'<div class="metric-delta {cls}">{sign} {abs(delta):.2f}{unit}</div>'
    pill_html = f'<div style="margin-top:6px">{signal_pill(pill_label)}</div>' if pill_label else ""
    pct_html  = percentile_badge_html(pct, pct_invert) if pct is not None else ""
    return (
        f'<div class="metric-tile {color_class}">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'{delta_html}{pct_html}{pill_html}'
        f'</div>'
    )

# DATA FETCHING
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

def compute_spy_vix_ratio(spy_series, vix_series, window=63):
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

# SESSION STATE
_ss_defaults = {
    "s5th": 55, "s5fi": 48, "ndth": 52, "ndfi": 44,
    "sp_oi": 1_932_596, "sp_oi_prev": 1_918_311,
    "margin_debt": 1_279_042, "margin_debt_prev": 1_225_597,
    "period": "1y",
}
for _k, _v in _ss_defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# SIDEBAR
with st.sidebar:
    st.markdown(
        '<div style="font-family:Syne;font-size:1.2rem;font-weight:800;color:#00f5c4;letter-spacing:-0.5px;">EQUITY PULSE</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.6rem;letter-spacing:3px;color:#4a6070;text-transform:uppercase;margin-bottom:16px;">Manual Data Input</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Breadth - S&P 500</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:2.1;margin-bottom:6px;">'
        '<a href="https://www.barchart.com/stocks/quotes/$S5TH/overview" target="_blank">$S5TH</a>'
        ' - % S&amp;P500 sopra 200MA<br>'
        '<a href="https://www.barchart.com/stocks/quotes/$S5FI/overview" target="_blank">$S5FI</a>'
        ' - % S&amp;P500 sopra 50MA</div>', unsafe_allow_html=True)
    s5th = st.number_input("S5TH - % S&P500 sopra 200MA", 0, 100, value=st.session_state["s5th"], key="s5th")
    s5fi = st.number_input("S5FI - % S&P500 sopra 50MA",  0, 100, value=st.session_state["s5fi"], key="s5fi")

    st.markdown('<div class="sidebar-section">Breadth - Nasdaq</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:2.1;margin-bottom:6px;">'
        '<a href="https://www.barchart.com/stocks/quotes/$NDTH/overview" target="_blank">$NDTH</a>'
        ' - % Nasdaq sopra 200MA<br>'
        '<a href="https://www.barchart.com/stocks/quotes/$NDFI/overview" target="_blank">$NDFI</a>'
        ' - % Nasdaq sopra 50MA</div>', unsafe_allow_html=True)
    ndth = st.number_input("NDTH - % Nasdaq sopra 200MA", 0, 100, value=st.session_state["ndth"], key="ndth")
    ndfi = st.number_input("NDFI - % Nasdaq sopra 50MA",  0, 100, value=st.session_state["ndfi"], key="ndfi")

    st.markdown('<div class="sidebar-section">Futures Open Interest</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:1.7;margin-bottom:6px;">'
        'Fonte: <a href="https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.volume.html" target="_blank">CMEGroup.com</a>'
        ' - E-mini S&amp;P500 - MAR26 AT CLOSE</div>', unsafe_allow_html=True)
    sp_oi      = st.number_input("S&P500 Futures OI (contratti)", min_value=0, value=st.session_state["sp_oi"],      step=10_000, key="sp_oi")
    sp_oi_prev = st.number_input("OI settimana precedente",        min_value=0, value=st.session_state["sp_oi_prev"], step=10_000, key="sp_oi_prev")

    st.markdown('<div class="sidebar-section">Margin Debt (FINRA)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:1.7;margin-bottom:6px;">'
        'Fonte: <a href="https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics" target="_blank">FINRA.org</a>'
        ' - aggiorna mensilmente</div>', unsafe_allow_html=True)
    margin_debt      = st.number_input("Margin Debt corrente ($M)",        min_value=0, value=st.session_state["margin_debt"],      step=1_000, key="margin_debt")
    margin_debt_prev = st.number_input("Margin Debt mese precedente ($M)", min_value=0, value=st.session_state["margin_debt_prev"], step=1_000, key="margin_debt_prev")

    st.markdown('<div class="sidebar-section">COT Report (CFTC)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:1.7;margin-bottom:6px;">'
        'Fonte: <a href="https://www.cftc.gov/dea/futures/financial_lf.htm" target="_blank">CFTC.gov</a>'
        ' - copia testo pagina - incolla qui</div>', unsafe_allow_html=True)
    cot_text = st.text_area("Testo report CFTC", height=120,
        placeholder="Incolla qui il testo del report CFTC...",
        label_visibility="collapsed",
        value=st.session_state.get("cot_raw_text", ""))

    if st.button("Parsa dati CFTC", use_container_width=True):
        if cot_text.strip():
            st.session_state["cot_raw_text"] = cot_text
            try:
                lines = cot_text.splitlines()
                target_idx = None
                for i, line in enumerate(lines):
                    if "13874A" in line or "E-MINI S&P 500" in line:
                        target_idx = i
                        break
                if target_idx is None:
                    st.session_state["cot_parse_ok"] = False
                    st.error("Blocco E-mini S&P 500 non trovato.")
                else:
                    oi_total, pos_line = None, None
                    for line in lines[target_idx:target_idx+15]:
                        if "Open Interest is" in line:
                            oi_total = int(''.join(filter(str.isdigit, line.split("Open Interest is")[1][:12])))
                        if pos_line is None and oi_total is not None:
                            nums = [x.replace(",","") for x in line.split() if x.replace(",","").lstrip("-").isdigit()]
                            if len(nums) >= 8:
                                pos_line = nums
                    if pos_line and len(pos_line) >= 8:
                        am_l = int(pos_line[3])
                        am_s = int(pos_line[4])
                        lf_l = int(pos_line[6])
                        lf_s = int(pos_line[7])
                        st.session_state["cot_data"] = {
                            "oi": oi_total,
                            "am_long": am_l, "am_short": am_s, "net_am": am_l - am_s,
                            "lf_long": lf_l, "lf_short": lf_s, "net_lf": lf_l - lf_s,
                            "dealer_long": int(pos_line[0]), "dealer_short": int(pos_line[1]),
                        }
                        st.session_state["cot_parse_ok"] = True
                        st.rerun()
                    else:
                        st.error("Posizioni non trovate nel blocco.")
            except Exception as e:
                st.error(f"Errore: {e}")
        else:
            st.warning("Incolla prima il testo del report.")

    if st.session_state.get("cot_parse_ok"):
        _cd = st.session_state["cot_data"]
        net_am_col = "#00f5c4" if _cd["net_am"] > 0 else "#ff4d6d"
        net_lf_col = "#00f5c4" if _cd["net_lf"] > 0 else "#ff4d6d"
        st.markdown(
            '<div style="font-size:0.62rem;background:#080e14;border:1px solid #1c2a3a;'
            'padding:8px 10px;border-radius:4px;line-height:2;margin-top:4px">'
            f'<b style="color:#00f5c4">E-mini S&P 500 parsato</b><br>'
            f'Net AM: <b style="color:{net_am_col}">{_cd["net_am"]:+,}</b><br>'
            f'Net LF: <b style="color:{net_lf_col}">{_cd["net_lf"]:+,}</b>'
            '</div>',
            unsafe_allow_html=True)
        if st.button("Rimuovi COT", use_container_width=True):
            for k in ["cot_data", "cot_raw_text", "cot_parse_ok"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.markdown('<div class="sidebar-section">Put/Call CSV (Barchart)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.68rem;color:#8ab0c8;line-height:1.7;margin-bottom:6px;">'
        'Fonte: <a href="https://www.barchart.com/options/put-call-ratios/spx" target="_blank">Barchart.com</a>'
        ' - SPX Options - Put/Call Ratios - Download CSV</div>', unsafe_allow_html=True)
    _uploaded = st.file_uploader("SPX P/C CSV", type="csv", label_visibility="collapsed")
    if _uploaded is not None:
        _bytes = _uploaded.getvalue()
        if _bytes and len(_bytes) > 10:
            st.session_state["pcr_csv_bytes"] = _bytes
            st.session_state["pcr_csv_name"]  = _uploaded.name
    if "pcr_csv_bytes" in st.session_state:
        _fname = st.session_state.get("pcr_csv_name", "file.csv")
        st.markdown(f'<div style="font-size:0.65rem;color:#00f5c4;margin-top:4px;">OK {_fname}</div>', unsafe_allow_html=True)
        if st.button("Rimuovi CSV", use_container_width=True):
            del st.session_state["pcr_csv_bytes"]
            del st.session_state["pcr_csv_name"]
            st.rerun()

    st.markdown('<div class="sidebar-section">Impostazioni</div>', unsafe_allow_html=True)
    period_opts = ["6mo", "1y", "2y", "5y"]
    period = st.selectbox("Finestra storica grafici", period_opts,
        index=period_opts.index(st.session_state["period"]), key="period")
    st.caption("Percentili sempre calcolati su 2 anni indipendentemente dalla finestra display.")

    if st.button("Aggiorna Dati", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.58rem;color:#4a6070;line-height:1.8;">'
        'Automatico: SPY, QQQ, VIX, VIX3M, HYG, LQD, TNX, IRX<br>'
        'Percentili: finestra fissa 2Y rolling<br>'
        'SPY/VIX Regime: z-score rolling 63 giorni<br>'
        'Manuale: Breadth (sett.), OI, Margin Debt<br>'
        'P/C Ratio: CSV Barchart (giornaliero)'
        '</div>', unsafe_allow_html=True)

# HEADER
st.markdown('<div class="main-title">Equity Pulse</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multi-Indicator Market Timing - S&P 500 &amp; Nasdaq</div>', unsafe_allow_html=True)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(
    f'<div class="ts-bar">Last fetch: {now} &nbsp;|&nbsp; Breadth/OI/Margin: manuale &nbsp;|&nbsp; Percentili: 2Y rolling</div>',
    unsafe_allow_html=True)

# FETCH & COMPUTE
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
qqq_2y        = get_close(data_2y, "QQQ")
vix_2y        = get_close(data_2y, "^VIX")
tnx_2y        = get_close(data_2y, "^TNX")
pcr_2y        = get_close(data_2y, "^CPC")
hyg_lqd_2y    = compute_hyg_lqd(data_2y)
skew_2y, _, _ = compute_skew_vix(data_2y)

spy_vix_norm_disp, spy_vix_z_disp, spy_vix_raw_disp = compute_spy_vix_ratio(spy_s, vix_s, window=63)

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
tnx_last      = last(tnx_s)
irx_last      = last(irx_s)
spread_2y10y  = round(tnx_last - irx_last, 2) if (tnx_last and irx_last) else None
active_pcr    = pcr_barchart_val if pcr_barchart_val else (pcr_last if pcr_last else None)

spy_vix_norm_last = last(spy_vix_norm_disp)
spy_vix_z_last    = last(spy_vix_z_disp)

spy_delta = (spy_last - prev(spy_s)) if spy_s is not None and len(spy_s) > 1 else None
qqq_delta = (qqq_last - prev(qqq_s)) if qqq_s is not None and len(qqq_s) > 1 else None
vix_delta = (vix_last - prev(vix_s)) if vix_s is not None and len(vix_s) > 1 else None

pct_spy   = percentile_of(spy_2y,      spy_last)
pct_qqq   = percentile_of(qqq_2y,      qqq_last)
pct_vix   = percentile_of(vix_2y,      vix_last)
pct_pcr   = percentile_of(pcr_2y,      active_pcr)
pct_hl    = percentile_of(hyg_lqd_2y,  hyg_lqd_last)
pct_tnx   = percentile_of(tnx_2y,      tnx_last)
pct_skew  = percentile_of(skew_2y,     skew_last)

def spy_vix_regime(z):
    if z is None:  return "NEUTRAL",     AMBER, "Dati insufficienti"
    if z > 1.0:    return "RISK-ON",     CYAN,  "SPY forte vs VIX - regime favorevole agli asset rischiosi"
    if z < -1.0:   return "RISK-OFF",    RED,   "VIX elevato vs prezzo - regime difensivo"
    return             "TRANSITIONAL", AMBER, "Regime incerto - momentum debole o inversione in corso"

regime_label, regime_color, regime_desc = spy_vix_regime(spy_vix_z_last)

# COMPOSITE SIGNAL
max_score = 10

def score_breadth(s5, nd, s5f, ndf):
    pts = 0
    if s5  > 60: pts += 1
    if nd  > 60: pts += 1
    if s5f > 55: pts += 0.5
    if ndf > 55: pts += 0.5
    return pts

def score_vix(v):
    if v is None: return 0
    return 1 if v < 15 else (0.5 if v < 25 else 0)

def score_pcr(p):
    if p is None: return 0
    if p < 0.7:  return 0
    if p < 1.0:  return 1
    return 0.5

def score_skew(r):
    if r is None: return 0
    return 1 if r < 1.05 else 0

def score_oi(oi, prev_oi):   return 1 if oi > prev_oi else 0
def score_margin(m, mp):     return 1 if m  > mp      else 0

def score_10y(y):
    if y is None: return 0
    return 1 if y < 3.5 else (0.5 if y < 4.5 else 0)

def score_hyg_lqd(ratio):
    if ratio is None: return 0
    return 1 if ratio > 0.80 else (0.5 if ratio > 0.70 else 0)

def score_spy_vix(z):
    if z is None:  return 0
    if z > 1.0:    return 1.0
    if z > -1.0:   return 0.5
    return 0.0

total = (score_breadth(s5th, ndth, s5fi, ndfi) +
         score_vix(vix_last) +
         score_pcr(active_pcr) +
         score_skew(skew_last) +
         score_oi(sp_oi, sp_oi_prev) +
         score_margin(margin_debt, margin_debt_prev) +
         score_hyg_lqd(hyg_lqd_last) +
         score_10y(tnx_last) +
         score_spy_vix(spy_vix_z_last))

composite_pct   = (total / max_score) * 100
composite_label = "BULL" if composite_pct > 60 else ("BEAR" if composite_pct < 38 else "NEUTRAL")

# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Breadth", "Sentiment", "Structure", "Regime"
])

# ══════════════════════════════════════════════
#  TAB 1 - OVERVIEW
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

        _sc_breadth  = score_breadth(s5th, ndth, s5fi, ndfi)
        _sc_vix      = score_vix(vix_last)
        _sc_pcr      = score_pcr(active_pcr)
        _sc_skew     = score_skew(skew_last)
        _sc_hyg      = score_hyg_lqd(hyg_lqd_last)
        _sc_oi       = score_oi(sp_oi, sp_oi_prev)
        _sc_margin   = score_margin(margin_debt, margin_debt_prev)
        _sc_10y      = score_10y(tnx_last)
        _sc_spy_vix  = score_spy_vix(spy_vix_z_last)

        def _bar(score, max_s):
            pct_v  = int((score / max_s) * 100)
            col    = '#00f5c4' if pct_v >= 80 else ('#f5a623' if pct_v >= 40 else '#ff4d6d')
            filled = int(score / max_s * 8)
            empty  = 8 - filled
            bar    = (f'<span style="color:{col}">{"X" * filled}</span>'
                      f'<span style="color:#1c2a3a">{"." * empty}</span>')
            return bar, col

        _rows = [
            ('Breadth',        _sc_breadth, 3),
            ('VIX',            _sc_vix,     1),
            ('Put/Call',       _sc_pcr,     1),
            ('VIX3M/VIX',      _sc_skew,    1),
            ('HYG/LQD',        _sc_hyg,     1),
            ('OI Futures',     _sc_oi,      1),
            ('Margin Debt',    _sc_margin,  1),
            ('10Y Yield',      _sc_10y,     1),
            ('SPY/VIX Regime', _sc_spy_vix, 1),
        ]
        _rows_html = ''.join([
            f'<tr>'
            f'<td style="padding:2px 6px;font-size:0.58rem;color:#7a9ab0;white-space:nowrap">{name}</td>'
            f'<td style="padding:2px 6px;font-size:0.58rem">{_bar(sc, mx)[0]}</td>'
            f'<td style="padding:2px 6px;font-size:0.58rem;color:{_bar(sc, mx)[1]};text-align:right">{sc}/{mx}</td>'
            f'</tr>'
            for name, sc, mx in _rows
        ])
        st.markdown(
            f'<div style="background:#080e14;border:1px solid #1c2a3a;border-radius:4px;padding:10px 12px;margin-top:10px">'
            f'<div style="font-size:0.55rem;letter-spacing:3px;color:#4a6070;text-transform:uppercase;margin-bottom:6px">Score Breakdown</div>'
            f'<table style="width:100%;border-collapse:collapse">{_rows_html}</table>'
            f'<div style="font-size:0.52rem;color:#4a6070;margin-top:6px;text-align:right">Totale: {total:.1f} / {max_score} pt</div>'
            f'</div>',
            unsafe_allow_html=True)

    with col_m:
        st.markdown('<div class="section-label">Price &amp; Volatility</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            v  = f"${spy_last:.2f}" if spy_last else "N/A"
            cc = "" if (spy_delta is None or spy_delta >= 0) else "red"
            st.markdown(tile("SPY - S&P 500 ETF", v, spy_delta, cc, "$", pct=pct_spy), unsafe_allow_html=True)
        with c2:
            v  = f"${qqq_last:.2f}" if qqq_last else "N/A"
            cc = "" if (qqq_delta is None or qqq_delta >= 0) else "red"
            st.markdown(tile("QQQ - Nasdaq ETF", v, qqq_delta, cc, "$", pct=pct_qqq), unsafe_allow_html=True)
        with c3:
            v        = f"{vix_last:.2f}" if vix_last else "N/A"
            vix_pill = "BULL" if vix_last and vix_last < 15 else ("BEAR" if vix_last and vix_last > 25 else "NEUTRAL")
            cc       = "red" if vix_last and vix_last > 25 else ("" if vix_last and vix_last < 15 else "amber")
            st.markdown(tile("VIX - Fear Index", v, vix_delta, cc, "", vix_pill, pct=pct_vix, pct_invert=True), unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px">Quick Indicators</div>', unsafe_allow_html=True)
        c4, c5, c6, c7, c8 = st.columns(5)
        with c4:
            skew_v = f"{skew_last:.3f}" if skew_last else "N/A"
            sp_s_  = "BULL" if (skew_last and skew_last < 1.05) else "NEUTRAL"
            st.markdown(tile("VIX3M/VIX", skew_v, None, "blue", "", sp_s_, pct=pct_skew), unsafe_allow_html=True)
        with c5:
            pcr_v  = f"{active_pcr:.2f}" if active_pcr else "N/A"
            pp     = "BULL" if (active_pcr and 0.7 < active_pcr < 1.0) else ("BEAR" if (active_pcr and active_pcr > 1.1) else "NEUTRAL")
            pcr_cc = "red" if (active_pcr and active_pcr > 1.1) else "amber"
            st.markdown(tile("Put/Call", pcr_v, None, pcr_cc, "", pp, pct=pct_pcr, pct_invert=True), unsafe_allow_html=True)
        with c6:
            oi_delta = sp_oi - sp_oi_prev
            oi_v     = f"{sp_oi/1e6:.2f}M"
            op       = "BULL" if oi_delta > 0 else "BEAR"
            st.markdown(tile("S&P OI", oi_v, oi_delta/1e3, "blue" if oi_delta > 0 else "red", "K", op), unsafe_allow_html=True)
        with c7:
            if hyg_lqd_last:
                hl_v = f"{hyg_lqd_last:.4f}"
                hl_p = "BULL" if hyg_lqd_last > 0.80 else ("BEAR" if hyg_lqd_last < 0.70 else "NEUTRAL")
                hl_c = "blue" if hyg_lqd_last > 0.80 else ("red" if hyg_lqd_last < 0.70 else "amber")
            else:
                hl_v, hl_p, hl_c = "N/A", "NEUTRAL", "amber"
            st.markdown(tile("HYG/LQD", hl_v, None, hl_c, "", hl_p, pct=pct_hl), unsafe_allow_html=True)
        with c8:
            if tnx_last:
                tnx_v  = f"{tnx_last:.2f}%"
                tnx_p  = "BULL" if tnx_last < 3.5 else ("BEAR" if tnx_last > 4.5 else "NEUTRAL")
                tnx_cc = "blue" if tnx_last < 3.5 else ("red" if tnx_last > 4.5 else "amber")
            else:
                tnx_v, tnx_p, tnx_cc = "N/A", "NEUTRAL", "amber"
            st.markdown(tile("10Y Treasury", tnx_v, None, tnx_cc, "", tnx_p, pct=pct_tnx, pct_invert=True), unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px">Market Regime - SPY/VIX Z-Score</div>', unsafe_allow_html=True)
        z_disp_str    = f"{spy_vix_z_last:+.2f}" if spy_vix_z_last is not None else "N/A"
        norm_disp_str = f"{spy_vix_norm_last:.0f}/100" if spy_vix_norm_last is not None else "N/A"
        pill_regime   = regime_label if regime_label != "TRANSITIONAL" else "NEUTRAL"
        st.markdown(
            f'<div class="regime-panel">'
            f'<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
            f'<div>'
            f'<div style="font-size:0.58rem;letter-spacing:3px;color:#4a6070;text-transform:uppercase">Rolling 63d - Composite contributo 1/10</div>'
            f'<div style="font-family:Syne;font-size:1.1rem;font-weight:700;color:{regime_color};margin-top:2px">'
            f'{z_disp_str} - {regime_label}</div>'
            f'<div style="font-size:0.62rem;color:#8ab0c8;margin-top:3px">{regime_desc}</div>'
            f'</div>'
            f'<div style="margin-left:auto;text-align:right">'
            f'<div style="font-size:0.55rem;color:#4a6070;letter-spacing:2px">GAUGE NORM.</div>'
            f'<div style="font-family:Syne;font-size:1.5rem;font-weight:700;color:{regime_color}">{norm_disp_str}</div>'
            f'<div style="margin-top:4px">{signal_pill(pill_regime)}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True)

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
#  TAB 2 - BREADTH
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Breadth Gauges</div>', unsafe_allow_html=True)
    st.info("Aggiorna settimanalmente i valori nella sidebar - Barchart: $S5TH, $S5FI, $NDTH, $NDFI")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.plotly_chart(gauge(s5th, "S5TH - S&P >200MA", 0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.plotly_chart(gauge(s5fi, "S5FI - S&P >50MA",  0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})
    with c3:
        st.plotly_chart(gauge(ndth, "NDTH - NDX >200MA", 0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})
    with c4:
        st.plotly_chart(gauge(ndfi, "NDFI - NDX >50MA",  0, 100, [30, 70], "%", ".0f"),
                         use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-label">Signal Interpretation</div>', unsafe_allow_html=True)

    def _interp_row(name, val, bull_thresh, bear_thresh, bull_txt, bear_txt, neutral_txt):
        is_bull  = val > bull_thresh
        is_bear  = val < bear_thresh
        zone_col = "#00f5c4" if is_bull else ("#ff4d6d" if is_bear else "#f5a623")
        zone_ico = "BULL"    if is_bull else ("BEAR"    if is_bear else "NEUTRAL")
        txt      = bull_txt  if is_bull else (bear_txt  if is_bear else neutral_txt)
        return (
            f'<tr>'
            f'<td style="padding:8px 12px;font-size:0.7rem;color:#c8d8e8;border-bottom:1px solid #1c2a3a">{name}</td>'
            f'<td style="padding:8px 12px;font-family:Syne;font-size:0.85rem;font-weight:700;color:{zone_col};border-bottom:1px solid #1c2a3a">{val}%</td>'
            f'<td style="padding:8px 12px;font-size:0.65rem;color:{zone_col};border-bottom:1px solid #1c2a3a">{zone_ico}</td>'
            f'<td style="padding:8px 12px;font-size:0.65rem;color:#8ab0c8;border-bottom:1px solid #1c2a3a">{txt}</td>'
            f'</tr>'
        )

    rows_html = (
        _interp_row("S5TH - S&P >200MA", s5th, 70, 30, "Ampia partecipazione - trend solido",   "Breadth debole - mercato fragile",  "Partecipazione mista - attendere conferma") +
        _interp_row("S5FI - S&P >50MA",  s5fi, 60, 30, "Momentum breve termine positivo",        "Pressione di vendita ST diffusa",   "Deterioramento in corso - cautela") +
        _interp_row("NDTH - NDX >200MA", ndth, 70, 30, "Nasdaq in salute - tech leader",          "Nasdaq debole - tech in crisi",     "Tech misto - divergenza possibile") +
        _interp_row("NDFI - NDX >50MA",  ndfi, 60, 30, "Trend breve NDX confermato",              "NDX sotto pressione ST",            "NDX border - monitorare")
    )

    breadth_score = sum([s5th > 60, s5fi > 55, ndth > 60, ndfi > 55])
    b_color = "#00f5c4" if breadth_score >= 3 else ("#ff4d6d" if breadth_score <= 1 else "#f5a623")
    b_label = "BULL"   if breadth_score >= 3 else ("BEAR"   if breadth_score <= 1 else "NEUTRAL")
    b_bg    = "#0a1a14" if b_label == "BULL" else ("#1a0a0a" if b_label == "BEAR" else "#1a150a")

    st.markdown(
        f'<div style="border:1px solid #1c2a3a;border-radius:4px;overflow:hidden">'
        f'<table style="width:100%;border-collapse:collapse;background:#080e14">'
        f'<thead><tr style="background:#0e1420">'
        f'<th style="padding:8px 12px;text-align:left;font-size:0.58rem;color:#4a6070">INDICATORE</th>'
        f'<th style="padding:8px 12px;text-align:left;font-size:0.58rem;color:#4a6070">VALORE</th>'
        f'<th style="padding:8px 12px;text-align:left;font-size:0.58rem;color:#4a6070">ZONA</th>'
        f'<th style="padding:8px 12px;text-align:left;font-size:0.58rem;color:#4a6070">INTERPRETAZIONE</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'<tfoot><tr style="background:#0e1420">'
        f'<td colspan="3" style="padding:8px 12px;font-size:0.62rem;color:#7a9ab0">BREADTH COMPOSITE</td>'
        f'<td style="padding:8px 12px">'
        f'<span style="background:{b_bg};color:{b_color};border:1px solid {b_color};padding:2px 10px;border-radius:2px;font-size:0.6rem;">{b_label} ({breadth_score}/4)</span>'
        f'</td></tr></tfoot></table></div>',
        unsafe_allow_html=True)

    st.markdown('<div class="section-label">NYSE Advance/Decline Line</div>', unsafe_allow_html=True)
    _ad_img = st.file_uploader("Carica screenshot A/D Line", type=["png","jpg","jpeg","webp"],
                                label_visibility="collapsed", key="ad_screenshot")
    if _ad_img is not None:
        st.session_state["ad_img_bytes"] = _ad_img.getvalue()
        st.session_state["ad_img_name"]  = _ad_img.name
        st.session_state["ad_img_date"]  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if "ad_img_bytes" in st.session_state:
        _upload_date = st.session_state.get("ad_img_date", "")
        _upload_name = st.session_state.get("ad_img_name", "")
        st.markdown(
            f'<div style="border:1px solid #1c2a3a;border-radius:4px;overflow:hidden;margin-bottom:8px">'
            f'<div style="background:#0e1420;padding:6px 12px;font-size:0.58rem;color:#7a9ab0;">'
            f'NYSE A/D LINE - Caricato: {_upload_date} - {_upload_name}'
            f'</div></div>',
            unsafe_allow_html=True)
        st.image(st.session_state["ad_img_bytes"], use_container_width=True)
        c_rem, c_src = st.columns([1, 3])
        with c_rem:
            if st.button("Rimuovi A/D", use_container_width=True, key="rm_ad_img"):
                del st.session_state["ad_img_bytes"]
                del st.session_state["ad_img_name"]
                del st.session_state["ad_img_date"]
                st.rerun()
        with c_src:
            st.markdown('<div style="font-size:0.6rem;color:#4a6070;padding-top:8px">Fonte: marketinout.com - stockcharts.com - $NYAD</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="background:#0e1420;border:1px solid #1c2a3a;border-radius:4px;padding:32px;text-align:center">'
            '<div style="font-family:Syne;font-size:0.9rem;color:#c8d8e8;margin-bottom:8px">Carica lo screenshot A/D Line</div>'
            '<div style="font-size:0.62rem;color:#7a9ab0;">Fonti: marketinout.com - stockcharts.com - $NYAD</div>'
            '</div>',
            unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  TAB 3 - SENTIMENT
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Volatility &amp; Options Sentiment</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        vix_val = vix_last if vix_last else 20
        fig_vix = gauge(vix_val, "VIX - CBOE Volatility Index", 10, 50,
                         thresholds=[12, 38], unit="", fmt=".1f", invert=True)
        st.plotly_chart(fig_vix, use_container_width=True, config={"displayModeBar": False})
        if vix_s is not None:
            fig_vh = go.Figure()
            fig_vh.add_trace(go.Scatter(x=vix_s.index, y=vix_s.values, name="VIX",
                                         line=dict(color=RED, width=1.3)))
            if vix_2y is not None and len(vix_2y) > 20:
                p25v = float(np.percentile(vix_2y.dropna(), 25))
                p75v = float(np.percentile(vix_2y.dropna(), 75))
                fig_vh.add_hline(y=p75v, line_dash="dot", line_color=RED, line_width=1,
                                  annotation_text=f"75 pct ({p75v:.1f})", annotation_position="right",
                                  annotation_font=dict(color=RED, size=8))
                fig_vh.add_hline(y=p25v, line_dash="dot", line_color=CYAN, line_width=1,
                                  annotation_text=f"25 pct ({p25v:.1f})", annotation_position="right",
                                  annotation_font=dict(color=CYAN, size=8))
            fig_vh.add_hline(y=25, line_dash="solid", line_color=RED,  line_width=0.5, opacity=0.3)
            fig_vh.add_hline(y=15, line_dash="solid", line_color=CYAN, line_width=0.5, opacity=0.3)
            title_vix = f"VIX History - {pct_vix:.0f} pct 2Y" if pct_vix else "VIX History"
            fig_vh.update_layout(**base_layout(title_vix, 260))
            st.plotly_chart(fig_vh, use_container_width=True, config={"displayModeBar": False})

    with c2:
        skew_val = skew_last if skew_last else 1.0
        fig_sk = gauge(skew_val, "VIX3M/VIX - Term Structure", 0.8, 1.4,
                        thresholds=[15, 55], unit="x", fmt=".3f", invert=False)
        st.plotly_chart(fig_sk, use_container_width=True, config={"displayModeBar": False})
        if skew_ratio is not None:
            fig_skh = go.Figure()
            fig_skh.add_trace(go.Scatter(x=skew_ratio.index, y=skew_ratio.values, name="VIX3M/VIX",
                                          line=dict(color=AMBER, width=1.3)))
            if skew_2y is not None and len(skew_2y) > 20:
                p25s = float(np.percentile(skew_2y.dropna(), 25))
                p75s = float(np.percentile(skew_2y.dropna(), 75))
                fig_skh.add_hline(y=p75s, line_dash="dot", line_color=CYAN, line_width=1,
                                   annotation_text=f"75 pct ({p75s:.3f})", annotation_position="right",
                                   annotation_font=dict(color=CYAN, size=8))
                fig_skh.add_hline(y=p25s, line_dash="dot", line_color=RED, line_width=1,
                                   annotation_text=f"25 pct ({p25s:.3f})", annotation_position="right",
                                   annotation_font=dict(color=RED, size=8))
            fig_skh.add_hline(y=1.0, line_dash="dot", line_color=TEXT_COL, line_width=1,
                               annotation_text="1.0", annotation_position="right",
                               annotation_font=dict(color=TEXT_COL, size=8))
            fig_skh.update_layout(**base_layout("VIX3M/VIX Ratio History - Bande percentile 2Y", 260))
            st.plotly_chart(fig_skh, use_container_width=True, config={"displayModeBar": False})

    _vix_zone  = "low" if vix_last and vix_last < 15 else ("mid" if vix_last and vix_last < 25 else "high")
    _skew_zone = "cont" if skew_last and skew_last >= 1.00 else "back"
    _scenario_map = {
        ("low",  "cont"): ("EUFORIA",      "VIX basso e curva piatta: compiacenza massima.", AMBER),
        ("mid",  "cont"): ("NERVOSISMO",   "VIX in tensione ma struttura normale: paura temporanea.", AMBER),
        ("high", "cont"): ("PAURA/FONDO?", "VIX alto ma contango intatto: spesso contrarian bullish.", AMBER),
        ("low",  "back"): ("ANOMALIA",     "VIX basso con inversione: raro, monitorare.", RED),
        ("mid",  "back"): ("STRESS",       "VIX in tensione e curva invertita: paura in aumento.", RED),
        ("high", "back"): ("CRISI ACUTA",  "VIX alto e backwardation: capitolazione in corso.", RED),
    }
    _key = (_vix_zone, _skew_zone)
    _sc_label, _sc_text, _sc_col = _scenario_map.get(_key, ("N/D", "Dati insufficienti", AMBER))

    st.markdown(
        f'<div style="background:#0a0f18;border:1px solid #1c2a3a;border-radius:4px;padding:14px 18px;margin:4px 0">'
        f'<div style="font-size:0.58rem;letter-spacing:3px;color:#4a6070;margin-bottom:6px;text-transform:uppercase">VIX - VIX3M/VIX - Scenario Combinato</div>'
        f'<div style="font-size:0.72rem;font-weight:700;color:{_sc_col};margin-bottom:4px">{_sc_label}</div>'
        f'<div style="font-size:0.63rem;color:#8ab0c8;line-height:1.7">{_sc_text}</div>'
        f'</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="section-label">Put/Call Ratio SPX</div>', unsafe_allow_html=True)
    _csv_loaded = "pcr_csv_bytes" in st.session_state
    _parse_err  = st.session_state.get("pcr_parse_error", None)
    if not _csv_loaded:
        st.info("Carica il CSV Barchart nella sidebar per il P/C Ratio SPX.")
    elif _parse_err:
        st.error(f"Errore parsing CSV: {_parse_err}")
    elif pcr_barchart_val:
        st.success(f"CSV caricato - PCR SPX = {pcr_barchart_val:.4f} ({st.session_state.get('pcr_csv_name','')})")

    pcr_source = "Barchart CSV" if pcr_barchart_val else ("yfinance ^CPC" if pcr_last else "N/A")
    c3, c4 = st.columns([1, 3])
    with c3:
        fig_pcr_g = gauge(active_pcr if active_pcr else 0.85, f"Put/Call - {pcr_source}",
                           0.4, 1.8, thresholds=[21, 50], unit="x", fmt=".2f", invert=True)
        st.plotly_chart(fig_pcr_g, use_container_width=True, config={"displayModeBar": False})
        if pct_pcr is not None:
            st.markdown(f'<div style="text-align:center;margin-top:-8px">{percentile_badge_html(pct_pcr, invert=True)}</div>', unsafe_allow_html=True)
        if pcr_barchart_val and pcr_barchart_puts and pcr_barchart_call:
            pct_put = pcr_barchart_puts / (pcr_barchart_puts + pcr_barchart_call) * 100
            st.markdown(
                f'<div style="font-size:0.62rem;color:#8ab0c8;border:1px solid #1c2a3a;padding:8px;border-radius:4px;margin-top:8px;line-height:1.9">'
                f'<b style="color:#c8d8e8">SPX Near-Term (&lt;60 DTE)</b><br>'
                f'Put Vol: <b style="color:{RED}">{pcr_barchart_puts:,}</b><br>'
                f'Call Vol: <b style="color:{CYAN}">{pcr_barchart_call:,}</b><br>'
                f'% Put: <b>{pct_put:.1f}%</b>'
                f'</div>',
                unsafe_allow_html=True)

    with c4:
        if pcr_s is not None:
            pcr_ma = pcr_s.rolling(10).mean()
            fig_pcr = go.Figure()
            fig_pcr.add_trace(go.Bar(x=pcr_s.index, y=pcr_s.values, name="Daily P/C",
                                      marker_color="rgba(77,166,255,0.25)"))
            fig_pcr.add_trace(go.Scatter(x=pcr_ma.index, y=pcr_ma.values, name="10d SMA",
                                          line=dict(color=BLUE, width=1.8)))
            if pcr_2y is not None and len(pcr_2y) > 20:
                p75p = float(np.percentile(pcr_2y.dropna(), 75))
                p25p = float(np.percentile(pcr_2y.dropna(), 25))
                fig_pcr.add_hline(y=p75p, line_dash="dot", line_color=RED, line_width=1,
                                   annotation_text=f"75 pct ({p75p:.2f})", annotation_position="right",
                                   annotation_font=dict(color=RED, size=8))
                fig_pcr.add_hline(y=p25p, line_dash="dot", line_color=CYAN, line_width=1,
                                   annotation_text=f"25 pct ({p25p:.2f})", annotation_position="right",
                                   annotation_font=dict(color=CYAN, size=8))
            if pcr_barchart_val:
                fig_pcr.add_hline(y=pcr_barchart_val, line_dash="solid", line_color=AMBER, line_width=1.5,
                                   annotation_text=f"Oggi CSV: {pcr_barchart_val:.2f}", annotation_position="top right",
                                   annotation_font=dict(color=AMBER, size=9))
            fig_pcr.update_layout(**base_layout("Storico P/C (^CPC) - Bande percentile 2Y", 280))
            st.plotly_chart(fig_pcr, use_container_width=True, config={"displayModeBar": False})
        elif pcr_barchart_val:
            color_pcr = "#ff4d6d" if pcr_barchart_val > 1.1 else ("#f5a623" if pcr_barchart_val > 0.7 else "#00f5c4")
            st.markdown(
                f'<div style="background:#0e1420;border:1px solid #1c2a3a;padding:20px;border-radius:4px;text-align:center;margin-top:20px">'
                f'<div style="font-size:0.6rem;letter-spacing:3px;color:#7a9ab0">P/C RATIO OGGI (CSV)</div>'
                f'<div style="font-family:Syne;font-size:3rem;font-weight:700;color:{color_pcr}">{pcr_barchart_val:.3f}</div>'
                f'</div>',
                unsafe_allow_html=True)
        else:
            st.info("Carica il CSV Barchart nella sidebar per il P/C Ratio SPX.")

    st.markdown(
        '<div style="font-size:0.65rem;color:#8ab0c8;border:1px solid #1c2a3a;padding:10px;border-radius:4px;line-height:1.8;margin-top:12px">'
        '<b style="color:#c8d8e8">P/C Guide:</b> &lt;0.7 Complacency - 0.7-1.0 Healthy Fear - &gt;1.1 Bear signal'
        '</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top:28px">HYG / LQD - Credit Spread Proxy</div>', unsafe_allow_html=True)
    c_hyg1, c_hyg2 = st.columns([1, 2])
    with c_hyg1:
        hl_val = hyg_lqd_last if hyg_lqd_last else 0.86
        fig_hl_g = gauge(hl_val, "HYG/LQD - Credit Ratio", 0.60, 1.02,
                          thresholds=[24, 48], unit="x", fmt=".4f", invert=False)
        st.plotly_chart(fig_hl_g, use_container_width=True, config={"displayModeBar": False})
        if pct_hl is not None:
            st.markdown(f'<div style="text-align:center;margin-top:-8px">{percentile_badge_html(pct_hl)}</div>', unsafe_allow_html=True)
        if hyg_lqd_last:
            if hyg_lqd_last > 0.80:
                hl_label, hl_msg, hl_col = "RISK-ON",  "Spread compressi - HY reggono - no stress sistemico", CYAN
            elif hyg_lqd_last > 0.70:
                hl_label, hl_msg, hl_col = "NEUTRALE", "Zona normale - HY stabile - monitorare trend", AMBER
            else:
                hl_label, hl_msg, hl_col = "RISK-OFF", "Spread ampi - stress HY - recessione pricing", RED
            st.markdown(
                f'<div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;font-size:0.63rem;line-height:1.9">'
                f'<b style="color:{hl_col}">{hl_label}</b><br>'
                f'<span style="color:#8ab0c8">{hl_msg}</span>'
                f'</div>',
                unsafe_allow_html=True)

    with c_hyg2:
        _hl_data = hyg_lqd_long if (hyg_lqd_long is not None and len(hyg_lqd_long) > 5) else hyg_lqd
        if _hl_data is not None and len(_hl_data) > 5:
            hl_ma20 = _hl_data.rolling(20).mean()
            fig_hl  = go.Figure()
            fig_hl.add_trace(go.Scatter(x=_hl_data.index, y=_hl_data.values, name="HYG/LQD",
                                         line=dict(color=CYAN, width=1.5),
                                         fill="tozeroy", fillcolor="rgba(0,245,196,0.05)"))
            fig_hl.add_trace(go.Scatter(x=hl_ma20.index, y=hl_ma20.values, name="MA20",
                                         line=dict(color=AMBER, width=1.2, dash="dot")))
            if hyg_lqd_2y is not None and len(hyg_lqd_2y) > 20:
                p25h = float(np.percentile(hyg_lqd_2y.dropna(), 25))
                p75h = float(np.percentile(hyg_lqd_2y.dropna(), 75))
                fig_hl.add_hline(y=p75h, line_dash="dot", line_color=CYAN, line_width=1,
                                  annotation_text=f"75 pct ({p75h:.4f})", annotation_position="right",
                                  annotation_font=dict(color=CYAN, size=8))
                fig_hl.add_hline(y=p25h, line_dash="dot", line_color=RED, line_width=1,
                                  annotation_text=f"25 pct ({p25h:.4f})", annotation_position="right",
                                  annotation_font=dict(color=RED, size=8))
            fig_hl.add_hline(y=0.80, line_dash="solid", line_color=CYAN, line_width=0.5, opacity=0.3)
            fig_hl.add_hline(y=0.70, line_dash="solid", line_color=RED,  line_width=0.5, opacity=0.3)
            fig_hl.update_layout(**base_layout("HYG/LQD - Bande percentile 2Y", 300))
            fig_hl.update_yaxes(range=[0.55, 1.05])
            st.plotly_chart(fig_hl, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
#  TAB 4 - STRUCTURE
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-label">Market Structure Indicators</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-label">S&amp;P 500 Futures Open Interest</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;color:#8ab0c8;margin-bottom:10px;line-height:1.8">'
            'Fonte: <a href="https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.volume.html" target="_blank" style="color:#00f5c4;font-weight:700;text-decoration:none;">CMEGroup.com</a>'
            ' - seleziona MAR26 AT CLOSE</div>', unsafe_allow_html=True)

        oi_chg     = sp_oi - sp_oi_prev
        oi_chg_pct = (oi_chg / sp_oi_prev * 100) if sp_oi_prev else 0

        fig_oi = go.Figure(go.Indicator(
            mode="number+delta",
            value=sp_oi,
            delta=dict(reference=sp_oi_prev, valueformat=",", suffix=" contracts",
                       increasing=dict(color=CYAN), decreasing=dict(color=RED)),
            number=dict(valueformat=",", font=dict(family="Syne", size=32, color=CYAN if oi_chg > 0 else RED)),
            title=dict(text="E-mini S&P 500 OI (input manuale)", font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        ))
        fig_oi.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                               height=180, margin=dict(l=20, r=20, t=40, b=10),
                               font=dict(family="Space Mono", color=TEXT_COL))
        st.plotly_chart(fig_oi, use_container_width=True, config={"displayModeBar": False})

        oi_pill = "BULL" if oi_chg > 0 else "BEAR"
        st.markdown(
            f'<div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;font-size:0.7rem;line-height:2">'
            f'WoW Change: <b style="color:{"#00f5c4" if oi_chg>0 else "#ff4d6d"}">{oi_chg:+,} contracts ({oi_chg_pct:+.1f}%)</b><br>'
            f'Signal: {signal_pill(oi_pill)}<br>'
            f'<span style="color:#8ab0c8">Rising OI + rising price = strong trend - Rising OI + falling price = distribution</span>'
            f'</div>',
            unsafe_allow_html=True)

        # COT parsed data display
        if st.session_state.get("cot_parse_ok"):
            _cd = st.session_state["cot_data"]
            st.markdown('<div class="section-label" style="margin-top:16px">COT - E-mini S&P 500 (13874A)</div>', unsafe_allow_html=True)

            net_am     = _cd["net_am"]
            net_lf     = _cd["net_lf"]
            divergence = net_am - net_lf
            cot_signal = "BULL" if (net_am > 0 and net_lf < 0) else ("BEAR" if (net_am < 0 and net_lf > 0) else "NEUTRAL")

            ca, cb, cc = st.columns(3)
            with ca:
                st.markdown(tile(
                    "NET ASSET MANAGER",
                    f"{net_am:+,}",
                    color_class="blue" if net_am > 0 else "red"
                ), unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-size:0.6rem;color:#7a9ab0;margin-top:4px">Long: {_cd["am_long"]:,} - Short: {_cd["am_short"]:,}</div>',
                    unsafe_allow_html=True)
            with cb:
                st.markdown(tile(
                    "NET LEVERAGED FUNDS",
                    f"{net_lf:+,}",
                    color_class="red" if net_lf < 0 else "blue"
                ), unsafe_allow_html=True)
                st.markdown(
                    f'<div style="font-size:0.6rem;color:#7a9ab0;margin-top:4px">Long: {_cd["lf_long"]:,} - Short: {_cd["lf_short"]:,}</div>',
                    unsafe_allow_html=True)
            with cc:
                st.markdown(tile(
                    "DIVERGENZA AM vs LF",
                    f"{divergence:+,}",
                    color_class="blue" if divergence > 0 else "red",
                    pill_label=cot_signal
                ), unsafe_allow_html=True)

            fig_cot = go.Figure()
            fig_cot.add_trace(go.Bar(
                x=["Asset Manager", "Leveraged Funds"],
                y=[net_am, net_lf],
                marker_color=[CYAN if net_am > 0 else RED, CYAN if net_lf > 0 else RED],
                text=[f"{net_am:+,}", f"{net_lf:+,}"],
                textposition="outside",
                textfont=dict(size=11, color=TEXT_COL)
            ))
            fig_cot.add_hline(y=0, line_color=GRID_COL, line_width=1)
            fig_cot.update_layout(**base_layout("COT Net Position - E-mini S&P 500", 280))
            st.plotly_chart(fig_cot, use_container_width=True, config={"displayModeBar": False})

            st.markdown(
                '<div style="font-size:0.63rem;color:#8ab0c8;border:1px solid #1c2a3a;'
                'padding:10px 14px;border-radius:4px;line-height:1.9;margin-top:8px">'
                '<b style="color:#c8d8e8">Interpretazione:</b><br>'
                'AM Long + LF Short = divergenza classica: <b style="color:#00f5c4">Smart money compra, speculatori vendono</b><br>'
                'AM Short + LF Long = inversione: <b style="color:#ff4d6d">Istituzionali difensivi, retail esuberante</b><br>'
                '<span style="color:#4a6070">Dati al: venerdi precedente - aggiorna ogni settimana - codice CFTC: 13874A</span>'
                '</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="background:#0e1420;border:1px solid #1c2a3a;border-radius:4px;'
                'padding:20px;text-align:center;margin-top:12px">'
                '<div style="font-size:0.8rem;color:#4a6070">Incolla il report CFTC nella sidebar e premi Parsa dati CFTC</div>'
                '</div>',
                unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-label">Margin Debt (FINRA Mensile)</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;color:#8ab0c8;margin-bottom:10px;line-height:1.8">'
            'Fonte: <a href="https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics" target="_blank" style="color:#00f5c4;font-weight:700;text-decoration:none;">FINRA.org</a>'
            ' - aggiorna mensilmente</div>', unsafe_allow_html=True)

        md_chg     = margin_debt - margin_debt_prev
        md_chg_pct = (md_chg / margin_debt_prev * 100) if margin_debt_prev else 0

        fig_md = go.Figure(go.Indicator(
            mode="number+delta",
            value=margin_debt,
            delta=dict(reference=margin_debt_prev, valueformat=",.0f", suffix="M",
                       increasing=dict(color=CYAN), decreasing=dict(color=RED)),
            number=dict(valueformat=",.0f", suffix="M",
                        font=dict(family="Syne", size=32, color=CYAN if md_chg > 0 else RED)),
            title=dict(text="FINRA Margin Debt - USD ($M)", font=dict(family="Space Mono", size=10, color=TEXT_COL)),
        ))
        fig_md.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                               height=180, margin=dict(l=20, r=20, t=40, b=10),
                               font=dict(family="Space Mono", color=TEXT_COL))
        st.plotly_chart(fig_md, use_container_width=True, config={"displayModeBar": False})

        md_pill = "BULL" if md_chg > 0 else "NEUTRAL"
        st.markdown(
            f'<div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;font-size:0.7rem;line-height:2">'
            f'MoM Change: <b style="color:{"#00f5c4" if md_chg>0 else "#ff4d6d"}">{md_chg:+,}M ({md_chg_pct:+.1f}%)</b><br>'
            f'Signal: {signal_pill(md_pill)}<br>'
            f'<span style="color:#8ab0c8">Rising margin - leveraged risk-on - Rapid collapse - forced selling risk</span>'
            f'</div>',
            unsafe_allow_html=True)

    st.markdown('<div class="section-label">Tassi &amp; Curva - Contesto Macro</div>', unsafe_allow_html=True)
    c_r1, c_r2, c_r3 = st.columns([1, 1, 2])

    with c_r1:
        tnx_val = round(tnx_last, 2) if tnx_last else 4.3
        fig_tnx = gauge(tnx_val, "10Y Treasury Yield", 1.0, 6.0,
                        thresholds=[42, 58], unit="%", fmt=".2f", invert=True)
        st.plotly_chart(fig_tnx, use_container_width=True, config={"displayModeBar": False})
        if pct_tnx is not None:
            st.markdown(f'<div style="text-align:center;margin-top:-8px">{percentile_badge_html(pct_tnx, invert=True)}</div>', unsafe_allow_html=True)
        if tnx_last:
            if tnx_last < 3.5:   _tnx_l, _tnx_c = "ACCOMODANTE - valutazioni supportate", CYAN
            elif tnx_last < 4.5: _tnx_l, _tnx_c = "NEUTRALE - pressione moderata", AMBER
            else:                 _tnx_l, _tnx_c = "RESTRITTIVO - multipli sotto pressione", RED
            st.markdown(
                f'<div style="background:#0e1420;border:1px solid #1c2a3a;padding:10px;border-radius:4px;font-size:0.62rem;line-height:1.8">'
                f'<b style="color:{_tnx_c}">{_tnx_l}</b><br>'
                f'<span style="color:#4a6070">Soglie: &lt;3.5% bull - 3.5-4.5% neutrale - &gt;4.5% bear</span>'
                f'</div>',
                unsafe_allow_html=True)

    with c_r2:
        _sp_val = round(spread_2y10y, 2) if spread_2y10y is not None else 0.0
        fig_sp = gauge(_sp_val, "Spread 10Y-3M - Curva", -2.0, 3.0,
                       thresholds=[40, 60], unit="%", fmt="+.2f", invert=False)
        st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar": False})
        if spread_2y10y is not None:
            if spread_2y10y > 0.5:   _sp_l, _sp_c = "NORMALE - nessun segnale recessivo", CYAN
            elif spread_2y10y > 0:   _sp_l, _sp_c = "PIATTA - monitorare", AMBER
            else:                     _sp_l, _sp_c = "INVERTITA - precede recessione (6-18m)", RED
            st.markdown(
                f'<div style="background:#0e1420;border:1px solid #1c2a3a;padding:10px;border-radius:4px;font-size:0.62rem;line-height:1.8">'
                f'<b style="color:{_sp_c}">{_sp_l}</b><br>'
                f'<span style="color:#4a6070">Indicatore lento - non nel composite - segnala contesto recessivo</span>'
                f'</div>',
                unsafe_allow_html=True)

    with c_r3:
        if tnx_s is not None:
            fig_rates = go.Figure()
            fig_rates.add_trace(go.Scatter(x=tnx_s.index, y=tnx_s.values, name="10Y Yield",
                                            line=dict(color=AMBER, width=1.5)))
            if irx_s is not None:
                fig_rates.add_trace(go.Scatter(x=irx_s.index, y=irx_s.values, name="3M Yield",
                                                line=dict(color=BLUE, width=1.2, dash="dot")))
            if tnx_2y is not None and len(tnx_2y) > 20:
                p25t = float(np.percentile(tnx_2y.dropna(), 25))
                p75t = float(np.percentile(tnx_2y.dropna(), 75))
                fig_rates.add_hrect(y0=p25t, y1=p75t, fillcolor="rgba(77,166,255,0.04)", line_width=0,
                                     annotation_text="IQR 2Y", annotation_position="top right",
                                     annotation_font=dict(color="#4a6070", size=8))
            fig_rates.add_hline(y=4.5, line_dash="dot", line_color=RED,  line_width=1,
                                 annotation_text="4.5%", annotation_position="right",
                                 annotation_font=dict(color=RED, size=8))
            fig_rates.add_hline(y=3.5, line_dash="dot", line_color=CYAN, line_width=1,
                                 annotation_text="3.5%", annotation_position="right",
                                 annotation_font=dict(color=CYAN, size=8))
            fig_rates.update_layout(**base_layout("10Y e 3M Treasury Yield - IQR percentile 2Y", 300))
            st.plotly_chart(fig_rates, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-label">SPY vs VIX Overlay</div>', unsafe_allow_html=True)
    if spy_s is not None and vix_s is not None:
        fig_ov = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                                subplot_titles=("SPY Price", "VIX"), row_heights=[0.65, 0.35])
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
                               xaxis2=dict(gridcolor=GRID_COL), yaxis2=dict(gridcolor=GRID_COL))
        st.plotly_chart(fig_ov, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
#  TAB 5 - REGIME
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-label">SPY/VIX Regime Indicator - Z-Score Rolling 63 Giorni</div>', unsafe_allow_html=True)

    bull_bg = '#0a1a14' if (spy_vix_z_last is not None and spy_vix_z_last > 1.0)  else 'transparent'
    mid_bg  = '#1a150a' if (spy_vix_z_last is not None and -1.0 <= spy_vix_z_last <= 1.0) else 'transparent'
    bear_bg = '#1a0a0a' if (spy_vix_z_last is not None and spy_vix_z_last < -1.0) else 'transparent'

    st.markdown(
        f'<div style="background:#080e14;border:1px solid #1c2a3a;border-radius:4px;padding:16px 20px;margin-bottom:16px">'
        f'<div style="display:flex;gap:32px;flex-wrap:wrap">'
        f'<div style="flex:2;min-width:240px">'
        f'<div style="font-family:Syne;font-size:0.85rem;font-weight:700;color:{regime_color};margin-bottom:6px">'
        f'Regime Corrente: {regime_label}</div>'
        f'<div style="font-size:0.63rem;color:#8ab0c8;line-height:1.8">{regime_desc}</div>'
        f'<div style="margin-top:10px;font-size:0.6rem;color:#4a6070;line-height:1.7">'
        f'<b style="color:#7a9ab0">Come funziona:</b><br>'
        f'1. Raw = SPY / VIX (price-to-fear ratio)<br>'
        f'2. Z-score = (raw - media 63d) / std 63d<br>'
        f'3. Normalizzato 0-100: z=-3 a 0, z=0 a 50, z=+3 a 100<br>'
        f'4. Ortogonale a breadth, PCR, VIX standalone'
        f'</div></div>'
        f'<div style="flex:1;min-width:180px">'
        f'<table style="font-size:0.6rem;border-collapse:collapse;width:100%">'
        f'<tr style="color:#4a6070"><td style="padding:3px 8px">Z-Score</td><td style="padding:3px 8px">Regime</td></tr>'
        f'<tr style="background:{bull_bg}"><td style="padding:3px 8px;color:#7a9ab0">&gt; +1.0</td>'
        f'<td style="padding:3px 8px;color:#00f5c4">RISK-ON - 1 pt</td></tr>'
        f'<tr style="background:{mid_bg}"><td style="padding:3px 8px;color:#7a9ab0">-1 a +1</td>'
        f'<td style="padding:3px 8px;color:#f5a623">TRANSITIONAL - 0.5 pt</td></tr>'
        f'<tr style="background:{bear_bg}"><td style="padding:3px 8px;color:#7a9ab0">&lt; -1.0</td>'
        f'<td style="padding:3px 8px;color:#ff4d6d">RISK-OFF - 0 pt</td></tr>'
        f'</table>'
        f'<div style="font-size:0.55rem;color:#4a6070;margin-top:8px;line-height:1.6">'
        f'Window 63d - 1 trimestre<br>Cattura mean-reversion tra cicli'
        f'</div></div></div></div>',
        unsafe_allow_html=True)

    col_g2, col_ch = st.columns([1, 3])

    with col_g2:
        norm_val = spy_vix_norm_last if spy_vix_norm_last is not None else 50
        fig_reg = gauge(norm_val, "SPY/VIX Z-Score Normalized", 0, 100,
                         thresholds=[33, 67], unit="", fmt=".0f", invert=False)
        st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": False})

        pill_regime2 = regime_label if regime_label != "TRANSITIONAL" else "NEUTRAL"
        z_str = f"{spy_vix_z_last:+.2f}" if spy_vix_z_last is not None else "N/A"
        st.markdown(
            f'<div style="background:#0e1420;border:1px solid #1c2a3a;padding:12px;border-radius:4px;'
            f'font-size:0.65rem;line-height:2;text-align:center">'
            f'<div style="color:#4a6070;font-size:0.55rem;letter-spacing:2px">Z-SCORE CORRENTE</div>'
            f'<div style="font-family:Syne;font-size:2rem;font-weight:700;color:{regime_color}">{z_str}</div>'
            f'<div style="margin-top:4px">{signal_pill(pill_regime2)}</div>'
            f'<div style="font-size:0.55rem;color:#4a6070;margin-top:8px">Score: {_sc_spy_vix:.1f}/1.0</div>'
            f'</div>',
            unsafe_allow_html=True)

    with col_ch:
        if spy_vix_z_disp is not None and len(spy_vix_z_disp) > 5:
            colors_z = [CYAN if v > 1.0 else (RED if v < -1.0 else AMBER) for v in spy_vix_z_disp.values]
            fig_z = go.Figure()
            fig_z.add_trace(go.Bar(x=spy_vix_z_disp.index, y=spy_vix_z_disp.values,
                                    name="Z-Score", marker_color=colors_z, opacity=0.8))
            z_sma = spy_vix_z_disp.rolling(10).mean()
            fig_z.add_trace(go.Scatter(x=z_sma.index, y=z_sma.values, name="10d SMA",
                                        line=dict(color=TEXT_COL, width=1.5)))
            fig_z.add_hline(y=1.0,  line_dash="dot", line_color=CYAN, line_width=1.2,
                             annotation_text="+1 Risk-On", annotation_position="right",
                             annotation_font=dict(color=CYAN, size=9))
            fig_z.add_hline(y=-1.0, line_dash="dot", line_color=RED,  line_width=1.2,
                             annotation_text="-1 Risk-Off", annotation_position="right",
                             annotation_font=dict(color=RED, size=9))
            fig_z.add_hline(y=0, line_dash="solid", line_color=GRID_COL, line_width=1)
            fig_z.update_layout(**base_layout("SPY/VIX Z-Score - Cyan=Risk-On - Ambra=Transitional - Rosso=Risk-Off", 320))
            st.plotly_chart(fig_z, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-label">SPY/VIX Raw Ratio - Bande Percentile 2Y</div>', unsafe_allow_html=True)
    if spy_vix_raw_disp is not None and len(spy_vix_raw_disp) > 5:
        raw_ma20 = spy_vix_raw_disp.rolling(20).mean()
        p25r = float(np.percentile(spy_vix_raw_disp.dropna(), 25))
        p50r = float(np.percentile(spy_vix_raw_disp.dropna(), 50))
        p75r = float(np.percentile(spy_vix_raw_disp.dropna(), 75))
        pct_raw = percentile_of(spy_vix_raw_disp, last(spy_vix_raw_disp))
        fig_raw = go.Figure()
        fig_raw.add_hrect(y0=p25r, y1=p75r, fillcolor="rgba(77,166,255,0.05)", line_width=0,
                           annotation_text="IQR 2Y", annotation_position="top right",
                           annotation_font=dict(color="#4a6070", size=8))
        fig_raw.add_trace(go.Scatter(x=spy_vix_raw_disp.index, y=spy_vix_raw_disp.values,
                                      name="SPY/VIX", line=dict(color=BLUE, width=1.5),
                                      fill="tozeroy", fillcolor="rgba(77,166,255,0.04)"))
        fig_raw.add_trace(go.Scatter(x=raw_ma20.index, y=raw_ma20.values, name="MA20",
                                      line=dict(color=AMBER, width=1.2, dash="dot")))
        fig_raw.add_hline(y=p75r, line_dash="dot", line_color=CYAN, line_width=1,
                           annotation_text=f"75 pct ({p75r:.1f})", annotation_position="right",
                           annotation_font=dict(color=CYAN, size=8))
        fig_raw.add_hline(y=p50r, line_dash="dot", line_color=AMBER, line_width=1,
                           annotation_text=f"Mediana ({p50r:.1f})", annotation_position="right",
                           annotation_font=dict(color=AMBER, size=8))
        fig_raw.add_hline(y=p25r, line_dash="dot", line_color=RED, line_width=1,
                           annotation_text=f"25 pct ({p25r:.1f})", annotation_position="right",
                           annotation_font=dict(color=RED, size=8))
        title_raw = f"SPY/VIX Raw - Percentile oggi: {pct_raw:.0f}" if pct_raw else "SPY/VIX Raw Ratio"
        fig_raw.update_layout(**base_layout(title_raw, 300))
        st.plotly_chart(fig_raw, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-label">Regime Timeline - Classificazione Storica</div>', unsafe_allow_html=True)
    if spy_vix_z_disp is not None and len(spy_vix_z_disp) > 5:
        regime_colors_ts = [
            CYAN  if v > 1.0  else
            RED   if v < -1.0 else
            AMBER
            for v in spy_vix_z_disp.values
        ]
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=spy_vix_z_disp.index,
            y=[1] * len(spy_vix_z_disp),
            mode="markers",
            marker=dict(color=regime_colors_ts, size=6, symbol="square"),
            name="Regime",
            hovertext=[
                f"{'RISK-ON' if v>1 else ('RISK-OFF' if v<-1 else 'TRANSITIONAL')} (z={v:.2f})"
                for v in spy_vix_z_disp.values
            ],
            hoverinfo="x+text"
        ))
        fig_timeline.update_layout(
            paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            height=80, margin=dict(l=48, r=16, t=8, b=24),
            font=dict(family="Space Mono", color=TEXT_COL, size=9),
            xaxis=dict(gridcolor=GRID_COL, showgrid=True, zeroline=False, tickfont=dict(size=9)),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            showlegend=False, hovermode="x"
        )
        st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            '<div style="font-size:0.58rem;color:#4a6070;text-align:center;margin-top:-8px">'
            '<span style="color:#00f5c4">Risk-On</span> &nbsp;|&nbsp;'
            '<span style="color:#f5a623">Transitional</span> &nbsp;|&nbsp;'
            '<span style="color:#ff4d6d">Risk-Off</span>'
            '</div>',
            unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown(
    '<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#4a6a80;text-align:center;line-height:2">'
    'EQUITY PULSE - For informational purposes only - Not financial advice<br>'
    'Automatico: SPY, QQQ, VIX, VIX3M, HYG, LQD, TNX, IRX (yfinance - finestra 2Y per percentili)<br>'
    'Manuale: Breadth (sett.), OI, Margin Debt - P/C: CSV Barchart - SPY/VIX Regime: z-score rolling 63d'
    '</div>',
    unsafe_allow_html=True)
