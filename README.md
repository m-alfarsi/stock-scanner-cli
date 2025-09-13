# 📊 strict-signal-scanner

A fast, multi-ticker CLI tool that scans stocks using strict SMA, RSI, and MACD logic.  
Outputs BUY, SELL, or HOLD signals with color-coded feedback and clear reasoning.  
Built for disciplined traders who want clean, actionable insights without noise.

---

## 🔧 Features

- ✅ Scans multiple tickers in one run  
- 📊 Uses SMA5/10, RSI(7), MACD(6,13,4) for signal logic  
- 🖥️ CLI-based, lightweight, and fast  
- 🎨 Color-coded output with signal breakdowns  
- 📁 Fallback support for CSV data if API fails  
- 🧠 Designed for weekend prep, batch scanning, and strict workflows

---

## 🚀 How to Use

### 1. Install dependencies

Make sure you have Python 3.8+ and install required packages:

```bash
pip install yfinance pandas termcolor
