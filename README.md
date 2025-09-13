# stock-scanner-cli
A fast, multi-ticker CLI tool that scans stocks using strict SMA, RSI, and MACD logic. Outputs BUY, SELL, or HOLD signals with color-coded feedback and clear reasoning. Built for disciplined traders who want clean, actionable insights without noise.

🚀 How to Use
- Install dependencies
Make sure you have Python 3.8+ and install required packages:
pip install yfinance pandas termcolor
- Run the scanner
Use the command line to scan multiple tickers:
python resilient_multi_ticker_signal.py AAPL MSFT NVDA
- Read the output
The script will print a color-coded summary:
- 🟢 BUY — All conditions met (SMA5 > SMA10, RSI < 70, MACD > Signal)
- 🔴 SELL — Reverse conditions met
- 🟡 HOLD — At least one condition failed (with reason shown)
- Fallback to CSV ()
If live data fails, place a file named TICKER.csv in the same folder.
It should include columns like Date, Open, High, Low, Close, Volume.

Note: You need to download your own csv.

