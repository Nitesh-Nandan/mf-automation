# 📈 Stock Dip Analyzer

Blue-chip stock dip-buying analyzer for Indian market.

## 🚀 Quick Start

```bash
cd src/stocks
uv run python stock_dip_analyzer.py
```

## 📂 Files

| File | Purpose |
|------|---------|
| `stock_dip_analyzer.py` | Main analyzer - run this |
| `stock_data_fetcher.py` | Fetches price & fundamentals from yfinance |
| `fundamental_analyzer.py` | Quality scoring & checks |
| `config.py` | Configuration & thresholds |
| `stocks_watchlist.csv` | Your watchlist |

## ⚙️ Configuration

Edit `config.py` to adjust:
- Fundamental defaults (market averages)
- P/E scoring thresholds
- Quality check criteria
- Dip buying sensitivity

## 📊 How It Works

8-factor scoring system:
1. **Dip Depth** (0-15 pts) - How far from peak
2. **Historical Context** (0-20 pts) - vs past dips
3. **Mean Reversion** (0-15 pts) - Below average
4. **Volatility** (0-15 pts) - Risk/reward
5. **Recovery Speed** (0-15 pts) - Resilience
6. **Market Cap** (0-5 pts) - Size bonus
7. **Fundamentals** (0-20 pts) - Quality metrics
8. **Technicals** (0-10 pts) - RSI, volume, support

**Total:** 0-125 points → normalized to 100

## 📖 Documentation

See `docs/` folder for:
- Refactoring summary
- Scoring enhancements
- Full analyzer guide

## 🎯 Modes

- **Conservative** (65+) - High quality only
- **Moderate** (55+) - Balanced
- **Aggressive** (45+) - More opportunities

Change mode in script or pass as argument.
