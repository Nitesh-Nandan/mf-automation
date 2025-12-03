# Quick Start Guide - Stock Backtest

## 🚀 5-Minute Setup

### 1. Prerequisites

Make sure you have:
- ✅ Python environment set up
- ✅ `UPSTOX_ACCESS_TOKEN` in your `.env` file
- ✅ Dependencies installed (`uv sync` or `pip install -r requirements.txt`)

### 2. Test with Sample Stocks

```bash
# Navigate to backtest directory
cd src/stocks/backtest

# Run backtest on sample stocks
python run_backtest.py --csv sample_stocks.csv --mode conservative
```

This will:
- Backtest 5 quality stocks (Asian Paints, HDFC Bank, Infosys, TCS, Reliance)
- Use conservative mode (75+ score threshold)
- Simulate last 2 years
- Generate JSON + text reports

**Expected time**: 3-5 minutes (depends on API speed)

### 3. Check Results

Two files will be created:
```
backtest_results_conservative_YYYYMMDD_HHMMSS.json
backtest_report_conservative_YYYYMMDD_HHMMSS.txt
```

Open the `.txt` file to see human-readable results!

## 📊 Understanding Output

### Console Output
```
[1/5] Backtesting ASIANPAINT (Asian Paints)...
  Fetching 1095 days of data...
  ✓ Fetched 523 days of data
  Evaluating 74 time points...
  ✅ Completed | Signals: 6 | Return: +18.2% | vs Baseline: +2.5%
```

**Key metrics:**
- **Signals**: Number of buy opportunities (6 in 2 years = good)
- **Return**: Total return including uninvested capital
- **vs Baseline**: Outperformance compared to buy-and-hold

### Report File

```
📊 OVERALL SUMMARY
Stocks Tested: 5
Total Buy Signals: 24
Avg Outperformance: +1.8%
Stocks Beating Baseline: 4/5 (80.0%)

📈 INDIVIDUAL STOCK RESULTS

ASIANPAINT - Asian Paints
  Signals: 6
  Total Invested: ₹60,000
  Strategy Return: +18.2%
  Baseline Return: +15.7%
  Outperformance: +2.5%
  Win Rate: 83.3%
```

## 🎯 Next Steps

### Use Your Own Watchlist

Create a CSV file with your stocks:

```csv
name,symbol,instrument_key
Your Stock,SYMBOL,NSE_EQ|INE123456789
```

Then run:
```bash
python run_backtest.py --csv your_watchlist.csv --mode conservative
```

### Try Different Modes

```bash
# More selective (fewer, better signals)
python run_backtest.py --csv sample_stocks.csv --mode ultra_conservative

# More opportunities
python run_backtest.py --csv sample_stocks.csv --mode moderate

# Maximum signals
python run_backtest.py --csv sample_stocks.csv --mode aggressive
```

### Single Stock Backtest

```bash
python run_backtest.py \
  --symbol ASIANPAINT \
  --name "Asian Paints" \
  --key "NSE_EQ|INE021A01026" \
  --mode conservative
```

### Different Time Periods

```bash
# 1 year backtest
python run_backtest.py --csv sample_stocks.csv --days 365

# 3 years backtest
python run_backtest.py --csv sample_stocks.csv --days 1095
```

## 💡 Tips

### Avoiding Rate Limits

If you see `Error: 429 - Too Many Requests`:

```bash
# Add 2-second delay between stocks
python run_backtest.py --csv sample_stocks.csv --delay 2.0
```

### Best Stocks for Backtesting

✅ **Good:**
- Large-cap quality stocks (HDFC, Asian Paints, TCS)
- Established companies (5+ years listed)
- Your "forever stocks"

❌ **Avoid:**
- Recent IPOs (insufficient data)
- Penny stocks
- Highly volatile momentum stocks

### Interpreting Results

**Outperformance:**
- `+5% or more`: Excellent fit for dip buying ⭐⭐⭐
- `+2% to +5%`: Good fit ⭐⭐
- `-2% to +2%`: Neutral (check market phase) ⭐
- `Negative`: Likely bull market period (expected behavior)

**Win Rate:**
- `80%+`: Excellent ⭐⭐⭐
- `70-80%`: Very good ⭐⭐
- `60-70%`: Good ⭐
- `<50%`: Review threshold or stock

## 🔧 Troubleshooting

### No Buy Signals

**Problem**: Zero transactions in 2 years

**Fix**: Try moderate or aggressive mode
```bash
python run_backtest.py --csv sample_stocks.csv --mode moderate
```

### Insufficient Data Error

**Problem**: Stock doesn't have enough history

**Fix**: Use shorter backtest period
```bash
python run_backtest.py --csv sample_stocks.csv --days 365
```

### All Stocks Underperform

**Likely Cause**: Bull market period (this is NORMAL!)

The dip-buying strategy is designed to:
- Outperform in corrections/bear markets ✅
- Match or underperform in bull markets ❌

This is expected behavior - the strategy holds cash waiting for dips.

## 📚 More Information

- Full documentation: `README.md`
- Algorithm details: `../docs/TECHNICAL_ALGORITHM_DOCUMENTATION.md`
- Scoring reference: `../docs/SCORING_REFERENCE.md`

## ❓ Common Questions

**Q: Why does strategy underperform in backtest?**  
A: If testing during a bull market, this is expected. The strategy keeps cash waiting for dips. Try testing across a full market cycle (3+ years) including corrections.

**Q: How many signals should I expect?**  
A: Conservative mode: 2-4 per year. Moderate: 4-8 per year. Depends on market volatility.

**Q: Can I test sell strategy too?**  
A: Not yet. This is a buy-only backtest (like smart SIP). Exit strategy backtest coming soon!

**Q: How accurate is the backtest?**  
A: Very accurate. Uses actual historical data, no future peeking, realistic timing. Only limitation is it assumes execution at close price (no slippage).

---

**Happy Backtesting! 🚀**

*Start with sample_stocks.csv and experiment from there!*

