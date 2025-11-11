# 📊 Investment Automation Suite

Intelligent dip-buying algorithms for Indian Mutual Funds and Stocks.

## 🎯 Two Independent Modules

### 1. Mutual Fund Analyzer (`src/mf/`)
Analyzes mutual funds for dip-buying opportunities using historical NAV data.

**Quick Start:**
```bash
cd src/mf
uv run python dip_analyzer.py
```

[📖 MF Documentation](src/mf/README.md)

---

### 2. Stock Analyzer (`src/stocks/`)
Analyzes blue-chip stocks with comprehensive fundamental + technical scoring.

**Quick Start:**
```bash
cd src/stocks
uv run python stock_dip_analyzer.py
```

[📖 Stock Documentation](src/stocks/README.md)

---

## 🚀 Installation

```bash
# Clone repository
git clone <repo-url>
cd mf-automation

# Install dependencies
uv sync

# Or with pip
pip install -r requirements.txt
```

## 📂 Project Structure

```
mf-automation/
├── src/
│   ├── mf/                    # Mutual Fund Module
│   │   ├── dip_analyzer.py    # Main MF analyzer
│   │   ├── mf_funds.csv       # Your fund portfolio
│   │   ├── docs/              # MF documentation
│   │   └── README.md
│   │
│   └── stocks/                # Stock Module
│       ├── stock_dip_analyzer.py  # Main stock analyzer
│       ├── config.py          # Configurable thresholds
│       ├── stocks_watchlist.csv   # Your watchlist
│       ├── docs/              # Stock documentation
│       └── README.md
│
├── README.md                  # This file
├── QUICK_START.md            # Quick start guide
└── pyproject.toml            # Dependencies
```

## 🎯 Philosophy

### SIP + Opportunistic Dip Buying

**Regular Investment (SIP):**
- Disciplined monthly investments
- Rupee cost averaging
- Long-term wealth building

**Opportunistic Dip Buying:**
- Deploy extra capital during significant dips
- Algorithm identifies quality opportunities
- Risk-managed position sizing

**Not:**
- Market timing
- Trading
- Replacement for SIP

## ⚙️ Configuration

Both modules are highly configurable:

**MF:** Edit algorithm parameters in `src/mf/dip_analyzer.py`  
**Stocks:** Edit thresholds in `src/stocks/config.py`

## 📊 Key Features

### Mutual Fund Module
- ✅ Historical NAV analysis
- ✅ 6-factor scoring system
- ✅ Volatility & recovery analysis
- ✅ Conservative/Moderate/Aggressive modes
- ✅ Multiple timeframe analysis

### Stock Module
- ✅ 8-factor comprehensive scoring
- ✅ Fundamental quality checks (6 metrics)
- ✅ Technical indicators (RSI, volume, support)
- ✅ Market-adjusted P/E thresholds
- ✅ Intelligent defaults for missing data
- ✅ Configurable risk profiles

## 🎓 Learning Resources

- **MF Algorithm:** `src/mf/docs/ALGORITHM_DOCUMENTATION.md`
- **MF Backtest:** `src/mf/docs/BACKTEST_RESULTS.md`
- **Stock Scoring:** `src/stocks/docs/FUNDAMENTAL_SCORING_ENHANCEMENTS.md`
- **Code Refactoring:** `src/stocks/docs/REFACTORING_SUMMARY.md`

## ⚠️ Disclaimer

This tool is for educational and research purposes. It provides analysis and suggestions but:
- Not financial advice
- Always do your own research
- Verify fundamentals before investing
- Past performance ≠ future results
- Consider your risk tolerance

## 🤝 Contributing

Feel free to:
- Add more funds/stocks to watchlists
- Adjust thresholds for your risk profile
- Improve algorithms
- Share feedback

## 📝 License

For personal use.

---

## 🚀 Quick Commands

```bash
# Analyze Mutual Funds
cd src/mf && uv run python dip_analyzer.py

# Analyze Stocks
cd src/stocks && uv run python stock_dip_analyzer.py

# Validate stock configuration
cd src/stocks && uv run python config.py

# Update dependencies
uv sync
```

---

**Built for disciplined investors who want to enhance SIP with intelligent opportunistic buying.**

*Stay invested. Stay disciplined. Buy quality on dips.* 📈
