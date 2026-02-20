# ⚡ Equity Pulse — Market Timing Dashboard

Multi-indicator market timing dashboard for **S&P 500 & Nasdaq** with dark theme gauges.

## 📊 Indicators

| Indicator | Source | Method |
|-----------|--------|--------|
| SPY / QQQ prices | yfinance | Auto |
| VIX | yfinance `^VIX` | Auto |
| VIX3M/VIX ratio (SKEW proxy) | yfinance `^VIX3M` | Auto |
| Put/Call Ratio | yfinance `^CPC` | Auto |
| NYSE Advance/Decline Line | yfinance `^NYADV/^NYDEC` | Auto |
| S5TH / S5FI (S&P breadth) | StockCharts | **Manual sidebar** |
| NDTH / NDFI (Nasdaq breadth) | StockCharts | **Manual sidebar** |
| S&P500 Futures Open Interest | CME Group | **Manual sidebar** |
| Margin Debt | FINRA | **Manual sidebar** |

## 🚀 Deploy on Streamlit Cloud

1. Fork / push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo
4. Set **Main file path**: `app.py`
5. Click **Deploy** — done!

No API keys required. All automated data is free via `yfinance`.

## 🔄 Updating Manual Data

- **Breadth (S5TH/S5FI/NDTH/NDFI):** Weekly via [StockCharts.com](https://stockcharts.com) → enter as `$S5TH` etc.
- **Futures OI:** Weekly from [CME Group](https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.html)
- **Margin Debt:** Monthly from [FINRA Margin Statistics](https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics)

## 📁 Project Structure

```
equity_dashboard/
├── app.py           # Main Streamlit app
├── requirements.txt # Python dependencies
└── README.md
```

## 🧠 Composite Signal Logic

The **Market Pulse** gauge scores 7 factors (0–7):
- Breadth: S5TH>60% (+1), NDTH>60% (+1), S5FI/NDFI>55% (+1)
- VIX: <15 (+1), <20 (+0.5)
- Put/Call: 0.7–1.0 (+1) — healthy fear zone
- VIX3M/VIX: <1.05 (+1) — calm term structure
- OI: rising WoW (+1) — institutional conviction
- Margin: rising MoM (+1) — risk-on leverage

Score >60% → 🟢 BULL | 38–60% → 🟡 NEUTRAL | <38% → 🔴 BEAR

## ⚠️ Disclaimer

For informational purposes only. Not financial advice.
