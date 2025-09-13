# 📊 stock-scanner-cli

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

### 1. Clone the repo

```bash
git clone https://github.com/m-alfarsi/stock-scanner-cli.git
cd stock-scanner-cli
```

### 2. Install dependencies
Make sure you have Python 3.8+ and install required packages:

```bash
pip install yfinance pandas termcolor
```

### 3. Run the scanner
Use the command line to scan multiple tickers:
```bash
python scanner-cli.py <STOCK SYMBOL>
```

### 4. Read the output
The script will print a color-coded summary:
- 🟢 BUY — All conditions met
SMA5 > SMA10, RSI < 70, MACD > Signal
- 🔴 SELL — Reverse conditions met
SMA5 < SMA10, RSI > 30, MACD < Signal
- 🟡 HOLD — At least one condition failed (reason shown)


If its not running, find the location of the scanner-cli.py file and copy its address/file location:
```bash
python <file location> <STOCK SYMBOL>
```





