# 📊 Stock Technical Analysis

Algorithmic dip-buying analyzer for fundamentally strong Indian stocks using 6-factor scoring system.

## 🎯 Quick Start

```bash
# Run live analysis
python src/stocks/run_analysis.py

# Backtest strategy over historical data
python src/stocks/backtest/run_backtest.py --csv backtest/sample_stocks.csv
```

## 📁 Project Structure

```
src/stocks/
├── TechnicalAnalysis.py    # Main analyzer class
├── TechnicalScore.py        # Scoring configuration & logic
├── models.py                # Type definitions
├── historical_data.py       # Upstox API integration
├── run_analysis.py          # Standalone runner script
├── analyze_and_update_sheet.py  # Google Sheets integration
├── backtest/                # 🆕 Backtesting framework
│   ├── backtest_stock_strategy.py  # Backtest engine
│   ├── run_backtest.py      # CLI interface
│   ├── sample_stocks.csv    # Sample stocks for testing
│   ├── README.md            # Comprehensive documentation
│   └── QUICK_START.md       # 5-minute quick start
└── docs/
    └── TECHNICAL_ALGORITHM_DOCUMENTATION.md  # Algorithm details
```

## 🔧 Core Components

### **TechnicalAnalysis Class**
Main orchestrator that fetches data and coordinates scoring.

```python
from stocks import TechnicalAnalysis

analyzer = TechnicalAnalysis(
    stock_name="Asian Paints",
    stock_symbol="ASIANPAINT",
    instrument_key="NSE_EQ|INE021A01026"
)

result = analyzer.analyze()
```

### **6-Factor Scoring System** (Total: 100 points)

1. **Dip Depth** (0-20 pts) - How far from 90-day peak?
2. **Historical Context** (0-25 pts) - Is this dip rare for THIS stock?
3. **Mean Reversion** (0-15 pts) - Distance from 100 DMA
4. **Volatility** (0-10 pts) - Stock-specific risk (relative scoring)
5. **Recovery Speed** (0-20 pts) - How fast does it bounce back?
6. **Technicals** (0-10 pts) - RSI + Volume + Support levels

### **Recommendations**

| Score | Action | Position Multiplier |
|-------|--------|-------------------|
| 85-100 | **STRONG BUY** | 1.0x standard position |
| 75-84 | **BUY** | 0.75x |
| 60-74 | **ACCUMULATE** | 0.50x |
| 50-59 | **NIBBLE** | 0.25x |
| < 50 | **WAIT** | 0x |

## 🚀 Usage Examples

### **Single Stock Analysis**

```python
from stocks import TechnicalAnalysis

analyzer = TechnicalAnalysis(
    stock_name="HDFC Bank",
    stock_symbol="HDFCBANK",
    instrument_key="NSE_EQ|INE040A01034"
)

result = analyzer.analyze()

if result:
    print(f"Score: {result['final_score']}/100")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Current: ₹{result['current_price']} | RSI: {result['rsi']}")
```

### **Batch Analysis**

```python
import csv
from stocks import TechnicalAnalysis

# Load watchlist
with open('src/stocks/stocks_watchlist.csv') as f:
    stocks = list(csv.DictReader(f))

# Analyze each
for stock in stocks:
    analyzer = TechnicalAnalysis(
        stock_name=stock['name'],
        stock_symbol=stock['symbol'],
        instrument_key=stock.get('instrument_key', '')  # Add this column
    )
    result = analyzer.analyze()
    if result and result['final_score'] >= 60:
        print(f"{stock['symbol']}: {result['final_score']:.0f} - {result['recommendation']}")
```

## ⚙️ Configuration

All scoring thresholds are in `TechnicalScore.py`:

```python
# Adjust dip depth thresholds
DIP_DEPTH_THRESHOLDS = {
    20: 20,  # >=20% dip → 20 points
    15: 18,  # >=15% dip → 18 points
    # ...
}

# Adjust recommendation thresholds
RECOMMENDATION_THRESHOLDS = {
    85: ("STRONG BUY", 1.0),
    75: ("BUY", 0.75),
    # ...
}
```

## 📊 Data & API

- **Source**: Upstox API (requires `UPSTOX_ACCESS_TOKEN` in `.env`)
- **Lookback**: 730 days (2 years) for historical context
- **Updates**: Real-time LTP during market hours

## 🎓 Algorithm Philosophy

> **"Human for Quality, Machine for Timing"**

This algorithm assumes you've already filtered for fundamental quality (strong balance sheet, good management, etc.). It focuses purely on **timing** the entry during corrections.

**Key Features:**
- ✅ Stock-specific calibration (what's normal for HUL vs Zomato)
- ✅ Relative volatility (compares to stock's own history)
- ✅ 100 DMA for active dip-buying (more signals than 200 DMA)
- ✅ Recovery speed as quality proxy

## 🔬 Backtesting

Validate the strategy over historical periods:

```bash
# Quick backtest with sample stocks
cd src/stocks/backtest
python run_backtest.py --csv sample_stocks.csv --mode conservative

# Backtest your watchlist
python run_backtest.py --csv ../stocks_watchlist.csv --mode moderate

# Single stock, 1-year period
python run_backtest.py --symbol ASIANPAINT --name "Asian Paints" \
  --key "NSE_EQ|INE021A01026" --days 365
```

**Features:**
- ✅ No future peeking (strict historical simulation)
- ✅ Multiple risk modes (ultra_conservative to aggressive)
- ✅ Win rate, outperformance vs buy-and-hold
- ✅ Detailed transaction history with scores

**Documentation:**
- Quick start: `backtest/QUICK_START.md`
- Full guide: `backtest/README.md`

## ⚠️ Important Warning

**This algorithm CANNOT detect fundamental deterioration.**

Always check news before buying:
- Management changes
- Regulatory issues
- Earnings misses
- Sector headwinds

A high score means "technical opportunity" not "safe investment."

## 📚 Documentation

- **Algorithm Details**: `docs/TECHNICAL_ALGORITHM_DOCUMENTATION.md`
- **Quick Reference**: `QUICK_START.md`

## 🔄 Version

**v2.0** - Technical Only (100 DMA, Relative Volatility)
- Updated: November 2025
- Based on 6-factor price action system
