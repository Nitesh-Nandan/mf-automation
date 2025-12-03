# Stock Technical Analysis - Backtest Documentation

## Overview

This backtest simulates the performance of the stock technical analysis dip-buying strategy over historical periods. It evaluates whether the algorithm would have outperformed a simple buy-and-hold strategy using actual market data.

## Key Features

### ✅ No Future Peeking
- Uses only historical data available at each decision point
- Simulates real-time decision making
- Realistic transaction timing (weekly evaluation)

### ✅ Handles Rate Limits
- Built-in delays between API calls
- Graceful error handling
- Fetches data once per stock

### ✅ Multiple Risk Modes
- **Ultra Conservative** (threshold: 85) - STRONG BUY signals only
- **Conservative** (threshold: 75) - BUY or better (recommended)
- **Moderate** (threshold: 60) - ACCUMULATE or better
- **Aggressive** (threshold: 50) - NIBBLE or better

### ✅ Comprehensive Metrics
- Returns vs buy-and-hold baseline
- Win rate (% profitable transactions)
- Transaction history with scores
- Per-stock and overall performance
- Score breakdowns for each buy

## How It Works

### Simulation Process

1. **Data Collection**: Fetch 2+ years of historical OHLCV data from Upstox
2. **Time Walking**: Evaluate strategy every 7 days (weekly)
3. **Score Calculation**: Use only data available up to that point
4. **Buy Decisions**: Execute when score ≥ threshold and capital available
5. **Portfolio Tracking**: Monitor portfolio value over time
6. **Comparison**: Compare against buy-and-hold baseline

### Scoring Algorithm

The backtest uses the exact same 6-factor scoring system as production:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Dip Depth** | 0-20 pts | Current dip magnitude from 90-day peak |
| **Historical Context** | 0-25 pts | Comparison with past dips (2-year history) |
| **Mean Reversion** | 0-15 pts | Distance from 100 DMA |
| **Volatility** | 0-10 pts | Risk/reward balance (relative to stock) |
| **Recovery Speed** | 0-20 pts | Historical bounce-back time |
| **Technicals** | 0-10 pts | RSI + Volume + Support levels |

**Total: 100 points**

### Buy Logic

```python
if score >= threshold and capital >= investment_amount:
    execute_buy()
```

- Invest fixed amount (default: ₹10,000) per signal
- Keep remaining capital for future opportunities
- No selling (buy-only strategy, like SIP but smarter)

## Usage

### Quick Start

```bash
# Navigate to the backtest directory
cd src/stocks/backtest

# Batch backtest using sample stocks
python run_backtest.py --csv sample_stocks.csv --mode conservative

# Or use your own watchlist
python run_backtest.py --csv ../stocks_watchlist.csv --mode moderate
```

### Single Stock Backtest

```bash
# Backtest Asian Paints with conservative mode
python run_backtest.py \
  --symbol ASIANPAINT \
  --name "Asian Paints" \
  --key "NSE_EQ|INE021A01026" \
  --mode conservative
```

### Custom Parameters

```bash
# 1-year backtest with higher capital
python run_backtest.py \
  --csv sample_stocks.csv \
  --mode aggressive \
  --days 365 \
  --capital 200000 \
  --investment 20000

# Conservative mode with custom output directory
python run_backtest.py \
  --csv sample_stocks.csv \
  --mode conservative \
  --output ../../backtest_results

# Slower API calls (avoid rate limits)
python run_backtest.py \
  --csv sample_stocks.csv \
  --delay 2.0
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--csv` | Path to CSV file with stocks | - |
| `--symbol` | Stock symbol (for single stock) | - |
| `--name` | Stock name (with --symbol) | - |
| `--key` | Instrument key (with --symbol) | - |
| `--mode` | Risk mode (ultra_conservative, conservative, moderate, aggressive) | conservative |
| `--days` | Number of days to backtest | 730 (2 years) |
| `--capital` | Initial capital per stock | 100000 |
| `--investment` | Amount per buy signal | 10000 |
| `--output` | Output directory for results | . (current) |
| `--delay` | Delay between API calls (seconds) | 1.0 |

### Input CSV Format

Your CSV file should have these columns (see `sample_stocks.csv`):

```csv
name,symbol,instrument_key
Asian Paints,ASIANPAINT,NSE_EQ|INE021A01026
HDFC Bank,HDFCBANK,NSE_EQ|INE040A01034
```

**Required columns:**
- `name`: Full company name
- `symbol`: NSE symbol
- `instrument_key`: Upstox instrument key (format: `NSE_EQ|ISIN`)

### Output Files

The backtest generates two files:

1. **JSON Results** (`backtest_results_{mode}_{timestamp}.json`)
   - Detailed transaction history
   - Portfolio values over time
   - Score breakdowns for each buy
   - Machine-readable format for further analysis

2. **Text Report** (`backtest_report_{mode}_{timestamp}.txt`)
   - Human-readable summary
   - Performance metrics
   - Top trades by return
   - Stock-by-stock analysis

## Interpreting Results

### Key Metrics

#### Strategy Performance
- **Signals**: Number of buy signals triggered
- **Total Invested**: Capital deployed in dip buys
- **Shares Accumulated**: Total shares purchased
- **Avg Buy Price**: Average purchase price
- **Final Price**: Stock price at end of backtest
- **Strategy Return %**: Total return including uninvested capital
- **Win Rate**: % of profitable transactions

#### Baseline Performance
- **Baseline Start Price**: Entry price at start of period
- **Baseline Shares**: Shares if bought at start with full capital
- **Baseline Return %**: Buy-and-hold return

#### Comparison
- **Outperformance**: Strategy return - Baseline return
  - Positive = Strategy beat buy-and-hold ✅
  - Negative = Buy-and-hold was better ❌

### Sample Output

```
🔬 BACKTESTING STOCK STRATEGY - CONSERVATIVE MODE
================================================================================
Period: Last 730 days (~2 years)
Initial Capital: ₹100,000 per stock
Investment per Signal: ₹10,000
Buy Threshold: 75 points
================================================================================

[1/5] Backtesting ASIANPAINT (Asian Paints)...
  Fetching 1095 days of data...
  ✓ Fetched 523 days of data
  Evaluating 74 time points...
  ✅ Completed | Signals: 6 | Return: +18.2% | vs Baseline: +2.5%

[2/5] Backtesting HDFCBANK (HDFC Bank)...
  ✅ Completed | Signals: 4 | Return: +12.1% | vs Baseline: -1.8%

================================================================================
✅ Backtest Complete! 5/5 stocks successful
================================================================================

📊 OVERALL SUMMARY
--------------------------------------------------------------------------------
Stocks Tested: 5
Total Buy Signals: 24
Avg Outperformance: +1.8%
Stocks Beating Baseline: 4/5 (80.0%)

📈 INDIVIDUAL STOCK RESULTS
--------------------------------------------------------------------------------

ASIANPAINT - Asian Paints
  Period: 2023-01-15 to 2024-12-02 (730 days)
  Signals: 6
  Total Invested: ₹60,000
  Avg Buy Price: ₹2,845 | Final Price: ₹3,100
  Strategy Return: +18.2%
  Baseline Return: +15.7%
  Outperformance: +2.5%
  Win Rate: 83.3%
  
  Top 3 Buys:
    1. 2023-03-22 | ₹2,720 | Score: 78 | Return: +14.0%
    2. 2023-08-15 | ₹2,890 | Score: 76 | Return: +7.3%
    3. 2024-02-05 | ₹2,950 | Score: 75 | Return: +5.1%
```

## What to Expect

### Signal Frequency by Mode

Based on typical market conditions:

| Mode | Threshold | Expected Signals/Year | Best For |
|------|-----------|---------------------|----------|
| Ultra Conservative | 85 | 0-2 | Bear markets, crashes |
| Conservative | 75 | 2-4 | Balanced, quality dips |
| Moderate | 60 | 4-8 | Active dip buying |
| Aggressive | 50 | 8-15 | Maximum opportunities |

### Performance Patterns

#### Bull Markets
- **Fewer signals** (stocks don't dip much)
- **Likely underperformance** vs buy-and-hold (expected!)
- Strategy keeps cash waiting for dips
- This is NORMAL and by design

#### Volatile/Sideways Markets
- **Moderate signals** (5-10 per year)
- **Likely outperformance** vs buy-and-hold
- Sweet spot for dip buying
- Strategy shines here

#### Bear Markets/Corrections
- **Many signals** (10-20 per year)
- **Significant outperformance** potential
- Buys during panic
- Validates strategy purpose

### Dip Distribution

Typical breakdown by dip size:

```
5-8%:   40% of buys (moderate dips)
8-10%:  30% of buys (good dips)
10-15%: 20% of buys (excellent dips)
15%+:   10% of buys (crash opportunities)
```

### Win Rate Expectations

- **60-70%**: Good (typical for quality stocks)
- **70-80%**: Very good
- **80%+**: Excellent
- **< 50%**: Review stock quality or threshold

## Troubleshooting

### No Buy Signals

**Problem**: Zero transactions over 1-2 years

**Possible Causes**:
1. Threshold too high for market conditions
2. Strong bull market (no significant dips)
3. Stock doesn't dip much (low volatility)

**Solutions**:
- Try `moderate` or `aggressive` mode
- Increase backtest period to 3 years
- Check if stock is suitable for dip buying

### API Rate Limit Errors (429)

**Problem**: `Error: 429 - Too Many Requests`

**Possible Causes**:
1. Too many stocks, too fast
2. Upstox API rate limits

**Solutions**:
- Increase `--delay` parameter (try 2.0 or 3.0)
- Reduce number of stocks per batch
- Run backtest during off-peak hours

### Strategy Always Underperforms

**Problem**: Consistent negative outperformance

**Possible Causes**:
1. Bull market period (expected behavior)
2. Not enough time for dips to occur
3. Stock selection (avoid momentum stocks)

**Solutions**:
- Check market phase (bull = underperformance is normal)
- Extend backtest to include corrections
- This strategy works on mean-reverting quality stocks
- Wait for full market cycle (3+ years)

### Insufficient Data Error

**Problem**: `Error: Insufficient data for backtest period`

**Possible Causes**:
1. Stock recently listed
2. API data availability limited
3. Requested backtest period too long

**Solutions**:
- Reduce `--days` parameter (try 365 instead of 730)
- Use older, well-established stocks
- Check Upstox data availability

## Technical Details

### Performance Optimization

- Fetches data once per stock (not per evaluation)
- Weekly evaluation (vs daily) for speed and realism
- Efficient indicator calculations
- Minimal API calls

### Data Handling

- Handles missing data gracefully
- Validates minimum data requirements (100+ days)
- Sorts data once, reuses everywhere
- No look-ahead bias (strict historical simulation)

### Accuracy

- Uses actual OHLCV data from Upstox
- No future peeking (strict time-series simulation)
- Realistic transaction costs (0% - add if needed)
- Weekly evaluation (conservative timing)

## Best Practices

### Stock Selection

✅ **Good candidates:**
- Large/mid-cap quality stocks
- Established companies (5+ year track record)
- Mean-reverting behavior
- Your "forever stocks"

❌ **Avoid:**
- Penny stocks
- Momentum/growth stocks (ZOMATO, PAYTM in early days)
- Recently listed companies
- Fundamentally weak stocks

### Mode Selection

| Your Goal | Recommended Mode |
|-----------|-----------------|
| Maximize signals | Moderate/Aggressive |
| Only best opportunities | Conservative |
| Crash-only buying | Ultra Conservative |
| Balanced approach | Conservative |

### Interpreting Outperformance

- **+5% or more**: Excellent strategy fit
- **+2% to +5%**: Good fit
- **-2% to +2%**: Neutral (consider market phase)
- **-2% to -5%**: Likely bull market (expected)
- **-5% or worse**: Review stock selection

## Advanced Usage

### Custom Analysis

The JSON output can be loaded for custom analysis:

```python
import json

with open('backtest_results_conservative_20241202_143022.json') as f:
    results = json.load(f)

# Analyze transaction patterns
for stock_result in results:
    for txn in stock_result['transactions']:
        print(f"{txn['date']}: Score {txn['score']}, "
              f"Dip {txn['breakdown']['change_from_peak_pct']:.1f}%")
```

### Parameter Optimization

Test different thresholds to find optimal cutoff:

```bash
# Test all modes
for mode in ultra_conservative conservative moderate aggressive; do
    python run_backtest.py --csv stocks.csv --mode $mode --output results_$mode
done
```

### Comparison with Production

To validate that backtest matches production algorithm:

1. Run backtest for recent period (last 30 days)
2. Compare scores with live analysis
3. Scores should match exactly for same date/data

## Limitations

### What This Backtest Does NOT Include

1. **Transaction costs** - No brokerage/STT (add 0.5% if needed)
2. **Slippage** - Assumes execution at close price
3. **Dividends** - Not included in returns
4. **Tax** - No LTCG/STCG considerations
5. **Position sizing** - Fixed investment per signal
6. **Selling** - Buy-only strategy (no exit logic)

### Known Issues

- **Rate limits**: Upstox has API limits (use `--delay` to mitigate)
- **Data gaps**: Some stocks may have missing historical data
- **Recent IPOs**: Need 2+ years of data for accurate backtest

## Future Enhancements

### Potential Additions

1. **Transaction Costs**: Add realistic brokerage fees
2. **Tax Impact**: Include LTCG/STCG calculations
3. **Position Sizing**: Dynamic investment based on score
4. **Exit Strategy**: Profit booking / stop loss logic
5. **Sector Analysis**: Performance by sector
6. **Drawdown Analysis**: Maximum portfolio drawdown
7. **Sharpe Ratio**: Risk-adjusted returns

## Support

### Getting Help

1. Check this README first
2. Review sample output files
3. Test with `sample_stocks.csv` first
4. Check `--help` for command options

### Reporting Issues

If you encounter bugs:

1. Note the exact command used
2. Include error message
3. Check if stock has sufficient historical data
4. Try with a known working stock (e.g., ASIANPAINT)

## Related Documentation

- **Algorithm Documentation**: `src/stocks/docs/TECHNICAL_ALGORITHM_DOCUMENTATION.md`
- **Production Code**: `src/stocks/TechnicalAnalysis.py`
- **Scoring Logic**: `src/stocks/TechnicalScore.py`

---

**Happy Backtesting! 📊**

*Remember: Past performance doesn't guarantee future results. This is a tool for strategy validation, not a crystal ball.*

